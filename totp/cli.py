import argparse
import sys
from collections import OrderedDict, defaultdict
from functools import reduce

import totp

# Suggestion from https://stackoverflow.com/a/26379693/302264, refactored
def _ensure_default_subparser(default, parser, args):
    """Ensure a subcommand is present in `args`; if no valid subcommand is
    found, `default` is inserted as the first element of `args`.
    default: the name of the subparser to call by default
    args: the argument list that is to be handed to parse_args()
    """
    def add_default_subcommand(args, default):
        # insert default in first position, this implies no
        # global options without a sub_parsers specified
        args.insert(0, default)

    def has_explicit_subcommand(args, parser):
        return any(sp_name in args
            for action in parser._subparsers._actions
                   if isinstance(action, argparse._SubParsersAction)
            for sp_name in action._name_parser_map.keys())

    for arg in args:
        if arg in ['-h', '--help']:  # global help if no subparser
            return

    if not has_explicit_subcommand(args, parser):
        add_default_subcommand(args, default=default)

def _parse_args(args):
    parser = argparse.ArgumentParser(
        description='Print a TOTP token getting the shared key from pass(1).'
    )

    subparsers = parser.add_subparsers(dest='command')

    # ---
    add_parser = subparsers.add_parser('add',
        description='Add a new TOTP entry to the database.',
        help='add a new TOTP entry to the database')

    add_parser.add_argument('identifier',
        help='the identifier under the \'2fa\' folder where the key should be saved')

    # ---
    show_parser = subparsers.add_parser('show',
        description='Show the current TOTP token for a registered entry.',
        help='(default action) show the current TOTP token for a registered entry')

    show_parser.add_argument('-s', dest='offset_seconds', metavar='SECONDS', default=0,
        help='offset the clock by the given number of seconds')

    show_parser.add_argument('identifier',
        help='the identifier by which the key can be found under the \'2fa\' folder')

    # ---
    _ensure_default_subparser('show', parser, args)
    return parser.parse_args(args)

def run():
    args = _parse_args(sys.argv[1:])
    try:
        _run(args)
    except KeyboardInterrupt:
        print()

def _run(args):
    if args.command == 'add':
        totp.add_pass_entry(args.identifier)
    elif args.command == 'show':
        totp.generate_token(args.identifier, seconds=args.offset_seconds)
    else:
        assert False, 'unexpected command: %r' % args.command

if __name__ == '__main__':
    run()
