import sys
# Command below is to Disable pyc file generate.
sys.dont_write_bytecode = True
import os as os
import time
import GW_ping as gw
import globavar as gl
import threading


gl.read_ip_ini()
gl.read_config_ini()
TIME_GAP = gl.time_gap*60    #1 min unit.

lock = threading.Lock()
CHECK = False

def process_handler():
    if gl.config_dict['check_onoff'] and gl.config_dict['restart_onoff'] and CHECK:
        for ip in gl.ip_addr_list:
            gl.serial_port_check_process(ip)



def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


if __name__ == '__main__':
    print("Start ping all IP！")
    first = True

    if os.path.isfile("GW_ip_response.txt"):
        os.remove("GW_ip_response.txt")
    if os.path.isfile("Device_response.txt"):
        os.remove("Device_response.txt")
    if os.path.isfile("reboot_time.txt"):
        os.remove("reboot_time.txt")

    time_work = time_write_txt = time.time()

    #check process
    if gl.config_dict['check_onoff'] and gl.config_dict['restart_onoff']:
        '''
        per GW need 8 sec for safety go through all control.
        Thus, each GW * 8 secs as time interval.
        '''
        set_interval(process_handler, gl.GW_length * 8)


    try:
        while True:
            sleep_time = 0.3
            device_count = 0
            time_normal = time.time()
            time_interval = round(time_normal - time_work, 2)


            if time_interval >= TIME_GAP or first is True:
                lock.acquire()
                CHECK = False
                first = False
                for ip in gl.ip_addr_list:
                    if gl.config_dict['ping_onoff']:
                        gw.check_gateway_alive(ip, gl.get_connected_count())

                    if gl.config_dict['checked_device_onoff']:
                        gw.check_device_realtime_near_gateway(ip, gl.get_device_addr(ip))

                    device_count += 1
                    if device_count % 10 == 0:
                        time.sleep(240)

                    time.sleep(sleep_time)
                    time_work = time_normal = time.time()


                print("Finished a loop and rest for ", TIME_GAP, "mins... then will restart again.")
                CHECK = True
                lock.release()
            # 10 mins will enter to refresh txt.
            if gl.config_dict['reboot_onoff'] and (time_normal - time_write_txt >= 600):
                time_write_txt = time.time()
                gl.write_reboot_time_txt(time_interval)


    except KeyboardInterrupt:
        print("\n[KeyInterrupt] Application exit!")





    '''
    with open('ip.ini', 'r') as f:      #ip.txt为本地文件记录所有需要检测连通性的ip
        for i in f:
            p = Pool.Process(target=gw.check_alive, args=(i,))
            p.start()
    '''
