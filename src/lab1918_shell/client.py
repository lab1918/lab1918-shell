import requests
from lab1918_shell.config import Config


def get_config():
    config = Config().get_config(profile="default")
    assert config.get("api_server") == "api.lab1918.com"
    assert config.get("api_key") != "<replace with api key>"
    return config["api_server"], config["api_key"]


class Client:
    def __init__(self) -> None:
        api_server, api_key = get_config()
        self.url = f"https://{api_server}"
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": api_key})


class TopologyClient(Client):
    def __init__(self) -> None:
        super().__init__()
        self.path = "topology"

    def get_all_topologies(self):
        response = self.session.get(url=f"{self.url}/{self.path}")
        return response

    def create_topology(self, topology_name):
        body = {
            "topology_name": topology_name,
        }
        response = self.session.post(
            url=f"{self.url}/{self.path}",
            json=body,
        )
        return response
