#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import os
import time
import json
import requests
from lxml import html
from lib.xml_lib import *
from lib import url_lib
from lib import time_lib


__version__ = "1.1"


class ScrapeBot:
    
    def __init__(self, base_dir, params, config_fn='scrap_config.xml'):
        self.start_time = time_lib.now()
        self.BASE_DIR = base_dir
        self.params = list(params)
        self.errors = 0
        self.config_fn = config_fn
        self.config = None

        self._log = list()
        self.base_url = None
        self.list_name = None
        self.report_list = None
        self.report_col_values = []

        self.script = None
        if len(params) < 2:
            self.log_msg("ScrapBot usage: >python bot.py script.xml")
            self.script_fn = 'default_script.xml'
        else:
            self.script_fn = params[1]

        self.load_config()
        self.consel_host = xml_str_param(self.config, "consel_host", "localhost")
        self.consel_port = xml_str_param(self.config, "consel_port", "8080")
        self.cache_path = os.path.join(self.BASE_DIR, xml_str_param(self.config, "cache_path", "cache"))
        self.data_path = os.path.join(self.BASE_DIR, xml_str_param(self.config, "data_path", "data"))
        self.consel_init()

        self.load_script()

        if self.errors == 0:
            self.log_msg("ScrapBot version %s was started OK" % __version__)

        return 

    def log_msg(self, msg, is_error=False):
        if is_error:
            self.errors += 1
        # self._log.append(msg)
        print(msg)

    def load_config(self):
        if not os.path.exists(self.config_fn):
            self.config = etree.Element("config", name="scrap bot")
            return
        try:
            f = open(self.config_fn, 'r')
            try:
                xml_str = f.read()
            finally:
                f.close()
            self.config = etree.fromstring(xml_str)
        except IOError as ex:
            self.config = etree.Element("config", name="scrap bot")
            self.log_msg(" error: config file was not loaded: "+str(ex), True)
            return
        except Exception as ex:
            self.config = etree.Element("config", name="scrap bot")
            self.log_msg("error: config has wrong format: "+str(ex), True)
            return
           
    def load_script(self):
        if not os.path.exists(self.script_fn):
            self.log_msg(" error: script file not found: "+self.script_fn, True)
            return

        self.script = etree.Element("bot")
        try:
            f = open(self.script_fn, 'r')
            try:
                xmlstr = f.read()
            finally:
                f.close()
            self.script = etree.fromstring(xmlstr)
        except IOError as ex:
            self.log_msg(" error: config file not loaded: "+str(ex), True)
            return
            
        except Exception as ex:
            self.log_msg("error: config has wrong format: "+str(ex), True)
            return

    def do_store_log(self):
        for m in self._log:
            print(m)

    def finalize(self):
        time_delta = time_lib.now() - self.start_time
        self.log_msg('time: '+str(time_delta))
        self.do_store_log()

    def execute(self):
        try:
            for site_tag in self.script:
                self.do_process_site_tag(site_tag) 
        except Exception as ex:
            self.log_msg("execute error: "+str(ex))

    def consel_init(self):
        s = " - init consel: %s:%s" % (self.consel_host, self.consel_port)
        self.log_msg(s)
        return 0

    def get_consel_url(self):
        return "http://%s:%s/" % (self.consel_host, self.consel_port)

    def consel_get(self, url, w="", wto=10, k=""):
        q = self.get_consel_url()+'get?url='+url
        if len(w) > 0:
            q += "&w="+w+'&wto='+str(wto)
            if len(k) > 0:
                q += "&k="+k

        r = requests.get(q)
        if r.status_code == 200:
            return True
        raise Exception("page status code: %d" % r.status_code)

    def consel_page(self):
        r = requests.get(self.get_consel_url()+'page')
        if r.status_code == 200:
            return r.content.decode('utf-8')
        raise Exception("page status code: %d" % r.status_code)

    def consel_has(self, c):
        r = requests.get(self.get_consel_url()+'has?c='+c)
        if r.status_code == 200:
            return True
        raise Exception("page status code: %d" % r.status_code)

    def consel_nav(self, a, b, c, h):
        q = self.get_consel_url()+'nav?a='+a
        if len(b) > 0:
            q += '&b='+b
        if len(c) > 0:
            q += '&c=' + c
        if len(h) > 0:
            q += '&h=' + h
        r = requests.get(q)
        if r.status_code == 200:
            return True
        raise Exception("page status code: %d" % r.status_code)

    def consel_quit(self):
        requests.get(self.get_consel_url() + 'quit')
        return True

    def url_to_cache_filename(self, url):
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
        fn = os.path.join(self.cache_path, url_lib.url_to_filename(url)+'.cache')
        return fn

    def report_name_to_data_filename(self, report_name):
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        fn = os.path.join(self.data_path, report_name+'.json')
        return fn

    def do_store_cache(self, url):
        try:
            page_html = self.consel_page()
            page_tree = html.fromstring(page_html)
            fn = self.url_to_cache_filename(url)
            is_need_remove = 0
            try:
                f = open(fn, 'w')
                is_need_remove = 1
                try:
                    f.write(page_html.encode('utf-8'))
                    # self.log_msg("- write cache, url: %s" % url)
                finally:
                    f.close()
            except Exception as ex:
                self.log_msg("error store cache, url: %s, message: %s, cache was deleted" % (url, str(ex)))
                if is_need_remove > 0:
                    os.remove(fn)
            return page_tree
        except Exception as ex:
            self.log_msg("error store cache, url: %s, message: %s" % (url, str(ex)))

    def do_load_cache(self, url):
        try:
            fn = self.url_to_cache_filename(url)
            f = open(fn, 'r')
            try:
                page_html = f.read().decode('utf-8')
                # self.log_msg("- load cache, file: %s" % fn)
            finally:
                f.close()
            page_tree = html.fromstring(page_html)
            return page_tree
        except Exception as ex:
            raise Exception('error load cache, url: %s, message: %s' % (url, str(ex)))

    def do_load_url(self, tag, url):
        ttl = xml_int_param(tag, 'ttl', 0)

        w = xml_str_param(tag, 'waitfor')
        wto = xml_int_param(tag, 'wait_to', 10)
        k = xml_str_param(tag, 'expect_kind', 'presence')
        self.log_msg("- load url: %s ttl: %d" % (url, ttl))

        if ttl <= 0:
            try:
                if not self.consel_get(url, w, wto, k):
                    raise Exception('unknown error')

            except Exception as ex:
                raise Exception('error load url %s, message: %s' % (url, str(ex)))
            return None

        cache_fn = self.url_to_cache_filename(url)
        cache_time = time_lib.time_delta_in_minutes(time_lib.now(), time_lib.file_time(cache_fn))
        #  self.log_msg("- cache fn: %s time: %d" % (cache_fn, cache_time))

        if cache_time > ttl:
            try:
                if not self.consel_get(url, w, wto, k):
                    raise Exception("wrong page content")
            except Exception as ex:
                raise Exception('error load url %s, message: %s' % (url, str(ex)))

            return self.do_store_cache(url)

        return self.do_load_cache(url)

    def do_process_site_tag(self, site_tag):
        site_name = xml_str_param(site_tag, 'name', 'NA')
        stage = 'init'
        try:
            report_name = xml_str_param(site_tag, 'report_name', site_name)
            site_url = xml_str_param(site_tag, 'url')
            site_debug = xml_int_param(site_tag, 'debug', 0)
            is_date_in_report_name = xml_int_param(site_tag, 'use_date', 1)
            is_filter_in_report_name = xml_int_param(site_tag, 'use_filter', 1)

            if is_date_in_report_name == 1:
                report_name = time_lib.add_time_stamp_to_name(report_name)
            if is_filter_in_report_name == 1:
                for i in range(2, len(self.params)):
                    report_name += '_'+url_lib.url_proc_param(self.params[i], "-")

            if site_url == "":
                self.log_msg("error: site tag has no url attribute in bot script", True)
                return

            title = xml_str_param(site_tag, 'title', 'Unknown')
            self.base_url = url_lib.get_base_url(site_url)
            self.list_name = xml_str_param(site_tag, 'list', 'list')
            self.report_list = list()
            self.report_col_values = list()

            self.log_msg("Scrap info from site: %s" % site_name)

            report_table = dict(title=title, date=time_lib.datetime_str(time_lib.now()),
                                site=(site_name, site_url))

            try:
                try:
                    stage = 'load_url'
                    root_element = self.do_load_url(site_tag, site_url)

                    stage = 'process_acts'
                    self.do_process_actions_tag(root_element, site_tag)
                    # self.driver.close()  # for firefox - lead to crash
                finally:
                    self.store_report_table(report_name, report_table)
            finally:
                if site_debug == 0:
                    self.consel_quit()

        except Exception as ex:
            msg = str(ex)
            self.log_msg("error scrap info on stage %s from site: %s, message: %s" % (stage, site_name, msg))

    def store_report_table(self, report_name, report_table):
        try:
            if len(self.report_list) == 0:
                self.log_msg('result was not stored (nothing to store)')
                return False

            if self.list_name is not None:
                report_table.update({self.list_name: self.report_list})
            json_str = json.dumps(report_table)
            fn = self.report_name_to_data_filename(report_name)
            f = open(fn, "w")
            try:
                f.write(json_str)
                self.log_msg('result was stored to: ' + fn+' items collected: '+str(len(self.report_list)))
                return True
            finally:
                f.close()
        except Exception as ex:
            self.log_msg("store report error: "+str(ex))

    def do_process_actions_tag(self, cur_element, parent_tag):
        for act_tag in parent_tag:
            act_name = act_tag.tag
            if act_name == 'nav':
                self.do_site_nav(act_tag)
            elif act_name == 'base':
                self.do_site_base(cur_element, act_tag)
            elif act_name == 'foreach':
                r = self.do_site_for_each(cur_element, act_tag)
                if not r:
                    return False
            elif act_name == 'if':
                self.do_site_if(cur_element, act_tag)
            elif act_name == 'delay':
                t = xml_int_param(act_tag, 't', 5)
                self.log_msg('delay: '+str(t))
                time.sleep(t)
            elif act_name == 'collect':
                self.do_site_collect(cur_element, act_tag)
            elif act_name == 'break':
                self.log_msg('break')
                return False
            else:
                self.log_msg('warning: unknown action tag: '+act_name)
                return False
        return True

    def do_site_nav(self, act_tag):
        n = xml_str_param(act_tag, 'name')
        a = xml_str_param(act_tag, 'action', 'click')
        try:
            b = xml_str_param(act_tag, 'by', 'xpath')
            c = xml_str_param(act_tag, 'c')
            h = xml_str_param(act_tag, 'h')
            self.consel_nav(a, b, c, h)
        except Exception as ex:
            self.log_msg("site nav (%s:%s) error: %s" % (n, a, str(ex)))

    def get_page_tree(self, cur_element):
        if cur_element is None:
            page_html = self.consel_page()
            page_tree = html.fromstring(page_html)
        else:
            page_tree = cur_element
        return page_tree

    def do_site_base(self, cur_element, act_tag):
        r = True
        name = xml_str_param(act_tag, 'name')
        try:
            c = xml_str_param(act_tag, 'c')
            page_tree = self.get_page_tree(cur_element)

            nav_list = page_tree.xpath(c)
            if len(nav_list) == 0:
                raise Exception('base: not found')

            self.log_msg('set base: %s OK: %s' % (name, str(len(nav_list))))
            for nav in nav_list:
                self.do_process_actions_tag(nav, act_tag)

        except Exception as ex:
            self.log_msg("set base %s error: %s" % (name, str(ex)))

        return r

    def get_filter_value(self, filter_str):
        if len(filter_str) == 0:
            return None
        f_vals = filter_str.split('.')
        if len(f_vals) > 1:
            n = int(f_vals[1])
            if n < len(self.params):
                return url_lib.url_proc_param(self.params[n])
            else:
                return None
        return filter_str

    def do_site_for_jumps(self, act_tag, tag_list, header_list=None):
        r = True
        name = xml_str_param(act_tag, 'name')
        filter_param = xml_str_param(act_tag, 'filter')
        filter_value = self.get_filter_value(filter_param)

        nn = 0
        links = []
        i_ref = 0
        for tag in tag_list:
            if header_list is None:
                hd = tag.text
            else:
                hd = header_list[i_ref].text
            if filter_value is not None:
                if hd.count(filter_value) == 0:
                    i_ref += 1
                    continue

            u = tag.get('href')
            links.append([u, hd])
            i_ref += 1

        if len(links) == 0:
            raise Exception("filter: `%s` was not passed any link titles" % filter_value)

        self.log_msg('foreach: %s started: links found: %s' % (name, str(len(links))))

        self.report_col_values.append("")
        for link in links:
            self.report_col_values[len(self.report_col_values) - 1] = link[1]
            link_url = url_lib.update_url(self.base_url, link[0])
            root_element = self.do_load_url(act_tag, link_url)
            nn += 1
            r = self.do_process_actions_tag(root_element, act_tag)
            if not r:
                break

        self.report_col_values.pop()
        self.log_msg('foreach: ' + name + '/jumps finished OK: ' + str(nn))
        return r

    def do_site_for_navs(self, act_tag, nav_list):
        r = True
        name = xml_str_param(act_tag, 'name')
        nn = 0
        for nav in nav_list:
            r = self.do_process_actions_tag(nav, act_tag)
            nn += 1
            if not r:
                break

        self.log_msg('foreach: ' + name + '/jumps OK: ' + str(nn))
        return r

    def do_site_for_each(self, cur_element, act_tag):
        r = True
        name = xml_str_param(act_tag, 'name')
        a = xml_str_param(act_tag, 'action', 'jumps')

        page_tree = self.get_page_tree(cur_element)

        try:
            h = xml_str_param(act_tag, 'h')
            data_header = None
            if len(h) > 0:
                header_list = page_tree.xpath(h)
                if len(header_list) > 0:
                    data_header = header_list[0]

            if data_header is not None:
                t = data_header.text
                self.report_col_values.append(t)

            selector = xml_str_param(act_tag, 'c')
            header_selector = xml_str_param(act_tag, 'hc')
            header_list = None
            if len(selector) > 0:
                nav_list = page_tree.xpath(selector)
                if len(nav_list) == 0:
                    raise Exception("empty list for selector: %s" % selector)

                if len(header_selector) > 0:
                    header_list = page_tree.xpath(header_selector)
                if a == 'jumps':
                    r = self.do_site_for_jumps(act_tag, nav_list, header_list)
                elif a == 'navs':
                    r = self.do_site_for_navs(act_tag, nav_list)

            if data_header is not None:
                self.report_col_values.pop()

        except Exception as ex:
            self.log_msg("site foreach: %s/%s error: %s" % (name, a, str(ex)))
        return r

    def do_site_if(self, cur_element, act_tag):
        try:
            selector = xml_str_param(act_tag, 'c')
            try:
                r = self.consel_has(selector)
                if r:
                    self.log_msg("site if: was found: OK")
                    self.do_process_actions_tag(cur_element, act_tag)
            except Exception as ex:
                s = str(ex)
                if s.count('found') > 0:
                    self.log_msg("site if: selector was not found: %s" % selector)
                else:
                    self.log_msg("site if: error: %s" % s)

        except Exception as ex:
            self.log_msg("site if error: " + str(ex), True)

    def do_site_collect(self, cur_element, act_tag):
        page_tree = self.get_page_tree(cur_element)
        try:
            cols = []
            for col_tag in act_tag:
                c = xml_str_param(col_tag, 'c')
                col_data = page_tree.xpath(c)
                cols.append(col_data)

            i_row = 0
            col1 = cols[0]
            for d in col1:
                try:
                    dt = d.text
                    if dt is None:
                        dt = ""
                except:
                    dt = ""

                dd = dt.strip()
                if len(dd) == 0:
                    continue

                ef = xml_str_param(act_tag[0], 'exfilter')
                if len(ef) > 0:
                    if dd.count(ef) > 0:
                        i_row += 1
                        continue

                fl = xml_int_param(act_tag[0], 'first_line_only', 0)
                if fl == 1:
                    dd1 = dd.split('\n')
                    dd = dd1[0]

                sf = xml_int_param(act_tag[0], 'skip_first', 0)
                if sf > 0:
                    dd1 = dd.split(' ')
                    while sf > 0:
                        if len(dd1) > 1:
                            del dd1[0]
                        sf -= 1
                    dd = ' '.join(dd1)

                d_row = list(self.report_col_values)
                d_row.append(dd)
                for i_col in range(1, len(cols)):
                    try:
                        c = cols[i_col]
                        d2 = c[i_row].text
                        if d2 is None:
                            d2 = ""
                    except:
                        d2 = ''
                    d_row.append(d2.strip())
                self.report_list.append(d_row)
                i_row += 1
            self.log_msg("collected items OK: "+str(i_row))
        except Exception as ex:
            self.log_msg("site collect error: "+str(ex))
