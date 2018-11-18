# -*- coding: utf-8 -*-
import json
import time
import datetime
import hashlib


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def sha1(text):
    hash = hashlib.sha1()
    hash.update(text.encode('utf-8'))
    return hash.hexdigest()


def currentTime():
    current = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return current


def dictToJson(po):
    jsonstr = json.dumps(po, ensure_ascii = False, cls = CJsonEncoder)
    return jsonstr


def jsonToDict(jsonstr):
    d = json.loads(jsonstr)
    return d


