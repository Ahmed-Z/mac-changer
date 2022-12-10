import subprocess
import fcntl
import socket
import struct
import argparse
import re
import string
import random

def check_mac(mac):
    # Compile a regular expression pattern to match a MAC address
    pattern = re.compile("\A\w\w:\w\w:\w\w:\w\w:\w\w:\w\w\Z")

    # Use the `match` method to check if the pattern matches the given MAC address
    if pattern.match(mac) != None:
        # If the pattern matches, return True
        return True
    # If the pattern does not match, return False
    return False


def check_interface(ifname):
    try:
        # Create a socket using the AF_INET (Internet) and SOCK_DGRAM (datagram) protocols
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Use the ioctl method to retrieve information about the given interface
        # The ioctl method takes the file descriptor of the socket, a command (0x8927)
        # and a packed binary string representing the interface name
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
        return info
    except OSError:
        return False
    
def generate_random_mac():
    # Create a string of characters that can be used in a MAC address
    char = "abcdef" + string.digits
    return random.choice(char) + random.choice("26ae") + ":" + "".join(random.choice(char) + random.choice(char) + ":"  for _ in range(5))[:-1]

def getHwAddr(ifname):
    info = check_interface(ifname)
    if info:
        return ':'.join('%02x' % b for b in info[18:24])
    return f"Interface {ifname} does not exist."

def change_mac(interface,new_mac):
    # Use the `check_output` method of the `subprocess` module to run the `ifconfig` command
    # with the `down` option to disable the given interface
    subprocess.check_output(["sudo","ifconfig",interface,"down"])

    # Use the `check_output` method of the `subprocess` module to run the `ifconfig` command
    # with the `hw` and `ether` options to change the MAC address of the given interface
    subprocess.check_output(["sudo","ifconfig",interface,"hw","ether",new_mac])

    # Use the `check_output` method of the `subprocess` module to run the `ifconfig` command
    # with the `up` option to enable the given interface
    subprocess.check_output(["sudo","ifconfig",interface,"up"])


def main():
    # Create an ArgumentParser object to parse command-line arguments
    parser = argparse.ArgumentParser()

    # Add a `--change` option to the ArgumentParser
    # If this option is specified, the `args.change` variable will be set to `True`
    parser.add_argument('--change', action='store_true')

    # Add a `--show` option to the ArgumentParser
    # This option takes a string argument that represents the name of an interface
    # If this option is specified, the `args.show` variable will be set to the specified string
    parser.add_argument('--show', type=str, required=False)

    # Add an `--interface` option to the ArgumentParser
    # This option takes a string argument that represents the name of an interface
    # If this option is specified, the `args.interface` variable will be set to the specified string
    parser.add_argument('--interface', type=str, required=False)

    # Add a `--fake` option to the ArgumentParser
    # This option takes a string argument that represents a fake MAC address
    # If this option is specified, the `args.fake` variable will be set to the specified string
    parser.add_argument('--fake', type=str, required=False)

    # Add a `--random` option to the ArgumentParser
    # If this option is specified, the `args.random` variable will be set to `True`
    parser.add_argument('--random', action='store_true')

    # Parse the command-line arguments using the ArgumentParser
    args = parser.parse_args()

    # If the `--show` option was specified, retrieve the MAC address of the specified interface
    # and print it to the console
    if args.show:
        print(getHwAddr(args.show))

    # If the `--change` option was specified, change the MAC address of the specified interface
    if args.change:
        # If the `--interface` option was not specified, print an error message and exit
        if not args.interface:
            print("Please specify an interface.")
            exit()

        # If the `--fake` or `--random` option was not specified, print an error message and exit
        if not (args.fake or args.random):
            print("Please specify --random or --fake <fake_mac>.")
            exit()

        # If the `--interface` option was not specified, print an error message and exit
        if not args.interface:
            print("You must select an interface first.")
            exit()

        # Check if the specified interface exists
        if not check_interface(args.interface):
            # If the interface does not exist, print an error message and exit
            print(f"Interface {args.interface} does not exist.")
            exit()

        # If the `--random` option was specified, generate a random MAC address
        if args.random:
            # Generate a random MAC address
            fake_mac = generate_random_mac()

            # Change the MAC address of the specified interface to the random MAC address
            change_mac(args.interface, fake_mac)

            # Print the current MAC address to the console
            print("Current MAC address: ",fake_mac)

        
if __name__ == "__main__":
    main()
