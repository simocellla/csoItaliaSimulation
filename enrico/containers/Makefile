.PHONY: build
build: novnc sumo simbackend simyellow bus palina prometheus grafana 

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

.PHONY: palina
palina:
	sudo setenforce 0 || true
	sudo podman build -t crltp-palina palina

.PHONY: prometheus
prometheus:
	sudo setenforce 0 || true
	sudo podman build -t crltp-prometheus prometheus
	sudo podman create --name prometheus -p 9090:9090 \
    --volume prometheus-config:/etc/prometheus \
    --network=mgmt-crltp \
    --ip=10.254.254.104 \
    crltp-prometheus

.PHONY: grafana
grafana:
	sudo setenforce 0 || true
	sudo podman run -d --name crltp-grafana -p 3000:3000 --network mgmt-crltp --restart always grafana

#.PHONY: grafana
#	sudo setenforce 0 || true
#	sudo podman build -t grafana:latest .
#