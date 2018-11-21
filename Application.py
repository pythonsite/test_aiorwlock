#! /usr/bin/env python3
# .-*- coding:utf-8 .-*-


from aiohttp import web
import asyncio
import aiomysql
import configparser
import ssl
import logging
import time
from logging.handlers import RotatingFileHandler

from handler.Database import Database
from handler.cnthandler import CntHandler


class Application:

    def __init__(self):
        self.db = None
        self.loop = None
        self.mysql = {}
        self.http = {}
        self.log = {}

    def setLog(self):
        handler = RotatingFileHandler(self.log["file"], maxBytes=self.log["size"] * 1024 * 1024, backupCount=self.log["backup"])
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)

    def load(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.http["host"] = config.get("general", "host")
        self.http["port"] = config.getint("general", "port")
        self.http["sslenable"] = config.getboolean("general", "sslenable")
        self.http["ca"] = config.get("general", "ca")
        self.http["key"] = config.get("general", "key")
        self.http["cert"] = config.get("general", "cert")
        self.mysql["host"] = config.get("mysql", "host")
        self.mysql["port"] = config.getint("mysql", "port")
        self.mysql["user"] = config.get("mysql", "user")
        self.mysql["password"] = config.get("mysql", "password")
        self.mysql["db"] = config.get("mysql", "db")
        self.mysql["minsize"] = config.getint("mysql", "minsize")
        self.mysql["maxsize"] = config.getint("mysql", "maxsize")
        self.log["file"] = config.get("log", "file")
        self.log["size"] = config.getint("log", "size")
        self.log["backup"] = config.getint("log", "backup")

    async def app_factory(self):
        pool = await aiomysql.create_pool(host=self.mysql["host"], port=self.mysql["port"], user=self.mysql["user"],
                                          password=self.mysql["password"], db=self.mysql["db"],
                                          minsize=self.mysql["minsize"], maxsize=self.mysql["maxsize"],
                                          loop=self.loop, autocommit=True)
        self.db = Database(pool)

        cnt_handler = CntHandler(self.db, self.loop)
        app = web.Application()
        app.add_routes([
            web.post("/interface_cnt/set", cnt_handler.cnt_set),
            web.post("/interface_cnt/inc", cnt_handler.cnt_inc),
            web.post("/interface_cnt/dec", cnt_handler.cnt_dec),
        ])
        return app

    def run_forever(self):
        while True:
            try:
                self.load()
                # self.setLog()
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                ctx = None
                if self.http["sslenable"]:
                    ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                    ctx.load_verify_locations(self.http["ca"])
                    ctx.load_cert_chain(certfile=self.http["cert"], keyfile=self.http["key"])
                web.run_app(self.app_factory(), ssl_context=ctx, host=self.http["host"], port=self.http["port"])
                break
            except Exception as e:
                logging.error(e)
                time.sleep(2)
