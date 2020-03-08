# subcommands
complete -xc totp -n '__fish_use_subcommand' -a show -d 'Show the current TOTP token for a registered entry'
complete -xc totp -n '__fish_use_subcommand' -a show-only -d 'Show the current TOTP token for a registered entry - don\'t copy to clipboard'
complete -xc totp -n '__fish_use_subcommand' -a add -d 'Add a new TOTP entry to the database'

# 2FA codes
test -z "$PASSWORD_STORE_DIR"; and set PASSWORD_STORE_DIR "$HOME/.password-store"
complete -xc totp -a '(command ls $PASSWORD_STORE_DIR/2fa)' -d "2FA code"
