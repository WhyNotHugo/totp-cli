totp-cli
========

totp-cli is a simple command line application to generate OTP tokens for two
factor authentication using [RFC6238](http://tools.ietf.org/html/rfc6238).  

These are compatible with many popular services such as facebook, github,
google, eve-online, battle.net, etc.

totp-cli fetches your shared key (aka: code) from [pass][pass], generates the
token, outputs it to stdout and copies it to your CLIPBOARD X selection.
Default X selection can be overidden with the PASSWORD_STORE_X_SELECTION
environment variable.

Shared keys should be stored in your pass storage under `2fa/SERVICE/code`,
for example `2fa/github/code`. The add command can be used to add this less
painfully

[pass]: http://www.passwordstore.org/

Usage
-----

    totp SERVICE

For example:

    $ totp generate github
    621787

You don't need to run `totp` from the command line if you just want to paste
the code; you can run if from `dmenu`, or whatever your application launcher
is.

Requirements
------------

 * [pass](http://www.passwordstore.org/)
 * [xclip](http://sourceforge.net/projects/xclip)
 * [python](https://www.python.org/)


Installation
------------

Installation is quite simple:

    $ pip install totp-cli

There is also an [AUR package][aur-package] available for ArchLinux users.

[aur-package]: https://aur.archlinux.org/packages/totp-cli/

License
-------

totp-cli is distrbuted under the terms of the ISC license. See LICENSE for
details.

Copyright (c) 2014-2016 Hugo Osvaldo Barrera <hugo@barrera.io>
