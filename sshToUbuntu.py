'''
Python遠端登入Linux伺服器並執行相關命令
'''
#!/usr/bin/python

import paramiko
import globavar as gl


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

        serial_cmd = "ls /dev/ttyUSB*"
        stdin, stdout, stderr = client.exec_command(serial_cmd)
        data = stdout.readlines()
        print(data)

        ''' 決定是否要重新啟動GW '''
        if gl.reboot:
            serial_cmd = "sudo reboot"
            stdin, stdout, stderr = client.exec_command(serial_cmd, get_pty=True)
            stdin.write(gl.ip_address_info_dict['password'] + '\n')
            print(ip + ' reboot...')

        client.close()
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