# Keyboard layout switching
# kbdd 
# Set background
nitrogen --restore &

# Enable touchpad tap to click
xinput set-prop "SynPS/2 Synaptics TouchPad" 300 1 &
xinput set-prop "SynPS/2 Synaptics TouchPad" "libinput Tapping Enabled" 1 &

# Bluetooth manager
blueman-applet &
nm-applet &

# Parcellite
parcellite &

# Sane alt-tab behaviour
(sleep 5 && alttab -fg "#52baff" -bg "#4a4a4a" -frame "#52baff" -t 128x150 -i 127x64) &

