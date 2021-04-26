import socket
import sys
import binascii
import math

DNS_table = {}

def fileToDict():
    f = open("PROJI-DNSRS.txt", "r")
    Lines = f.readlines()

    for line in Lines:
        new_list = []
        line = line.strip()
        pairs = line.split(' ')
        hostname = pairs[0]
        ip_addr = pairs[1]
        cmd = pairs[2]
        new_list.append(ip_addr)
        new_list.append(cmd)
        DNS_table[hostname] = new_list

    f.close()

def checkHostInDict(host):
    if host in DNS_table.keys():
        return True
    else:
        return False

def toString(host):
    hname = host
    ip = str(DNS_table[host][0])
    cmd = str(DNS_table[host][1])
    name = hname+" "+ip+" "+cmd
    return name

def getTSHostname():
    for key in DNS_table.keys():
        if DNS_table[key][1] == "NS":
            hname = str(key)
            break

    msg = str(hname) + " " + str(DNS_table[hname][0]) + " " + str(DNS_table[hname][1])
    return msg


# fileToDict()
#
# try:
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     print ("[RS]: Socket successfully created")
# except socket.error as err:
#     print ("[RS]: Socket creation failed with error %s" %(err))
#
# port = int(argv[1])
# host = socket.gethostname()
# server_binding = ('', port)
#
# try:
#     s.bind(server_binding)
#     print("[RS]: Socket bind successfull")
# except socket.error as err:
#     print("[RS]: Socket bind fail with error %s" %(err))
#
# s.listen(1)
#
# csockid, addr = s.accept()
# print ("[RS]: Got a connection request from a client at {}".format(addr))
#
# while True:
#     data = csockid.recv(1024).decode()
#     data = str(data)
#     data = data.lower()
#
#     if not data:
#         break
#
    # if checkHostInDict(str(data)) is True:
    #     msg = toString(str(data))
#     else:
#         msg = getTSHostname()
#
#     csockid.send(msg.encode('utf-8'))
#
# s.close()

def send_message(message, address, port):
    print("Mesg in func: ",message)
    server_addr = (address,port)
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        ss.sendto(binascii.unhexlify(message), server_addr)
        print(binascii.unhexlify(message))
        data, _ = ss.recvfrom(4096)
        print(data)
        temp = data
        print("Temp before split: ",temp)
        temp = temp.split(b'\xc0')
        print(temp)
        list = []

        for i in range(1,len(temp)):
            print("In loop")
            get_ip = parse_IP(binascii.hexlify(temp[i]).decode("utf-8"))
            print("Get IP:", get_ip)
            list.append(get_ip)

    except Exception as e:
        print(str(e))
    finally:
        ss.close()
    return binascii.hexlify(data).decode("utf-8"),list

def parse_IP(data):
    print("Data in parse:", data)
    if checkType(data) == -1:
        return "Other"
    elif checkType(data) == 0:
        return ""
    else:
        num = int(data, 16)
        data_mask = pow(2,32) - 1
        length_mask = data_mask << 16
        r_legnth = length_mask.bit_length()
        ip = num & data_mask
        bin_ip = bin(ip).replace("0b", "")
        ip = bin_to_ipv4(bin_ip)
        return ip

def checkType(data):
    print("checkType data:", data)
    if 5 > len(data):
        return 0

    if data[5] != '1':
        return -1
    return 1

def check_Last_Ip(list, ip):
    print(list)
    if list[len(list)-1] != ip:
        if list[len(list)-1] == "Other":
            list.append(ip)
        else:
            list[len(list)-1] = ip
    return list

def connect_to_client(port):

    list = []
    sock_to_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('',port)
    try:
        sock_to_client.bind(server_address)
        print("{S}: Socket create and bind successful")
    except socket.error as err:
        print("Error in socket bind")

    sock_to_client.listen(1)

    csockid, addr = sock_to_client.accept()

    while True:
        data = csockid.recv(1024).decode()
        data = str(data)

        if not data:
            break

        if checkHostInDict(str(data)) is True:
            print("In table")
            send_data = "IP from table"
        else:
            ip = getIP(data)
            print(ip)
            send_data = ""
            if len(ip) == 1:
                send_data = ip[0]
            else:
                for i in range(len(ip)):
                    #print(ip)
                    if i == 0:
                        send_data =  ip[i]
                    elif ip[i] == "":
                        continue
                    else:
                        send_data = send_data + ", " + ip[i]
            #storeIpToTable(data, send_data)
        csockid.send(send_data.encode('utf-8'))

    sock_to_client.close()
    return

def format_list(elements):
    i = 1
    ip = ""
    ip = ip + elements[0]
    while i <= len(elements) - 1:
        ip = ip + "." + elements[i]
        i += 1
    return ip

def bin_to_ipv4(in_binary):
    in_binary = str(in_binary)

    in_binary = in_binary[::-1]


    format_bin = [(in_binary[i:i+8]) for i in range(0, len(in_binary), 8)]

    format_bin = [x[::-1] for x in format_bin]
    format_bin.reverse()
    format_bin = [str(int(x,2)) for x in format_bin]

    return format_list(format_bin)

def getRequest(name):
    temp = name.split(".")

    request = ""

    for i in range(len(temp)):
        print("get request temp:" , temp)
        host = temp[i]
        host_length = len(host)

        if host_length < 10:
            host_length = "0" + str(host_length)
            print("host length < 10", host_length)
        else:
            host_length=""+str(host_length)

        part = str(host_length)
        print("part", part)
        request = request + part
        print("request:",request)
        print(host_length)
        for j in range(int(host_length)):
            request = request  + " " + "".join(hex(ord(host[j]))[2:]) + " "

    return request + " 00 00 01 00 01"

def get_number_of_ip(length):
    return length/4

def getIP(name):
    header = "AA AA 01 00 00 01 00 00 00 00 00 00"

    request = getRequest(name)
    message = header + " " + request
    print(message)
    message = message.replace(" ","").replace("\n","")
    print(message)
    data,response = send_message(message, "8.8.8.8", 53)
    print("Data", data)
    print("Response", response)
    num = int(data, 16)
    data_mask = pow(2,32) - 1
    length_mask = data_mask << 16
    r_legnth = length_mask.bit_length()
    ip = num & data_mask
    bin_ip = bin(ip).replace("0b", "")
    ip = bin_to_ipv4(bin_ip)
    response = check_Last_Ip(response, ip)
    return response

def format_hex(hex): #Refered from David Pham's rectiation number 7
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)

def getRDLength(number):
    in_number = str(bin(number).replace("0b",""))
    in_number = in_number[::-1]
    format_bin = [(in_number[i:i+8]) for i in range(0, len(in_number), 8)]
    format_bin = [x[::-1] for x in format_bin]
    format_bin.reverse()
    return int(format_bin[0],2)


connect_to_client(int(sys.argv[1]))
