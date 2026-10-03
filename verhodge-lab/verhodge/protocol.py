"""The verification protocol and the results collector.

Mirrors the hodge-laboratory discipline: every run executes a fixed
sequence of V-runs (V1 census two-scheme, V13 unified exact layer,
V15 certificate K, V16 SNF engine, V17 computed lattices, V18 Gross
normalization, V19 HODGE-INPUT parser, V20 Level-0 documents end to
end, V21 Dwork stand) and records a verdict for each into a JSON
results file.  The final line is ALL CHECKS PASSED or the failing
run — the asymmetric contract in action.
"""

import json
import platform
import time
from typing import Any, Dict, List

from . import __version__, __author__, __orcid__


class Results:
    def __init__(self):
        self.data: Dict[str, Any] = {
            "meta": {"version": __version__, "author": __author__,
                     "orcid": __orcid__,
                     "python": platform.python_version(),
                     "started": time.strftime("%Y-%m-%dT%H:%M:%S")},
            "runs": {},
            "stands": {},
            "certificates": {},
        }
        self.failures: List[str] = []

    def record(self, group: str, name: str, passed: bool,
               data=None) -> bool:
        entry = {"pass": bool(passed), "data": data}
        self.data.setdefault(group, {})[name] = entry
        if not passed:
            self.failures.append(f"{group}/{name}")
        return bool(passed)

    def all_passed(self) -> bool:
        return not self.failures

    def dump(self, path: str) -> None:
        self.data["meta"]["finished"] = time.strftime(
            "%Y-%m-%dT%H:%M:%S")
        self.data["meta"]["all_checks_passed"] = self.all_passed()
        with open(path, "w") as f:
            json.dump(self.data, f, indent=1, sort_keys=True, default=str)
