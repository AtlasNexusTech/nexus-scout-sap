"""
Client mémoire pour agents — utilisant le serveur central sur le LOQ.
Usage:
  from agent_memory_client import AgentMemory
  mem = AgentMemory("mon-agent", server="http://10.40.202.77:9736")
  mem.set("derniere_tache", "bounty #42 resolue")
  print(mem.get("derniere_tache"))
  print(mem.list_all())
"""

import urllib.request, json

LOQ_IP = "10.40.202.77"
DEFAULT_SERVER = f"http://{LOQ_IP}:9736"

class AgentMemory:
    def __init__(self, agent_id: str, server: str = DEFAULT_SERVER):
        self.agent_id = agent_id
        self.base = f"{server.rstrip('/')}/memory/{agent_id}"

    def _req(self, method: str, path: str = "", body: dict | None = None):
        url = f"{self.base}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return json.loads(e.read())

    def set(self, key: str, value: str) -> dict:
        return self._req("POST", body={"key": key, "value": value})

    def get(self, key: str) -> str | None:
        result = self._req("GET", f"/{key}")
        return result.get("value")

    def list_all(self) -> list[dict]:
        result = self._req("GET")
        return result.get("memories", [])

    def delete(self, key: str) -> dict:
        return self._req("DELETE", f"/{key}")
