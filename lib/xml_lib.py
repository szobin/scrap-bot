#!/usr/bin/python
# -*- coding: utf-8 -*-


def xml_str_param(tag, name, default=""):
    if tag is None:
        return default

    try:
        v = tag.get(name)
        if v is None:
            return default
        if v == "":
            return default
        return v
    except:
        return default


def xml_int_param(tag, name, default=0):
    if tag is None:
        return default

    try:
        return int(tag.get(name))
    except:
        return default


def xml_float_param(tag, name, dec=2, default=0):
    if tag is None:
        return default

    try:
        return round(float(tag.get(name)), dec)
    except:
        return default


def xml_search_tag(xml_tag, name):
    if xml_tag is None:
        return None

    if xml_tag.tag == name:
        return xml_tag

    for sub_tag in xml_tag:
        if sub_tag.tag == name:
            return sub_tag
    return None


def xml_get_value_by_path(xml_tag, path):
    names = path.split('.')
    n = len(names)
    if n == 0:
        return ""

    tag = xml_tag
    if tag.tag == names[0]:
        del names[0]
        n = len(names)

    for name in names:
        if tag is None:
            return ""

        if n <= 1:
            v = tag.get(name)
            if v is None:
                v = ""
            return v

        tag = xml_search_tag(tag, name)
        n -= 1
    return ""


def update_url(url):
    url = url.replace('&amp;', '&')
    return url