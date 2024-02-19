import sys
import re

def is_valid_packet(packet):
    source_ip = packet[0]
    destination_ip = packet[1]
    subnet = "142.58.22"

    # Check if the source IP falls within the subnet
    if not source_ip.startswith(subnet):
        return False

    # Check if the destination IP falls outside the subnet
    if destination_ip.startswith(subnet):
        return False

    return True

def filter_packets(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    packets = re.findall(r'([0-9a-fA-F]{4}\s)+', ''.join(lines))

    for i, packet in enumerate(packets, start=1):
        packet = packet.strip().split()
        source_ip = ''.join(packet[2:6]).replace(' ', '')
        destination_ip = ''.join(packet[6:10]).replace(' ', '')

        if is_valid_packet([source_ip, destination_ip]):
            print(f"{i} no")
        else:
            print(f"{i} yes")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 filter.py -i <filename>")
        sys.exit(1)

    option = sys.argv[1]
    filename = sys.argv[2]

    if option != '-i':
        print("Invalid option. Only -i is supported for egress filtering.")
        sys.exit(1)

    filter_packets(filename)
