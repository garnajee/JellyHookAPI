# Discord Connector

## Overview

This connector allows JellyHookAPI to send notifications to a Discord channel using a webhook.

## Setting Up the Discord webhook

To set up a Discord webhook, follow these steps:

1. **Create a Webhook in Discord**

    - Open your Discord server.
    - Go to the channel where you want to receive notifications.
    - Click on the settings icon next to the channel name.
    - Select **Integrations**.
    - Click on **Create Webhook**.
    - Name your webhook and copy the **Webhook URL**.

2. **Configure the .env File**

    Create a `.env` file in the `connectors/discord` directory based on the `.env.example` file:

    ```sh
    cp .env.example .env
    ```

    Edit the `.env` file and add your Discord webhook URL:

    ```env
    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
    ```

## Testing the script

You can test the Discord connector script by running it directly. Ensure you have the necessary environment variables set up in your `.env` file.

```sh
pip install requests
python discord_service.py
```

