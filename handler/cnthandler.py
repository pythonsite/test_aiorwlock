#! /usr/bin/env python3
# .-*- coding:utf-8 .-*-


import logging
from asyncio import locks
from aiohttp import web
import uuid

from utils import util


class CntHandler(object):

    def __init__(self, db, loop):
        self.db = db
        self.loop = loop
        self.company_lock = {}

    def response(self, request, msg):
        peer = request.transport.get_extra_info('peername')
        logging.info("request url[%s] from[%s]: %s", request.raw_path, peer, msg)
        origin = request.headers.get("Origin")
        if origin is not None:
            headers = {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true"}
            resp = web.Response(text=util.dictToJson(msg), content_type='application/json', headers=headers)
        else:
            resp = web.Response(text=util.dictToJson(msg), content_type='application/json')
        return resp

    async def cnt_set(self, request):
        post = await request.post()
        logging.info('post %s', post)
        company_name = post.get("company")
        cnt = post.get("cnt")
        sql = "update shield.company set count=%s where name=%s"
        args_values = [cnt, company_name]
        rwlock = self.company_lock.get(company_name, "")
        if not rwlock:
            rwlock = locks.Lock(loop=self.loop)
            self.company_lock[company_name] = rwlock
        with await rwlock:
            msg = dict()
            po_sql = "select * from shield.company where name=%s"
            po = await self.db.get(po_sql, company_name)
            if not po:  # 找不到企业
                logging.error("not found company name [%s]", company_name)
                msg["code"] = 404
                msg["code"] = "not found company"
                return self.response(request, msg)
            res = await self.db.execute(sql, args_values)
            if not isinstance(res, int):
                logging.error("sql update is err:", res)
                msg["code"] = 403
                msg["reason"] = "set fail"
                return self.response(request, msg)
            logging.info("company [%s] set cnt [%s] is success", company_name, cnt)
            msg["code"] = 200
            msg["reason"] = "ok"
            return self.response(request, msg)

    async def cnt_inc(self, request):
        post = await request.post()
        logging.info('post %s', post)
        company_name = post.get("company")
        cnt = int(post.get("cnt", 0))
        rwlock = self.company_lock.get(company_name, "")
        if not rwlock:
            rwlock = locks.Lock(loop=self.loop)
            self.company_lock[company_name] = rwlock
        logging.info(rwlock)
        with await rwlock:
            uuid_s = uuid.uuid1().hex
            logging.debug("[%s]---[%s]", uuid_s, id(rwlock))
            msg = dict()
            sql = "select * from shield.company where name=%s"
            po = await self.db.get(sql, company_name)
            if not po:  # 找不到企业
                logging.error("not found company name [%s]", company_name)
                msg["code"] = 404
                msg["code"] = "not found company"
                return self.response(request, msg)
            old_cnt = po.get("count")
            po_cnt = int(po.get("count"))
            res = po_cnt + cnt
            update_sql = "update shield.company set count=%s where name=%s"
            args_values = [res, company_name]
            update_res = await self.db.execute(update_sql, args_values)
            if not isinstance(update_res, int):  # 数据库update失败
                logging.error("sql update is err:", update_res)
                msg["code"] = 403
                msg["reason"] = "inc fail"
                return self.response(request, msg)
            logging.info("uuid [%s] lock [%s] company [%s] inc cnt [%s] old cnt [%s]  true will is [%s] success", uuid_s,id(rwlock), company_name, cnt, old_cnt, res)
            msg["code"] = 200
            msg["reason"] = "ok"
            return self.response(request, msg)

    async def cnt_dec(self, request):
        post = await request.post()
        logging.info('post %s', post)
        company_name = post.get("company")
        cnt = int(post.get("cnt", 0))
        rwlock = self.company_lock.get(company_name, "")
        if not rwlock:
            rwlock = locks.Lock(loop=self.loop)
            self.company_lock[company_name] = rwlock
        logging.info(rwlock)
        with await rwlock:
            uuid_s = uuid.uuid1().hex
            logging.debug("[%s]---[%s]", uuid_s, id(rwlock))
            msg = dict()
            sql = "select * from shield.company where name=%s"
            po = await self.db.get(sql, company_name)
            if not po:      # 找不到企业
                logging.error("not found company name [%s]", company_name)
                msg["code"] = 404
                msg["code"] = "not found company"
                return self.response(request, msg)
            po_cnt = int(po.get("count"))
            old_cnt = po.get("count")
            if po_cnt == 0:
                logging.error("company [%s] cnt is 0", company_name)
                msg["code"] = 400
                msg["reason"] = "cnt is 0"
                return self.response(request, msg)
            if po_cnt < cnt:  # 数据库余额不足
                logging.error("company [%s] count is not enough", company_name)
                msg["code"] = 405
                msg["reason"] = "count is not enough"
                return self.response(request, msg)
            res = po_cnt - cnt
            update_sql = "update shield.company set count=%s where name=%s"
            args_values = [res, company_name]
            update_res = await self.db.execute(update_sql, args_values)
            if not isinstance(update_res, int): # 执行update 失败
                logging.error("sql update is err:", update_res)
                msg["code"] = 403
                msg["reason"] = "inc fail"
                return self.response(request, msg)
            logging.info("uuid [%s] lock [%s] company [%s] dec cnt [%s] old cnt [%s] true will is [%s] success",uuid_s,id(rwlock), company_name, cnt, old_cnt, res)

            msg["code"] = 200
            msg["reason"] = "ok"
            return self.response(request, msg)



