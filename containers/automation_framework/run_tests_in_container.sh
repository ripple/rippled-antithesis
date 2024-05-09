#!/bin/bash

mkdir auto
tar xfzv automation-main.tar.gz -C auto

docker run --rm -it \
  -v $PWD:/root/automation_framework \
  -w /root/automation_framework  \
  --network rippled-net \
  --name automation \
  python:3.12-slim-bullseye bash -c "./run_tests.sh"
