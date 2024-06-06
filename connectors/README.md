# Connectors

This directory contains the connectors for various third-party services that JellyHookAPI supports. Each connector is responsible for forwarding messages to a specific service.

## Adding a New Service Connector

To add a new service connector, follow these steps:

### 1. Create a Directory for the New Service

Create a new directory under the `connectors` folder named after the service you are integrating. Use lowercase letters and hyphens if necessary.

```sh
cd connectors
mkdir new-service
cd new-service
```

### 2. Add Environment Variables

Create a `.env` file within the new service directory. This file should contain the necessary environment variables for your service. Use the template provided in the `template` directory.

```sh
cp ../template/.env.template .env
```

### 3. Implement the Connector

Create a Python script with the following name: `myConnector_service.py`. **The script name must end with `_service.py`.**

This script should contain the implementation of the connector. Use the template provided in the `template` directory.

```sh
cp ../template/connector_template_service.py new_service.py
```

### 4. Function `send_message`

The `send_message` function is responsible for sending the formatted message to the new service. It should take two arguments:

- `message` (str): The message to be sent.
- `options` (dict): Additional options for the message (e.g., phone number, email address).

The function should return the response from the service, which can be logged or used to handle errors.

### 5. Update the Main Application

Ensure that the main application dynamically loads and uses the new connector. The application should automatically detect the new connector based on its directory and script name.

### Example

Here is a complete example of adding a new service connector for "NewService":

1. **Create Directory**

    ```sh
    mkdir connectors/new-service
    cd connectors/new-service
    ```

2. **Add Environment Variables**

    Create a `.env` file using the template:

    ```sh
    cp ../template/.env.template .env
    ```

3. **Implement the Connector**

    Create a file `new_service.py` using the template:

    ```sh
    cp ../template/connector_template.py new_service.py
    ```

4. **Verify and Test**

    Ensure the main application correctly detects and uses the new connector. Test the integration by sending a sample message and verifying the response.

By following these steps, you can easily add new service connectors to JellyHookAPI, making it more versatile and adaptable to various third-party services.

