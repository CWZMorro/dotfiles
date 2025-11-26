if status is-interactive
    function fish_greeting
        set_color normal
        echo "Welcome to a friendly interactive shell~~"
        set_color yellow
        echo -n "Note: "
        set_color normal
        echo "use 'nvm use lts' to use npm"
    end

    alias gpt4.1 "uvx llm chat -m github_copilot/gpt-4.1 -s \"Input short answer.\""
    alias gPro "uvx llm chat -m github_copilot/gemini-2.5-pro -s \"Input long answer.\""
    alias bonsai "cbonsai -li"
    alias weather "curl -s https://weather.gc.ca/rss/city/ab-50_e.xml | grep \"Current Conditions\""
    alias lg lazygit

end
