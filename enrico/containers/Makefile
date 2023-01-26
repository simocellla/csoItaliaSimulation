.PHONY: build
build: novnc sumo simbackend simyellow bus palina

.PHONY: novnc
novnc:
	sudo setenforce 0 || true
	sudo podman build -t crltp-novnc novnc 

.PHONY: sumo
sumo:
	sudo setenforce 0 || true
	sudo podman build -t crltp-sumo sumo

.PHONY: simbackend
simbackend:
	sudo setenforce 0 || true
	sudo podman build -t crltp-simbackend simbackend

.PHONY: simyellow
simyellow:
	sudo setenforce 0 || true
	sudo podman build -t crltp-simyellow simyellow

.PHONY: bus
bus:
	sudo setenforce 0 || true
	sudo podman build -t crltp-bus bus

#.PHONY: palina
#palina:
#	sudo setenforce 0 || true
#	sudo podman build -t crltp-palina palina