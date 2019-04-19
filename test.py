from arkclient import ArkClient
import os

client = ArkClient(os.environ.get("THEARK_SERVER", "http://0.0.0.0:5000"))

name = "CrowdControl"
if not client.login("admin", "password"):
    raise Exception("Couldnt log in")
addrs = client.getAddresses(name)
