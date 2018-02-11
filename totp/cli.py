import argparse
import sys
from collections import OrderedDict, defaultdict, namedtuple
from functools import reduce

import totp

_subcommands = {}

_argument = namedtuple('argument', ['args', 'kwargs'])
def argument(*args, **kwargs):
    return _argument(args, kwargs)

def subcommand(name, *args, **kwargs):
    def decorator(func):
        _subcommands[name] = (args, kwargs, func)
    return decorator

def _parse_args(args):
    parser = argparse.ArgumentParser(
        description='Print a TOTP token getting the shared key from pass(1).'
    )

    subparsers = parser.add_subparsers(dest='command')
    aliases = {}

    for name, (_args, kwargs, func) in _subcommands.items():
        _parser = subparsers.add_parser(name, **kwargs)
        _parser.set_defaults(func=func)
        for arg in _args:
            _parser.add_argument(*arg.args, **arg.kwargs)

        _aliases = kwargs.get('aliases', ())
        for alias in _aliases:
            aliases[alias] = name

    def replace_aliases(args, aliases):
        for i, arg in enumerate(args):
            if arg in aliases:
                args[i] = aliases[arg]

    def add_default_subcommand_if_omitted(args, default):
        if not any(arg in ('-h', '--help') or arg in subparsers.choices for arg in args):
            args.insert(0, default)

    replace_aliases(args, aliases)
    add_default_subcommand_if_omitted(args, 'show')

    return parser.parse_args(args)

def run():
    args = _parse_args(sys.argv[1:])
    try:
        args.func(args)
    except KeyboardInterrupt:
        print()

@subcommand('add',
    argument('identifier',
        help='the identifier under the \'2fa\' folder where the key should be saved'),
    aliases=['-a'],
    description='Add a new TOTP entry to the database.',
    help='add a new TOTP entry to the database')
def _cmd_add(args):
    totp.add_pass_entry(args.identifier)

@subcommand('show',
    argument('-s', dest='offset_seconds', metavar='SECONDS', default=0,
        help='offset the clock by the given number of seconds'),
    argument('identifier',
        help='the identifier by which the key can be found under the \'2fa\' folder'),
    description='Show the current TOTP token for a registered entry.',
    help='(default action) show the current TOTP token for a registered entry')
def _cmd_show(args):
    totp.generate_token(args.identifier, seconds=args.offset_seconds)

if __name__ == '__main__':
    run()
