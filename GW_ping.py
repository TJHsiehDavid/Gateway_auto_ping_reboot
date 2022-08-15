#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess
from subprocess import call
import requests
import globavar as gl

headers = {'Content-Type': 'application/json'}

from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=2))
s.mount('https://', HTTPAdapter(max_retries=2))

def check_gateway_alive(ip, try_count):
    address = ip
    response = subprocess.call(['ping', '-c', try_count, address])

    if response == 0:
        print("ping to", address, "OK")
    elif response == 2:
        print("no response from", address)
        print('\033[31m%s\033[0m ping 不通！' %ip)
    else:
        print("ping to", address, "failed!")

    gl.write_ip_config_txt(ip, response, gl.ip_location_dict)




# http://localhost:8088/v2/device/uniAddress/52?realtime=onOff
def check_device_realtime_near_gateway(ip, uniaddress):
    print("Get device realtime function. Device address: " + uniaddress + ", near GW ip: " + ip)
    url = "http://" + ip + ":8088/" + "v2/device/uniAddress/" + uniaddress + '?realtime=onOff'
    #url = "http://localhost:8088/" + "v2/device/uniAddress/" + "12" + "?realtime=onOff"
    try:
        response = s.get(url=url, headers=headers, verify=False, timeout=(30, 20))

        if response.status_code == 200:
            print("status = Success!")
            print(url)  # 查看傳送的 URL
        else:
            print("status = Fail!")
            print(url)  # 查看傳送的 URL

        # Response is json format.
        gl.write_device_response_config_txt(ip, uniaddress, response, gl.ip_location_dict)

    except requests.exceptions.RequestException as e:
        # Connection is fail, so the msg of exception still write into ini.
        gl.write_device_response_config_txt(ip, uniaddress, e, gl.ip_location_dict)
        print(e)

