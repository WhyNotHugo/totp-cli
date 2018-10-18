#!/usr/bin/env python
#
# Print a TOTP token getting the shared key from pass(1).

import getpass
import os
import platform
import re
import subprocess
import sys
from base64 import b32decode

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

    while True:
        try:
            shared_key = return_secret(getpass.getpass('Shared key: '))
            b32decode(shared_key)
            if shared_key == "":
                raise ValueError('The key entered was empty')
            break
        except ValueError as err:
            print(err.args)

    pass_entry = "{}\ndigits: {}\n".format(shared_key, token_length)

    p = subprocess.Popen(
        ['pass', 'insert', '-m', '-f', code_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    pass_output, err = p.communicate(
        input=bytearray(pass_entry, encoding='utf-8')
    )

    if len(err) > 0:
        print("pass returned an error:")
        print(err)
        sys.exit(-1)


def get_pass_entry(path):
    """Return the entire entry as provided via pass."""
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

def return_secret(pass_entry):
    pass_length = len(pass_entry)
    if pass_length % 8 == 0:
        secret = pass_entry
        return secret
    else:
        closestmultiple = 8 * (int(pass_length / 8) + (pass_length % 8 > 0))
        secret = pass_entry.ljust(closestmultiple,'=')
        return secret

def generate_token(path, seconds=0):
    """Generate the TOTP token for the given path and the given time offset"""
    import time
    clock = time.time() + float(seconds)

    pass_entry = get_pass_entry(path)

    # Remove the trailing newline or any other custom data users might have
    # saved:
    pass_entry = pass_entry.splitlines()

    secret = return_secret(pass_entry[0])

    digits = get_length(pass_entry)
    token = onetimepass.get_totp(secret, as_string=True, token_length=digits,
                                 clock=clock)

    print("The totp token for " + sys.argv[1] + " is:\n" + token.decode())
    copy_to_clipboard(token)

def help():
    print("Usage: totp [option] service")
    print("Options:")
    print("-a          : Add the named service to pass")
    print("-h          : This help")
    print("-s -/+[sec] : Add an offset to the time.")

def run():
    if len(sys.argv) == 1:
        help()
    elif sys.argv[1] == '-a':
        add_pass_entry(sys.argv[2])
    elif sys.argv[1] == '-s':
        generate_token(sys.argv[3], seconds=sys.argv[2])
    elif sys.argv[1] == '-h':
        help()
    else:
        generate_token(sys.argv[1])


if __name__ == '__main__':
    run()
