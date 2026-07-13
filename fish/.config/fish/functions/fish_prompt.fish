function fish_prompt
    set -l last_status $status

    set -l os_icon (prompt_os_icon)
    if test -n "$os_icon"
        set_color cyan
        printf '%s ' $os_icon
        set_color normal
    end

    set_color blue
    if test "$PWD" = "$HOME"
        printf ' ~ '
    else
        printf ' %s ' (path basename -- $PWD)
    end
    set_color normal

    # jj > git
    set -l vcs (prompt_jj_info)
    if test -z "$vcs"
        set vcs (prompt_git_info)
    end
    if test -n "$vcs"
        set_color yellow
        printf ' %s ' $vcs
        set_color normal
    end

    if test $last_status -eq 0
        set_color green
    else
        set_color red
    end
    printf '❯ '
    set_color normal
end
