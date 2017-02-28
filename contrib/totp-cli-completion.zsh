#compdef totp

_totp() {
    local prefix="${PASSWORD_STORE_DIR:-$HOME/.password-store}"
    _values 'services' \
        ${$(find -L "$prefix" \( -name .git -o \
                                 -name .gitattributes -o \
                                 -name .gpg-id \) -prune -o $@ -print 2>/dev/null | \
          sed -e '/\/code\.gpg$/ {
                     '"s#${prefix}/2fa/\{0,1\}##"'
                     s#\\#\\\\#
                     s#/code\.gpg$##
                     p
                 }
                 d' | \
          sort):-""}
}
