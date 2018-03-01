#!/usr/bin/env python
#
# Print a TOTP token getting the shared key from pass(1).

import os
import platform
import re
import subprocess
import sys
import urllib.parse

import onetimepass


DIGITS_DEFAULT = 6


class BackendError(Exception):
    backend_name = '<none>'

    def __init__(self, msg):
        self.msg = msg

class PassBackendError(BackendError):
    backend_name = 'pass'


def _read_backend_error(err):
    if isinstance(err, bytes):
        try:
            err = err.decode('utf-8')
        except UnicodeDecodeError:
            return bytestr
    return err.rstrip('\n')


class ValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg

def validate(*args):
    for (validator, error_message) in args:
        if not validator():
            raise ValidationError(error_message)


def get_length(pass_entry):
    """Return the required token length."""
    for line in pass_entry:
        if line.lower().startswith('digits:'):
            return int(re.search('\d+', line).group())

    return 6


def add_pass_entry_from_uri(path, uri):
    parsed = parse_otpauth_uri(uri)
    add_pass_entry(path, parsed['digits'], parsed['secret'])


def add_pass_entry(path, token_length, shared_key):
    """Add a new entry via pass."""
    code_path = "2fa/{}/code"
    code_path = code_path.format(path)

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
        raise PassBackendError(_read_backend_error(err))


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
        raise PassBackendError(_read_backend_error(err))

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


def normalize_secret(secret):
    s = secret.replace(' ', '')

    if len(s) % 8 != 0:
        missing = 8 - (len(s) % 8)
        s += '=' * missing

    return s


def generate_token(path, seconds=0):
    """Generate the TOTP token for the given path and the given time offset"""
    import time
    clock = time.time() + float(seconds)

    pass_entry = get_pass_entry(path)

    # Remove the trailing newline or any other custom data users might have
    # saved:
    pass_entry = pass_entry.splitlines()
    secret = normalize_secret(pass_entry[0])

    digits = get_length(pass_entry)
    token = onetimepass.get_totp(secret, as_string=True, token_length=digits,
                                 clock=clock)

    print(token.decode())
    copy_to_clipboard(token)


def parse_otpauth_uri(uri):
    parsed = urllib.parse.urlsplit(uri)
    query = urllib.parse.parse_qs(parsed.query)

    secret = query.get('secret', [])
    digits = query.get('digits', [])
    issuer = query.get('issuer', [])

    validate(
        (lambda: parsed.scheme == 'otpauth', 'invalid URI scheme: %s' % parsed.scheme),
        (lambda: parsed.netloc == 'totp', 'unsupported key type: %s' % parsed.netloc),
        (lambda: len(secret) <= 1, 'too many \'secret\' arguments'),
        (lambda: len(digits) <= 1, 'too many \'digits\' arguments'),
        (lambda: len(issuer) <= 1, 'too many \'issuer\' arguments'),
        (lambda: len(secret) == 1, 'no secret found'),
    )

    secret, = secret
    issuer = issuer[0] if issuer else None
    digits = int(digits[0]) if digits else DIGITS_DEFAULT

    return {
        'secret': secret,
        'digits': digits,
        'issuer': issuer,
        'label': parsed.path.lstrip('/'),
    }
