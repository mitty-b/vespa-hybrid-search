#!/bin/bash

# Stop and remove Vespa container
docker ps -a | grep vespa | awk '{print $1}' | xargs -r docker stop
docker ps -a | grep vespa | awk '{print $1}' | xargs -r docker rm