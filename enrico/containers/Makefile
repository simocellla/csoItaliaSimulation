.PHONY: build
build: novnc sumo simbackend

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
