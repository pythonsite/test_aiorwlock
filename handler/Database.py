import aiomysql
import logging
import traceback


class Database:

    def __init__(self, pool):
        self.pool = pool

    async def get(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                conn.autocommit(True)
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(sql, args)
                    value = await cur.fetchone()
                    await conn.commit()
                    return value
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e

    async def query(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                conn.autocommit(True)
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(sql, args)
                    value = await cur.fetchall()
                    await conn.commit()
                    return value
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e

    async def insert(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                conn.autocommit(True)
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    ret = await cur.execute(sql, args)
                    await conn.commit()
                    if ret > 0:
                        return cur.lastrowid
                    return -1
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e

    async def execute(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                conn.autocommit(True)
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    ret = await cur.execute(sql, args)
                    await conn.commit()
                    return ret
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e