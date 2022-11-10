#!/bin/bash

#--gui-settings-file (shortcut -g) allows to load a previously saved gui-settings file (see below)
#-S, --start: starts the simulation upon opening the gui (without the need to click the start button
#-Q, --quit-on-end: closes the gui upon simulation end
#-d, --delay: sets an initial simulation delay to prevent the simulation from running to quickly
#--window-size WIDTH,HEIGHT: sets the iniial window size (by default the previous size is restored)
#--window-pos X,Y: sets the initial window position (by default the previous position is restored)

WSIZE="${WSIZE:=1024,768}"
RPORT="${RPORT:=8813}"

if [ "$DELAY" != "" ]; then
     DELAY="--delay $DELAY"
fi

if [ "$START" == "1" ]; then
     START="--start"
else
     START=""
fi

if [ -f $CONFIG ]; then
     echo "Starting sumo with $CONFIG"
     sumo-gui -c $CONFIG --remote-port $RPORT --window-pos 0,0 --window-size $WSIZE $START $DELAY
else
     sumo-gui --remote-port $RPORT --window-pos 0,0 --window-size $WSIZE
fi