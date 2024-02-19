import socket
import sys
from scapy.all import *


def read_data(packets):
    packet_data =[]

    with open(packets, 'r') as f:
        lines = f.readlines()
    current = "" 
    for line in lines:
        if line.strip().isdigit():
            # store the previous packet data
            if current:
                packet_data.append(current.strip())
            current = ""  
        else:    
            current += line.strip()
    if current:
        packet_data.append(current.strip())
    return packet_data  

def egress_filter(packet_data):
    # print(len(packet_data))
    packets= [] 
    subnet = "142.58.22"
    source_ip=[]
    source_ip_int=[]

    for packet in packet_data:
        source_ip = packet[39:48].replace(" ", "")
        source_ip_bytes = bytes.fromhex(source_ip)
        source_ip_int.append(socket.inet_ntoa(source_ip_bytes))

    #print(source_ip_int)
    #print(source_ip_int[0][0:9])

    for i in range(len(source_ip_int)):
        #checking if the packet is incoming
        if (subnet == source_ip_int[i][0:9]):
            print(i+1, "no")
        else:
            print(i+1, "yes")

    # print (packet_data)

def ICMP_ping(packet_data):

    offset = []
    max_len =[]
    dest_ip=[]
    dest_ip_int=[]
    protocol = []
    broadcast = "142.58.22.255"


    for packet in packet_data:
        offset_temp = packet[24:28].replace(" ", "")
        #print(packet[24:28])
        offset_bin = bin(int(offset_temp ,16))
        #print(offset_bin)
        offset.append(int((offset_bin),2)*8)

        max_len_temp = packet[14:19].replace(" ","")
        max_len_bin = bin(int(max_len_temp,16))
        max_len.append(int((max_len_bin),2))

        dest_ip = packet[57:66].replace(" ", "")
        dest_ip_bytes = bytes.fromhex(dest_ip)
        dest_ip_int.append(socket.inet_ntoa(dest_ip_bytes))

        protocol_temp = packet[31:33]
        protocol_bin = bin(int(protocol_temp,16))
        protocol.append(int(protocol_bin,2))
    # print(max_len)   
    # print(offset)
    #print(protocol)
    #print(dest_ip_int)
  
    for i in range(len(packet_data)):
        #checking if ICMP
        if(protocol[i]==1):
            if(offset[i] + max_len[i] > 65535 or broadcast == dest_ip_int[i]):# checking if offset + max len is higher than 65535 or the destination ip is a broadcast ip
                print(i+1, "yes")
            else:
                print(i+1, "no")

        else:
            print(i+1, "no")

def Syn_filter(packet_data):

    subnet = "142.58.22"
    protocol=[]
    sequence_no=[]
    source_ip_int=[]
    dest_ip_int=[]
    ack_no=[]
    flag = []
    srcport=[]
    desport=[]
    source_ip_count={}
    

    for packet in packet_data:
        #obtaining the necessary info from the packets_data
        protocol_temp = packet[31:33]
        protocol_bin = bin(int(protocol_temp,16))
        protocol.append(int(protocol_bin,2))

        seq_temp = packet[77:86].replace(" ","")
        seq_bin = bin(int(seq_temp,16))
        sequence_no.append(int(seq_bin,2))

        source_ip = packet[39:48].replace(" ", "")
        source_ip_bytes = bytes.fromhex(source_ip)
        source_ip_int.append(socket.inet_ntoa(source_ip_bytes))

        dest_ip = packet[57:66].replace(" ", "")
        dest_ip_bytes = bytes.fromhex(dest_ip)
        dest_ip_int.append(socket.inet_ntoa(dest_ip_bytes))

        ack_temp = packet[87:96].replace(" ","")
        ack_bin = bin(int(ack_temp,16))
        ack_no.append(int(ack_bin,2))

        flag_temp = packet[107:109].replace(" ","")
        flag_bin= bin(int(flag_temp,16))
        flag.append(int(flag_bin,2))


        srcport_temp = packet[67:71].replace(" ","")
        srcport_bin= bin(int(srcport_temp,16))
        srcport.append(int(srcport_bin,2))

        desport_temp = packet[67:71].replace(" ","")
        desport_bin= bin(int(desport_temp,16))
        desport.append(int(desport_bin,2))




    #print(flag)
    for i in range(len(packet_data)):
        # Check if it's a TCP packet
        if protocol[i] == 6:  
            # Check if it's a SYN packet (SYN flag is set)
            if flag[i] == 2:  
                source_ip = (source_ip_int[i],dest_ip_int[i],srcport[i], desport[i], sequence_no[i])
                if subnet!= source_ip_int[i][0:9]:
                    # Check if it's a new half-open connection for the given source ip/port 
                    if  source_ip not in source_ip_count:
                        source_ip_count[source_ip] = 1
                        #Sprint(source_ip_count)
                      
                    else:
                        source_ip_count[source_ip] += 1
                        #print(source_ip_count)

                    if source_ip_count[source_ip] < 10:
                        print(f"{i + 1} no") 
                        #print(source_ip_count)
                    else:
                        print(f"{i + 1} yes") 
                        #print(source_ip_count)
                else:
                    print(f"{i + 1} no")


            elif flag[i] ==16:
                if subnet!= source_ip_int[i][0:9]:
                    source_ip_check=(source_ip_int[i],dest_ip_int[i],srcport[i], desport[i], sequence_no[i]-1)
                    source_ip = (source_ip_int[i],dest_ip_int[i],srcport[i], desport[i],sequence_no[i]-1) 
                    if source_ip_check in source_ip_count:
                        source_ip_count[source_ip]-=1
                        #print("here")
                print(f"{i + 1} no")
                        #print(source_ip_count)

            elif flag[i] == 17 or flag[i] == 1 or flag[i] == 20 or flag[i] == 4:
                source_ip = (source_ip_int[i],dest_ip_int[i],srcport[i], desport[i],sequence_no[i])
                for key in list(source_ip_count.keys()):
                    # Check if a connection exist between that source ip/port and the destination ip/port
                    if key[:4] == source_ip[:4]:  
                        del source_ip_count[key]
                        #print("here3")

                print(f"{i + 1} no")
                #print(source_ip_count)

            else:
                print(f"{i + 1} no")
                #print(source_ip_count)




        else:
            print(f"{i + 1} no")
            #print(source_ip_count)



def main():

    if len(sys.argv) < 2:
        print("please use the correct command")
        return -1

    packets = sys.argv[2]
    packet_data = read_data(packets)
    #print (packet_data[2][77:86])
    option = sys.argv[1][1]
    

    

    if option == "i":
        egress_filter(packet_data)

    elif option =="j":
        ICMP_ping(packet_data)

    elif option =="k":
        Syn_filter(packet_data)


if __name__ == "__main__":
    main()