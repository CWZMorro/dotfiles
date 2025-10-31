# Set the monitor configuration
# Run autorandr to load correct profile
# autorandr --change &
# Bluetooth
blueman-applet &

# Start network manager
nm-applet &
volumeicon & #volume control

picom -b --config ~/.config/picom/picom.conf
udiskie &
# Start notification daemon
dunst &
