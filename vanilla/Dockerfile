FROM openjdk:jre-alpine


# Install python for update script
RUN apk add --no-cache python3


# Minecraft Server Options
ENV MINECRAFT_XMS 1G
ENV MINECRAFT_XMX 1G
ENV MINECRAFT_VERSION release


# Mount server data volume and expose Minecraft port
VOLUME /opt/minecraft/data/
EXPOSE 25565


# Install update & launch scripts
ADD start.sh /opt/minecraft/start.sh
ADD update.py /opt/minecraft/update.py
RUN chmod +x /opt/minecraft/start.sh /opt/minecraft/update.py


# Ready
WORKDIR /opt/minecraft/
CMD /opt/minecraft/update.py && /opt/minecraft/start.sh
