#!/usr/bin/env python3

import requests

url = "https://your.matrix.server/_matrix/client/r0/login"
username = "registeredusername"
password = "thepassword"

headers = {
    "Content-Type": "application/json"
}
payload = {
    "type": "m.login.password",
    "user": username,
    "password": password
}

response = requests.post(url, headers=headers, json=payload)
access_token = response.json().get("access_token")
print(f"Access Token: {access_token}")

