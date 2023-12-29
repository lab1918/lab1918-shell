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

    def get_topology(self, topology_id):
        response = self.session.get(url=f"{self.url}/{self.path}/{topology_id}")
        return response

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

    def delete_topology(self, topology_id):
        response = self.session.delete(url=f"{self.url}/{self.path}/{topology_id}")
        return response

    def update_topology(self, topology_id, topology_name):
        body = {
            "topology_name": topology_name,
        }
        response = self.session.patch(
            url=f"{self.url}/{self.path}/{topology_id}", json=body
        )
        return response

    def deploy(self, topology_id, topology_config):
        body = {
            "topology_config": topology_config,
        }
        response = self.session.post(
            url=f"{self.url}/{self.path}/{topology_id}/deploy", json=body
        )
        return response

    def undeploy(self, topology_id, topology_config):
        body = {
            "topology_config": topology_config,
        }
        response = self.session.post(
            url=f"{self.url}/{self.path}/{topology_id}/undeploy", json=body
        )
        return response

    def reserve(self, topology_id, host):
        body = host
        response = self.session.post(
            url=f"{self.url}/{self.path}/{topology_id}/reserve", json=body
        )
        return response

    def release(self, topology_id, reservation_id):
        body = {
            "reservation_id": reservation_id,
        }
        response = self.session.post(
            url=f"{self.url}/{self.path}/{topology_id}/release", json=body
        )
        return response
