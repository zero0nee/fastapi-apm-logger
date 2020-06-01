#!/bin/sh

curl -L -O https://artifacts.elastic.co/downloads/apm-server/apm-server-7.6.1-amd64.deb
dpkg -i apm-server-7.6.1-amd64.deb
service apm-server start