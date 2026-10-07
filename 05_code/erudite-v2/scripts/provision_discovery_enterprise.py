import google.auth
from google.auth.transport.requests import Request
import requests
import os

PROJECT_ID = os.environ.get("PROJECT_ID", "project-a1f62154-a7ad-4b37-93b")

print("Acquiring Google Application Default Credentials...")
credentials, project = google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

print("Refreshing credentials to obtain access token...")
auth_request = Request()
credentials.refresh(auth_request)
token = credentials.token

url = f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}:provision"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "x-goog-user-project": PROJECT_ID
}

data = {
    "name": f"projects/{PROJECT_ID}",
    "acceptDataUseTerms": True,
    "dataUseTermsVersion": "2022-11-23"
}

print(f"Sending POST request to {url} with terms-acceptance payload...")
response = requests.post(url, headers=headers, json=data)

print(f"HTTP Status Code: {response.status_code}")
print("Response Text:")
print(response.text)
