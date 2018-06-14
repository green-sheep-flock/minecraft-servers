#!/usr/bin/env sh
cd /opt/minecraft/data && java -jar -Xms$SPIGOT_XMS -Xmx$SPIGOT_XMX -XX:+UseConcMarkSweepGC -d64 -jar /opt/minecraft/data/server.jar
