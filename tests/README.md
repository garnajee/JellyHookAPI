# Manual Integration Testing Guide

This document provides instructions for setting up an environment for manual end-to-end testing of JellyHookAPI with a live Jellyfin server.

**Note:** These are not automated tests. The main project `README.md` refers to a command for running unit tests (`python3 -m unittest discover tests`), but this repository currently does not contain any automated test files. The instructions below are for manual verification only.

## Prerequisites

- Docker and Docker Compose
- A cloned version of this JellyHookAPI repository.
- A sample movie file to add to the Jellyfin library.

## Setup Instructions

The testing setup involves running two services in Docker: Jellyfin and JellyHookAPI itself.

### 1. Prepare Jellyfin Folders

You need to create local directories that will be mounted by the Jellyfin container for configuration and media.

From the root of this repository, run:
```sh
mkdir -p tests/jellyfin_test_data/{config,data/movies}
```
This ensures the test-specific data for Jellyfin is contained within the `tests` directory.

### 2. Configure Environment Variables

You will need to configure two `.env` files:

- **JellyHookAPI:** Copy the root `.env.example` to `.env` and fill in the required values (like `TMDB_API_KEY`). The Jellyfin URL should be `http://jellyfin:8096` to connect to the Jellyfin container.
- **Connector:** Go to the connector directory you want to test (e.g., `connectors/discord/`), copy its `.env.example` to `.env`, and fill in the service-specific details (e.g., Discord webhook URL).

### 3. Run Docker Compose

To run the test environment, you will use two `docker-compose` files together. From the root of the repository, run:
```sh
docker-compose -f docker-compose.yml -f tests/docker-compose-jellyfin.yml up --build
```
This command starts both the JellyHookAPI service (from the main `docker-compose.yml`) and the Jellyfin test server (from `tests/docker-compose-jellyfin.yml`).

### 4. Configure Jellyfin

Once the containers are running, you need to set up Jellyfin and the webhook plugin:

1.  Open your browser and navigate to the Jellyfin UI (e.g., `http://localhost:8097`).
2.  Complete the initial Jellyfin setup wizard.
3.  Install the **Webhook plugin** from `Dashboard > Plugins > Catalogue`. Restart Jellyfin when prompted.
4.  Configure the webhook plugin (`Dashboard > Plugins > Webhook`) as described in the main [README.md](https://github.com/garnajee/JellyHookAPI#1-jellyfin-configuration), using `http://jellyhookapi:7778/api` as the Webhook URL.

### 5. Trigger a Notification

1.  Place your sample movie file into the `tests/jellyfin_test_data/data/movies` directory on your host machine.
2.  In the Jellyfin Dashboard, go to `Scheduled Tasks`.
3.  Run the **Scan Media Library** task to make Jellyfin detect the new file.
4.  Once the scan is complete, run the **Webhook Notifier** task.

You should receive a notification in the service you configured (e.g., Discord).

### Cleaning Up

To stop and remove the test containers, run:
```sh
docker-compose -f docker-compose.yml -f tests/docker-compose-jellyfin.yml down
```

To perform another test, you can remove the movie file from the media folder, re-scan the library, and then add it back to trigger the notification again.
