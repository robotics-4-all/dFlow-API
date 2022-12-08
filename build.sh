#!/usr/bin/env bash

TAG=0.1.0

docker build --build-arg GIT_ACCESS_TOKEN=${GIT_ACCESS_TOKEN} -t dflow-api:${TAG} .
