####
# This sample demonstrates three ways to supply Tableau credentials --
#
#   1. Command-line arguments      (highest precedence)
#   2. TABLEAU_* environment variables
#   3. Interactive password prompt via --interactive (password only)
#
# Any credential missing from the CLI is looked up in the environment;
# with --interactive, a missing password is prompted for on the terminal
# via getpass. PATs are never prompted for; nobody wants to type a
# 40-character random string.
#
# Environment variables are TABLEAU_-prefixed to avoid collision with
# generic shell vars like USERNAME (which Windows sets automatically):
#   TABLEAU_SERVER       (required) Server URL, e.g. https://10ax.online.tableau.com
#   TABLEAU_SITE         (optional) Site content URL; "" for the default site
#   TABLEAU_TOKEN_NAME   PAT name  (preferred if both PAT vars are set)
#   TABLEAU_TOKEN        PAT value (preferred if both PAT vars are set)
#   TABLEAU_USERNAME     username  (fallback if both basic vars are set)
#   TABLEAU_PASSWORD     password  (fallback if both basic vars are set)
#   TABLEAU_API_VERSION  (optional) Pin REST API version; if absent, the
#                        sample negotiates with the server.
#
# To run this sample, you must have installed Python 3.10 or later.
####

import argparse
import getpass
import logging
import os
import sys

import tableauserverclient as TSC

logger = logging.getLogger(__name__)


def get_env(key: str, default: str | None = None) -> str | None:
    """Return the value of environment variable ``key``, or ``default`` if unset."""
    return os.environ.get(key, default)


# If a sample has additional arguments, it should call this method and then add its
# own; otherwise it can just call set_up_and_log_in().
def sample_define_common_options(parser: argparse.ArgumentParser) -> None:
    """Add the standard credential/logging arguments to an argparse parser."""
    parser.add_argument("--server", "-s", help="server address")
    parser.add_argument("--site", "-t", help="site content URL; '' for the default site")
    auth = parser.add_mutually_exclusive_group(required=False)
    auth.add_argument("--token-name", "-tn", help="name of the personal access token used to sign into the server")
    auth.add_argument("--username", "-u", help="username to sign into the server")

    parser.add_argument("--token-value", "-tv", help="value of the personal access token used to sign into the server")
    parser.add_argument("--password", "-p", help="password used to sign into the server")
    parser.add_argument("--api-version", help="pin a REST API version; otherwise auto-negotiate with the server")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="prompt for a missing password via getpass (requires a TTY)",
    )
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )


def resolve_credentials(args: argparse.Namespace) -> argparse.Namespace:
    """Populate credential fields on ``args`` from TABLEAU_* env vars, and
    (with ``--interactive``) an interactive password prompt.

    Precedence per field: CLI arg > TABLEAU_* env var > (password only,
    when ``--interactive`` is set, ``--username`` is set, and stdin is a
    TTY) getpass prompt.

    Raises ``ValueError`` on a partial credential pair (username without
    password, or token-name without token-value), or if ``--interactive``
    was requested but stdin is not a TTY so the prompt would hang.
    """
    field_env = {
        "server": "TABLEAU_SERVER",
        "site": "TABLEAU_SITE",
        "token_name": "TABLEAU_TOKEN_NAME",
        "token_value": "TABLEAU_TOKEN",
        "username": "TABLEAU_USERNAME",
        "password": "TABLEAU_PASSWORD",
        "api_version": "TABLEAU_API_VERSION",
    }
    for field, env_var in field_env.items():
        if getattr(args, field, None) is None:
            setattr(args, field, get_env(env_var))

    if args.interactive and args.username and not args.password:
        if not sys.stdin.isatty():
            raise ValueError(
                "--interactive requires a TTY; set TABLEAU_PASSWORD/--password " "or run from a real terminal"
            )
        args.password = getpass.getpass(f"Password for {args.username}: ")

    if bool(args.token_name) ^ bool(args.token_value):
        missing = "TABLEAU_TOKEN/--token-value" if args.token_name else "TABLEAU_TOKEN_NAME/--token-name"
        raise ValueError(f"Partial PAT credentials: {missing} is not set")
    if bool(args.username) ^ bool(args.password):
        missing = "TABLEAU_PASSWORD/--password" if args.username else "TABLEAU_USERNAME/--username"
        raise ValueError(f"Partial basic credentials: {missing} is not set")

    return args


def build_server_and_auth(
    args: argparse.Namespace,
) -> tuple[TSC.Server, TSC.TableauAuth | TSC.PersonalAccessTokenAuth]:
    """Build the Server and Auth objects from resolved args. Does NOT sign in.

    Callers who want to control the sign-in scope themselves (e.g. wrap it
    in ``with server.auth.sign_in(auth): ...``) should use this instead of
    :func:`sample_connect_to_server`.
    """
    if not args.server:
        raise ValueError("Server URL is required: pass --server or set TABLEAU_SERVER")

    site = args.site or ""

    if args.token_name and args.token_value:
        auth: TSC.TableauAuth | TSC.PersonalAccessTokenAuth = TSC.PersonalAccessTokenAuth(
            token_name=args.token_name, personal_access_token=args.token_value, site_id=site
        )
        logger.info("Using PAT authentication")
    elif args.username and args.password:
        auth = TSC.TableauAuth(username=args.username, password=args.password, site_id=site)
        logger.info("Using username/password authentication")
    else:
        raise ValueError(
            "No credentials found: set --token-name/--token-value "
            "(or TABLEAU_TOKEN_NAME/TABLEAU_TOKEN) or --username/--password "
            "(or TABLEAU_USERNAME/TABLEAU_PASSWORD)"
        )

    if args.api_version:
        server = TSC.Server(args.server, use_server_version=False)
        server.version = args.api_version
    else:
        server = TSC.Server(args.server, use_server_version=True)

    return server, auth


def sample_connect_to_server(args: argparse.Namespace) -> TSC.Server:
    """Resolve credentials, build the Server and Auth objects, and sign in.

    Returns a Server that has an active session. The caller is responsible
    for signing out (or use :func:`build_server_and_auth` and wrap the
    sign-in yourself with a ``with`` block).
    """
    resolve_credentials(args)
    server, auth = build_server_and_auth(args)
    identity = args.token_name or args.username
    print(f"\nSigning in...\nServer: {args.server}\nSite: {args.site or '(default)'}\nAs: {identity}")
    server.auth.sign_in(auth)
    return server


def set_up_and_log_in() -> None:
    parser = argparse.ArgumentParser(description="Log in to Tableau Server.")
    sample_define_common_options(parser)
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    server = sample_connect_to_server(args)
    info = server.server_info.get()
    print(f"Product version: {info.product_version}")
    print(f"REST API version: {server.version}")
    print(f"Site: {server.site_id}  User: {server.user_id}")


if __name__ == "__main__":
    set_up_and_log_in()
