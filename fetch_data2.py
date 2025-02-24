import requests
import json


def fetch_standings():
    url = "https://tulospalvelu.leijonat.fi/serie/helpers/getStandings.php"
    payload = {
        "season": "2025",
        "stgid": "8723"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }

    response = requests.post(url, data=payload, headers=headers)
    print("Status code:", response.status_code)

    try:
        data = response.json()
        print("JSON data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Response text:", response.text)


if __name__ == "__main__":
    fetch_standings()
