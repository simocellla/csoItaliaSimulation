PODNAME?=sumo
CONF=sumo.yaml
NET=

ifdef ETH0_NET
NET := $(NET) --network=$(ETH0_NET):interface_name=eth0,ip=$(ETH0_IP)
endif

ifdef ETH1_NET
NET := $(NET) --network=$(ETH1_NET):interface_name=eth1,ip=$(ETH1_IP)
endif

ifdef ETH2_NET
NET := $(NET) --network=$(ETH2_NET):interface_name=eth2,ip=$(ETH2_IP)
endif

ifdef ETH3_NET
NET := $(NET) --network=$(ETH3_NET):interface_name=eth3,ip=$(ETH3_IP)
endif

.PHONY: start
start: 
	envsubst < $(CONF) | sudo podman play kube \
		$(NET) \
		--replace -

.PHONY: stop
stop:
	sudo podman pod rm -f $(PODNAME)