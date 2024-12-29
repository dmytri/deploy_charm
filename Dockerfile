FROM ghcr.io/astral-sh/uv:python3.13-alpine

# Install OpenSSH
RUN apk add --no-cache openssh

WORKDIR /code

COPY pyproject.toml .
COPY tests/deploy.feature tests/
COPY tests/test_deploy.py tests/

# Set up SSH configuration
RUN ssh-keygen -A && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "Port 2222" >> /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 2222

# Start SSH service before running the main command
CMD /usr/sbin/sshd && uv run poe ci
