function prompt_repo_root --description "Walk up from PWD looking for a file/dir named \$argv[1] (e.g. .git or .jj), print the dir if found."
    set -l dir $PWD
    while true
        if test -e "$dir/$argv[1]"
            printf '%s' $dir
            return 0
        end
        if test "$dir" = /
            return 1
        end
        set dir (path dirname -- $dir)
    end
end
