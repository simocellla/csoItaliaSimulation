#!/bin/bash

file='../../../containers/grafana/plugins.txt'  
  
i=1  

while read line; do  
  
#Reading each line  
echo "$line"  
i=$((i+1))  
done < $file  
