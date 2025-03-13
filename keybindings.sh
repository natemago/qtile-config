#!/usr/bin/env bash

declare -a obds=()
obds+=("-- Switch between windows --" "ignore")
obds+=("[Alt ↑] Focus window above" "qtile cmd-obj -o layout -f up")
obds+=("[Alt ↓] Focus window down" "qtile cmd-obj -o layout -f down")
obds+=("[Alt ←] Focus window left" "qtile cmd-obj -o layout -f left")
obds+=("[Alt →] Focus window right" "qtile cmd-obj -o layout -f right")
#obds+=("[Shift Tab] Next window" "qtile cmd-obj -o layout -f next")
obds+=(" " "ignore")

obds+=("-- Move and manage windows --" "ignore")
obds+=("[Win-Alt ↑] Move window up" "qtile cmd-obj -o layout -f shuffle_up")
obds+=("[Win-Alt ↓] Move window down" "qtile cmd-obj -o layout -f shuffle_down")
obds+=("[Win-Alt m] Set window as main" "qtile cmd-obj -o layout -f swap_main")
obds+=("[Win-Alt o] Maximize" "qtile cmd-obj -o layout -f maximize")
obds+=("[Win-Alt g] Grow window size" "qtile cmd-obj -o layout -f grow")
obds+=("[Win-Alt s] Shrink window size" "qtile cmd-obj -o layout -f shrink")
obds+=(" " "ignore")

obds+=("-- Layout --" "ignore")
obds+=("[Win Tab] Next layout" "qtile cmd-obj -o cmd -f next_layout")
obds+=("[Win-Shift Tab] Previous layout" "qtile cmd-obj -o cmd -f prev_layout")
obds+=(" " "ignore")

obds+=("-- Screens/Groups --" "ignore")
obds+=("[Ctrl-Alt ->] Next screen right" "qtile cmd-obj -o screen -f next_group")
obds+=("[Ctrl-Alt <-] Next screen left" "qtile cmd-obj -o screen -f prev_group")
screens=(1 2 3 4 5 6 7 8)
for i in "${screens[@]}"; do
    obds+=("[Win $i] Move to group $i" "qtile cmd-obj -o group $i -f toscreen")
    obds+=("[Win-Shift $i] Move window to group $i" "qtile cmd-obj -o window $i -f togroup -a $i")
done
obds+=(" " "ignore")

obds+=("-- Qtile commands --" "ignore")
obds+=("[Win-Ctrl r] Restart Qtile" "qtile cmd-obj -o cmd -f restart")
obds+=("[Win-Ctrl q] Quit Qtile" "qtile cmd-obj -o cmd -f shutdown")
obds+=("[Win w] Close current window" "qtile cmd-obj -o window -f kill")
obds+=(" " "ignore")

obds+=("-- Monitor --" "ignore")
obds+=("[Ctrl-Alt l] Lock screen" "qtile cmd-obj -o cmd -f spawn -a 'i3lock --color 000000'")
obds+=("[Win-Ctrl s] Secondary monitor only" "qtile cmd-obj -o cmd -f spawn -a 'mons -s'")
obds+=("[Win-Ctrl p] Primary monitor only" "qtile cmd-obj -o cmd -f spawn -a 'mons -o'")

declare -A bindings=()
declare -a labels=()
i=0
label=""
for kbds in "${obds[@]}"; do
    if [ "$((i%2))" == "0" ]; then
        label="${kbds}"
        labels+=("${kbds}")
    else
        bindings["${label}"]="${kbds}"
    fi
    ((i=i+1))
done


if [ ! -z "$1" ]; then
    if [ "$1" == "ignore" ]; then
        exit 0
    fi
    #echo ${bindings["$1"]}
    ${bindings["$1"]} &>/dev/null
    exit 0
fi

for key in "${labels[@]}"; do
echo "${key}"
done