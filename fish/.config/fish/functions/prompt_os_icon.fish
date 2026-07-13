function prompt_os_icon --description "Print a nerd-font distro icon based on /etc/os-release"
    test -r /etc/os-release; or return 1
    # read + parse with fish builtins (redirection + string match)
    set -l os_id (string match -rg '^ID=(.*)$' < /etc/os-release 2>/dev/null)
    test -n "$os_id"; or return 1
    set os_id (string trim -c '"' -- $os_id[1])
    switch $os_id
        case arch
            printf ''
        case nixos
            printf ''
        case '*'
            return 1
    end
end
