from libqtile.widget import GenPollText
from libqtile import widget as defWidget

#qtile extra
from qtile_extras.widget.decorations import PowerLineDecoration
from qtile_extras import widget 
 
def get_brightness():
    try:
        # Run the command and find the output
        command = "brightnessctl -m | awk -F, '{print $4}' | tr -d '%' "
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        # The output is the clean percentage number (e.g., "50")
        brightness = result.stdout.strip()
        return f"  {brightness}%"
    except subprocess.CalledProcessError:
        return "N/A" # Return N/A if command fails


def clockWidgets(powerLine):
    return[
        widget.Clock(
            background = colors["blue"],
            foreground = colors["white"],
            padding = 10,
            format="%Y-%m-%d %a",
            **powerLine
        ),
        widget.Clock(
            background = colors["purple"],
            foreground = colors["white"],
            padding = 10,
            format="%H:%M",
        )
    ]

def CPUWidget():
    return[
        widget.TextBox(
            background = colors["green"],
            fmt = "",
            padding = 5,
        ),
        defWidget.CPU(
            background = colors["green"],
            foreground = colors["white"],
            format = ': {load_percent}%', 
            update_interval = 1.0,
        ),
        defWidget.Memory(
            background = colors["green"],
            foreground = colors["white"],
            format = ': {MemUsed:.2f}GB/{MemTotal:.2f}GB',
            measure_mem = 'G', 
            update_interval = 1.0,
        ),
        widget.TextBox(
            background = colors["green"],
            fmt = "",
            **powerLine
        )
    ]

def Systray(powerLine):
    return[
        widget.Systray(
            padding = 5,
            icon_size = 25,
            **powerLine
        )
    ]

def batteryWidget(powerLine):
    return [
        widget.GenPollText(
            background = colors["red"],
            fmt = "",
        ),
        widget.UPowerWidget(
            background = colors["red"],
            foreground = colors["white"],
            battery_height = 15,
            battery_width = 30,
            text_charging = "(Plugged In)",
            text_discharging = "(On Battery)",
        ),
        widget.Battery(
            background = colors["red"],
            foreground = colors["white"],
            format='{percent:2.0%}',
            padding = 10,
            **powerLine
        )
    ]

def volumeWidget(powerLine):
    return [
        widget.Volume(
            background = colors["orange"],
            foreground = colors["black"],
            fmt="   {}", 
            channel="Master",
            padding = 10,
            **powerLine
        ),
    ]

def brightnessWidget(powerLine):
    return [
        widget.GenPollText(
            background = colors["yellow"],
            foreground = colors["black"],
            name='brightness_display',
            func=get_brightness, 
            update_interval=0.5,
            format='{}',
            padding = 10,
            **powerLine
        ),
    ]
