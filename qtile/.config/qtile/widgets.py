from libqtile import widget as defWidget

# qtile extra
from qtile_extras import widget
from qtile_extras.widget.decorations import BorderDecoration

from colors import colors
import subprocess

import urllib.request
import xml.etree.ElementTree as ET

WEATHER_ICONS = {
    "default": "",
    "sun": "󰖙",
    "cloud": "󰖐",
    "rain": "󰖖",
    "snow": "󰼶",
    "fog": "󰖑",
}


def separator():
    return [
        defWidget.Sep(
            linewidth=2,
            foreground=colors["white"],
            padding=15,
            size_percent=60,
        )
    ]


def get_weather_condition(condition_text):
    if not condition_text:
        return WEATHER_ICONS["default"]

    condition = condition_text.lower()

    # 1. Snow / Ice / Winter
    # Matches: Light Snow, Flurries, Ice Crystals, Freezing Rain, Hail, Blowing Snow
    if any(
        x in condition
        for x in ["snow", "flurr", "ice", "hail", "freezing", "squall", "drift", "blow"]
    ):
        return WEATHER_ICONS["snow"]

    # 2. Rain / Liquid Precipitation
    # Matches: Rain, Drizzle, Showers, Thunderstorm
    if any(x in condition for x in ["rain", "shower", "drizzle", "thunder", "storm"]):
        return WEATHER_ICONS["rain"]

    # 3. Fog / Visibility / Atmosphere
    # Matches: Fog, Mist, Haze, Smoke, Volcanic Ash
    if any(x in condition for x in ["fog", "mist", "haze", "smoke", "ash"]):
        return WEATHER_ICONS["fog"]

    # 4. Clouds
    # Matches: Cloudy, Mostly Cloudy, Overcast, Partly Cloudy, A mix of sun and cloud
    if any(x in condition for x in ["cloud", "overcast", "gloom"]):
        return WEATHER_ICONS["cloud"]

    # 5. Sun / Clear (Default fallback for nice weather)
    # Matches: Sunny, Mainly Sunny, Clear, Mainly Clear
    if any(x in condition for x in ["sun", "clear"]):
        return WEATHER_ICONS["sun"]

    # Fallback if text matches nothing (e.g. empty string or unknown term)
    return WEATHER_ICONS["default"]


def get_edmonton_weather():
    try:
        # Stable RSS Feed for Edmonton (Blatchford) - (ab-50)
        url = "https://weather.gc.ca/rss/city/ab-50_e.xml"

        # Use User Agent to prevent the server from blocking the request (403 Error)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req, timeout=10) as response:
            tree = ET.parse(response)
            root = tree.getroot()

            # RSS feeds use the Atom namespace
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            # Look for the specific entry titled "Current Conditions"
            for entry in root.findall("atom:entry", ns):
                title_node = entry.find("atom:title", ns)

                if title_node is None:
                    continue  # Skip if no title found

                title = title_node.text

                if title and title.startswith("Current Conditions:"):
                    data_part = title.split(": ", 1)[1]
                    parts = data_part.split(", ")

                    if len(parts) >= 2:
                        condition_text = parts[0]
                        temp_text = parts[-1]
                    else:
                        # Fallback if format is weird (e.g. just temp)
                        condition_text = "N/A"
                        temp_text = parts[0]

                    icon = get_weather_condition(condition_text)
                    return f"{icon} {temp_text}"

            return "N/A"

    except Exception:
        return "N/A"


def underLine(color):
    return {
        "decorations": [
            BorderDecoration(
                colour=color,
                border_width=[0, 0, 4, 0],  # Top, Right, Bottom, Left
                padding_x=None,
                padding_y=None,
            )
        ],
    }


def get_brightness():
    try:
        # Run the command and find the output
        command = "brightnessctl -m | awk -F, '{print $4}' | tr -d '%' "
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        # The output is the clean percentage number (e.g., "50")
        brightness = result.stdout.strip()
        return f" {brightness}%"
    except subprocess.CalledProcessError:
        return "N/A"  # Return N/A if command fails


def dateWidget():
    return [
        widget.Clock(
            background=colors["black"],
            foreground=colors["blue"],
            format="%Y-%m-%d %a",
            padding=10,
            **underLine(colors["blue"]),
        ),
    ] + separator()


def timeWidget():
    return [
        widget.Clock(
            background=colors["black"],
            foreground=colors["purple"],
            format="%H:%M",
            padding=10,
            **underLine(colors["purple"]),
        ),
    ]


# def CPUWidget(powerLine):
#     return [
#         widget.TextBox(
#             background=colors["green"],
#             fmt="",
#             padding=5,
#         ),
#         defWidget.CPU(
#             background=colors["green"],
#             foreground=colors["white"],
#             format=": {load_percent}%",
#             update_interval=1.0,
#         ),
#         defWidget.Memory(
#             background=colors["green"],
#             foreground=colors["white"],
#             format=": {MemUsed:.2f}GB/{MemTotal:.2f}GB",
#             measure_mem="G",
#             update_interval=1.0,
#         ),
#         widget.TextBox(background=colors["green"], fmt="", **powerLine),
#     ]


def Systray():
    return [
        widget.Systray(
            padding=5,
            icon_size=25,
        ),
    ] + separator()


def batteryWidget():
    return [
        widget.GenPollText(
            background=colors["black"],
            fmt="",
            **underLine(colors["red"]),
        ),
        widget.UPowerWidget(
            background=colors["black"],
            foreground=colors["red"],
            battery_height=12,
            battery_width=28,
            text_charging="(Plugged In)",
            text_discharging="(On Battery)",
            **underLine(colors["red"]),
        ),
        widget.Battery(
            background=colors["black"],
            foreground=colors["red"],
            format="{percent:2.0%}",
            padding=10,
            **underLine(colors["red"]),
        ),
    ] + separator()


def volumeWidget():
    return [
        widget.Volume(
            background=colors["black"],
            foreground=colors["orange"],
            fmt=" {}",
            channel="Master",
            padding=10,
            **underLine(colors["orange"]),
        ),
    ] + separator()


def brightnessWidget():
    return [
        widget.GenPollText(
            background=colors["black"],
            foreground=colors["yellow"],
            name="brightness_display",
            func=get_brightness,
            update_interval=0.5,
            format="{}",
            padding=10,
            **underLine(colors["yellow"]),
        ),
    ] + separator()


def weatherWidget():
    return [
        widget.GenPollText(
            background=colors["black"],
            foreground=colors["green"],
            func=get_edmonton_weather,
            update_interval=300,  # Update every 5 mins
            fmt="{}",
            padding=10,
            **underLine(colors["green"]),
        ),
    ] + separator()
