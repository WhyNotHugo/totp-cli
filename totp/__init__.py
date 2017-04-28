#!/usr/bin/env python
#
# Print a TOTP token getting the shared key from pass(1).

import os
import platform
import re
import subprocess
import sys

import getpass

import onetimepass


def get_length(pass_entry):
    """Return the required token length."""
    for line in pass_entry:
        if line.lower().startswith('digits:'):
            return int(re.search('\d+', line).group())

    return 6


def add_pass_entry(path):
    """Add a new entry via pass."""
    code_path = "2fa/{}/code"
    code_path = code_path.format(path)

    token_length = input('Token length [6]: ')
    token_length = int(token_length) if token_length else 6

    shared_key = getpass.getpass('Shared key: ')

    pass_entry = "digits: {}\n{}".format(token_length, shared_key)

    p = subprocess.Popen(
        ['pass', 'insert', '-m', code_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    pass_output, err = p.communicate(input=bytearray(pass_entry,encoding='utf-8'))

    if len(err) > 0:
        print("pass returned an error:")
        print(err)
        sys.exit(-1)


def get_pass_entry(path):
    """Return the entrie entry as provided via pass."""
    code_path = "2fa/{}/code"
    code_path = code_path.format(path)

    p = subprocess.Popen(
        ['pass', code_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    pass_output, err = p.communicate()

    if len(err) > 0:
        print("pass returned an error:")
        print(err)
        sys.exit(-1)

    return pass_output.decode()


def copy_to_clipboard(text):
    try:
        if platform.system() == 'Darwin':
            command = ['pbcopy']
        elif platform.system() == 'Windows':
            command = ['clip']
        else:
            selection = os.environ.get(
                'PASSWORD_STORE_X_SELECTION',
                'clipboard',
            )
            command = ['xclip', '-selection', selection]

        p = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        p.stdin.write(text)
        p.stdin.close()
        p.wait()
    except FileNotFoundError:
        print(
            '{} not found. Not copying code'.format(command[0]),
            file=sys.stderr,
        )


def generate_token(path):
    """Generate the TOTP token for the given path"""
    pass_entry = get_pass_entry(path)

    # Remove the trailing newline or any other custom data users might have
    # saved:
    pass_entry = pass_entry.splitlines()
    secret = pass_entry[0]

    digits = get_length(pass_entry)
    token = onetimepass.get_totp(secret, as_string=True, token_length=digits)

    print(token.decode())
    copy_to_clipboard(token)


def run():
    if sys.argv[1] == '-a':
        add_pass_entry(sys.argv[2])
    else:
        generate_token(sys.argv[1])


if __name__ == '__main__':
    run()
