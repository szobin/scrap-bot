#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import time


def now():
    return datetime.datetime.now()


def time_delta_in_hours(time1, time2):
    dt = time1 - time2
    d = dt.seconds / 3600.0 + dt.days*24
    return d


def time_delta_in_minutes(time1, time2):
    dt = time1 - time2
    d = dt.seconds / 60.0 + dt.days*24*60
    return d


def date_str(dt):
    return "%s-%s-%s" % (str(dt.year).zfill(4), str(dt.month).zfill(2), str(dt.day).zfill(2))


def datetime_str(dt):
    return "%s-%s-%s" % (str(dt.year).zfill(4), str(dt.month).zfill(2), str(dt.day).zfill(2))


def add_time_stamp_to_name(name):
    name += "-%s" % datetime_str(now())
    return name


def file_time(fn):
    if fn is None:
        t = 0
    else:
        try:
            t = os.path.getmtime(fn)
        except:
            t = 0

    lt = time.localtime(t)
    dt = datetime.datetime(lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
    return dt

