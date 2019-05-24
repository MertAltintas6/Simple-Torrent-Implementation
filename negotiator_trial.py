import threading
import time
import socket
import queue
import os, fcntl, struct


def get_uuid():
    if os.geteuid() > 0:
     print("ERROR: Must be root to use")
     return False

    with open("/dev/sda", "rb") as fd:
        # tediously derived from the monster struct defined in <hdreg.h>
        # see comment at end of file to verify
        hd_driveid_format_str = "@ 10H 20s 3H 8s 40s 2B H 2B H 4B 6H 2B I 36H I Q 152H"
        # Also from <hdreg.h>
        HDIO_GET_IDENTITY = 0x030d
        # How big a buffer do we need?
        sizeof_hd_driveid = struct.calcsize(hd_driveid_format_str)

        # ensure our format string is the correct size
        # 512 is extracted using sizeof(struct hd_id) in the c code
        assert sizeof_hd_driveid == 512

        # Call native function
        buf = fcntl.ioctl(fd, HDIO_GET_IDENTITY, " " * sizeof_hd_driveid)
        fields = struct.unpack(hd_driveid_format_str, buf)
        serial_no = fields[10].strip()
        #model = fields[15].strip()
        #print("Hard Disk Model: %s" % model)
        #print("  Serial Number: %s" % serial_no)
        return str(serial_no)


class loggerThread(threading.Thread):
    def __init__(self, name, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue

    def run(self):
        print(self.name + " starting.")
        while True:
            msg = self.logQueue.get()
            if msg == "QUIT":
                print(self.name + ": QUIT received.")
                break
            print(str(time.ctime()) + " - " + str(msg.strip()))
        print(self.name + " exiting." )


class readThread(threading.Thread):
    def __init__(self, name, clientSocket, addr, fihrist,socketFihrist, threadQueue, logQueue, uuid):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue
        self.threadQueue = threadQueue
        self.c = clientSocket
        self.addr = addr
        self.fihrist = fihrist
        self.socketFihrist = socketFihrist
        self.uuid = uuid
        self.control = False
        self.peer_uuid = ""

    def run(self):
        self.logQueue.put("Starting " + self.name)
        while True:
            msg = self.c.recv(1024).decode()
            if msg != "":
                self.logQueue.put("Received message from " + str(self.addr) + ": " + msg)
                ret = self.parser(msg)
                self.threadQueue.put(ret)
                # exit message is received
                if ret == "EOK\n":
                    break
        self.logQueue.put("Exiting " + self.name)

    def parser(self,message):
        message.strip()
        command = message[:3]

        # if connection established for connected peer
        if self.peer_uuid in self.socketFihrist.keys():
            self.control=True

        if command == "HEL":
            try :
                data = message[4:].strip().split(" ")
                self.peer_uuid = data[0].strip()
                peer_ip = data[1]
                peer_port = data[2]
                peer_type = data[3].strip()
            except:
                return "ERR\n"

            # control thread is not yet started
            isWaiting = False

            #if user is not registered
            array = list(self.fihrist)
            if self.peer_uuid not in array:
                # first status will be "Pending"
                status = "Pending"
            else :
                #user's current status in the fihrist
                status = self.fihrist[self.peer_uuid][2]
                if status == "Pending":
                    # control thread is already processing
                    isWaiting = True

            #updating user's info
            info = [peer_ip, peer_port, status, peer_type, str(time.ctime())]
            self.fihrist[self.peer_uuid] = info

            # starting the control thread, if it is not already started
            if not isWaiting:
                try:
                    # open a connection to given server address of the peer
                    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    c.connect((peer_ip, int(peer_port)))

                    # add this socket to socket list
                    self.socketFihrist[self.peer_uuid ] = c

                    # controling peer's server side connection info
                    newClientControl = clientControl(c,self.peer_uuid, self.fihrist, self.uuid, self.logQueue)
                    newClientControl.start()

                except socket.error:
                    # if cannot connect to given server info
                    status ="NOK"
                    self.fihrist[self.peer_uuid][2] = status
                    self.fihrist[self.peer_uuid][-1] = str(time.ctime())
                    self.logQueue.put("Control Client Connection Error for " + self.uuid)

            status = self.fihrist[self.peer_uuid][2]

            return "HEY " + status + "\n"

        elif command == "EXI":
            return "EOK\n"

        elif command == "BOO":
            self.peer_uuid = message[4:].strip()
            return "POW " + self.uuid + "\n"

        elif self.control:

            if command == "LSP":
                data = []
                for key, value in self.fihrist.items():
                    #sending peers' info that has status "OK", except himself
                    if self.fihrist[key][2] == "OK" and key != self.peer_uuid:
                        data.append(str(key) + ">" + str(value))
                return "PLS " + "-".join(data[:5]) + "\n"

            else :
                # wrong protocol message
                return "ERR" + "\n"
        else :
            #the peer is not registered
            return "ERL" + "\n"


class writeThread(threading.Thread):
    def __init__(self, name, clientSocket, addr, fihrist, threadQueue, logQueue, uuid):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue
        self.threadQueue = threadQueue
        self.c = clientSocket
        self.addr = addr
        self.fihrist = fihrist
        self.uuid = uuid

    def run(self):
        self.logQueue.put("Starting " + self.name)
        while True:
            # reading from threadQueue and sending to client
            msg = self.threadQueue.get()
            self.c.send(msg.encode())
            self.logQueue.put("Sending message to " + str(self.addr) + ": " + msg)
            # exit is received, closing socket
            if msg[:3] == "EOK":
                self.c.close()
                self.logQueue.put("Closing socket " + str(self.addr))
                break

        self.logQueue.put("Exiting " + self.name)


class clientControl(threading.Thread):
    def __init__(self, soc, uuid, fihrist, s_uuid, lQueue):
        threading.Thread.__init__(self)
        self.soc = soc
        self.uuid = uuid.strip()
        self.fihrist = fihrist
        self.s_uuid = s_uuid
        self.logQueue = lQueue
    def run(self):
        try :
            # sending the control message
            msg = "BOO " + self.s_uuid + "\n"
            self.soc.send(msg.encode())
            self.logQueue.put("Sending message to " + str(self.uuid) + ": " + msg)

            # receiving the message from given address
            data = self.soc.recv(2000)
            ret = data.decode().strip()
            self.logQueue.put("Received message from " + str(self.uuid) + ": " + ret)

            # control process and changing user's status
            if ret == "POW " + self.uuid.strip():
                status = "OK"
            else:
                status = "NOK"
        except :
            # if message sending fails
            status = "NOK"

        # updating status
        self.fihrist[self.uuid][2] = status
        self.fihrist[self.uuid][-1] = str(time.ctime())
        self.logQueue.put("Status " + str(self.uuid) + ": " + status)


class clientRequest(threading.Thread):
    def __init__(self, soc, host_ip, host_port,host_uuid, host_type, socketFihrist, fihrist, uuid, logQueue):
        threading.Thread.__init__(self)
        self.soc = soc
        self.host_ip =host_ip
        self.host_port = host_port
        self.host_type = host_type
        self.host_uuid = host_uuid
        self.socketFihrist = socketFihrist
        self.fihrist = fihrist
        self.uuid = uuid
        self.logQueue = logQueue

    def run(self):
        try :
            # sending the request list message
            msg = "LSP\n"
            self.soc.send(msg.encode())
            self.logQueue.put("Sending message to " + str(self.uuid) + ": " + msg)

            # receiving the message from given address
            data = self.soc.recv(2000)
            ret = data.decode().strip()
            self.logQueue.put("Receiving message from " + str(self.uuid) + ": " + ret)

            msg = ret[:3].strip()

            # parsing message, updating list
            if msg == "PLS":
                self.fihrist = listParsing(ret, self.fihrist)
                self.logQueue.put("Peer list updated from " + self.uuid)

                array = list(self.fihrist)
                for i in array:
                    array2 = list(self.socketFihrist)
                    if i not in array2:
                        try:
                            # connecting the new peer
                            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            c.connect((self.fihrist[i][0], int(self.fihrist[i][1])))

                            #introduce(c, self.host_ip, self.host_port, self.host_uuid,self.host_type, self.uuid,self.logQueue)
                            first_msg = "HEL " + self.host_uuid + " " + self.host_ip + " " + str(self.host_port) + " " + self.host_type
                            c.send(first_msg.encode())
                            self.logQueue.put("Sending introduce message to " + i)

                            # connected peer's response
                            ret = c.recv(2000).decode()
                            status = ret[4:]

                            self.logQueue.put("Registration Succeed for " + i)
                            #updating socket fihrist
                            self.socketFihrist[i] = c
                            self.logQueue.put("Connection Succesful for " + i)
                        except:
                            # if connection fails, update status
                            self.fihrist[i][2]="NOK"
                            self.fihrist[i][-1] = str(time.ctime())
                            self.logQueue.put("Connection Error for " + i)

            else:
                self.logQueue.put("Error while receiving peer list from " + str(self.uuid))
        except:
            self.logQueue.put("Connection error while receiving peer list from " + str(self.uuid))


def listParsing(ret,fihrist):
    data = ret[4:].split("-")

    for item in range(0, len(data)):
        try:
            peer = data[item].strip().split(">")
            uuid = peer[0].strip()
            value = peer[1].split("\'")
            ip = value[1]
            port = value[3]
            status = value[5]
            type = value[7]
            time = value[9]
            input = [ip, port, status, type, time]
            fihrist[uuid] = input

        except:
            pass
    return fihrist


class autoTask(threading.Thread):
    def __init__(self,socketFihrist, fihrist ,host_uuid,host_ip, host_port, host_type, lqueue):
        threading.Thread.__init__(self)
        self.socketFihrist = socketFihrist
        self.fihrist = fihrist
        self.host_uuid=host_uuid
        self.host_port = host_port
        self.host_ip = host_ip
        self.host_type = host_type
        self.logQueue = lqueue

    def run(self):
        counter = 0
        while True:
            # waiting 60 secs
            time.sleep(60)
            counter += 1
            # controling the status of peers in the list every 1 min
            if self.socketFihrist:
                self.logQueue.put("Automatic Control Started! ")
                array = list(self.socketFihrist)
                for i in array:
                    newClientControl = clientControl(self.socketFihrist[i], i, self.fihrist, self.host_uuid, self.logQueue)
                    newClientControl.start()

            if counter == 3 :
                # requesting list from peers with status "OK" , every 3 minutes
                if self.fihrist:
                    self.logQueue.put("Automatic Request Started! ")
                    array = list(self.socketFihrist)
                    for i in array:
                        if self.fihrist[i][2] == "OK":
                            newClientRequest = clientRequest(self.socketFihrist[i],self.host_ip, self.host_port, self.host_uuid,
                                                             self.host_type, self.socketFihrist, self.fihrist,i,self.logQueue)
                            newClientRequest.start()

                counter = 0


def main():
    # fihrist of peers
    fihrist = {}
    # fihrist of peers' socket info
    socketFihrist = {}
    # start the logger thread
    lQueue = queue.Queue()
    lThread = loggerThread("Logger", lQueue)
    lThread.start()

    # start listening
    s = socket.socket()
    host = "0.0.0.0"
    port = 12000
    h_type = "S"
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    s.listen(5)
    lQueue.put("Waiting for connection")

    uuid = get_uuid()

    # give unique name to all of the threads
    counter = 0

    # start automatic processes for peer control and list request
    newautoTask = autoTask(socketFihrist,fihrist,uuid, host , port , h_type, lQueue)
    newautoTask.start()

    while True:
        # close the port gracefully
        try:
            c, addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            lQueue.put('QUIT')
            break
        lQueue.put('Got new connection from ' + str(addr))

        # start new write and read thread
        tQueue = queue.Queue()
        newreadThread = readThread('ReadThread-' + str(counter),
                                   c,
                                   addr,
                                   fihrist,socketFihrist, tQueue,
                                   lQueue, uuid)
        newwriteThread = writeThread('WriteThread-' + str(counter),
                                     c,
                                     addr,
                                     fihrist, tQueue,
                                     lQueue, uuid)
        newreadThread.start()
        newwriteThread.start()

        counter += 1


if __name__ == '__main__':
    main()