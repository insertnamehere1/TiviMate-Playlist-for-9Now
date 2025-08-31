FROM python:3.12-alpine

# Set working directory
WORKDIR /kodi.proxy

# Install OS packages you need
RUN apk add --no-cache \
    bash \
    curl \
    git \
    iputils \
    procps \
    iproute2 \
    vim \
    less \
    build-base \
    unzip

# Clone kodi.proxy
RUN git clone https://github.com/matthuisman/kodi.proxy.git .

# Download and install Slyguy addons
RUN mkdir -p /kodi.proxy/addons && \
    curl -L -o /tmp/slyguy.9now.zip https://github.com/matthuisman/slyguy.addons/raw/master/slyguy.9now/slyguy.9now-0.4.4.zip && \
    unzip /tmp/slyguy.9now.zip -d /kodi.proxy/addons && \
    rm /tmp/slyguy.9now.zip && \
    \
    curl -L -o /tmp/repository.slyguy.zip https://github.com/matthuisman/slyguy.addons/raw/master/repository.slyguy/repository.slyguy-0.0.9.zip && \
    unzip /tmp/repository.slyguy.zip -d /kodi.proxy/addons && \
    rm /tmp/repository.slyguy.zip && \
    \
    curl -L -o /tmp/script.module.slyguy.zip https://github.com/matthuisman/slyguy.addons/raw/master/script.module.slyguy/script.module.slyguy-0.86.43.zip && \
    unzip /tmp/script.module.slyguy.zip -d /kodi.proxy/addons && \
    rm /tmp/script.module.slyguy.zip && \
    \
    curl -L -o /tmp/slyguy.dependencies.zip https://github.com/matthuisman/slyguy.addons/raw/master/slyguy.dependencies/slyguy.dependencies-0.0.29.zip && \
    unzip /tmp/slyguy.dependencies.zip -d /kodi.proxy/addons && \
    rm /tmp/slyguy.dependencies.zip

# Install Python deps via pip
RUN pip install --no-cache-dir requests

# Copy your patched plugin.py into the 9now addon
# Make sure you have plugin.py in the same folder as the Dockerfile
COPY plugin.py /kodi.proxy/addons/slyguy.9now/resources/lib/plugin.py

# Ensure plugin.py is executable
RUN chmod +x /kodi.proxy/addons/slyguy.9now/resources/lib/plugin.py

# Copy entrypoint script
COPY entrypoint.py /kodi.proxy/entrypoint.py

# Expose ports
EXPOSE 8181

# Entrypoint
ENTRYPOINT ["python3", "entrypoint.py"]

