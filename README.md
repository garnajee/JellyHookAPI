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

## Example

JellyHookAPI can receive media notifications and forward markdown-formatted messages with media details and trailers to services like WhatsApp. 

For instance, when a new movie is added to your media server, after receiving notification from Jellyfin, JellyHookAPI can send a detailed message including the movie title, overview, IMDb and TMDb links, and trailer links to your preferred communication platforms.

---

## Supported Services

Total Supported Services: **2**

| Service  | Send Messages | Send Images |
|----------|:-------------:|:-----------:|
| WhatsApp | ✅            | ✅          |
| *Soon*   | ✅            | ❌          |

---

## Prerequisites

- Docker and Docker Compose
- TMDB API Key ([it's free](https://www.themoviedb.org/signup))

---

## Installation

### Clone the Repository

Usgin `git`:

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

### Docker Setup

Ensure Docker and Docker Compose are installed. Use the following command to build and run the application:

```sh
docker-compose up -d
```

---

## Configuration

JellyHookAPI is designed to be extensible through connectors. Each connector is responsible for forwarding messages to a third-party service.

### Example: Configuring WhatsApp Connector

See this [README](connectors/README.md) for more informations.

---

## Contributing

I'd be happy to welcome contributions to JellyHookAPI! To contribute:

### Adding a New Connector

1. **Fork the Repository**: Fork the repo on GitHub and clone your fork locally.
2. **Create a Branch**: Create a new branch for your connector.
3. **Add Your Connector**: Create a new folder in `connectors` and add your connector implementation.
4. **Update Documentation**: Update the README in the new connector folder to include details of the new connector and its setup.
5. **Pull Request**: Submit a pull request with a detailed description of your changes.

### General Code Contributions

1. **Fork the Repository**: Fork the repo on GitHub and clone your fork locally.
2. **Create a Branch**: Create a new branch for your changes (`git checkout -b feature/AmazingFeature`)
3. **Make Changes**: Make your changes, including documentation.
4. **Push to the Branch**: Push your changes to the new branch (`git push origin feature/AmazingFeature`)
5. **Pull Request**: Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

