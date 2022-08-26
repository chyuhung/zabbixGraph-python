#zabbix server ip
zbx_host = '10.191.101.101'
#zabbix server port
zbx_port = '80'
#zabbix server username
zbx_user = 'Admin'
#zabbix server user password
zbx_pwd = 'zabbix'
#zabbix auth url
zbx_url = 'http://'+zbx_host+':'+zbx_port+'/'+'api_jsonrpc.php'
#zabbix graph url
graphurl = 'http://'+zbx_host+':'+zbx_port+'/'+'chart2.php'
#zabbix login url
loginurl = 'http://'+zbx_host+':'+zbx_port+'/'+'index.php'


#download images to imgsDir
imgsDir = './images'
#image width
imgWidth='800'
#image hight
imgHeight='200'
#hosts file
hostsFile='./hosts.txt'

#itemNameList
itemNameList=["CPU utilization","Memory usage"]
#time from
timeFrom='now-7d'
#time to
timeTo='now'

'''
graphListInfoList = [
    {"hostip":"10.191.101.101","hostid":hostid,"itemNameList":["CPU utilization","Memory usage"],},
    {"hostip":"10.191.101.101","hostid":hostid,"itemNameList":["Network traffic on ens33","Disk space usage /"],},
]
'''
