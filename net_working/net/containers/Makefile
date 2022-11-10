.PHONY: build
build: novnc sumo traci # startsim

.PHONY: novnc
novnc:
	sudo setenforce 0 || true
	sudo podman build -t crltp-novnc novnc 

.PHONY: sumo
sumo:
	sudo setenforce 0 || true
	sudo podman build -t crltp-sumo sumo

.PHONY: traci
traci:
	sudo setenforce 0 || true
	sudo podman build -t crltp-traci traci 

.PHONY: startsim
startsim:
	sudo setenforce 0 || true
	sudo podman build -t crltp-startsim startsim