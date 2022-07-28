requirment:
sudo pip install requests
sudo pip install paramiko

[in ubuntu]
python3.8 -m pip install paramiko 
python3.8 -m pip install requests

When install paramiko, Python pip raising 'NewConnectionError' while installing libraries 
The only solution I used is to add "nameserver 8.8.8.8"
then,
1. cd /etc/  ---  resolv.conf file
2. sudo cp resolv.conf resolv.conf_bak
3. sudo nano resolv.conf
   modify ip address to 8.8.8.8 (Google public free DNS server)
4. sudo reboot
