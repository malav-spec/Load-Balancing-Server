import socket
import sys


DNS_table = {}
ts1_list = []
ts2_list = []

# def empty_socket(sock):
#     """remove the data present on the socket"""
#     input = [sock]
#     while 1:
#         inputready, o, e = select.select(input,[],[], 0.0)
#         if len(inputready)==0: break
#         for s in inputready: s.recv(1)


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
ts1.settimeout(3)
# ts1.settimeout(0.0000000000000000000001)

#Open ts2 socket
try:
    ts2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("[RS]: Socket successfully created")
except socket.error as err:
    print ("[RS]: Socket creation failed with error %s" %(err))

ts2_server_addr = (sys.argv[4], int(sys.argv[5]))
ts2.connect(ts2_server_addr)
# ts2.settimeout(0.0000000000000000000001)
ts2.settimeout(3)

counter = 0

while True:

    data = csockid.recv(1024).decode()
    data = str(data)
    data = data.lower()
    print(data)
    msg="recv"
    ip=""
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
        print(data)
        try:
            ts1.sendall(data.encode('utf-8'))
            ip = ts1.recv(1024)
            ip = ip.decode('utf-8')
            print("In ts1", ip)
            counter = 1
            csockid.send(ip.encode('utf-8'))
            continue
        except socket.timeout as e:
            print("TS1 timeout") #If ts1 timeout send to ts2
            try:
                ts2.sendall(data.encode('utf-8'))
                ip = ts2.recv(1024)
                ip = ip.decode('utf-8')
                print(ip)
                counter = 1
                csockid.send(ip.encode('utf-8'))
                continue
            except socket.timeout as e:
                print("TS2 also timeout") # if ts2 also timeout send error message
                ip = data + " - Error:HOST NOT FOUND"

                if data in ts1_list:
                    ts1_list.remove(data)
                elif data in ts2_list:
                    ts2_list.remove(data)
                csockid.send(ip.encode('utf-8'))
                counter = 1
                continue

    elif counter == 1:
        print(data)
        try:
            ts2.sendall(data.encode('utf-8'))
            ip = ts2.recv(1024)
            ip = ip.decode('utf-8')
            print("In ts2", ip)
            counter = 0
            csockid.send(ip.encode('utf-8'))
            continue
        except socket.timeout as e:
            print("TS2 timeout")#If ts2 timeout send to ts1
            try:
                ts1.sendall(data.encode('utf-8'))
                ip = ts1.recv(1024)
                ip = ip.decode('utf-8')
                print(ip)
                counter = 0
                csockid.send(ip.encode('utf-8'))
                continue
            except socket.timeout as e:
                print("TS1 also timeout")# if ts1 also timeout send error message
                ip = data + " - Error:HOST NOT FOUND"

                if data in ts1_list:
                    ts1_list.remove(data)
                elif data in ts2_list:
                    ts2_list.remove(data)

                csockid.send(ip.encode('utf-8'))
                counter = 0
                continue

    csockid.send(ip.encode('utf-8'))

s.close()
