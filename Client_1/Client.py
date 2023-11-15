import socket, os, time, threading, sys, pickle
sys.path.append(os.path.abspath(
                    os.path.join(os.getcwd(), os.pardir)))
from HSTTP import *
TIME = 1
class Client:
    def __init__(self, maxPeers, serverSocket: tuple = ("127.0.0.1", 8000), 
                 clientSocket: tuple = ("127.0.1.1", 8001), hostname = "client1"):
        
        self.PATH = os.getcwd() + "/Repository/"
        self.chunksize = 1024
        self.chosenFileName = "file.txt"
        self.hostname = hostname #socket.gethostname()
        
        self.threadList = []
        self.stop = False

        self.SERVER_SOCKET = serverSocket

        #self.CLIENT_SOCKET = clientSocket #(socket.gethostbyname(self.hostname), 8002)
        self.CLIENT_SOCKET = None

        self.PEERS_SOCKETS = [] # [(ip, port),...]

        self.MAX_PEERS = maxPeers

        # server_socket: socket at server side
        # client_peer (socket): socket at client (this host) side
        # peer_client (socket): socket at peer (client connecting to this host) side

        self.server_socket = None

        self.client_peer = None

        self.peer_client = None
        
        self.listenThread = []

    #==================================
    def connectServer(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        #self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,1)
        print(f'connecting to %s port ' + str(self.SERVER_SOCKET))
        self.server_socket.connect(self.SERVER_SOCKET)

        self.listenThread.append(
            threading.Thread(target = self.listenHosts, args = (True,))) # listen server
        self.listenThread[-1].start()

        packet = HSTTP()
        packet.openConnection(sender = self.hostname, 
                              source = socket.gethostbyname(socket.gethostname()))
        self.sendToHost(packet, self.server_socket)
        time.sleep(TIME) # wait for a second

    def publish(self, fname, allFile = False):
        if self.server_socket == None:
            print("You need to connect to server first!")
            return

        msg = ""
        if allFile:
            listFile = os.listdir(self.PATH)
            for file in listFile:
                msg += file + " "
        else:
            msg = fname

        packet = HSTTP()
        packet.inform(data = msg, sender = self.hostname, 
                      source = self.CLIENT_SOCKET)
        self.sendToHost(packet, self.server_socket)

    def fetch(self, fname):
        if self.server_socket == None or self.client_peer == None:
            print("server_socket: ", self.server_socket, "\n")
            print("client_socket: ", self.client_peer, "\n")
            
            print("You need to connect to server first!")
            return

        self.chosenFileName = fname
        packet = HSTTP()
        listfile = os.listdir(os.getcwd()+"/Repository")
        for file in listfile:
            if file == fname:
                print(fname,"has already existed in client's repository")
                return 0
        # firstly, fetch
        initLength = len(self.PEERS_SOCKETS) # get the initial length of PEERS_ADDRESS
        packet.fetch(fname, sender = self.hostname, 
                     source = self.CLIENT_SOCKET)
        self.sendToHost(packet, self.server_socket)

        # then, wait for changes in length of PEERS_ADDRESS (means that client has received response message)
        while len(self.PEERS_SOCKETS) - initLength <= 0:
            pass

        #self.connectToPeers(self.PEERS_SOCKETS[-1]) # connect to peer
        for peer_socket in self.PEERS_SOCKETS[-1]: # concurrenly connect to public and private peer addr
            try:
                self.connectToPeers(peer_socket)
            except:
                continue
            else:
                break

        # thirdly, send a request to download file from target peer,
        # including client address
        packet.requestFile(fname = fname, source = self.CLIENT_SOCKET)
        self.sendToHost(packet, self.peer_client)

        # finally, wait for transfering
        time.sleep(TIME)
        
        if os.path.exists(self.PATH + fname):
            return True
        else:
            return False
    #==================================

    def handleMessage(self, packet, acceptParams: tuple):
        host, _ = acceptParams
        
        if packet is not None and type(packet) is HSTTP:
            if packet.type == 0: # open connection
                self.CLIENT_SOCKET = (socket.gethostbyname(socket.gethostname()), 
                                      packet.payload[1]) # (local ip, ex)

                self.client_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_peer.setsockopt(socket.SOL_SOCKET, 
                                            socket.SO_REUSEADDR, 1)
                self.client_peer.bind(self.CLIENT_SOCKET)
                self.client_peer.listen(self.MAX_PEERS)

                self.listenThread.append(
                    threading.Thread(target = self.listenHosts, args = (False,))) # listen peers
                self.listenThread[-1].start()
                #print("client: ", self.client_peer)
            elif packet.type == 3: # response fetch
                # payload format for response fetch: "[self.hostname, (public addr, private addr)]"
                self.PEERS_SOCKETS.append(packet.payload[1])
            elif packet.type == 4: # request file
                source, requestedFname = packet.sourceSocket, packet.payload
                # if client receive this message, this means that some
                # peer want to create a connection to this client
                self.connectToPeers(source)

                # begin sending file to the target peer
                targetFname = self.PATH + requestedFname
                sendingPacket = HSTTP()
                print("sending: ", requestedFname)
                with open(targetFname, "rb") as f:
                    #size = os.path.getsize(targetFname)
                    chunk = f.read(self.chunksize) # read file in chunk
                    while chunk:
                        sendingPacket.sendFile(chunk, source = self.CLIENT_SOCKET)
                        self.sendToHost(sendingPacket, self.peer_client)
                        chunk = f.read(self.chunksize)
                
                print("finish sending")
                # send an "end file" signal
                sendingPacket.endFile()
                self.sendToHost(sendingPacket, self.peer_client)
            elif packet.type == 5: # "send file" message
                # this type of messages contains requested file
                with open(self.PATH + self.chosenFileName, "wb") as f:
                    # if client receive None/type != 5 packet more than 
                    # countNone times it stops listening
                    countNone = 3
                    
                    while countNone > 0:
                        if packet.type == 6: # check for end file message
                            break
                        else: # else, continue to write
                            if packet.payload:
                                f.write(packet.payload)
                            countNone = 3

                        l = host.recv(MAX_HEADERS_SIZE)
                        # decode and remove null
                        length = l.decode("utf8").replace("\x00", "")
                        
                        if length:
                            data = host.recv(int(length))

                            if data is not None:
                                packet = pickle.loads(data)

                        # if client receive None/type != 5 packet more 
                        # than countNone times it stops listening
                        if packet is None or packet.type != 5:
                            countNone -= 1
                            continue
            elif packet.type == 7: # discover message
                self.publish(fname = None, allFile = True)
            elif packet.type == 8: # ping message
                print("Someone say hi to me!")
                sendingPacket = HSTTP()
                sendingPacket.responsePing(sender = self.hostname)
                self.sendToHost(sendingPacket, self.server_socket)
    
    def chooseFileName(self): 
        # this function is to choose custom filename
        self.chosenFileName = "file.txt" # GUI here

    def sendToHost(self, data, socket: socket.socket):
        encodedData = pickle.dumps(data)
        socket.sendall(getDataLengthInBytes(encodedData))
        socket.sendall(encodedData)

    def stopListen(self):
        self.stop = True

    def listenHosts(self, isServer = False):
        self.stop = False
        if isServer:
            while not self.stop:
                #server, addr = self.server_socket.accept()
                server = self.server_socket
                
                l = server.recv(MAX_HEADERS_SIZE)
                # decode and remove null
                length = l.decode("utf8").replace("\x00", "")

                packet = None
                if length:
                    data = server.recv(int(length))

                    if data is not None:
                        packet = pickle.loads(data)
                
                self.handleMessage(packet, (server, None))
        else:
            self.remaining = self.MAX_PEERS
            while self.remaining > 0 or not self.stop:
                acceptParams = self.client_peer.accept()
                
                # create new thread
                self.threadList.append(
                    threading.Thread(
                        target = self.onNewPeers, 
                        args = (acceptParams,)
                    )
                )
                self.threadList[-1].start()

                self.remaining -= 1

            self.client_peer.close()

    def onNewPeers(self, acceptParam):
        client, addr = acceptParam

        try:
            print('Connected by', addr)
            while True:
                l = client.recv(MAX_HEADERS_SIZE)
                # decode and remove null
                length = l.decode("utf8").replace("\x00", "")

                packet = None
                if length:
                    data = client.recv(int(length))

                    if data is not None:
                        packet = pickle.loads(data)

                self.handleMessage(packet, acceptParam)
        finally:
            client.close()
            self.remaining += 1

    def connectToPeers(self, addr): # addr: (TARGET CLIENT, TARGET PORT)
        PEER, PORT_P = addr

        self.peer_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_address = (PEER, PORT_P)
        print(f'connecting to %s port ' + str(peer_address))
        self.peer_client.connect(peer_address)

# client = Client(10, serverSocket = ("116.109.187.234", 1234),
#                 clientSocket = ("192.168.1.8", 1234))
client = Client(10, serverSocket = ("192.168.56.1", 1234))
#client = Client(10)
client.connectServer()

client.publish(fname = None, allFile= True)
#client.publish("file3.txt")
#client.publish("file1.txt")
#client.publish("avatar.jpg")
#client.publish("songa.txt")
#client.fetch("file3.txt")
#os.system("pause")