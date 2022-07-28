import os
import platform
from configparser import ConfigParser
from datetime import datetime
import json
import sshToUbuntu as ssh


ip_device_dict = {}
ip_location_dict = {}
serial_is_alive_dict = {}
ip_address_info_dict = {}

ip_addr_list = []

time_gap = 0
reboot = 0


def read_config_ini():
    global try_connected_count
    global check_device_status
    global reboot
    global time_gap

    sdk_dir = os.path.dirname(os.path.abspath(__file__))

    ip_config = ConfigParser()
    ip_config.read(sdk_dir + '/ip.ini')

    # Read ini index info
    ip_length = int(ip_config['ip_length']['size'])
    print('ip size: ' + str(ip_length))

    ip_address_info_dict['port'] = int(ip_config['ip_address_info']['port'])
    print('ip port: ' + str(ip_address_info_dict['port']))
    ip_address_info_dict['password'] = ip_config['ip_address_info']['password']
    print('ip password: ' + str(ip_address_info_dict['password']))
    ip_address_info_dict['username'] = ip_config['ip_address_info']['username']
    print('ip username: ' + str(ip_address_info_dict['username']))
    check_device_status = int(ip_config['check_device_flag']['checked'])
    print('check device status: ' + 'yes' if check_device_status else 'no')

    try_connected_count = ip_config['try_connected_counts']['times']
    print('connection retry time ' + try_connected_count)

    reboot = int(ip_config['gateway']['reboot'])
    print('gateway reboot ' + 'yes' if check_device_status else 'no')
    time_gap = int(ip_config['gateway']['timegap'])
    print('gateway timegap ' + str(time_gap))

    # device nearest GW
    ip_list = ip_config.items("ip_device_dictionary")
    for key, val in ip_list:
        print("read_config_ini ip-list key:" + str(key) + " val:" + str(val))
        ip_device_dict[str(key)] = str(val)

    for i in range(0, ip_length, 1):
        ip_addr_list.append(ip_config.items("ip_device_dictionary")[i][0])

    print(ip_addr_list)

    # location info
    ip_location_list = ip_config.items("ip_location_dictionary")
    for key, val in ip_location_list:
        print("read_config_ini ip-location key:" + str(key) + " val:" + str(val))
        ip_location_dict[str(key)] = str(val)


    '''
    ip_addr = ip_config.items("ip")[0][0]
    ip_to_uniaddr = ip_config.items("ip")[0][1]
    print(ip_to_uniaddr)
    print(ip_addr)
    '''

def write_config_ini():
    sdk_dir = os.path.dirname(os.path.abspath(__file__))
    config = ConfigParser()
    config.read(sdk_dir + '/ip.ini')
    config.set("Time_to_reboot", "NOW", str(datetime.now()))

    hd = open(sdk_dir + '/ip.ini', "w")
    config.write(hd)
    hd.close()


def write_ip_config_txt(ip, resp, location):
    now = datetime.now()
    timestamp = now.strftime('%Y/%m/%d %H:%M:%S')

    bSerial = serial_port_is_alive(ip)
    if bSerial == 0:
        msg = 'Fail (Serial port not detected in this ip)'
    elif bSerial == 1:
        msg = ('Ok (' + str(serial_is_alive_dict[ip]) + ')')
    else:
        msg = ('Fail (' + 'Cannot ssh to this ip. Checked the domain.)')

    with open('GW_ip_response.txt', 'a') as f:
        if resp == 0:
            info = ('[' + ip + ' --- ' + location[ip] + ']\n' +
                    'Gateway network connection---------OK\n' +
                    'Gateway current time---------------' + timestamp + '\n' +
                    'Gateway program execution----------OK\n' +
                    'Gateway and Dongle C connection----' + msg + '\n' +
                    'Gateway reboot---------------------' + ('Yes\n' if reboot else 'False\n'))
                    #'Gateway and Dongle C connection----' + ('Ok (' + str(serial_is_alive_dict[ip]) + ')\n' if bSerial else 'Fail\n'))
        elif resp == 2:
            info = ('[' + ip + ' --- ' + location[ip] + ']\n' +
                    'Gateway network connection---------No response\n' +
                    'Gateway current time---------------' + timestamp + '\n' +
                    'Gateway program execution----------OK\n' +
                    'Gateway and Dongle C connection----Fail because network no response\n')
        else:
            info = ('[' + ip + ' --- ' + location[ip] + ']\n' +
                    'Gateway network connection---------Have no this address\n' +
                    'Gateway current time---------------' + timestamp + '\n' +
                    'Gateway program execution----------OK\n' +
                    'Gateway and Dongle C connection----Fail because have no this address\n')

        f.write(info)
        f.write(" \n")
        f.close()

def write_device_response_config_txt(ip, uniaddress, response_text, location):
    now = datetime.now()
    timestamp = '[' + now.strftime('%Y/%m/%d %H:%M:%S') + ']'


    if is_json_format(response_text):
        response_json = json.loads(response_text.text)

        if response_json['message'] == "":
            msg = 'success'
        else:
            msg = response_json['message']

        with open('Device_response.txt', 'a') as f:
            if response_json['code'] == 200:
                info = ('[' + ip + ' --- ' + location[ip] + ']\n' +
                        'Current time------------------' + timestamp + '\n' +
                        'Device address = ' + uniaddress + ' ping-------Success\n' +
                        'Response message-------------- ' + msg + '\n' +
                        'Response payload--------------' + str(response_json['payload']) + '\n'
                        )
            else:
                info = ('[' + ip + ' --- ' + location[ip] + ']\n' +
                        'Current time------------------' + timestamp + '\n' +
                        'Device address = ' + uniaddress + ' ping-------Fail\n' +
                        'Response message-------------- ' + msg + '\n' +
                        'Response payload--------------' + str(response_json['payload']) + '\n'
                        )

            f.write(info)
            f.write(" \n")
            f.close()
    else:
        with open('Device_response.txt', 'a') as f:
            info = ('[' + ip + ' --- ' + location[ip] + ']\n' +
                    'Current time------------------' + timestamp + '\n' +
                    'Device address = ' + uniaddress + '----------max retries exceed\n' +
                    'Response message-------------- ' + str(response_text) + '\n'
                    )

            f.write(info)
            f.write(" \n")
            f.close()

def serial_port_is_alive(ip):
    os_platform = platform.system()
    print('OS platform is ' + os_platform)

    data = ssh.ssh_make_connect(ip)
    if data == None:
        print('Cannot ssh to this ip:' + ip)
        return 2
    elif len(data) == 0 or data[0] == '':
        print('Serial port not detected in this ip:' + ip)
        return 0
    else:
        serial_is_alive_dict[ip] = data
        return 1


def get_device_addr(ip):
    return ip_device_dict[ip]

def get_connected_count():
    ''' ini決定是否要 connection count '''
    return try_connected_count

def get_device_status():
    ''' ini決定是否要get鄰近裝置onoff狀態 '''
    return check_device_status

def is_json_format(message):
    if isinstance(message, str):  # 首先判斷變數是否為字串
        try:
            json.loads(message)
        except ValueError:
            return False
        return True
    else:
        return False