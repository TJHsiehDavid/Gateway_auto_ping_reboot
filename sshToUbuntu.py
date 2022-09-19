'''
Python遠端登入Linux伺服器並執行相關命令
'''
#!/usr/bin/python
import paramiko
import globavar as gl
import time
from scp import SCPClient


def ssh_check_process(ip):
    try:
        # 建立一個ssh client物件
        # 允許將信任的主機自動加入到host_allow 列表，此方法必須放在connect方法的前面
        # 呼叫connect方法連線伺服器
        # 執行命令
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=gl.ip_address_info_dict['username'], password=gl.ip_address_info_dict['password'], timeout=20)
        print('ssh is connected.')
        process_count = 0

        time.sleep(0.1)
        ''' 決定是否要檢查usb通訊正常與否
            (在ubuntu內的各種local cmd都透過此方法傳送) '''
        if gl.config_dict['ping_onoff']:
            serial_cmd = "ls /dev/ttyUSB*"
            stdin, stdout, stderr = client.exec_command(serial_cmd)
            data_usb = stdout.readlines()
            if len(data_usb) >= 2:
                process_count = 2
            else:
                process_count = 1

        if gl.config_dict['check_onoff']:
            # kill all app.py process in ubuntu.
            for i in range(0, process_count):
                serial_cmd = "ps ax | grep sdk" + str(i+1) + "/app.py" + " | grep -v grep"
                stdin, stdout, stderr = client.exec_command(serial_cmd)
                data = stdout.readlines()
                print(data)
                if len(data) == 0:
                    ''' restart process by sending cmd. '''
                    if gl.config_dict['restart_onoff']:
                        serial_cmd = "./bin/start_sdk" + str(i + 1) + ".sh"
                        stdin, stdout, stderr = client.exec_command(serial_cmd)
                        print("restart process done!")


        return data_usb

    except Exception as e:
        print(e)


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
        process_count = 0

        time.sleep(0.1)
        ''' 決定是否要檢查usb通訊正常與否
            (在ubuntu內的各種local cmd都透過此方法傳送) '''
        if gl.config_dict['ping_onoff']:
            serial_cmd = "ls /dev/ttyUSB*"
            stdin, stdout, stderr = client.exec_command(serial_cmd)
            data_usb = stdout.readlines()
            if len(data_usb) >= 2:
                process_count = 2
            else:
                process_count = 1

            print(data_usb)



        if gl.config_dict['check_onoff']:
            # kill all app.py process in ubuntu.
            serial_cmd = "ps ax | grep " + "app.py" + " | grep -v grep"
            stdin, stdout, stderr = client.exec_command(serial_cmd)
            data = stdout.readlines()
            for i in range(0, len(data)):
                if gl.config_dict['kill_onoff']:
                    lol_string = ''.join(map(str, data[i]))
                    fields = lol_string.split()
                    pid = fields[0]         # extracting Process ID from the output
                    serial_cmd = "kill -9 " + str(pid)       # terminating process
                    stdin, stdout, stderr = client.exec_command(serial_cmd)
                    print("Process Successfully terminated")
                print("Process: ", data[i])


            # move file from local to other local destination in ubuntu.
            #serial_cmd = "mv ./sdk1/aci_evt.py ./sdk1/pyaci/aci/"
            #stdin, stdout, stderr = client.exec_command(serial_cmd)

        time.sleep(0.5)
        ''' 決定是否要用檔案傳輸用的SCP 
            (從local端傳送檔案至remote端) '''
        if gl.config_dict['scp_onoff']:
            for i in range(0, process_count):
                with SCPClient(client.get_transport()) as scp:
                    # scp.put('local full path', 'remote full path')
                    '''
                    scp.put('/home/davidhsieh/Pictures/aci_uart.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/aci/')
                    scp.put('/home/davidhsieh/Pictures/aci_config.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/aci/')
                    scp.put('/home/davidhsieh/Pictures/aci_utils.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/aci/')
                    scp.put('/home/davidhsieh/Pictures/aci_cmd.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/aci/')
                    scp.put('/home/davidhsieh/Pictures/aci_evt.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/aci/')
    
                    scp.put('/home/davidhsieh/Pictures/interactive.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/')
                    scp.put('/home/davidhsieh/Pictures/interactive_pyaci.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/')
    
                    scp.put('/home/davidhsieh/Pictures/sensor.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/models/')
                    scp.put('/home/davidhsieh/Pictures/lsbu.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/models/')
                    scp.put('/home/davidhsieh/Pictures/light_lc.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/models/')
    
                    scp.put('/home/davidhsieh/Pictures/globalvar.py', recursive=True, remote_path='/home/ubuntu/sdk1/')
                    scp.put('/home/davidhsieh/Pictures/app.py', recursive=True, remote_path='/home/ubuntu/sdk1/')
                    scp.put('/home/davidhsieh/Pictures/apiApp.py', recursive=True, remote_path='/home/ubuntu/sdk1/')
    
                    scp.put('/home/davidhsieh/Pictures/deviceService.py', recursive=True, remote_path='/home/ubuntu/sdk1/service/')
    
                    scp.put('/home/davidhsieh/Pictures/access.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/mesh/')
                    scp.put('/home/davidhsieh/Pictures/database.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/mesh/')
                    scp.put('/home/davidhsieh/Pictures/provisioning.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/mesh/')
                    scp.put('/home/davidhsieh/Pictures/types.py', recursive=True, remote_path='/home/ubuntu/sdk1/pyaci/mesh/')
                    '''
                    #scp.put('/home/davidhsieh/Pictures/LTDMS.json', recursive=True, remote_path='/home/ubuntu/Setup_Encryption/build/Git_Delta_Gateway/pyaci/data/')
                    #scp.put('/home/davidhsieh/Pictures/deviceService.py', recursive=True, remote_path='/home/ubuntu/sdk'+ str(i+1) + '/service/')
                    #scp.put('/home/davidhsieh/Pictures/interactive.py', recursive=True, remote_path='/home/ubuntu/sdk'+ str(i+1) + '/pyaci/')
                    #scp.put('/home/davidhsieh/Pictures/globalvar.py', recursive=True, remote_path='/home/ubuntu/sdk' + str(i + 1))
                    scp.put('/home/davidhsieh/Pictures/device.ini', recursive=True, remote_path='/home/ubuntu/sdk' + str(i + 1))

                    print("scp ", ip, ' done!')
                    scp.close()

        time.sleep(0.5)
        ''' restart process by sending cmd. '''
        if gl.config_dict['restart_onoff'] and gl.config_dict['kill_onoff']:
            for i in range(0, process_count):
                serial_cmd = "./bin/start_sdk" + str(i+1) + ".sh"
                stdin, stdout, stderr = client.exec_command(serial_cmd)
                print("restart process done!")


        time.sleep(0.5)
        ''' 決定是否要重新啟動GW '''
        if gl.config_dict['reboot_onoff']:
            serial_cmd = "sudo reboot"
            stdin, stdout, stderr = client.exec_command(serial_cmd, get_pty=True)
            stdin.write(gl.ip_address_info_dict['password'] + '\n')

            time.sleep(5)
            client.close()
            print(ip + ' reboot...' + '\n\n')


        return data_usb

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
