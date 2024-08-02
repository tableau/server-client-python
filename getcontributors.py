import json
import requests


logins = json.loads(
    requests.get("https://api.github.com/repos/tableau/server-client-python/contributors?per_page=200").text
)
for login in logins:
    print(f"* [{login["login"]}]({login["html_url"]})")
