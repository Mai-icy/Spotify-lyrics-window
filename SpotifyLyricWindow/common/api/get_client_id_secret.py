#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
from pathlib import Path


def get_client_id_secret():
    CLIENT_ID_SECRET_PATH = Path(r"resource\client_id_secret.json")
    if not CLIENT_ID_SECRET_PATH.exists():
        json.dumps(json.dumps({"client_id": "", "client_secret": ""}, indent=4, ensure_ascii=False))
    with CLIENT_ID_SECRET_PATH.open(encoding="utf-8") as f:
        data_json = json.load(f)
    if data_json.get("client_id") and data_json.get("client_secret"):
        return data_json["client_id"], data_json["client_secret"]
    else:
        raise NotImplementedError("请完善resource文件夹中client_id_secret.json中的信息")