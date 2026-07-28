import requests
import os

NAMECOM_USER = os.getenv("NAMECOM_USER")
NAMECOM_TOKEN = os.getenv("NAMECOM_TOKEN")
BASE_URL = "https://api.name.com/v4"

def create_dns_record(subdomain, ip):
    url = f"{BASE_URL}/domains/neweb.me/records"
    res = requests.post(
        url,
        auth=(NAMECOM_USER, NAMECOM_TOKEN),
        json={
            "host": subdomain,
            "type": "A",
            "answer": ip,
            "ttl": 300
        }
    )
    data = res.json()
    print(f"name.com response: {data}")
    if res.status_code not in [200, 201]:
        raise Exception(f"DNS creation failed: {data}")
    return data

def delete_dns_record(record_id):
    url = f"{BASE_URL}/domains/neweb.me/records/{record_id}"
    res = requests.delete(
        url,
        auth=(NAMECOM_USER, NAMECOM_TOKEN)
    )
    return res.status_code == 204
