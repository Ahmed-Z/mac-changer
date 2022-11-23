import subprocess
import fcntl
import socket
import struct
import argparse
import re
import string
import random

def check_mac(mac):
    pattern = re.compile("\A\w\w:\w\w:\w\w:\w\w:\w\w:\w\w\Z")
    if pattern.match(mac) != None:
        return True
    return False

def check_interface(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
        return info
    except OSError:
        return False
def generate_random_mac():
    char = "abcdef" + string.digits
    return random.choice(char) + random.choice("26ae") + ":" + "".join(random.choice(char) + random.choice(char) + ":"  for _ in range(5))[:-1]

def getHwAddr(ifname):
    info = check_interface(ifname)
    if info:
        return ':'.join('%02x' % b for b in info[18:24])
    return f"Interface {ifname} does not exist."

def change_mac(interface,new_mac):
    subprocess.check_output(["sudo","ifconfig",interface,"down"])
    subprocess.check_output(["sudo","ifconfig",interface,"hw","ether",new_mac])
    subprocess.check_output(["sudo","ifconfig",interface,"up"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--change', action='store_true')
    parser.add_argument('--show', type=str, required=False)
    parser.add_argument('--interface', type=str, required=False)
    parser.add_argument('--fake', type=str, required=False)
    parser.add_argument('--random', action='store_true')
    args = parser.parse_args()
    if args.show:
        print(getHwAddr(args.show))
    if args.change:
        if not args.interface:
            print("Please specify an interface.")
            exit()
        if not (args.fake or args.random):
            print("Please specify --random or --fake <fake_mac>.")
            exit()
        if not args.interface:
            print("You must select an interface first.")
            exit()
        if not check_interface(args.interface):
            print(f"Interface {args.interface} does not exist.")
            exit()
        if args.random:
            fake_mac = generate_random_mac()
            change_mac(args.interface, fake_mac)
            print("Current MAC address: ",fake_mac)
            exit()
        if args.fake:
            if not check_mac(args.fake):
                print("MAC address is not valid.")
                exit()
            change_mac(args.interface, args.fake)
            print("Current MAC address: ",args.fake)
            exit()    
        
if __name__ == "__main__":
    main()