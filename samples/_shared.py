####
# Shared helpers for the sample scripts in this directory.
#
# The most important thing here is `resolve_credentials`, which lets samples
# accept a Tableau server URL, site, and credentials from three sources:
#
#   1. Command-line arguments (useful for CI, but note that these end up in
#      shell history and process listings, so avoid them for real secrets).
#   2. Environment variables. We look for a `.env` file in the current
#      working directory, in the samples/ directory, and at the repository
#      root, in that order, and load whichever we find first -- only the
#      standard `KEY=value` lines, no external dependency required.
#   3. Interactive prompts. Missing values are asked for on stdin when
#      stdin is a terminal; secrets are read with `getpass.getpass` so they
#      are not echoed. In non-interactive contexts (CI, piped input) we skip
#      the prompts and let `build_auth` raise instead of hanging on `input()`.
#
# CLI args take precedence, then environment, then interactive prompt.
# This lets a user set defaults in a `.env` file and override individual
# values on the command line.
#
# Sign-in short flags follow the tabcmd convention (-s server, -t site,
# -u username, -p password). --token-name and --token-value do not have
# short flags because tabcmd does not either and re-using a letter here
# would silently accept a token as a password on old command lines.
####

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path
from typing import Iterable

import tableauserverclient as TSC

# Recognized environment variable names, in the order we look them up.
# Older samples used TABLEAU_SERVER etc; keep those working as aliases.
_ENV_ALIASES: dict[str, tuple[str, ...]] = {
    "server": ("TABLEAU_SERVER", "SERVER"),
    "site": ("TABLEAU_SITE", "SITE"),
    "token_name": ("TABLEAU_TOKEN_NAME", "TOKEN_NAME"),
    "token_value": ("TABLEAU_TOKEN_VALUE", "TOKEN_VALUE"),
    "username": ("TABLEAU_USERNAME", "USERNAME"),
    "password": ("TABLEAU_PASSWORD", "PASSWORD"),
    "jwt": ("TABLEAU_JWT", "JWT"),
    "jwt_file": ("TABLEAU_JWT_FILE", "JWT_FILE"),
}


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the sign-in and logging arguments used by every sample.

    Short flags follow the tabcmd convention: -s server, -t site,
    -u username, -p password, -l logging-level. --token-name /
    --token-value and --jwt / --jwt-file intentionally have no short
    flag; re-using letters here risked silently accepting a token as
    a password on scripts that pre-date the shared helper. All args
    are optional; missing values are pulled from the environment or
    prompted for interactively.
    """
    parser.add_argument("--server", "-s", help="server address (env: TABLEAU_SERVER)")
    parser.add_argument("--site", "-t", help="site content URL (env: TABLEAU_SITE)")
    parser.add_argument(
        "--token-name",
        help="name of the personal access token used to sign into the server " "(env: TABLEAU_TOKEN_NAME)",
    )
    parser.add_argument(
        "--token-value",
        help="value of the personal access token used to sign into the server "
        "(env: TABLEAU_TOKEN_VALUE). Prefer the env var or interactive prompt over the "
        "command line so the secret does not land in shell history.",
    )
    parser.add_argument(
        "--username",
        "-u",
        help="username to sign into the server (env: TABLEAU_USERNAME). Only used if "
        "no personal access token or JWT is supplied.",
    )
    parser.add_argument(
        "--password",
        "-p",
        help="password (env: TABLEAU_PASSWORD). Prefer the env var or interactive " "prompt over the command line.",
    )
    parser.add_argument(
        "--jwt",
        help="encoded JSON Web Token for Connected-App sign-in (env: TABLEAU_JWT). "
        "Mutually exclusive with token/username auth; see JWTAuth in the docs.",
    )
    parser.add_argument(
        "--jwt-file",
        help="path to a file whose contents are the encoded JWT (env: TABLEAU_JWT_FILE). "
        "Useful for pipelines that mint a JWT into a file rather than an env var.",
    )
    parser.add_argument(
        "--env-file",
        help="path to a .env-style file with KEY=value lines to load. If omitted, "
        ".env is looked for in the current directory, the samples/ directory, and "
        "the repository root, and the first one found is loaded.",
    )
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )


def _load_env_file(path: Path) -> None:
    """Very small `.env` loader: `KEY=value` per line, `#` for comments.

    We do not want a runtime dependency on python-dotenv for the samples,
    so this parses just the common cases. Existing env vars are not
    overwritten -- a value already in `os.environ` wins.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _first_env(names: Iterable[str]) -> str | None:
    for name in names:
        val = os.environ.get(name)
        if val:
            return val
    return None


def _candidate_env_paths() -> list[Path]:
    """Locations we check for a .env file, in priority order.

    cwd first (so the invoker can override), then the directory that holds
    this shared module (samples/), then the repository root one level up.
    """
    module_dir = Path(__file__).resolve().parent
    return [
        Path.cwd() / ".env",
        module_dir / ".env",
        module_dir.parent / ".env",
    ]


def resolve_credentials(args: argparse.Namespace, *, allow_prompt: bool = True) -> None:
    """Fill in server/site/credential values on `args` from env or prompt.

    Precedence for each field: existing value on `args` > environment variable
    > interactive prompt (only when allow_prompt is true AND stdin is a TTY).

    Pass `allow_prompt=False`, or run with stdin redirected (CI, piped input),
    to skip the prompts entirely; the caller should then verify the fields it
    needs are set, or let `build_auth` raise a clear ValueError.
    """
    # Load `.env` file if one is requested or available.
    env_file = getattr(args, "env_file", None)
    if env_file:
        _load_env_file(Path(env_file))
    else:
        for candidate in _candidate_env_paths():
            if candidate.is_file():
                _load_env_file(candidate)
                break

    # For each field, prefer the CLI arg, then env, then prompt.
    for field, env_names in _ENV_ALIASES.items():
        current = getattr(args, field, None)
        if current:
            continue
        env_val = _first_env(env_names)
        if env_val:
            setattr(args, field, env_val)

    # If a JWT file was provided, read its contents into args.jwt (unless the
    # caller also passed --jwt directly, in which case the direct value wins).
    jwt_file = getattr(args, "jwt_file", None)
    if jwt_file and not getattr(args, "jwt", None):
        try:
            args.jwt = Path(jwt_file).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise SystemExit(f"Could not read --jwt-file {jwt_file!r}: {exc}") from exc

    # Skip prompting entirely if the caller opted out or stdin is not a
    # terminal. `input()` on a closed/piped stdin either blocks forever or
    # raises EOFError; neither is what a scripted invocation wants.
    if not allow_prompt or not sys.stdin.isatty():
        return

    # Prompt for what's still missing. We only prompt for the pieces we
    # actually need: server URL, and one of JWT / token / username+password.
    if not getattr(args, "server", None):
        args.server = input("Tableau server URL: ").strip()

    # Site is optional (empty string is the default site) so we don't prompt.

    has_jwt = bool(getattr(args, "jwt", None))
    has_token = bool(getattr(args, "token_name", None) and getattr(args, "token_value", None))
    has_user = bool(getattr(args, "username", None) and getattr(args, "password", None))

    if has_jwt or has_token or has_user:
        return

    # Partial info supplied -- fill in the matching missing piece.
    if getattr(args, "token_name", None) and not getattr(args, "token_value", None):
        args.token_value = getpass.getpass(f"Personal access token value for '{args.token_name}': ")
        return
    if getattr(args, "username", None) and not getattr(args, "password", None):
        args.password = getpass.getpass(f"Password for '{args.username}': ")
        return

    # Fully unspecified: default to PAT since that's what the docs recommend.
    print("No credentials found in args or environment. Sign in with a personal access token.")
    print("(Set TABLEAU_TOKEN_NAME / TABLEAU_TOKEN_VALUE in your env or a .env file to skip this prompt.)")
    args.token_name = input("Personal access token name: ").strip()
    args.token_value = getpass.getpass("Personal access token value: ")


def build_auth(args: argparse.Namespace) -> TSC.TableauAuth | TSC.PersonalAccessTokenAuth | TSC.JWTAuth:
    """Return the appropriate auth object based on what's set on `args`.

    Priority is JWT > PAT > username/password: a script that has a JWT
    minted for a specific session should never fall back to a longer-lived
    credential if the JWT-adjacent fields were left set by accident.
    """
    site = getattr(args, "site", None) or ""
    if getattr(args, "jwt", None):
        return TSC.JWTAuth(args.jwt, site_id=site)
    if getattr(args, "token_name", None) and getattr(args, "token_value", None):
        return TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=site)
    if getattr(args, "username", None) and getattr(args, "password", None):
        return TSC.TableauAuth(args.username, args.password, site_id=site)
    raise ValueError(
        "No usable credentials found. Provide --jwt/--jwt-file, "
        "--token-name/--token-value, --username/--password, or set the "
        "corresponding env vars."
    )
