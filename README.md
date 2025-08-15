<br/>
<p align="center">
  <img src="logo.png" alt="JellyHookAPI Logo" width="250px" height="250px"/>
  <h2 align="center">JellyHookAPI</h2>
</p>
<p align="center">
  <a href="https://github.com/garnajee/JellyHookAPI/issues/new?template=bug_report.md"><img src="https://img.shields.io/badge/report-issue-red" alt="Report Issue"></a> 
  <a href="https://github.com/garnajee/JellyHookAPI/issues/new?template=feature_request.md">
  <img src="https://img.shields.io/badge/request-feature-fuchsia" alt="Request Feature"></a>
  <br/>
  <img src="https://img.shields.io/github/contributors/garnajee/JellyHookAPI?color=dark-green" alt="Contributors">
  <img src="https://img.shields.io/github/issues/garnajee/JellyHookAPI" alt="Issues">
  <img src="https://img.shields.io/github/license/garnajee/JellyHookAPI?color=blue" alt="License">
</p>

---

## Table of Contents

1. [Introduction](#introduction)
2. [Example](#example)
3. [Supported Services](#supported-services)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Contributing](#contributing)
8. [License](#license)

---

## Introduction

JellyHookAPI is a flexible and extensible API that allows you to receive notifications from [Jellyfin](https://github.com/jellyfin/jellyfin) and forward them to multiple third-party services (*connectors*). The system is designed to be dynamic, enabling easy addition of new connectors without modifying the core code.

---

## Use Case

JellyHookAPI can receive media notifications and forward markdown-formatted messages with media details and trailers to services like WhatsApp. 

For instance, when a new movie is added to your media server, after receiving notification from Jellyfin, JellyHookAPI can send a detailed message including the movie title, overview, IMDb/TMDb links, and trailer links. It can also be configured to connect to your Jellyfin API to add technical details such as video resolution, audio tracks, and subtitles directly into the notification.

A notable feature for French-speaking users is its ability to automatically detect and label French audio tracks as `VFF` (Version Française de France) or `VFQ` (Version Française Québécoise) based on metadata, providing more precise information about the available audio.

---

## Supported Services

Total Supported Services: **3**

| Service  | Send Messages | Send Images |
|----------|:-------------:|:-----------:|
| Matrix   | ✅            | ✅          |
| WhatsApp | ✅            | ✅          |
| Discord  | ✅            | ✅          |
| *Soon*   | ✅            | ❌          |

---

## Prerequisites

- Docker and Docker Compose
- TMDB API Key ([it's free](https://www.themoviedb.org/signup))
- Jellyfin API Key (see Jellyfin Configuration section)

---

## Installation

### Clone the Repository

Using `git`:

```sh
git clone https://github.com/garnajee/JellyHookAPI.git
```

Or using `cURL`:

```sh
curl -L https://github.com/garnajee/JellyHookAPI/archive/main.tar.gz -o JellyHookAPI.tar.gz
tar xzf JellyHookAPI.tar.gz
rm JellyHookAPI.tar.gz
mv JellyHookAPI-main JellyHookAPI
```

Navigate to the folder:

```sh
cd JellyHookAPI
```

### Environment Setup

Modify the `.env.example` file in the project root directory and add your configuration variables.

```sh
mv .env.example .env
# Open it with your prefered editor to set the variables
```

### Docker Setup (Recommended for Production)

Ensure Docker and Docker Compose are installed. Use the following command to build and run the application:

```sh
docker-compose up -d
```

### Local Development (without Docker)

If you want to run the application without Docker for development purposes, you can follow these steps:

1.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2.  **Run the application with Gunicorn:**
    ```sh
    gunicorn --workers 4 --bind 0.0.0.0:7778 app:app
    ```
    The application will be available at `http://localhost:7778`.

---

## Configuration

You must first configure Jellyfin, then configure the connector(s) you want to use.

### 1. Jellyfin Configuration

To allow `JellyHookAPI` to fetch technical details, you need to provide it with access to your Jellyfin server.

1.  **Generate an API Key**: In your Jellyfin Dashboard, go to **API Keys**, click the **+** sign, give it a name (e.g., `jellyhookapi`), and save. Copy the generated key.
2.  **Find your User ID**: In the Jellyfin Dashboard, go to **Users**, click on your user profile, and copy the ID from the page's URL (it's the string of letters and numbers at the end).
3.  **Set Environment Variables**: In your `.env` file, set the following variables:
    -   `JELLYFIN_API_URL`: The full URL to your Jellyfin server (e.g., `http://192.168.1.10:8096`).
    -   `JELLYFIN_API_KEY`: The API key you generated.
    -   `JELLYFIN_USER_ID`: The User ID you found.

You also need to install the ["Webhook plugin"](https://github.com/jellyfin/jellyfin-plugin-webhook).

In your Jellyfin Web UI:

1. Go to **Dashboard > Plugins** > **Catalogue** > **Webhook**: install it and restart Jellyfin.
2. Go back to **Plugins** > **Webhook** > **Add Generic Destination**.
3. Fill in the following details:
   - **Webhook Name**: Choose a name (e.g., `jellyhookapi`).
   - **Webhook URL**: Use the URL for `jellyhookapi` (e.g., `http://jellyhookapi:7778/api`).
   - **Notification Type**: Select **Item Added**.
   - **Template**: Use the following code. This ensures the `ItemId` is sent, which is required to fetch technical details.

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
  "item_id": "{{ItemId}}",
  "watch_link": "{{ServerUrl}}/web/index.html#!/details?id={{ItemId}}&serverId={{ServerId}}"
}
```

3. Add a Request Header:
   - **Key**: `Content-Type`.
   - **Value**: `application/json`.
4. Save your configuration.


### 2. Configure a connector - Example: Configuring WhatsApp Connector

JellyHookAPI is designed to be extensible through connectors. Each connector is responsible for forwarding messages to a third-party service.

See this [README](connectors/whatsapp/README.md) for more informations.

### 3. (Optional) Disabling Episode Notifications

If you prefer not to receive notifications for newly added episodes, you can disable them by setting the following variable in your `.env` file:

```
SKIP_EPISODE_NOTIFICATIONS=True
```

By default, episode notifications are enabled (`False`).

---

## Testing

This project includes unit tests to ensure the reliability of its components. To run the tests, navigate to the root directory of the project and execute the following command:

```sh
python3 -m unittest discover tests
```

This will automatically discover and run all tests located in the `tests` directory.

---

## Contributing

I'd be happy to welcome contributions to JellyHookAPI! To contribute:

### Adding a New Connector

1. **Fork the Repository**: Fork the repo on GitHub and clone your fork locally.
2. **Create a Branch**: Create a new branch for your connector (`git checkout -b new-connector/your-connector`)
3. **Add Your Connector**: Create a new folder in `connectors` and add your connector implementation.
  - Follow [these steps](connectors/README.md) to add a new connector properly
4. **Update Documentation**: Update the README in the new connector folder to include details and its setup.
5. **Push to the Branch**: Push your changes to the new branch (`git push origin new-connector/your-connector`)
6. **Pull Request**: Submit a pull request with a detailed description of your changes.

### General Code Contributions

1. **Fork the Repository**: Fork the repo on GitHub and clone your fork locally.
2. **Create a Branch**: Create a new branch for your changes (`git checkout -b feature/AmazingFeature`)
3. **Make Changes**: Make your changes, including documentation.
4. **Push to the Branch**: Push your changes to the new branch (`git push origin feature/AmazingFeature`)
5. **Pull Request**: Submit a pull request with a detailed description of your changes.

---

#### TODO

- [x] send non-formatted links (trailer, t/imdb) to connectors
- [ ] improve non-movie/serie message without tmdb/imdb, or find other source

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

