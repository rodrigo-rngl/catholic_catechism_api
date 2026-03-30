from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

QUERY_SCOPE_PATH = Path(__file__).with_name("query_scope.json")

SCOPE_TO_LABEL: Dict[str, int] = {
    "catholic_doctrine": 0,
    "general_christian": 1,
    "off_topic": 2,
}


def load_raw_query_scope_data() -> List[Dict[str, str]]:
    with QUERY_SCOPE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_tuning_data() -> List[Dict[str, int | str]]:
    raw_data = load_raw_query_scope_data()
    return [
        {
            "text": item["query"],
            "label": SCOPE_TO_LABEL[item["scope"]],
        }
        for item in raw_data
    ]


RAW_QUERY_SCOPE_DATA = load_raw_query_scope_data()
TUNING_DATA = load_tuning_data()
