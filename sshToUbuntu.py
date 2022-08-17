'''
Python遠端登入Linux伺服器並執行相關命令
'''
#!/usr/bin/python

import paramiko
import globavar as gl
import time
from scp import SCPClient


def ssh_make_connect(ip):
    try:
        # 建立一個ssh client物件
        # 允許將信任的主機自動加入到host_allow 列表，此方法必須放在connect方法的前面
        # 呼叫connect方法連線伺服器
        # 執行命令
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=gl.ip_address_info_dict['username'], password=gl.ip_address_info_dict['password'], timeout=20)
        print('ssh is connected.')

        ''' 決定是否要檢查usb通訊正常與否
            (在ubuntu內的各種local cmd都透過此方法傳送) '''
        if gl.config_dict['ping_onoff']:
            serial_cmd = "ls /dev/ttyUSB*"
            stdin, stdout, stderr = client.exec_command(serial_cmd)
            data = stdout.readlines()

            # move file from local to other local destination in ubuntu.
            #serial_cmd = "mv ./sdk1/aci_evt.py ./sdk1/pyaci/aci/"
            #stdin, stdout, stderr = client.exec_command(serial_cmd)
            print(data)


        ''' 決定是否要用檔案傳輸用的SCP 
            (從local端傳送檔案至remote端) '''
        if gl.config_dict['scp_onoff']:
            with SCPClient(client.get_transport()) as scp:
                # scp.put('local full path', 'remote full path')
                scp.put('/home/davidhsieh/Pictures/device.ini', recursive=True, remote_path='/home/ubuntu/sdk1/')
                scp.put('/home/davidhsieh/Pictures/config.ini', recursive=True, remote_path='/home/ubuntu/sdk1/')
                scp.put('/home/davidhsieh/Pictures/interactive.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/')
                scp.put('/home/davidhsieh/Pictures/deviceService.py', recursive=True, remote_path='/home/ubuntu/sdk1/service/')
                scp.put('/home/davidhsieh/Pictures/globalvar.py', recursive=True, remote_path='/home/ubuntu/sdk1/')
                print("scp ", ip, ' done!')
                scp.close()


        ''' 決定是否要重新啟動GW '''
        if gl.config_dict['reboot_onoff']:
            serial_cmd = "sudo reboot"
            stdin, stdout, stderr = client.exec_command(serial_cmd, get_pty=True)
            stdin.write(gl.ip_address_info_dict['password'] + '\n')

            time.sleep(1)
            client.close()
            print(ip + ' reboot...')


        return data

    except Exception as e:
        print(e)

        return None


def check_connection(client):
    """
    This will check if the connection is still availlable.

    Return (bool) : True if it's still alive, False otherwise.
    """
    try:
        client.ssh.exec_command('ls', timeout=5)
        return True
    except Exception as e:
        print("Connection lost : %s" %e)
        return False
