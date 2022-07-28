import os as os
import time
import GW_ping as gw
import globavar as gl


gl.read_config_ini()
TIME_GAP = gl.time_gap      #1 min unit.

if __name__ == '__main__':
    print("Start ping all IP！")

    if os.path.isfile("GW_ip_response.txt"):
        os.remove("GW_ip_response.txt")
    if os.path.isfile("Device_response.txt"):
        os.remove("Device_response.txt")



    try:
        while True:
            sleep_time = 1
            for ip in gl.ip_addr_list:
                gw.check_gateway_alive(ip, gl.get_connected_count())

                if gl.get_device_status():
                    gw.check_device_realtime_near_gateway(ip, gl.get_device_addr(ip))


                time.sleep(sleep_time)

            time.sleep(TIME_GAP*60)
    except KeyboardInterrupt:
        print("\n[KeyInterrupt] Application exit!")

    '''
    with open('ip.ini', 'r') as f:      #ip.txt为本地文件记录所有需要检测连通性的ip
        for i in f:
            p = Pool.Process(target=gw.check_alive, args=(i,))
            p.start()
    '''