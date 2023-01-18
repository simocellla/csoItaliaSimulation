# name driver subnet gateway
define create_net
 @if [ $$(sudo podman network ls --filter name="$1" --format="{{.Name}}" | wc -l) -eq 0 ]; then \
	echo -n "Creating network: "; \
	sudo podman network create --subnet $3 \
	--gateway $4 -d $2 $1; \
 fi
endef

# name
define delete_net
 @if [ $$(sudo podman network ls --filter name="$1" --format="{{.Name}}" | wc -l) -eq 1 ]; then \
	echo -n "Deleting network: "; \
	sudo podman network rm $1; \
 fi
endef

.PHONY: start
# SUMO configurations
SUMO_CONFIGPATH=config/sumo
SUMO_STARTCONFIG=/sumo/csoItalia.sumocfg
SUMO_WINX=1024
SUMO_WINY=768
# 1: autostart sumo
SUMO_START=1
SUMO_DELAY=200
# SUMO remote TRACI port
SUMO_REMOTEPORT=8813
SUMO_NOVNC_PORT=9999
# REST API PORT for querying SUMO from CR
SIM_API_PORT=9090

start: network-create
	# sumo
	PODNAME=sumo \
	ETH0_NET=mgmt-crltp \
	ETH0_IP=10.254.254.100 \
	CONFIGPATH=$(shell pwd)/$(SUMO_CONFIGPATH) CONFIG=$(SUMO_STARTCONFIG) \
	DISPLAY_X=$(SUMO_WINX) DISPLAY_Y=$(SUMO_WINY) \
	START=$(SUMO_START) DELAY=$(SUMO_DELAY) \
	WSIZE="$(SUMO_WINX),$(SUMO_WINY)" \
	RPORT=$(SUMO_REMOTEPORT) \
	SUMO_NOVNC_PORT=$(SUMO_NOVNC_PORT) \
	SIM_API_PORT=$(SIM_API_PORT) \
	$(MAKE) -C ../../pods/sumo/ start
	# amt
	PODNAME=amt \
	ETH0_NET=mgmt-crltp \
	ETH0_IP=10.254.254.101 \
	ETH1_NET=amt-crltp \
	ETH1_IP=1.1.1.100 \
	$(MAKE) -C ../../pods/amt/ start

stop:
	PODNAME=sumo \
	$(MAKE) -C ../../pods/sumo/ stop
	PODNAME=amt \
	$(MAKE) -C ../../pods/amt/ stop

.PHONY: network-create
network-create:
	$(call create_net,mgmt-crltp,bridge,10.254.254.0/24,10.254.254.1)
	$(call create_net,amt-crltp,bridge,1.1.1.0/24,1.1.1.1)

.PHONY: network-delete
network-delete:
	$(call delete_net,mgmt-crltp)
	$(call delete_net,amt-crltp)


