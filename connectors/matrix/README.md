# Matrix Connector

This script allows you to send an image followed by a text message to a specified Matrix room. The image dimensions are hardcoded to width=342 and height=513, matching the `w342` image size downloaded from the TMDb API.

### Prerequisites

- A registered Matrix user

### Steps to Get Started

#### 1. Obtain an Access Token

To send messages to Matrix rooms, you need an access token for a registered Matrix user.

1. Modify the `get_access_token` script to include the correct `url`, `username`, and `password` for an already registered Matrix user.
2. Run the modified script to obtain the access token.

#### 2. Modify .env.example with Retrieved Information

Rename `.env.example` to `.env` and populate it with the retrieved information.

#### 2.1. Find the Room ID

To find the ID of a room in Matrix:

1. Open your Matrix client (e.g. Element).
2. Go to the room you want to send messages to.
3. Click on the room settings (usually a gear icon).
4. Look for the "Advanced" section or similar where you can find the "Internal room ID" (e.g. `!yourroomid:yourserver.com`).

