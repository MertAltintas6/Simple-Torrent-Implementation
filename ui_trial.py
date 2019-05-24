from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
import threading
import time
import socket
import queue
import os, fcntl, struct
import sys
import tempfile
import negotiator_trial as neg
import file_methods as fmet

class Ui_Dialog(object):
    def setupUi(self, Dialog, host, port, socketFihrist, fihrist, lQueue ):
        Dialog.setObjectName("Dialog")
        Dialog.resize(641, 601)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(10, 160, 127, 97))
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.widget)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        self.filename_input = QtWidgets.QLineEdit(self.widget)
        self.filename_input.setObjectName("filename_input")
        self.verticalLayout_2.addWidget(self.filename_input)
        self.search_pushButton = QtWidgets.QPushButton(self.widget)
        self.search_pushButton.setObjectName("search_pushButton")
        self.search_pushButton.clicked.connect(lambda: self.getFileName())
        self.verticalLayout_2.addWidget(self.search_pushButton)
        self.widget1 = QtWidgets.QWidget(Dialog)
        self.widget1.setGeometry(QtCore.QRect(11, 11, 127, 145))
        self.widget1.setObjectName("widget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.widget1)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.widget1)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.ip_input = QtWidgets.QLineEdit(self.widget1)
        self.ip_input.setObjectName("ip_input")
        self.verticalLayout.addWidget(self.ip_input)
        self.label_3 = QtWidgets.QLabel(self.widget1)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.port_input = QtWidgets.QLineEdit(self.widget1)
        self.port_input.setObjectName("port_input")
        self.verticalLayout.addWidget(self.port_input)
        self.connect_pushButton = QtWidgets.QPushButton(self.widget1)
        self.connect_pushButton.setObjectName("connect_pushButton")
        self.connect_pushButton.clicked.connect(lambda: self.getIPPort())
        self.verticalLayout.addWidget(self.connect_pushButton)
        self.widget2 = QtWidgets.QWidget(Dialog)
        self.widget2.setGeometry(QtCore.QRect(150, 16, 481, 241))
        self.widget2.setObjectName("widget2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_6 = QtWidgets.QLabel(self.widget2)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_3.addWidget(self.label_6)
        self.file_listView = QtWidgets.QListView(self.widget2)
        self.file_listView.setObjectName("file_listView")
        self.verticalLayout_3.addWidget(self.file_listView)
        self.select_input = QtWidgets.QLineEdit(self.widget2)
        self.select_input.setObjectName("select_input")
        self.verticalLayout_3.addWidget(self.select_input)
        self.select_pushButton = QtWidgets.QPushButton(self.widget2)
        self.select_pushButton.setObjectName("select_pushButton")
        self.verticalLayout_3.addWidget(self.select_pushButton)
        self.select_pushButton.clicked.connect(lambda: self.getFile())
        self.widget3 = QtWidgets.QWidget(Dialog)
        self.widget3.setGeometry(QtCore.QRect(10, 270, 621, 202))
        self.widget3.setObjectName("widget3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget3)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_7 = QtWidgets.QLabel(self.widget3)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_4.addWidget(self.label_7)
        self.msg_listView = QtWidgets.QListView(self.widget3)
        self.msg_listView.setObjectName("msg_listView")
        self.verticalLayout_4.addWidget(self.msg_listView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_8 = QtWidgets.QLabel(self.widget3)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout.addWidget(self.label_8)
        self.msg_input = QtWidgets.QLineEdit(self.widget3)
        self.msg_input.setObjectName("msg_input")
        self.horizontalLayout.addWidget(self.msg_input)
        self.send_pushButton = QtWidgets.QPushButton(self.widget3)
        self.send_pushButton.setObjectName("send_pushButton")
        self.send_pushButton.clicked.connect(lambda: self.getMessage())
        self.horizontalLayout.addWidget(self.send_pushButton)
        self.update_pushButton = QtWidgets.QPushButton(self.widget3)
        self.update_pushButton.setObjectName("update_pushButton")
        self.update_pushButton.clicked.connect(lambda: self.showFihrist())
        self.horizontalLayout.addWidget(self.update_pushButton)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.widget4 = QtWidgets.QWidget(Dialog)
        self.widget4.setGeometry(QtCore.QRect(10, 480, 321, 111))
        self.widget4.setObjectName("widget4")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget4)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_9 = QtWidgets.QLabel(self.widget4)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_5.addWidget(self.label_9)
        self.downloads_listView = QtWidgets.QListView(self.widget4)
        self.downloads_listView.setObjectName("downloads_listView")
        self.verticalLayout_5.addWidget(self.downloads_listView)

        self.widget5 = QtWidgets.QWidget(Dialog)
        self.widget5.setGeometry(QtCore.QRect(341, 480, 280, 111))
        self.widget5.setObjectName("widget5")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget5)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_10 = QtWidgets.QLabel(self.widget5)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_6.addWidget(self.label_10)
        self.peers_listView = QtWidgets.QListView(self.widget5)
        self.peers_listView.setObjectName("peers_listView")
        self.verticalLayout_6.addWidget(self.peers_listView)

        self.socketFihrist = socketFihrist
        self.host = host
        self.port = port
        self.fihrist = fihrist
        self.lQueue = lQueue
        self.retranslateUi(Dialog)
        self.login = False
        self.msg_list = []

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Peer"))
        self.label_4.setText(_translate("Dialog",
                                        "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">FILE SEARCH</span></p></body></html>"))
        self.label_5.setText(_translate("Dialog", "<html><head/><body><p>File Name:</p></body></html>"))
        self.search_pushButton.setText(_translate("Dialog", "Search"))
        self.label.setText(_translate("Dialog",
                                      "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">CONNECTION</span></p></body></html>"))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p>IP Number:</p></body></html>"))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p>Port Number:</p></body></html>"))
        self.connect_pushButton.setText(_translate("Dialog", "Connect"))
        self.label_6.setText(_translate("Dialog",
                                        "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">FILE LIST</span></p></body></html>"))
        self.select_pushButton.setText(_translate("Dialog", "Select"))
        self.label_7.setText(_translate("Dialog",
                                        "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">MESSAGE BOX</span></p></body></html>"))
        self.label_8.setText(_translate("Dialog", "<html><head/><body><p>Your Message</p></body></html>"))
        self.send_pushButton.setText(_translate("Dialog", "Send"))
        self.update_pushButton.setText(_translate("Dialog", "Update List"))
        self.label_9.setText(_translate("Dialog",
                                        "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">DOWNLOADS</span></p></body></html>"))
        self.label_10.setText(_translate("Dialog",
                                        "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">PEERS</span></p></body></html>"))

    def getIPPort(self):
        ui_ip = self.ip_input.text()
        ui_port = self.port_input.text()
        #self.uuid = neg.get_uuid()
        self.uuid = "b'ui_peer'"
        if ui_ip and ui_port:
            # ui input for first registration
            ui_input = str(ui_ip)+ " " + str(ui_port)
            # starting peer's client side
            self.newClient = clientThread(self.host,self.port,ui_input, self.fihrist, self.socketFihrist, self.lQueue, self.uuid)
            self.newClient.start()
            # if first register is successful with ui_input, login will be true
            self.login = self.newClient.selfIntroduce()
            # displaying the first peer's info
            self.showFihrist()

    def getMessage(self):
        # if already registered
        if self.login:
            ui_message = self.msg_input.text()
            ui_uuid = ""
            indexes = self.peers_listView.selectedIndexes()
            for i in indexes:
                item = i.data().strip()
                data = item.split(":")
                ui_uuid = data[0].strip()
            # if peer is selected and message is entered
            if ui_uuid and ui_message:
                soc = self.socketFihrist[ui_uuid]
                self.newClient.sendMessage(soc,ui_message)

                msg_toshow = "SENDED to " + ui_uuid + " : " + ui_message
                self.showMessage(msg_toshow)

    def getFileName(self):
        # if already registered
        if self.login:
            ui_filename = self.filename_input.text()
            # searching file, if it is entered
            if ui_filename:
                filelist = self.newClient.fileSearch(ui_filename)
                # showing file search results
                model = QtGui.QStandardItemModel(self.file_listView)
                if filelist:
                    for checksum in filelist:
                        data = checksum + " : " + str(filelist[checksum])
                        item = QtGui.QStandardItem(data)
                        model.appendRow(item)
                else:
                    # if no file found, clear listview
                    model.clear()
                self.file_listView.setModel(model)

    def showMessage(self, message):
        if self.login:
            model = QtGui.QStandardItemModel(self.msg_listView)
            self.msg_list.append(message)
            for m in self.msg_list:
                item = QtGui.QStandardItem(m)
                model.appendRow(item)
                self.msg_listView.setModel(model)

    def getFile(self):
        if self.login:
            ui_checksum = ""
            indexes = self.file_listView.selectedIndexes()
            for i in indexes:
                item = i.data().strip()
                data = item.split(":")
                ui_checksum = data[0].strip()
            if ui_checksum:
                # display the selected checksum
                self.select_input.setText(ui_checksum)
                # downloading
                filename = self.newClient.download_file(ui_checksum)
                if filename:
                    # display downloaded files
                    model = QtGui.QStandardItemModel(self.downloads_listView)
                    for name in filename:
                        line = name + " downloaded succesfully"
                        item= QtGui.QStandardItem(line)
                        model.appendRow(item)
                    self.downloads_listView.setModel(model)

    def showFihrist(self):
        if self.login:
            # display peer list
            model = QtGui.QStandardItemModel(self.peers_listView)
            array = list(self.fihrist)
            for peer in array:
                line = peer + " : " + str(self.fihrist[peer])
                item = QtGui.QStandardItem(line)
                model.appendRow(item)
            self.peers_listView.setModel(model)


class serv_thread(threading.Thread):
    def __init__(self, host, port, lQueue, fihrist, socketFihrist, ui):
        threading.Thread.__init__(self)
        self.lQueue = lQueue
        self.fihrist = fihrist
        self.socketFihrist = socketFihrist
        self.host = host
        self.port = port
        self.ui = ui

    def run(self):
        # start the logger thread
        lThread = neg.loggerThread("Logger", self.lQueue)
        lThread.start()
        #self.uuid = neg.get_uuid()
        self.uuid = "b'ui_peer'"
        # peer type
        h_type = "P"
        # start automatic processes for peer control and list request
        newautoTask = neg.autoTask(self.socketFihrist, self.fihrist, self.uuid, host, port, h_type, self.lQueue)
        newautoTask.start()
        # start listening
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)
        self.lQueue.put("Waiting for connection")

        # give unique name to all of the threads
        counter = 0
        while True:
            # close the port gracefully
            try:
                c, addr = s.accept()
            except KeyboardInterrupt:
                s.close()
                self.lQueue.put('QUIT')

            self.lQueue.put('Got new connection from ' + str(addr))

            # start new write and read thread
            tQueue = queue.Queue()
            newreadThread = readThread('ReadThread-' + str(counter),
                                       c,
                                       addr,
                                       self.fihrist,
                                       self.socketFihrist,
                                       tQueue,
                                       self.lQueue,
                                       self.uuid, self.ui)
            newwriteThread = neg.writeThread('WriteThread-' + str(counter),
                                         c,
                                         addr,
                                         self.fihrist, tQueue,
                                         self.lQueue, self.uuid)
            newreadThread.start()
            newwriteThread.start()

            counter += 1


class readThread(neg.readThread):
    def __init__(self, name, clientSocket, addr, fihrist, socketFihrist, threadQueue, logQueue, uuid, ui):
        # using negotiator's readThread init function
        super().__init__(name, clientSocket, addr, fihrist, socketFihrist, threadQueue, logQueue, uuid)
        self.path_dir = "./Shared/"
        self.files = {}
        self.chunkSize = 512
        self.ui = ui

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
                msg_toshow = "RECEIVED from " + self.peer_uuid + " : "+ msg
                self.ui.showMessage(msg_toshow)
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
    def __init__(self, host, port,ui_input,  fihrist, socketFihrist, logQueue, uuid):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.ui_input=ui_input
        self.logQueue = logQueue
        self.fihrist = fihrist
        self.uuid = uuid
        self.socketFihrist = socketFihrist
        self.filelist = {}
        self.tmp_paths = []
        self.downloaded_files = []
        self.key = False

    def run(self):
        self.logQueue.put("Peer Client Thread Started.")

    def download_file(self, checksum):
        # list of peers that has a file with given checksum
        peerList = []
        self.meta_name = self.filelist[checksum][0]
        array = list(self.socketFihrist)
        for i in array:
            # searching in all peers with status OK
            if self.fihrist[i][3] == "P" and self.fihrist[i][2] == "OK":
                soc = self.socketFihrist[i]
                # for this checksum search file
                ret = checksum_search(soc, checksum, self.tmp_paths, self.key)
                #if this checksum exist, set created meta file, append socket to list
                if ret != False or ret != "CRJ":
                    self.tmp_paths = ret[0]
                    self.meta_name = ret[1]
                    peerList.append(soc)
                else :
                    pass
        # while meta file is not empty
        while os.stat(self.meta_name).st_size > 0 :
            for soc in peerList:
                newSearch = downloadFile(soc, self.tmp_paths, self.meta_name, checksum)
                newSearch.start()
                newSearch.join()
        # finally joining tmp files
        if not b'\0' in self.tmp_paths:
            if checksum in self.filelist.keys():
                fmet.joinFiles(self.filelist[checksum][0].strip(), self.tmp_paths, checksum)
                self.downloaded_files.append(self.filelist[checksum][0].strip())
                return self.downloaded_files

    def fileSearch(self, filename):

        # list of results returned from file search by name
        array = list(self.socketFihrist)
        for i in array:
            # searching in all peers with status OK
            if self.fihrist[i][3] == "P" and self.fihrist[i][2] == "OK":
                soc = self.socketFihrist[i]
                self.filelist = {}
                # searching by file name
                result = filename_search(filename, soc, self.filelist)
                if not result:
                    self.logQueue.put("Error while searching file from " + i)
                elif result == "FNO":
                    self.logQueue.put("No such file in this peer: " + i)
        # Show search list in UI
        return self.filelist

    def sendMessage(self, soc, message):
        try:
            # sending ui message message
            msg_tosend = "SAB " + message
            soc.send(msg_tosend.encode())
            # receiving return message
            ret = soc.recv(4000).decode().strip()

            if ret == "SOK":
                self.logQueue.put("Message is sended succesfully.")
            else:
                self.logQueue.put("Error while sending message.")
        except:
            self.logQueue.put("Connection error while sending message.")

    def selfIntroduce(self):

        try:
            host_type = "P"
            # parsing the input
            info = self.ui_input.strip().split(" ")
            peer_ip = info[0].strip()
            peer_port = info[1].strip()

            # connecting to the specified peer
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c.connect((peer_ip, int(peer_port)))

            # self introducing
            first_msg = "HEL " + self.uuid + " " + self.host + " " + str(self.port) + " " + host_type
            c.send(first_msg.encode())

            # connected peer's response
            ret = c.recv(2000).decode()
            status = ret[4:]

            # taking conneted peer's uuid
            second_msg = "BOO " + self.uuid
            c.send(second_msg.encode())
            ret = c.recv(2000).decode().strip()
            peer_uuid = ret[4:]

            #control if it is peer or server
            third_msg = "SAB Welcome dear peer"
            c.send(third_msg.encode())
            ret = c.recv(2000).decode().strip()
            if ret[:3] == "SOK":
                ty = "P"
            else:
                ty = "S"
            # adding peer to peer fihrist
            peer_info = [peer_ip, peer_port, "OK", ty, str(time.ctime())]
            fihrist[peer_uuid] = peer_info
            socketFihrist[peer_uuid] = c

            # requesting peer's list
            newClientRequest = neg.clientRequest(c, self.host, self.port, self.uuid, host_type, self.socketFihrist,
                                                 self.fihrist,
                                                 peer_uuid, self.logQueue)
            newClientRequest.start()

            self.logQueue.put("First Registration Succeed!")

        except socket.error:
            self.logQueue.put("First Registration Connection Error!")
            return False
        except IndexError:
            self.logQueue("First Registration Input Error!")
            return False
        return True


class downloadFile(threading.Thread):
    def __init__(self, soc, tmp_paths, meta_name, checksum):
        threading.Thread.__init__(self)
        self.soc = soc
        self.tmp_paths = tmp_paths
        self.meta_name = meta_name
        self.checksum = checksum
    def run(self):
        # open and read the meta file
        f = open(self.meta_name, "r")
        lines = f.readlines()
        f.close()
        # download given chunk data
        for line in lines:
            chunk_no = line.split(" ")[0]
            ret = download_chunks(self.soc, chunk_no, self.checksum, self.tmp_paths)
            if type(ret) == list:
                self.tmp_paths = ret[0]
                ret = ret[1]
            if ret != False and ret != "CNO":
                f = open(self.meta_name, "r")
                lines = f.readlines()
                f.close()

                f = open(self.meta_name, "w")
                # delete downloaded chunk from meta file
                for line in lines:
                    chunk = line.split(" ")[0]
                    if chunk_no != chunk.strip():
                        f.write(line)
                f.close()
                return True
            else:
                return False


def checksum_search(soc, checksum, tmp_paths, key):
    try:
        # sending file search by checksum request
        msg_tosend = "CSR " + checksum
        soc.send(msg_tosend.encode())

        ret = soc.recv(4000).decode()
        # receiving message and parsing
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
                noOfChunks, meta_name = fmet.createMeta(filename, checksum, int(size), chunkSize=512)
                key = True
                #chunkların sayısı kadar boş bir liste oluştur.
                tmp_paths = [b'\0'] * noOfChunks
            return tmp_paths, meta_name
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


if __name__ == '__main__':
    # logger queue
    lQueue = queue.Queue()
    # fihrist of peers
    fihrist = {}
    # fihrist of peers' socket info
    socketFihrist = {}
    #set host and port
    host = "0.0.0.0"
    port = 12346
    # starting ui
    app = QtWidgets.QApplication(sys.argv)
    my = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(my, host, port, socketFihrist, fihrist, lQueue)
    # starting server side
    serv = serv_thread(host, port, lQueue, fihrist, socketFihrist, ui)
    serv.start()
    my.show()
    sys.exit(my.exec_())





