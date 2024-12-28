FROM alpine:3.21

# Install Dropbear
RUN apk add --no-cache dropbear

# Set up Dropbear configuration and authorized keys
RUN mkdir -p /etc/dropbear /root/.ssh && \
    chmod 700 /root/.ssh && \
    touch /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

# Set root password
RUN echo "root:xxxxxxxx" | chpasswd

# Expose SSH port
EXPOSE 22

WORKDIR /root

# Command to start Dropbear
CMD ["/usr/sbin/dropbear", "-R", "-F", "-E", "-j", "-k", "-p", "2222"]

