'''
    Author      : ExtraDev
    Date        : 24.01.2019
    Version     : 1.0
    Description : Network scanner in python.
    -------------------------------------------
    Example run : python3 scanner.py 192.168.0
    Example output:
    192.168.0.10 : [80, 443] ==> web_server.home
    192.168.0.13 : [] ==> pc123.home 
    192.168.0.19 : [80, 443] ==> lan.home
'''
import multiprocessing as mp
from multiprocessing import Process
import sys

import os
import socket

# -- Variables --
ipAvailable = list()
portAvailable = list()
output = mp.Queue() # output for ip available
outputPort = mp.Queue() # output for port available
portList = [80, 8080, 443, 3306, 22, 21, 23, 49, 53, 5000, 65535, 1194, 1024, 2048] #Contain the list of the port top ping on avaible ip address
portDescrib = ["Web", "webdev", "HTTPS", "MySql", "ssh", "FTP", "Telnet", "TACACS+", "DNS", "Synology", "minecraft", "VPN", "unknown", "unknown"] #Default protocol
pingProcesses = list()
pingPortProccess = list()

# -- Class --
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# -- Functions --
# Ping ip address
def ping(ipAddress, output):
    #for ipAddress in ipNetwork:
    response = os.system("ping -c 10 " + ipAddress)
    #and then check the response...
    if response == 0: #0 == up
        output.put(""+ipAddress+"")
    else:
        output.put("out")

# Check port on address
def ping_port(ipAddress, outputPort):
    for port in portList:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ipAddress, port))
        if result == 0:
            portAvailable.append(port)

        sock.close()

    try:
        host_name = socket.gethostbyaddr(ipAddress)
        outputPort.put((bcolors.BOLD + "%s"+ bcolors.ENDC +" : " + bcolors.OKGREEN + "%s" + bcolors.ENDC + " ==> %s") % (ipAddress, portAvailable, host_name[0]))
    except:
        outputPort.put((bcolors.BOLD + "%s"+ bcolors.ENDC +" : " + bcolors.OKGREEN + "%s" + bcolors.ENDC) % (ipAddress, portAvailable))

def how_top_use():
    print(bcolors.FAIL+"Attention vous devez donnez le prefix du réseau souhaité pour lancer le programme."+bcolors.ENDC)
    print("Exemple d'utilisation:")
    print(bcolors.BOLD+"python3 scanner.py 192.168.0"+bcolors.ENDC)

# -- Main --
if __name__ == '__main__':
    # Get argument (ip)
    if len(sys.argv) == 1:
        how_top_use()
        quit()

    ipPrefix = sys.argv[1]

    # Create process to ping address
    pingProcesses = [mp.Process(target=ping, args=('%s.%s' % (ipPrefix,ip), output)) for ip in range(1,255)]

    # Start all process
    for ping in pingProcesses:
        ping.start()
    # Wait to join all process
    for ping in pingProcesses:
        ping.join()

    # Get all results in array
    pingResults = [output.get(timeout=1) for p in pingProcesses]

    # Get only ip available
    for result in pingResults:
        if result != "out":
            ipAvailable.append(result)
    
    # Clear terminal
    clear = lambda: os.system('clear')
    clear()

    # Ping port
    print(" ------------------------------ Checking ports ------------------------------ ")
    # Create process to ping port on address
    pingPortProccess = [mp.Process(target=ping_port, args=(ipAvailable[ip], outputPort)) for ip in range(len(ipAvailable))]

    # Start all process
    for ping in pingPortProccess:
        ping.start()
    # Wait to join all process
    for ping in pingPortProccess:
        ping.join()

    # get all results in array
    pingPortResult = [outputPort.get(timeout=1) for p in pingPortProccess]

    # Display result
    for result in pingPortResult:
        print(result)
