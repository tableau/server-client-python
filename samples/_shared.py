####
# Shared helpers for the sample scripts in this directory.
#
# The most important thing here is `resolve_credentials`, which lets samples
# accept a Tableau server URL, site, and credentials from three sources:
#
#   1. Command-line arguments (useful for CI, but note that these end up in
#      shell history and process listings, so avoid them for real secrets).
#   2. Environment variables. If a `.env` file exists next to the sample
#      being run, or in the current working directory, we load it first --
#      only the standard `KEY=value` lines, no external dependency required.
#   3. Interactive prompts. Missing values are asked for on stdin; secrets
#      are read with `getpass.getpass` so they are not echoed.
#
# CLI args take precedence, then environment, then interactive prompt.
# This lets a user set defaults in a `.env` file and override individual
# values on the command line.
####

from __future__ import annotations

import argparse
import getpass
import os
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
}


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the sign-in and logging arguments used by every sample.

    Kept in sync with the historical inline definitions so no existing
    command line breaks. All arguments are optional -- missing values
    are pulled from the environment or prompted for interactively.
    """
    parser.add_argument("--server", "-s", help="server address (env: TABLEAU_SERVER)")
    parser.add_argument("--site", "-S", help="site content URL (env: TABLEAU_SITE)")
    parser.add_argument(
        "--token-name",
        "-p",
        help="name of the personal access token used to sign into the server " "(env: TABLEAU_TOKEN_NAME)",
    )
    parser.add_argument(
        "--token-value",
        "-v",
        help="value of the personal access token used to sign into the server "
        "(env: TABLEAU_TOKEN_VALUE). Prefer the env var or interactive prompt over the "
        "command line so the secret does not land in shell history.",
    )
    parser.add_argument(
        "--username",
        help="username to sign into the server (env: TABLEAU_USERNAME). Only used if "
        "no personal access token is supplied.",
    )
    parser.add_argument(
        "--password",
        help="password (env: TABLEAU_PASSWORD). Prefer the env var or interactive " "prompt over the command line.",
    )
    parser.add_argument(
        "--env-file",
        help="path to a .env-style file with KEY=value lines to load. If omitted, "
        ".env in the current directory is loaded automatically when present.",
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


def resolve_credentials(args: argparse.Namespace, *, allow_prompt: bool = True) -> None:
    """Fill in server/site/credential values on `args` from env or prompt.

    Precedence for each field: existing value on `args` > environment variable
    > interactive prompt (if allow_prompt and stdin is a terminal).

    Pass `allow_prompt=False` in CI environments where blocking on input would
    hang the job; the caller should then verify the fields it needs are set.
    """
    # Load `.env` file if one is requested or available.
    env_file = getattr(args, "env_file", None)
    if env_file:
        _load_env_file(Path(env_file))
    else:
        default_env = Path.cwd() / ".env"
        if default_env.is_file():
            _load_env_file(default_env)

    # For each field, prefer the CLI arg, then env, then prompt.
    for field, env_names in _ENV_ALIASES.items():
        current = getattr(args, field, None)
        if current:
            continue
        env_val = _first_env(env_names)
        if env_val:
            setattr(args, field, env_val)

    if not allow_prompt:
        return

    # Prompt for what's still missing. We only prompt for the pieces we
    # actually need: server URL, and one of token or username/password.
    if not getattr(args, "server", None):
        args.server = input("Tableau server URL: ").strip()

    # Site is optional (empty string is the default site) so we don't prompt.

    has_token = getattr(args, "token_name", None) and getattr(args, "token_value", None)
    has_user = getattr(args, "username", None) and getattr(args, "password", None)

    if has_token or has_user:
        return

    # Nothing configured yet. Ask which auth method to use.
    if getattr(args, "token_name", None) or getattr(args, "username", None):
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


def build_auth(args: argparse.Namespace) -> TSC.TableauAuth | TSC.PersonalAccessTokenAuth:
    """Return the appropriate auth object based on what's set on `args`."""
    site = getattr(args, "site", None) or ""
    if getattr(args, "token_name", None) and getattr(args, "token_value", None):
        return TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=site)
    if getattr(args, "username", None) and getattr(args, "password", None):
        return TSC.TableauAuth(args.username, args.password, site_id=site)
    raise ValueError(
        "No usable credentials found. Provide --token-name/--token-value, "
        "--username/--password, or set the corresponding env vars."
    )


def sign_in(args: argparse.Namespace, *, use_server_version: bool = True) -> TSC.Server:
    """Convenience helper: resolve credentials, build the server, and sign in.

    The caller is responsible for calling `server.auth.sign_out()` or using
    the `with server.auth.sign_in(...)` context manager pattern themselves
    when they need finer control. This helper is intended for the small
    samples that just want a signed-in server object to poke at.
    """
    resolve_credentials(args)
    auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=use_server_version)
    server.auth.sign_in(auth)
    return server
