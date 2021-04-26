import socket
import sys


DNS_table = {}
ts1_list = []
ts2_list = []
# def fileToDict():
#     f = open("PROJ3-HNS.txt", "r")
#     Lines = f.readlines()
#
#     for line in Lines:
#         new_list = []
#         line = line.strip()
#         pairs = line.split(' ')
#         hostname = pairs[0]
#         ip_addr = pairs[1]
#         cmd = pairs[2]
#         new_list.append(ip_addr)
#         new_list.append(cmd)
#         DNS_table[hostname] = new_list
#
#     f.close()
#
# def checkHostInDict(host):
#     if host in DNS_table.keys():
#         return True
#     else:
#         return False
#
# def toString(host):
#     hname = host
#     ip = str(DNS_table[host][0])
#     cmd = str(DNS_table[host][1])
#     name = hname+" "+ip+" "+cmd
#     return name
#
# def getTSHostname():
#     for key in DNS_table.keys():
#         if DNS_table[key][1] == "NS":
#             hname = str(key)
#             break
#
#     msg = str(hname) + " " + str(DNS_table[hname][0]) + " " + str(DNS_table[hname][1])
#     return msg
#
#
# fileToDict()

def addToList(counter, data):
    print("In add to list:" , data)
    print(counter)
    if counter == 0:
        ts1_list.append(data)
    elif counter == 1:
        ts2_list.append(data)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("[RS]: Socket successfully created")
except socket.error as err:
    print ("[RS]: Socket creation failed with error %s" %(err))

port = int(sys.argv[1])
host = socket.gethostname()
server_binding = ('', port)

try:
    s.bind(server_binding)
    print("[RS]: Socket bind successfull")
except socket.error as err:
    print("[RS]: Socket bind fail with error %s" %(err))

s.listen(1)

csockid, addr = s.accept()
print ("[RS]: Got a connection request from a client at {}".format(addr))

#Open ts1 socket
try:
    ts1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("[RS]: Socket successfully created")
except socket.error as err:
    print ("[RS]: Socket creation failed with error %s" %(err))

ts1_server_addr = (sys.argv[2], int(sys.argv[3]))
ts1.connect(ts1_server_addr)

#Open ts2 socket
try:
    ts2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("[RS]: Socket successfully created")
except socket.error as err:
    print ("[RS]: Socket creation failed with error %s" %(err))

ts2_server_addr = (sys.argv[4], int(sys.argv[5]))
ts2.connect(ts2_server_addr)

counter = 0

while True:

    data = csockid.recv(1024).decode()
    data = str(data)
    data = data.lower()
    print(data)
    msg="recv"

    if not data:
        break

    if data in ts1_list:
        print("ts1 list: ", ts1_list)
        counter = 0
    elif data in ts2_list:
        print("ts2 list: ", ts2_list)
        counter = 1
    else:
        addToList(counter, data)

    if counter == 0:
        ts1.sendall(data.encode('utf-8'))
        ip = ts1.recv(1024)
        ip = ip.decode('utf-8')
        print(ip)
        counter = 1
    else:
        ts2.sendall(data.encode('utf-8'))
        ip = ts2.recv(1024)
        ip = ip.decode('utf-8')
        print(ip)
        counter = 0
    # if checkHostInDict(str(data)) is True:
    #     msg = toString(str(data))
    # else:
    #     msg = getTSHostname()

    csockid.send(ip.encode('utf-8'))

s.close()
