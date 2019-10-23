#!/usr/bin/python
# -*- coding: utf-8 -*-

import urlparse
from string import maketrans


def get_base_url(url):
    r = urlparse.urlsplit(url)
    return r[0]+'://'+r[1]


def update_url(base_url, url):
    r = urlparse.urlsplit(url)
    if r[1] == "":
        return base_url+url
    else:
        return url


def url_proc_param(url_param, sp=" "):
    return url_param.replace("#20", sp) 


def url_to_filename(url):
    t = maketrans('/:.=?&;, ', '-'*9)
    s = url.translate(t)
    while True:
        p = s.count('--')
        if p == 0:
            break
        s = s.replace('--', '-')
    return s
