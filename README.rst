totp-cli
========

.. image:: https://img.shields.io/pypi/v/totp.svg
  :target: https://pypi.python.org/pypi/totp
  :alt: version on pypi

.. image:: https://img.shields.io/pypi/l/totp.svg
  :target: https://github.com/hobarrera/totp-cli/blob/master/LICENCE
  :alt: licence

totp-cli is a simple command line application to generate OTP tokens for two
factor authentication using RFC6238_.

.. _RFC6238: http://tools.ietf.org/html/rfc6238

These are compatible with many popular services such as Facebook, GitHub,
Google, eve-online, battle.net, etc.

totp-cli fetches your shared key (aka: code) from pass_, generates the
token, outputs it to stdout and copies it to your CLIPBOARD X selection.
Default X selection can be overridden with the PASSWORD_STORE_X_SELECTION
environment variable.

Shared keys should be stored in your pass storage under ``2fa/SERVICE/code``,
for example ``2fa/github/code``. The ``-a`` flag (or alternatively the ``add``
subcommand) can be used to add this less painfully.

.. _pass: http://www.passwordstore.org/

Usage
-----

Usage::

    totp SERVICE

For example::

    $ totp github
    621787

You don't need to run ``totp`` from the command line if you just want to paste
the code; you can run it from ``dmenu``, or whatever your application launcher
is.

To offset the clock by a number of seconds::

    totp -s SECONDS SERVICE

For example::

    $ totp -s +60 github
    735092
    $ totp -s -90 github
    909651

To add a service::

    totp -a SERVICE
    # OR
    totp add SERVICE

For example::

    $ totp -a github
    Token length [6]: 6
    Shared key: KEY

Note that if the service already exists, it will be overwritten without
warning.

To output without copying to the clipboard:

    $ totp -n SERVICE
    # OR
    $ totp --nocopy SERVICE


About pass entries
------------------

Pass entries are expected to have the TOTP secret in their first line (as
provided by the third party).
The amount of digits token must have (for example, battle.net uses 8), must be
provided in a separate line, with a format like:

    Digits: 8

For the moment, only customizing the token length is possible.

Requirements
------------

* `pass <http://www.passwordstore.org/>`_
* `python >= 3.3 <https://www.python.org/>`_

There are also some platform-specific requirements for copying code into the
clipboard:

* `xclip <http://sourceforge.net/projects/xclip>`_ for Xorg (Linux/BSD).

Installation
------------

Installation is quite simple:

    $ pip install totp

There is also an `AUR package`_ available for ArchLinux users.

.. _AUR package: https://aur.archlinux.org/packages/totp-cli/

You can also configure shell completion for totp-cli:

* Bash: Download `totp-cli-completion.bash <contrib/totp-cli-completion.bash>`_
  and source it from your bash configuration file (e.g. ``.bash_profile``)

* Zsh: Download `totp-cli-completion.zsh <contrib/totp-cli-completion.zsh>`_ as
  ``_totp`` to site-functions directory (e.g.
  ``/usr/local/share/zsh/site-functions``)

Usage with GitHub
-----------------

For GitHub, you may find the requested shared key by logging into your
account, clicking on your profile photo to deploy a drop down menu, clicking
on the "Settings" option in the drop down menu, then, in the "Access" section
of the sidebar, click on "Password and Authentication", then, in the
"Two-factor authentication" section of the page, click on "Enable two-factor
authentication", and, instead of scanning the QR code, click on "setup key".
The shared key required by `totp` will then be displayed on the screen.

License
-------

totp-cli is distrbuted under the terms of the ISC licence. See LICENCE for
details.

Copyright (c) 2014-2017 Hugo Osvaldo Barrera <hugo@barrera.io>
