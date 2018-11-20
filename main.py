#! /usr/bin/env python3
# .-*- coding:utf-8 .-*-


import sys
from Application import Application
import logging


def daemon():
    import os
    # create - fork 1
    try:
        pid = os.fork()
        if pid > 0:
            return pid
    except OSError as error:
        logging.error('fork #1 failed: %d (%s)' % (error.errno, error.strerror))
        return -1
    # it separates the son from the father
    # os.chdir('/opt/pbx')
    os.setsid()
    os.umask(0)
    # create - fork 2
    try:
        pid = os.fork()
        if pid > 0:
            return pid
    except OSError as error:
        logging.error('fork #2 failed: %d (%s)' % (error.errno, error.strerror))
        return -1
    sys.stdout.flush()
    sys.stderr.flush()
    si = open("/dev/null", 'r')
    so = open("/dev/null", 'ab')
    se = open("/dev/null", 'ab', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    return 0


def setLog():
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO,
                        format='[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s %(message)s')


def main():
    setLog()
    pid = daemon()
    if pid:
        return pid
    app = Application()
    app.run_forever()


if __name__ == "__main__":
    main()
