#!/usr/bin/env python

import copy
import base64
import re
import json
import requests


# ssd 格式: ssd://base64
# ssr 格式: base64 -> {"ssr://&remarks=base64&group=", "ssr://&remarks=base64&group="}
# v2ray 格式: base64 -> {'vmess://"ps":base64', 'vmess://"ps":base64'}
shadowsocksD_prefix = "ssd://"
shadowsocksR_prefix = "ssr://"
v2ray_prefix = "vmess://"


def b64_decode(self):
    if len(self) % 4 != 0:
        j = 4 - len(self) % 4
        self = self + " = " * j
    return base64.urlsafe_b64decode(self).decode("utf-8")


def parse_include_exclude(include, exclude, remarks):
    isInclude = False
    if include is not None:
        for include_server in include:
            if include_server in remarks:
                isInclude = True
                break
    else:
        isInclude = True

    isExclude = False
    if exclude is not None:
        for exclude_server in exclude:
            if exclude_server in remarks:
                isExclude = True
                break
    return isInclude, isExclude


def parse_type(server_list, type, include, exclude, nodes=None):
    if type == "ssr" or type == "v2ray":
        servers = []
        for server_node in server_list:
            if type == "ssr":
                remarks = b64_decode(re.split('&remarks=|&group=', b64_decode(
                    server_node[len(shadowsocksR_prefix):].rstrip('\n')))[-2])
            elif type == "v2ray":
                remarks = json.loads(b64_decode(
                    server_node[len(v2ray_prefix):].rstrip('\n')))['ps']

            isInclude, isExclude = parse_include_exclude(
                include, exclude, remarks)

            if isInclude and (not isExclude):
                servers.append(server_node)
        nodes_prefix = ''
        for server_node in servers:
            nodes_prefix += server_node

        return str(base64.b64encode(nodes_prefix.encode('utf-8'))).lstrip("b'").rstrip("'")

    elif type == "ssd":
        nodes_prefix = copy.deepcopy(nodes)
        remove_range = 0
        id = 0
        for server_node in nodes['servers']:
            remarks = server_node['remarks']

            isInclude, isExclude = parse_include_exclude(
                include, exclude, remarks)

            if (isInclude == False) or (isExclude == True):
                del nodes_prefix['servers'][id - remove_range]
                remove_range += 1
            id += 1

        return shadowsocksD_prefix + str(base64.urlsafe_b64encode(json.dumps(nodes_prefix).encode('utf-8'))).lstrip("b'").rstrip("'")


def split_by_vertical_virgule(origin):
    if origin is not None:
        if "|" in origin:
            origin = origin.split("|")
        else:
            # single word (string) to list
            origin = origin.split()
    return origin


def output(url, include, exclude):

    try:
        url_text = requests.get(url).text
    except:
        return "can't get url"

    include = split_by_vertical_virgule(include)
    exclude = split_by_vertical_virgule(exclude)

    if shadowsocksD_prefix == url_text[0:len(shadowsocksD_prefix)]:
        type = "ssd"
        nodes = json.loads(b64_decode(
            url_text[len(shadowsocksD_prefix):]))
        nodes_encode = parse_type(
            nodes['servers'], type, include, exclude, nodes)

    else:
        server_list = b64_decode(url_text).splitlines(True)

        if shadowsocksR_prefix == server_list[0][0:len(shadowsocksR_prefix)]:
            type = "ssr"
            nodes_encode = parse_type(server_list, type, include, exclude)

        elif v2ray_prefix == server_list[0][0:len(v2ray_prefix)]:
            type = "v2ray"
            nodes_encode = parse_type(server_list, type, include, exclude)

    return nodes_encode
