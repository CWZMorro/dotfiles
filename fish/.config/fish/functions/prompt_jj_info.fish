function prompt_jj_info --description "Print jj bookmark"
    command -sq jj; or return 1
    prompt_repo_root .jj >/dev/null; or return 1

    set -l info (jj log --no-graph --ignore-working-copy --color=never --revisions @ \
        --template 'separate(" ", coalesce(bookmarks, change_id.shortest(8)), if(conflict, "!conflict"))' \
        2>/dev/null)
    or return 1
    test -n "$info"; or return 1
    printf '%s' $info
end
