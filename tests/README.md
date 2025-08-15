# Integration Testing Guide with Mock Server

This document provides instructions for setting up a local testing environment for JellyHookAPI using a "mock" server to simulate Jellyfin API responses.

This approach is lighter and faster than running a full Jellyfin server.

## Prerequisites

- Docker and Docker Compose
- A cloned version of the JellyHookAPI repository.
- `curl` installed on your machine.

## How It Works

The test environment consists of two Docker services:
1.  **`jellyhookapi`**: Your application, which listens for notifications on port `7778`.
2.  **`mock_jellyfin`**: A small web server that simulates the Jellyfin API. When `jellyhookapi` requests details for an `item_id`, it will return a predefined JSON response.

Tests are triggered manually by sending `curl` requests to `jellyhookapi`, thereby simulating a notification sent by Jellyfin.

## 1. Environment Setup

You need to configure two `.env` files: one for the API and one for the connector.

### a. JellyHookAPI
Copy the `.env.example` file from the project root to a new file named `.env`.
**Fill in the required values** (e.g., `TMDB_API_KEY`).

**The most important setting** is the Jellyfin URL. It must point to our mock server:
```dotenv
# .env file at the project root
JELLYFIN_API_URL=http://mock_jellyfin:8096
JELLYFIN_API_KEY=any_fake_key_will_work
JELLYFIN_USER_ID=any_fake_user_id
# ... other variables ...
TMDB_API_KEY=YOUR_KEY_HERE
```

### b. Connector
Go to the directory of the connector you want to test (e.g., `connectors/discord/`), copy its `env.example` to `.env`, and fill in the service-specific details (e.g., the Discord webhook URL).

## 2. Launching the Test Environment

From the root of the project, run the following command:
```sh
docker-compose -f tests/docker-compose.test.yml up --build
```
This command will build and start the `jellyhookapi` and `mock_jellyfin` containers. You should see the logs from both services in your terminal.

## 3. Running the Tests

Open a **new terminal window**.

First, make the test scripts executable:
```sh
chmod +x tests/requests/*.sh
```

Next, run each script one by one to simulate different notifications:

```sh
# Test adding a movie
./tests/requests/01_add_movie.sh

# Test adding a 4K HDR episode
./tests/requests/02_add_episode.sh

# Test adding a season (should not call the Jellyfin API for details)
./tests/requests/03_add_season.sh

# Test adding a documentary
./tests/requests/04_add_documentary.sh
```

### Expected Outcome

For each script you run:
1.  The terminal will display a confirmation that the request was sent.
2.  In the terminal where `docker-compose` is running, you will see logs from `jellyhookapi` processing the request, and logs from `mock_jellyfin` showing it received a request for information.
3.  You should receive a formatted notification in the service you configured (e.g., Discord).

## 4. Cleaning Up

To stop and remove the test containers, return to the terminal where `docker-compose` is running, press `Ctrl+C`, and then run:
```sh
docker-compose -f tests/docker-compose.test.yml down
```

