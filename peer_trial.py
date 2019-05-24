import negotiator_trial as neg
import file_methods as fmet
import threading
import queue
import socket
import time
import tempfile


class readThread(neg.readThread):
    def __init__(self, name, clientSocket, addr, fihrist, socketFihrist, threadQueue, logQueue, uuid):
        # using negotiator's readThread init function
        super().__init__(name, clientSocket, addr, fihrist, socketFihrist, threadQueue, logQueue, uuid)
        self.path_dir = "./Shared/"
        self.files = {}
        self.chunkSize = 512
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

        # parsing protocol messages common with negotiator
        ret = super().parser(message)

        # peer specific protocol messages
        if ret == "ERR\n":
            if command == "SAB":
                msg = message[4:]
                # TODO show message on UI
                ret = "SOK\n"
            elif command == "FRQ":
                msg = message[4:].split(" ")
                chunkno = int(msg[0].strip())
                md5 = msg[1].strip()
                fname, size = self.files[md5]

                file = self.path_dir + fname.strip()

                requestedData = fmet.getChunkData(file, self.chunkSize, int(chunkno))
                if requestedData != False:
                    #if file is available in the peer
                    ret = "CHK "+str(chunkno)+" "+str(md5)+" :: " +str(requestedData)+"\n"
                else:
                    #if file is erased in the peer
                    ret = "CNO "+str(chunkno)+"\n"
            elif command == "FSR":
                self.files = {}

                filename = message[4:].strip().split(" ")[0]
                retval = fmet.search_filename(filename, self.path_dir)

                #same files with equal md5sums but saved in different names
                same = retval[0]
                #different md5sums but similar files
                sname = retval[1]
                sim = retval[2]

                if len(same)>0:
                    fname = same[0]
                    retval = fmet.get_attiributes(fname)
                    md5 = retval[0]
                    size = retval[1]
                    fname = fname.split(self.path_dir)[1].strip(".")
                    content = [fname, size]
                    self.files[md5] = content

                if len(sim)>0:
                    for name in sim:
                        fname = name
                        retval = fmet.get_attiributes(fname)
                        md5 = retval[0]
                        size = retval[1]
                        fname = fname.split(self.path_dir)[1].strip(".")
                        content = [fname, size]
                        #print(md5, content)
                        self.files[md5] = content

                if len(sname)>0:
                    for sn in sname:
                        fname = sn
                        retval = fmet.get_attiributes(fname)
                        md5 = retval[0]
                        size = retval[1]
                        fname = fname.split(self.path_dir)[1].strip(".")
                        content = [fname, size]
                        #print(md5, content)
                        self.files[md5] = content

                # if similar file exists
                if self.files:
                    line = []
                    for key, value in self.files.items():
                        line.append(str(key)+">"+str(value))
                    ret = "FLS "+"-".join(line)+"\n"

                # if no similar file
                else:
                    ret = "FNO\n"

            elif command == "CSR":

                md5 = message[4:].strip().split(" ")[0]
                if len(md5) == 32:
                    same = fmet.search_md5(md5, self.path_dir)
                    self.files = {}
                    if same != False:
                        for item in same:
                            fname = item
                            retval = fmet.get_attiributes(fname)
                            md5 = retval[0]
                            size = retval[1]
                            fname = fname.split(self.path_dir)[1].strip(".")
                            content = [fname, size]
                            self.files[md5] = content
                        if self.files:
                            line = []
                            for key, value in self.files.items():
                                line.append(str(key)+">"+str(value))
                        ret = "CLS "+"-".join(line)+"\n"
                    else:
                        #md5 not found
                        ret = "CRJ\n"
                else:
                    #wrong type of input
                    ret = "CRJ\n"
            else :
                return ret

        return ret


class clientThread(threading.Thread ):
    def __init__(self, host, port,  fihrist, socketFihrist, logQueue, uuid):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.logQueue = logQueue
        self.fihrist = fihrist
        self.uuid = uuid
        self.socketFihrist = socketFihrist
        self.filelist = {}
        self.tmp_paths = []
        self.key = False

    def run(self):
        self.logQueue.put("Peer Client Thread Started.")

        # From UI when first peer info was entered, self_introducing
        ui_input = input("Peer IP Port: ")
        self.fihrist, self.socketFihrist= self_introduce(ui_input, self.host,self.port,self.fihrist, self.socketFihrist,  self.uuid, self.logQueue)

        ui_message = input("Message: ")

        soc = self.socketFihrist["b'ui_peer'"]
        msg_tosend = "SAB " + ui_message
        soc.send(msg_tosend.encode())

        ret = soc.recv(4000).decode().strip()

        # From UI when file search is triggered
        ui_file_search = input("File name: ")
        # list of results returned from file search by name
        array = list(self.socketFihrist)
        for i in array:
            # searching in all peers with status OK
            if self.fihrist[i][3] == "P" and self.fihrist[i][2] == "OK":
                soc = self.socketFihrist[i]
                # searching by file name
                result = filename_search(ui_file_search, soc, self.filelist)
                if result == False:
                    self.logQueue.put("Error while searching file from " +i )
                elif result == "FNO":
                    self.logQueue.put("No such file in this ip: " + i)
        # Show search list in UI
        print(self.filelist)

        # TODO When file search by checksum is needed
        # TODO Interpret the CHK results
        array = list(self.socketFihrist)
        for i in array:
            # searching in all peers with status OK
            if self.fihrist[i][3] == "P" and self.fihrist[i][2] == "OK":
                soc = self.socketFihrist[i]
                # for this checksum download a file, first search then request

                # bunu değiştirerek dene
                checksum =  "906e664c9e8d4a4eb197a53c0b415328"
                #checksum ="3b75de9797415e94964c11936084357b"
                ret = checksum_search(soc, checksum, self.tmp_paths, self.key)

                if type(ret) == list:
                    self.tmp_paths = ret

                if not b'\0' in self.tmp_paths:
                    if checksum in self.filelist.keys():
                        fmet.joinFiles(self.filelist[checksum][0].strip(), self.tmp_paths)


def checksum_search(soc, checksum, tmp_paths, key):
    try:
        # sending file search by checksum request
        msg_tosend = "CSR " + checksum
        soc.send(msg_tosend.encode())

        ret = soc.recv(4000).decode()

        if ret[:3] == "CLS":
            data = ret[4:].split("-")
            for item in range(len(data)):
                try:
                    file = data[item].strip().split(">")
                    checksum = file[0].strip()
                    value = file[1].replace("[","").replace("]","").replace("'","").strip().split(",")
                    filename = value[0]
                    size = value[1]
                except IndexError:
                    return False

            # if no meta file, create.
            if not key:
                noOfChunks = fmet.createMeta(filename, int(size), chunkSize=512)
                key = True
                #chunkların sayısı kadar boş bir liste oluştur.
                tmp_paths = [b'\0'] * noOfChunks

            f = open("meta.txt", "r")
            lines = f.readlines()
            f.close()
            # chunk var mı kontrol et.
            result = True

            for l in lines:
                chunk_no = l.split(" ")[0]
                # download the chunk
                ret = download_chunks(soc,chunk_no,checksum,tmp_paths)
                if type(ret) == list:
                    tmp_paths = ret[0]
                    ret = ret[1]

                if ret != False and ret!= "CNO":

                    f = open("meta.txt", "r")
                    lines = f.readlines()
                    f.close()

                    f = open("meta.txt", "w")
                    # meta dosyasından sil
                    for line in lines:
                        chunk = line.split(" ")[0]
                        if chunk_no != chunk.strip():
                            f.write(line)
                    f.close()
                else :
                    return False
            return tmp_paths
        else :
            # no file with given checksum
            return "CRJ"
    except socket.error:
         return False


def download_chunks(socket, chunk_no, checksum, tmp_paths):
    try:
        #sending chunk request
        msg_tosend = "FRQ " + str(chunk_no) + " " + str(checksum)
        socket.send(msg_tosend.encode())

        ret = socket.recv(4000).decode()

        # parsing received response and putting data into tmp files.
        if ret[:3] == "CHK":
            msg = ret[4:].strip().split("::")
            info = msg[0].strip().split(" ")
            chunk_no = int(info[0].strip())
            data = msg[1].strip()
            datalist =data[1:-1].split(",")
            intdatalist = list(map(int, datalist))
            chunk_data=bytearray(intdatalist)
            file_md5 = info[1].strip()

            #tmp dosyaya chunk datayı kaydet.
            fp = tempfile.NamedTemporaryFile(delete=False)
            tmp_paths[int(chunk_no)] = fp.name
            fp.write(chunk_data)
            fp.close()
            return tmp_paths, "CHK"
        else:
            return "CNO"
    except :
        return False


def self_introduce(ui_input, host_ip,host_port,fihrist,socketFihrist, host_uuid, logQueue):

    try:
        host_type = "P"
        # parsing the input
        info = ui_input.strip().split(" ")
        ip = info[0].strip()
        port = info[1].strip()

        # connecting to the specified peer
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((ip, int(port)))

        # self introducing
        first_msg = "HEL " + host_uuid + " " + host_ip + " " + str(host_port) + " " + host_type
        c.send(first_msg.encode())
        logQueue.put("Sending first introduce message.")

        # connected peer's response
        ret = c.recv(2000).decode()
        status = ret[4:]

        # taking conneted peer's uuid
        second_msg = "BOO " + host_uuid
        c.send(second_msg.encode())
        ret = c.recv(2000).decode().strip()
        uuid = ret[4:]

        # adding peer to peer fihrist
        peer_info = [ip, port, "OK", "S", str(time.ctime())]
        fihrist[uuid] = peer_info
        socketFihrist[uuid] = c

        # requesting peer's list
        newClientRequest = neg.clientRequest(c,host_ip, host_port, host_uuid,host_type, socketFihrist,fihrist,uuid, logQueue)
        newClientRequest.start()

        logQueue.put("First Registration Succeed!")

    except socket.error:
        logQueue.put("First Registration Connection Error!")
    except IndexError:
        logQueue( "First Registration Input Error!")
    return fihrist, socketFihrist


def filename_search(filename, soc, filelist):
    # sending file search by name request
    msg_tosend = "FSR " + filename
    soc.send(msg_tosend.encode())

    ret = soc.recv(4000).decode()

    # parsing received response and putting similar files in a file list
    if ret[:3] == "FLS":
        data = ret[4:].split("-")
        return_msg = "FLS"
        for item in range(len(data)):
            try:
                file = data[item].strip().split(">")
                checksum = file[0].strip()
                value = file[1].replace("[", "").replace("]", "").replace("'", "").strip().split(",")
                name = value[0]
                size = value[1]
                input = [name, size]
                filelist[checksum] = input
            except IndexError:
                return_msg = False
        return return_msg
    else:
        # no similar file received
        return "FNO"


def main():
    # fihrist of peers
    fihrist = {}
    # fihrist of peers' socket info
    socketFihrist = {}
    # start the logger thread
    lQueue = queue.Queue()
    lThread = neg.loggerThread("Logger", lQueue)
    lThread.start()

    # start listening
    s = socket.socket()
    host = "0.0.0.0"
    port = 12345
    h_type = "P"
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    s.listen(5)
    lQueue.put("Waiting for connection")

    #uuid = neg.get_uuid()
    uuid = "c'peer_trial'"

    # give unique name to all of the threads
    counter = 0

    # start automatic processes for peer control and list request
    newautoTask = neg.autoTask(socketFihrist, fihrist, uuid, host, port, h_type, lQueue)
    newautoTask.start()

    # peer's client side
    newClient = clientThread(host,port,fihrist,socketFihrist, lQueue,uuid)
    newClient.start()

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
                                   fihrist, socketFihrist, tQueue,
                                   lQueue, uuid)
        newwriteThread = neg.writeThread('WriteThread-' + str(counter),
                                     c,
                                     addr,
                                     fihrist, tQueue,
                                     lQueue, uuid)
        newreadThread.start()
        newwriteThread.start()

        counter += 1


if __name__ == '__main__':
    main()