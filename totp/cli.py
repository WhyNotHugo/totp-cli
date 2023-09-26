import argparse
import getpass
import sys
from base64 import b32decode
from collections import namedtuple

import totp

_subcommands = {}

_argument = namedtuple("_argument", ["args", "kwargs"])


def argument(*args, **kwargs):
    return _argument(args, kwargs)


def subcommand(name, *args, **kwargs):
    def decorator(func):
        _subcommands[name] = (args, kwargs, func)

    return decorator


def _parse_args(args):
    parser = argparse.ArgumentParser(
        description="Print a TOTP token getting the shared key from pass(1)."
    )

    subparsers = parser.add_subparsers(dest="command")
    aliases = {}

    for name, (_args, kwargs, func) in _subcommands.items():
        _parser = subparsers.add_parser(name, **kwargs)
        _parser.set_defaults(func=func)
        for arg in _args:
            _parser.add_argument(*arg.args, **arg.kwargs)

        _aliases = kwargs.get("aliases", ())
        for alias in _aliases:
            aliases[alias] = name

    def replace_aliases(args, aliases):
        for i, arg in enumerate(args):
            if arg in aliases:
                args[i] = aliases[arg]

    def add_default_subcommand_if_omitted(args, default):
        if not any(
            arg in ("-h", "--help") or arg in subparsers.choices for arg in args
        ):
            args.insert(0, default)

    replace_aliases(args, aliases)
    add_default_subcommand_if_omitted(args, "show")

    return parser.parse_args(args)


def run():
    args = _parse_args(sys.argv[1:])
    try:
        args.func(args)
    except totp.BackendError as e:
        print("%s returned an error:\n%s" % (e.backend_name, e))
        raise SystemExit(-1)
    except KeyboardInterrupt:
        print()


@subcommand(
    "add",
    argument(
        "identifier",
        help="the identifier under the '2fa' folder where the key should be saved",
    ),
    argument("-u", "--uri", help="an optional otpauth uri to read the entry data from"),
    aliases=["-a"],
    description="Add a new TOTP entry to the database.",
    help="add a new TOTP entry to the database",
)
def _cmd_add(args):
    if args.uri:
        add_uri(args.identifier, args.uri)
    else:
        add_interactive(args.identifier)


def input_shared_key():
    while True:
        try:
            shared_key = totp.normalize_secret(getpass.getpass("Shared key: "))
            b32decode(shared_key.upper())
            if shared_key == "":
                raise ValueError("The key entered was empty")
            return shared_key
        except ValueError as err:
            print(*err.args)


def add_interactive(path):
    token_length = input("Token length [%d]: " % totp.DIGITS_DEFAULT)
    token_length = int(token_length) if token_length else totp.DIGITS_DEFAULT

    shared_key = input_shared_key()

    totp.add_pass_entry(path, token_length, shared_key)


def add_uri(path, uri):
    totp.add_pass_entry_from_uri(path, uri)


@subcommand(
    "show",
    argument(
        "-s",
        dest="offset_seconds",
        metavar="SECONDS",
        default=0,
        help="offset the clock by the given number of seconds",
    ),
    argument(
        "-n",
        "--nocopy",
        action="store_true",
        help="Do not copy the token, only show it.",
    ),
    argument(
        "identifier",
        help="the identifier by which the key can be found under the '2fa' folder",
    ),
    description="Show the current TOTP token for a registered entry.",
    help="(default action) show the current TOTP token for a registered entry",
)
def _cmd_show(args):
    totp.generate_token(
        args.identifier, seconds=args.offset_seconds, to_clipboard=not args.nocopy
    )


if __name__ == "__main__":
    run()
