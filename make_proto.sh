#!/usr/bin/env bash
protoc -I=./proto/ --python_out=./pbarray/ ./proto/pbarray.proto
