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

config_dict = {}

time_gap = 0
GW_length = 0

def read_ip_ini():
    global try_connected_count
    global time_gap
    global GW_length

    sdk_dir = os.path.dirname(os.path.abspath(__file__))

    ip_config = ConfigParser()
    ip_config.read(sdk_dir + '/ip.ini')

    # Read ini index info
    GW_length = ip_length = int(ip_config['ip_length']['size'])
    print('ip size: ' + str(ip_length))

    ip_address_info_dict['port'] = int(ip_config['ip_address_info']['port'])
    print('ip port: ' + str(ip_address_info_dict['port']))
    ip_address_info_dict['password'] = ip_config['ip_address_info']['password']
    print('ip password: ' + str(ip_address_info_dict['password']))
    ip_address_info_dict['username'] = ip_config['ip_address_info']['username']
    print('ip username: ' + str(ip_address_info_dict['username']))


    try_connected_count = ip_config['try_connected_counts']['times']
    print('connection retry time ' + try_connected_count)

    time_gap = int(ip_config['gateway']['timegap'])
    print('gateway timegap ' + str(time_gap))

    # device nearest GW
    ip_list = ip_config.items("ip_device_dictionary")
    for key, val in ip_list:
        print("read_ip_ini ip-list key:" + str(key) + " val:" + str(val))
        ip_device_dict[str(key)] = str(val)

    for i in range(0, ip_length, 1):
        ip_addr_list.append(ip_config.items("ip_device_dictionary")[i][0])

    print(ip_addr_list)

    # location info
    ip_location_list = ip_config.items("ip_location_dictionary")
    for key, val in ip_location_list:
        print("read_ip_ini ip-location key:" + str(key) + " val:" + str(val))
        ip_location_dict[str(key)] = str(val)


    '''
    ip_addr = ip_config.items("ip")[0][0]
    ip_to_uniaddr = ip_config.items("ip")[0][1]
    print(ip_to_uniaddr)
    print(ip_addr)
    '''

def read_config_ini():
    sdk_dir = os.path.dirname(os.path.abspath(__file__))

    config = ConfigParser()
    config.read(sdk_dir + '/config.ini')

    # Read ini index info
    IP_PING_ONOFF = int(config['PING']['ping_onoff'])
    print('IP PING ONOFF: ', 'yes' if IP_PING_ONOFF else 'no')

    REBOOT_ONOFF = int(config['REBOOT']['reboot_onoff'])
    print('REBOOT ONOFF: ', 'yes' if REBOOT_ONOFF else 'no')

    SCP_ONOFF = int(config['SCP']['scp_onoff'])
    print('SCP ONOFF: ', 'yes' if SCP_ONOFF else 'no')

    CHECK_DEVICE_ONOFF = int(config['CHECK_DEVICE_ONOFF']['checked_device_onoff'])
    print('CHECK DEVICE ONOFF: ', 'yes' if CHECK_DEVICE_ONOFF else 'no')

    CHECK_PROCESS = int(config['CHECK_PROCESS']['check_onoff'])
    print('CHECK PROCESS ONOFF: ', 'yes' if CHECK_PROCESS else 'no')
    KILL_PROCESS = int(config['KILL_PROCESS']['kill_onoff'])
    print('KILL PROCESS ONOFF: ', 'yes' if KILL_PROCESS else 'no')
    RESTART_PROCESS = int(config['RESTART_PROCESS']['restart_onoff'])
    print('RESTART PROCESS ONOFF: ', 'yes' if RESTART_PROCESS else 'no')

    for section in config.sections():
        #dictionary[section] = {}
        for option in config.options(section):
            config_dict[option] = int(config.get(section, option))



def write_reboot_time_txt(data):
    sdk_dir = os.path.dirname(os.path.abspath(__file__))
    f = open(sdk_dir + "/reboot_time.txt", 'w')
    info = 'time interval: ' + str(data) + ' >= time gap:' + str(time_gap* 60) + '\n'
    f.write(info)
    f.close()
    '''
    config = ConfigParser()
    config.read(sdk_dir + '/ip.ini')
    config.set("Time_to_reboot", "NOW", str(datetime.now()))

    hd = open(sdk_dir + '/ip.ini', "w")
    config.write(hd)
    hd.close()
    '''

def write_ip_config_txt(ip, resp, location):
    sdk_dir = os.path.dirname(os.path.abspath(__file__))
    now = datetime.now()
    timestamp = now.strftime('%Y/%m/%d %H:%M:%S')

    bSerial = serial_port_is_alive(ip)
    if bSerial == 0:
        msg = 'Fail (Serial port not detected in this ip)'
    elif bSerial == 1:
        msg = ('Ok (' + str(serial_is_alive_dict[ip]) + ')')
    else:
        msg = ('Fail (' + 'Cannot ssh to this ip. Checked the domain.)')


    f = open(sdk_dir + "/GW_ip_response.txt", 'a')
    if resp == 0:
        info = ('[' + ip + ' --- ' + location[ip] + ']\n' +
                    'Gateway network connection---------OK\n' +
                    'Gateway current time---------------' + timestamp + '\n' +
                    'Gateway program execution----------OK\n' +
                    'Gateway and Dongle C connection----' + msg + '\n' +
                    'Gateway reboot---------------------' + ('Yes\n' if config_dict['reboot_onoff'] else 'False\n'))
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

def serial_port_check_process(ip):
    data = ssh.ssh_check_process(ip)
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
    ''' ini??????????????? connection count '''
    return try_connected_count

def is_json_format(message):
    if isinstance(message, str):  # ?????????????????????????????????
        try:
            json.loads(message)
        except ValueError:
            return False
        return True
    else:
        return False