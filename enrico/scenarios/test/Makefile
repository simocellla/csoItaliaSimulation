.PHONY: start
# SUMO configurations
SUMO_CONFIGPATH=config/sumo
SUMO_STARTCONFIG=/sumo/002.sumocfg
SUMO_WINX=1024
SUMO_WINY=768
# 1: autostart sumo
SUMO_START=1
SUMO_DELAY=200
# sumo remote TRACI port
SUMO_REMOTEPORT=8813

start:
	CONFIGPATH=$(shell pwd)/$(SUMO_CONFIGPATH) CONFIG=$(SUMO_STARTCONFIG) \
	 DISPLAY_X=$(SUMO_WINX) DISPLAY_Y=$(SUMO_WINY) \
	 START=$(SUMO_START) DELAY=$(SUMO_DELAY) \
	 WSIZE="$(SUMO_WINX),$(SUMO_WINY)" \
	 RPORT=$(SUMO_REMOTEPORT) \
	 $(MAKE) -C ../../pods/sumo/ sumo

stop:
	$(MAKE) -C ../../pods/sumo/ sumo-stop
