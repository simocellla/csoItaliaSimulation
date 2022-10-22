.PHONY: sumo
sumo:
	envsubst < sumo.yaml | podman play kube --replace -

sumo-stop:
	podman pod rm -f sumopod
