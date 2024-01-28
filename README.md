## JellyHookAPI Docker Compose Setup

This docker-compose setup provides a straightforward way to deploy `jellyhookapi`, a Flask application that serves as a webhook receiver for Jellyfin media server notifications. Here's how to get it running and configured:

### Prerequisites

- Docker, and docker-compose or the compose plugin installed on your system.

### Getting Started

1. Clone this repository to your local machine or download it using `cURL` or `wget`:

```bash
# using cURL
$ curl -LOk https://github.com/garnajee/JellyHookAPI/archive/master.tar.gz

# using wget
$ wget https://github.com/garnajee/JellyHookAPI/archive/master.tar.gz

# extract content
$ tar xvzf master.tar.gz
```

2. Ensure you have a `.env` file in the root directory with the required environment variables (see below for details).
3. Modify the Jellyfin server configuration to send notifications to the webhook URL provided by `jellyhookapi`.

### Docker Compose Configuration

The `docker-compose.yml` file specifies the following configurations:

- **Container Name**: `jellyhookapi`.
- **Restart Policy**: Always.
- **Image**: Python Alpine.
- **Working Directory**: `/app`.
- **Environment Variables**: Loaded from the `.env` file.
- **Volumes**: Maps the current directory to `/app` in the container.
- **Command**: Installs dependencies and starts the `jellyhookapi.py` script.
- **Ports**: Maps port `7778` on the host to port `7778` in the container. You can change it to fit your configuration.

### Environment Variables

Make sure your `.env` file includes the following variables:

- `TMDB_API_KEY`: Your TMDB API key.
- `LANGUAGE`: Main language for media details.
- `LANGUAGE2`: Secondary language for trailers.
- `WHATSAPP_API_URL`: URL for your WhatsApp API.
- `WHATSAPP_NUMBER`: Your WhatsApp number or group ID.
- `WHATSAPP_API_USERNAME`: Username for WhatsApp API.
- `WHATSAPP_API_PWD`: Password for WhatsApp API.

### Running the Docker Compose

To start the Docker Compose setup, run the following command in the root directory of the repository:

```bash
$ sudo docker-compose up -d
```

### Jellyfin Configuration

In your Jellyfin Web UI:

1. Go to **Extensions** > **Webhook** > **Add Generic Destination**.
2. Fill in the following details:
   - **Webhook Name**: Choose a name.
   - **Webhook URL**: Use the URL provided by `jellyhookapi` (Depending your docker network configuraion)
   - **Notification Type**: Select **Item Added**.
   - **Template**: Use the provided code: 

```
{
  "media_type": "
    {{~#if_equals ItemType 'Movie'~}}
      movie
    {{~else~}}
      tv
    {{~/if_equals~}}",
  "title": "
    {{~#if_equals ItemType 'Season'~}}
        Season-added: {{{SeriesName}}}, {{{Name}}}
    {{~else~}}
      {{~#if_equals ItemType 'Episode'~}}
        Episode-added: {{{SeriesName}}}, S{{SeasonNumber00}}E{{EpisodeNumber00}} - {{{Name}}}
        {{~else~}}
          {{{Name}}} ({{Year}}) has been added
      {{~/if_equals~}}
    {{~/if_equals~}}
    ",
  "imdb": "{{Provider_imdb}}",
  "tmdb": "{{Provider_tmdb}}",
  "watch_link": "{{ServerUrl}}/web/index.html#!/details?id={{ItemId}}&serverId={{ServerId}}"
}
```

3. Add a Request Header:
   - **Key**: `Content-Type`.
   - **Value**: `application/json`.
4. Save your configuration.

With these configurations in place, your Jellyfin server will send notifications to `jellyhookapi` upon media item additions.

---

Feel free to reach out if you encounter any issues or need further assistance!


