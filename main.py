#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.cookiejar as cookielib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import requests
import config
import urllib


class ZabbixGraph(object):
    def __init__(self):
        self.graphurl = 'http://' + config.zbx_host + ':' + config.zbx_port + '/zabbix/' + 'chart2.php'
        self.loginurl = 'http://' + config.zbx_host + ':' + config.zbx_port + '/zabbix/' + 'index.php'
        self.name = config.zbx_user
        self.password = config.zbx_pwd
        self.imgsDir = config.imgsDir

    def getcookie(self):
        cookiejar = cookielib.CookieJar()
        urlOpener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
        values = {
            "name": self.name,
            'password': self.password,
            'autologin': 1,
            "enter": 'Sign in'
        }
        data = urllib.parse.urlencode(values).encode(encoding='UTF8')
        request = urllib.request.Request(self.loginurl, data)
        try:
            urlOpener.open(request, timeout=10)
            self.urlOpener = urlOpener
        except urllib.error.HTTPError as e:
            print(e)

    def downGraph(self, hostIP, graphName, graphid, width=config.imgWidth, height=config.imgHeight):
        self.getcookie()
        if graphid == 0:
            print("graphid error")
            sys.exit(1)
        '''
        chart2.php?
        graphid=1590
        from=now-1h
        to=now
        height=201
        width=1000
        profileIdx=web.charts.filter&_=v4jrumba
        '''
        values = {
            "graphid": graphid,
            "from": config.timeFrom,
            "to": config.timeTo,
            "width": width,
            "height": height,
            "profileIdx": "web.charts.filter"
        }
        data = urllib.parse.urlencode(values).encode(encoding='UTF8')
        request = urllib.request.Request(self.graphurl, data)
        url = self.urlOpener.open(request)
        image = url.read()

        imagesPath = os.path.join(self.imgsDir, hostIP).replace('\n', '')  # 从文件读入包含'\n'，需去掉否则创建异常
        if not os.path.exists(imagesPath):
            os.makedirs(imagesPath)

        imgName = "{}/{}.png".format(imagesPath, graphName, str(graphid))

        with open(imgName, 'wb') as f:
            f.write(image)
            f.flush()
            f.close()
        return imgName


class zabbixApi(ZabbixGraph):
    def __init__(self):
        super().__init__()
        self.token = None
        self.post_header = {'Content-Type': 'application/json'}
        self.excel_serial = 1
        self.writeToExcelList_warning = []
        self.zbx_url = 'http://' + config.zbx_host + ':' + config.zbx_port + '/zabbix/' + 'api_jsonrpc.php'

    # 调用zabbix api需要身份令牌auth
    def get_token(self):
        post_data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": config.zbx_user,
                "password": config.zbx_pwd
            },
            "id": "1"
        }

        ret = requests.post(self.zbx_url, data=json.dumps(post_data), headers=self.post_header)
        zbx_ret = json.loads(ret.text)
        try:
            self.token = zbx_ret.get('result')
        except Exception as e:
            print('''zabbix登录错误，请检查登录信息是否正确!
                     本次登录退出!
                     zbx_url: %s
                     zbx_user: %s
                     zbx_pwd: %s
                     错误信息: %s''' % (self.zbx_url, config.zbx_user, config.zbx_pwd, e))

    def getResponse(self, dataJson):
        resDataJson = requests.post(self.zbx_url, data=json.dumps(dataJson), headers=self.post_header)
        try:
            responseData = resDataJson.json()['result']
            return responseData
        except Exception as e:
            print('获取API接口失败！,%s' % e)

    def getGraphId(self, hostid, graphList):
        # 通过组名取货去到组的ID，返回给下个调用函数
        reqHostJson = {
            "jsonrpc": "2.0",
            "method": "graph.get",
            "params": {
                "output": ["graphid", "name"],
                "hostids": hostid,
                "filter": {
                    "name": graphList
                }
            },
            "auth": self.token,
            "id": 1
        }
        graphidInfo = self.getResponse(reqHostJson)
        # print(graphidInfo) # [{'graphid': '1525', 'name': '/: Disk space usage'}, {'graphid': '913', 'name': 'CPU jumps'}]
        return graphidInfo

    def getHostID(self, ip):
        reqHostJson = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["host"],
                "filter": {
                    "ip": ip
                }
            },
            "auth": self.token,
            "id": 1
        }
        result = self.getResponse(reqHostJson)
        if result:
            return result[0]["hostid"]
        else:
            return ""

    # 从文件读入ip
    def readHostsToGraphListInfoList(self, itemNameList=config.itemNameList):
        graphListInfoList = []
        f = open(config.hostsFile, 'r')
        try:
            lines = f.readlines()
            for line in lines:
                ip = line.replace("\n", "")
                hostid = self.getHostID(ip)
                if hostid != "":
                    graphListInfoList.append({"hostip": ip, "hostid": hostid, "itemNameList": itemNameList})
            return graphListInfoList
        except IOError as e:
            print("读取文件异常：" + e)
        finally:
            f.close()

    def downloadGraphs(self):  # 下载图片
        self.get_token()
        for graphListInfo in self.readHostsToGraphListInfoList():
            hostip = graphListInfo['hostip']
            hostid = graphListInfo['hostid']
            itemNameList = graphListInfo['itemNameList']
            graphInfoList = self.getGraphId(hostid, itemNameList)
            for graphInfo in graphInfoList:
                graphid = graphInfo['graphid']
                name = graphInfo['name'].replace(' ', '_').replace(':', '').replace('/','~')  # 由于监控名称存在特殊符号，这里需要进行处理，不然会报异常
                self.downGraph(hostip, name, graphid)


if __name__ == '__main__':
    zabbixApi = zabbixApi()
    zabbixApi.downloadGraphs()
