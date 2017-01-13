#!/usr/bin/env python
#
# Print a TOTP token getting the shared key from pass(1).

import os
import re
import subprocess
import sys

import onetimepass


def get_length(pass_entry):
    """Return the required token length."""
    for line in pass_entry:
        if line.lower().startswith('digits:'):
            return int(re.search('\d+', line).group())

    return 6


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
    selection = os.environ.get('PASSWORD_STORE_X_SELECTION', 'clipboard')
    try:
        p = subprocess.Popen(
            ['xclip', '-selection', selection],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        print('xclip not found. Not copying code', file=sys.stderr)

    p.stdin.write(text)
    p.stdin.close()
    p.wait()


def run():
    pass_entry = get_pass_entry(sys.argv[1])

    # Remove the trailing newline or any other custom data users might have
    # saved:
    pass_entry = pass_entry.splitlines()
    secret = pass_entry[0]

    digits = get_length(pass_entry)
    token = onetimepass.get_totp(secret, as_string=True, token_length=digits)

    print(token.decode())
    copy_to_clipboard(token)


if __name__ == '__main__':
    run()
