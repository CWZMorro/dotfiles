import os

from libqtile import bar, layout, qtile, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile import widget as defWidget

# qtile extra
from qtile_extras.widget.decorations import PowerLineDecoration
from qtile_extras import widget

# colors
from colors import colors

# custom layout
from dwindle import Dwindle

import subprocess


@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.Popen(["bash", home])


mod = "mod4"
terminal = "kitty"

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key(
        [mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"
    ),
    Key(
        [mod, "shift"],
        "l",
        lazy.layout.shuffle_right(),
        desc="Move window to the right",
    ),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key(
        [mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"
    ),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key(
        [mod],
        "t",
        lazy.window.toggle_floating(),
        desc="Toggle floating on the focused window",
    ),
    Key([mod, "control"], "u", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([mod], "d", lazy.spawn("rofi -show drun"), desc="Launch rofi"),
    Key(
        [],
        "Print",
        lazy.spawn("sh -c 'maim -s | xclip -selection clipboard -t image/png'"),
        desc="Capture area to clipboard",
    ),
    Key(
        [],
        "XF86AudioRaiseVolume",
        lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +2%"),
        desc="Volume up",
    ),
    Key(
        [],
        "XF86AudioLowerVolume",
        lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -2%"),
        desc="Volume down",
    ),
    Key(
        [mod],
        "XF86AudioRaiseVolume",
        lazy.spawn("brightnessctl set 5%+"),
        desc="Increase brightness",
    ),
    Key(
        [mod],
        "XF86AudioLowerVolume",
        lazy.spawn("brightnessctl set 5%-"),
        desc="Decrease brightness",
    ),
    # --- Dunst Shortcuts ---
    Key(
        ["control", "shift"], "a", lazy.spawn("dunstctl action"), desc="accept request"
    ),
    Key(["control"], "space", lazy.spawn("dunstctl close"), desc="close notification"),
    Key(
        ["control"],
        "grave",
        lazy.spawn("dunstctl history-pop"),
        desc="show dunst history",
    ),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc=f"Switch to group {i.name}",
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc=f"Switch to & move focused window to group {i.name}",
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

layoutFormat = {
    "border_width": 4,
    "margin": 2,
    "border_focus": colors["purple"],
    "border_normal": colors["black"],
}

layouts = [
    Dwindle(**layoutFormat)
    # layout.Columns(**layoutFormat),
    # layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(**layoutFormat),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
    # layout.Spiral(**layoutFormat,
    #              ratio = 0.5,
    #              main_pane = "right",
    #              new_client_position = "after_current",
    #              main_pane_direction = "vertical",
    #              )
]

widget_defaults = dict(
    font="JetBrainsMonoNFM-Regular",
    fontsize=15,
    padding=5,
)
extension_defaults = widget_defaults.copy()


def get_brightness():
    try:
        # Run the command and capture the output
        command = "brightnessctl -m | awk -F, '{print $4}' | tr -d '%' "
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        # The output is the clean percentage number (e.g., "50")
        brightness = result.stdout.strip()
        return f"  {brightness}%"
    except subprocess.CalledProcessError:
        return "N/A"  # Return N/A if command fails


powerLine = {
    "decorations": [
        PowerLineDecoration(
            path="arrow_left",
        )
    ]
}


def batteryWidget():
    return [
        widget.GenPollText(
            background=colors["red"],
            fmt="",
        ),
        widget.UPowerWidget(
            background=colors["red"],
            foreground=colors["white"],
            battery_height=15,
            battery_width=30,
            text_charging="(Plugged In)",
            text_discharging="(On Battery)",
        ),
        widget.Battery(
            background=colors["red"],
            foreground=colors["white"],
            format="{percent:2.0%}",
            padding=10,
            **powerLine,
        ),
    ]


def clockWidgets():
    return [
        widget.Clock(
            background=colors["blue"],
            foreground=colors["white"],
            padding=10,
            format="%Y-%m-%d %a",
            **powerLine,
        ),
        widget.Clock(
            background=colors["purple"],
            foreground=colors["white"],
            padding=10,
            format="%H:%M",
        ),
    ]


def CPUWidget():
    return [
        widget.TextBox(
            background=colors["green"],
            fmt="",
            padding=5,
        ),
        defWidget.CPU(
            background=colors["green"],
            foreground=colors["white"],
            format=": {load_percent}%",
            update_interval=1.0,
        ),
        defWidget.Memory(
            background=colors["green"],
            foreground=colors["white"],
            format=": {MemUsed:.2f}GB/{MemTotal:.2f}GB",
            measure_mem="G",
            update_interval=1.0,
        ),
        widget.TextBox(background=colors["green"], fmt="", **powerLine),
    ]


def init_bar():
    widgets_list = [
        widget.CurrentLayout(),
        widget.GroupBox(),
        widget.Prompt(),
        widget.WindowName(),
        widget.Chord(
            chords_colors={"launch": (colors["purple"], colors["blue"])},
            name_transform=lambda name: name.upper(),
        ),
        widget.Systray(padding=5, icon_size=25, **powerLine),
        *batteryWidget(),
        widget.Volume(
            background=colors["orange"],
            foreground=colors["black"],
            fmt="   {}",
            channel="Master",
            padding=10,
            **powerLine,
        ),
        widget.GenPollText(
            background=colors["yellow"],
            foreground=colors["black"],
            name="brightness_display",
            func=get_brightness,
            update_interval=0.5,
            format="{}",
            padding=10,
            **powerLine,
        ),
        *CPUWidget(),
        *clockWidgets(),
    ]
    return bar.Bar(widgets_list, 30, margin=[5, 8, 3, 8])


screens = [
    Screen(
        top=init_bar(),
        background=colors["black"],
        wallpaper="~/Downloads/dark mode ver 1.png",
        wallpaper_mode="fill",
    ),
]

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
focus_previous_on_window_remove = False
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
