import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml


class PoorMansBeaker:
    """
    An HTTPS client for Beaker for when RPC is too slow
    """
    def __init__(self, token: str, base_url: str = "https://beaker.org"):
        self.token = token
        self.base_url = f"{base_url}/api/v3"
    
    @classmethod
    def from_env(cls) -> "PoorMansBeaker":
        token = os.environ.get("BEAKER_TOKEN")
        if not token:
            config_path = Path.home() / ".beaker" / "config.yml"
            if config_path.exists():
                with open(config_path) as f:
                    token = yaml.safe_load(f)["user_token"]
        if not token:
            raise ValueError("No BEAKER_TOKEN found")
        return cls(token)
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        resp = requests.get(
            f"{self.base_url}/{endpoint}",
            headers={"Authorization": f"Bearer {self.token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json()


class JobClient:
    def __init__(self, beaker: PoorMansBeaker):
        self.beaker = beaker

    def get(self, job_id: str) -> Dict:
        """Get detailed info for a single job."""
        return self.beaker._get(f"jobs/{job_id}")

    def list(
        self,
        author: Optional[str] = None,
        finalized: bool = False,
        limit: Optional[int] = None,
        kind: Optional[str] = None,  # "execution" or "session"
    ) -> List[Dict]:
        params: Dict[str, Any] = {"finalized": finalized}

        if kind:
            params["kind"] = kind

        if author:
            # Resolve username to ID
            user = self.beaker._get(f"users/{author}")
            params["author"] = user["id"]

        jobs = []
        total_fetched = 0
        while True:
            page = self.beaker._get("jobs", params)
            page_data = page.get("data", [])
            if not page_data:
                # No jobs at all, just return []
                return []
            # Handle limit enforcement
            if limit is not None:
                needed = limit - total_fetched
                jobs.extend(page_data[:needed])
                total_fetched += len(page_data[:needed])
                if total_fetched >= limit:
                    break
            else:
                jobs.extend(page_data)
            cursor = page.get("next") or page.get("nextCursor")
            if not cursor:
                break
            params["cursor"] = cursor

        return jobs[:limit] if limit is not None else jobs


# Example use
if __name__ == "__main__":
    beaker = PoorMansBeaker.from_env()
    workloads = JobClient(beaker=beaker).list(author="davidh", finalized=False)
    print(f"Running experiments: {len(workloads)}")