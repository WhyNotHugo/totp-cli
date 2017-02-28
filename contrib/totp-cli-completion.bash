_totp() {
    local prefix="${PASSWORD_STORE_DIR:-$HOME/.password-store}"
    local cur="${COMP_WORDS[COMP_CWORD]}"

    COMPREPLY=()

    local items=( $(compgen -d "${prefix}/2fa/${cur}" ) )
    for item in ${items[*]}; do
        COMPREPLY+=(${item#${prefix}/2fa/})
    done
}

complete -o dirnames -o nospace -F _totp totp
