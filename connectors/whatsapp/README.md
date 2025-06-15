# WhatsApp Connector

> [!NOTE]
> This is the old way of sending messages on whatsapp. I recommend using matrix and the mautrix-whatsapp bridge.

## Overview

Since there is no free/public API for WhatsApp, you need to use a third-party service to send WhatsApp messages. In this connector, we use an open-source Docker solution called [go-whatsapp-web-multidevice](https://github.com/aldinokemal/go-whatsapp-web-multidevice) which simulates a WhatsApp Web connection and provides an API to send messages.

## Setting Up go-whatsapp-web-multidevice

Follow these steps to set up the go-whatsapp-web-multidevice service:

### 1. Clone the Repository

Clone the `go-whatsapp-web-multidevice` repository to your local machine.

```sh
git clone https://github.com/aldinokemal/go-whatsapp-web-multidevice.git
cd go-whatsapp-web-multidevice
```

### 2. Connect to the Same Docker Network

Ensure that the WhatsApp connector and JellyHookAPI are on the same Docker network. Modify your `docker-compose.yml` file to include the necessary configuration.

For example:

```yml
services:
  whatsapp_go:
    logging:
      driver: "json-file"
      options:
        max-size: "200k"
        max-file: "10"
    image: "aldinokemal2104/go-whatsapp-web-multidevice:latest"
    build:
      context: .
      dockerfile: ./docker/golang.Dockerfile
    restart: 'always'
    ports:
      - "3000:3000"
    networks:
      net-chill:
        ipv4_address: 10.10.66.200


networks:
  net-chill:
    external: true
    driver: bridge
    ipam:
      config:
        - subnet: 10.10.66.0/24
```

### 3. Build and Run the Docker Container

Build and run the Docker container for the WhatsApp service.

```sh
docker-compose up -d --build
```

### 4. Environment Variables

Modify the [`.env`](.env.example) file directory with the necessary environment variables:

```sh
mv .env.example .env
# Open it with your prefered editor to set the variables
```

By following these steps, you can successfully integrate the WhatsApp connector with JellyHookAPI using the `go-whatsapp-web-multidevice` service.

