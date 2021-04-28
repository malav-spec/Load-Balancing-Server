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

def storeIpToTable(host, ip):
    print("host: ", host)
    print("IP: ", ip)
    DNS_table[host] = ip

def getIPFromTable(host):
    return DNS_table[host]

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

        print(list)

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

    print("Data[5]:",data[5])
    if data[5] != '1':
        return -1
    return 1

def check_Last_Ip(list, ip):
    print(list)
    if not list:
        list = []
        list.append("Other")
        return list
    print(list)
    print("In last IP: ",ip)
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
            send_data = getIPFromTable(data)
        else:
            ip = getIP(data)
            send_data = ""
            print(ip)

            if ip[0] == "Other":
                send_data = data + " - Error:HOST NOT FOUND"
            elif len(ip) == 1:
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
            storeIpToTable(data, send_data)
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

def getHexLength(length):

    length =  hex(length).lstrip("0x").rstrip("L")
    if len(length) % 2 != 0:
        length = "0" + length
    return length

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
            host_length= getHexLength(host_length)

        part = str(host_length)
        print("part", part)
        request = request + part
        print("request:",request)
        print(host_length)
        for j in range(int(host_length, 16)):
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
    data,response = send_message(message, "1.1.1.1", 53)
    print("Data", data)
    print("Response", response)
    num = int(data, 16)
    data_mask = pow(2,32) - 1
    length_mask = data_mask << 16
    r_legnth = length_mask.bit_length()
    ip = num & data_mask
    print("IP::" , ip)
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
