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
AMT_API_PORT=9093
# Name of the busses:
BUS_name=A1
BUS_2nd=A2
# Name of the paline
SD_ONE=Marconi1-Fiera
SD_TWO=Marconi2-Rimessa
SD_THREE= Italia1-PuntaVagno
SD_FOUR=Italia2-Piave
SD_FIVE=Italia3-Zara


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

	# Bus A1
	PODNAME=busA1 \
	ETH0_NET=mgmt-crltp \
	ETH0_IP=10.254.254.102 \
	ETH1_NET=simint-crltp \
	ETH1_IP=3.3.0.2 \
	BUS_name=$(BUS_name) \
	PYTHONUNBUFFERED=1 \
	$(MAKE) -C ../../pods/bus/ start

	# Bus A2
	PODNAME=busA2 \
	ETH0_NET=mgmt-crltp \
	ETH0_IP=10.254.254.103 \
	ETH1_NET=simint-crltp \
	ETH1_IP=3.3.0.3 \
	BUS_name=$(BUS_2nd) \
	PYTHONUNBUFFERED=1 \
	$(MAKE) -C ../../pods/bus/ start
	
	# prometheus
	sudo podman start prometheus
    # PODNAME=prometheus \
	# $(MAKE) -C ../../pods/prometheus/ start 

#	# grafana run
#	sudo podman run -d --name crltp-grafana -p 3000:3000 --network mgmt-crltp --restart always grafana

	# grafana data-sources
	bash grafanaUpdate/updateDS.sh

	# grafana dashboard
	bash grafanaUpdate/updateDashboard.sh

#	# smartdisplay Marconi1-Fiera
#	PODNAME=smartdisplay_Marconi1 \
#	ETH0_NET=simint-crltp \
#	ETH0_IP=3.3.0.3 \
#	SD_name=$(SD_ONE) \
#	$(MAKE) -C ../../pods/smartdisplay/ start
#
#	# smartdisplay Marconi2-Rimessa
#	PODNAME=smartdisplay_Marconi2 \
#	ETH0_NET=simint-crltp \
#	ETH0_IP=3.3.0.4 \
#	SD_name=$(SD_TWO) \
#	$(MAKE) -C ../../pods/smartdisplay/ start
#
#	# smartdisplay Italia1-PuntaVagno
#	PODNAME=smartdisplay_Italia1 \
#	ETH0_NET=simint-crltp \
#	ETH0_IP=3.3.0.5 \
#	SD_name=$(SD_THREE) \
#	$(MAKE) -C ../../pods/smartdisplay/ start
#
#	# smartdisplay Italia2-Piave
#	PODNAME=smartdisplay_Italia2 \
#	ETH0_NET=simint-crltp \
#	ETH0_IP=3.3.0.6 \
#	SD_name=$(SD_FOUR) \
#	$(MAKE) -C ../../pods/smartdisplay/ start
#
#	# smartdisplay Italia3-Zara
#	PODNAME=smartdisplay_Italia3 \
#	ETH0_NET=simint-crltp \
#	ETH0_IP=3.3.0.7 \
#	SD_name=$(SD_FIVE) \
#	$(MAKE) -C ../../pods/smartdisplay/ start


stop:
	PODNAME=sumo \
	$(MAKE) -C ../../pods/sumo/ stop
	PODNAME=amt \
	$(MAKE) -C ../../pods/amt/ stop
	PODNAME=busA1 \
	$(MAKE) -C ../../pods/bus/ stop
	PODNAME=busA2 \
	$(MAKE) -C ../../pods/bus/ stop
	PODNAME=smartdisplay_Marconi1 \
	$(MAKE) -C ../../pods/smartdisplay/ stop
	PODNAME=smartdisplay_Marconi2 \
	$(MAKE) -C ../../pods/smartdisplay/ stop
	PODNAME=smartdisplay_Italia1 \
	$(MAKE) -C ../../pods/smartdisplay/ stop
	PODNAME=smartdisplay_Italia2 \
	$(MAKE) -C ../../pods/smartdisplay/ stop
	PODNAME=smartdisplay_Italia3 \
	$(MAKE) -C ../../pods/smartdisplay/ stop
# 	Prometheus
	sudo podman stop prometheus || true
	sudo podman rm prometheus || true
# 	Grafana
	sudo podman stop crltp-grafana || true
	sudo podman rm crltp-grafana || true


.PHONY: network-create
network-create:
	$(call create_net,mgmt-crltp,bridge,10.254.254.0/24,10.254.254.1)
	$(call create_net,amt-crltp,bridge,1.1.1.0/24,1.1.1.1)
	$(call create_net,simint-crltp,bridge,3.3.0.0/24,3.3.0.1)
	$(call create_net,comune-crltp,bridge,2.2.2.0/24,2.2.2.1)


.PHONY: network-delete
network-delete:
	$(call delete_net,mgmt-crltp)
	$(call delete_net,amt-crltp)
	$(call delete_net,simint-crltp)
	$(call delete_net,comune-crltp)