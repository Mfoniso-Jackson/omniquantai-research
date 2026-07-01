import json
from pathlib import Path
from typing import Any, Dict, Optional


class RunStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

    def all(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, run: Dict[str, Any]) -> None:
        runs = self.all()
        runs.append(run)
        self.path.write_text(json.dumps(runs, indent=2) + "\n", encoding="utf-8")

    def latest(self) -> Optional[Dict[str, Any]]:
        runs = self.all()
        return runs[-1] if runs else None

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        if not run_id:
            return None
        for run in self.all():
            if run.get("run_id") == run_id:
                return run
        return None
