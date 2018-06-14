#!/usr/bin/env sh
cd /opt/minecraft/data && java -jar -Xms$MINECRAFT_XMS -Xmx$MINECRAFT_XMX -d64 -jar /opt/minecraft/data/server.jar -o true nogui
