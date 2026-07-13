function prompt_git_info --description "Print git branch if inside a git repo"
    command -sq git; or return 1
    prompt_repo_root .git >/dev/null; or return 1

    set -l ref (command git rev-parse --abbrev-ref HEAD 2>/dev/null)
    test -n "$ref"; or return 1
    if test "$ref" = HEAD
        set ref (command git rev-parse --short HEAD 2>/dev/null)
        test -n "$ref"; or return 1
    end
    printf '%s' $ref
end
