#!/bin/bash
curl -H "Content-Type: application/json" \
-H "Authorization: Basic YWRtaW46YWRtaW4=" \
-X POST \
-d @../../containers/grafana/dashboard.json \
http://localhost:3000/api/dashboards/db