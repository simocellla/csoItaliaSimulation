for i in ../../containers/grafana/dataSources/*; do \
	curl -X "POST" "http://localhost:3000/api/datasources" \
		-H "Content-Type: application/json" \
		--user admin:admin \
		--data-binary @$i 
done