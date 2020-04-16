#!/usr/bin/env bash

docker build -t dc-nginx ./nginx
docker build -t dc-python ./DataCollector 
