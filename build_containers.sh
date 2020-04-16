#!/usr/bin/env bash

docker build ./nginx -t dc-nginx
docker build ./DataCollector -t dc-python
