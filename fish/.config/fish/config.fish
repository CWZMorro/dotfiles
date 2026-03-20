if status is-interactive
    function fish_greeting
        set_color normal
        echo "Welcome to a friendly interactive shell~~"
        # set_color yellow
        # echo -n "Note: "
        # set_color normal
        # echo "use 'nvm use lts' to use npm"
    end

    alias gpt5.1 "llm chat -m github_copilot/gpt-5.1 -s \"Input short answer.\""
    alias gPro "uvx llm chat -m github_copilot/gemini-2.5-pro -s \"Input long answer.\""
    alias bonsai "cbonsai -li"
    alias weather "curl -s https://weather.gc.ca/rss/city/ab-50_e.xml | grep \"Current Conditions\""
    alias lg lazygit
    alias tmat "tmux attach -t"
    alias qtlog "tail -f ~/.local/share/qtile/qtile.log"

    # Set nvim as the default editor
    set -gx VISUAL nvim
    set -gx EDITOR nvim

end

# uv
fish_add_path "/home/cielarchazure/.local/bin"

# zoxide
zoxide init fish --cmd cd | source

# fastfetch
if set -q TMUX
    fastfetch -c ~/.config/fastfetch/minimal.jsonc --logo-type none
else
    fastfetch -c ~/.config/fastfetch/minimal.jsonc
end

# ranger
function ranger --wraps=ranger --description="Run ranger and cd into last dir on exit"
    set -l tmpfile (mktemp -t "ranger-cd.XXXXXX")
    command ranger --choosedir=$tmpfile $argv
    if test -s $tmpfile
        read -l ranger_pwd <$tmpfile
        if test "$ranger_pwd" != "$PWD"
            builtin cd "$ranger_pwd"
        end
    end
    rm -f $tmpfile
    commandline -f repaint
end
bind \co ranger-cd

# eza
alias ls="eza --color=always --icons=always"
alias ll="eza -lg --color=always --icons=always"
alias lt="eza --tree --color=always --icons=always"

# pnpm
set -gx PNPM_HOME "/home/cielarchazure/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
    set -gx PATH "$PNPM_HOME" $PATH
end
