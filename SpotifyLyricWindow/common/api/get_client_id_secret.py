#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
from ..path import CLIENT_ID_SECRET_PATH


def get_client_id_secret():
    with CLIENT_ID_SECRET_PATH.open(encoding="utf-8") as f:
        data_json = json.load(f)
    if data_json.get("client_id") and data_json.get("client_secret"):
        return data_json["client_id"], data_json["client_secret"]
    else:
        raise NotImplementedError("请完善resource文件夹中client_id_secret.json中的信息")
