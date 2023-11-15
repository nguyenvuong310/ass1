import socket, threading, pickle, sys, os, time
sys.path.append(os.path.abspath(
                    os.path.join(os.getcwd(), os.pardir)))
from HSTTP import *

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

TIME = 1
class Server:
    def __init__(self, maxConnection, pathToTrackFname, serverSocket = ("127.0.0.1", 8000)):
        self.pathToTrackFname = pathToTrackFname
        self.clientAddr = {} # {"hostname": <host socket>} - this store client socket side
        
        # below store client socket side when connect to the server,
        # note that those sockets are differnt from clientAddr because
        # it is created due to connection, 
        # client not "actively" binded it
        self.clientInterface = {}

        self.maxConnection = maxConnection
        self.threadList = []
        self.stop = False

        self.server_socket = serverSocket

        # server_socket: socket at server side

        self.server_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_client.bind(self.server_socket)
        self.server_client.listen(self.maxConnection)
        self.server_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # self.threadList.append(
        #     threading.Thread(target = self.listenClients)
        # )
        # self.threadList[0].start()

    #==================================
    def discover(self, hostname):
        packet = HSTTP()
        packet.discover()
        try:
            self.sendToHost(packet, self.clientInterface[hostname])
            time.sleep(TIME) #wait for update tracked file
            return True
        except:
            return False
    def ping(self, hostname):
        packet = HSTTP()
        packet.ping()
        try:
            self.sendToHost(packet, self.clientInterface[hostname])
            return True
        except:
            return False
    #==================================

    def handleMessage(self, packet: HSTTP, senderSocket: socket.socket = None):
        client, addr = senderSocket

        if packet is not None and type(packet) is HSTTP:
            print(packet.hostname, ": ", client)
            if packet.type == 0: # open connection
                #print("open: ", packet.hostname)
                tempPack = HSTTP()
                tempPack.openConnection(data = addr) # send back new socket instance 
                self.sendToHost(tempPack, client)

                self.clientAddr.update({packet.hostname: (addr, (packet.sourceSocket, addr[1]))}) # store identity of sender (public ip, private ip)
                self.clientInterface.update({packet.hostname: client})
            elif packet.type == 1: # inform
                fname = packet.hostname + ".txt" # file track name
                fileInformed = packet.payload.split(" ")

                # # read tracked file
                # trackedFile = None
                # if os.path.exists(fname):
                #     with open(fname, "r") as f:
                #         trackedFile = f.read().split(" ")

                # # write to tracked file
                # with open(fname, "a") as f:
                #     for file in fileInformed:
                #         if trackedFile is not None and file not in trackedFile:
                #             f.write(file + " ")
                if os.path.exists(fname):
                    if packet.payload.endswith(" ") or packet.payload == "" : #publish all or no file => reset tracked file
                        f = open(fname,"r+")
                        f.truncate(0)
                        f.close()
                        f = open(fname,"w")
                        f.write(packet.payload) #no need " " because the payload has already had
                    else :                      #publish 1 file and update => only update the tracked file
                        f = open(fname,"a+")     
                        if packet.payload not in f.read().split(" "):
                            f.write(packet.payload + " ") #need " " because the payload only 1 file and no " "
                else:
                    print("Tracked file doesn't exist !")
                    return 0    
                    
                print(packet.hostname + ": " + packet.payload)
            elif packet.type == 2: #fetch
                listFile = os.listdir(self.pathToTrackFname)
                for file in listFile:
                    if file.endswith(".txt") and self.ping(file.split(".")[0]): # read each tracked file and client must be online
                        with open(file, "r") as f:
                            # if request file found in some clients
                            if packet.payload in f.read().split(" "):
                                tempPack = HSTTP()
                                tempPack.responseFetch(
                                    # send target identity in the response message
                                    self.clientAddr[file.split(".")[0]]
                                )
                                print("fetch: ", 
                                      self.clientAddr[file.split(".")[0]])
                                self.sendToHost(tempPack, client)
                                break
            elif packet.type == 9: # online
                if packet.hostname is None:
                    packet.hostname = "Target client"
                print(packet.hostname + " is online!")
                                
    def sendToHost(self, data, socket: socket.socket):
        if socket is None:
            raise TypeError("socket must not be null!")
        encodedData = pickle.dumps(data)
        socket.sendall(getDataLengthInBytes(encodedData))
        socket.sendall(encodedData)

    def stopListen(self):
        self.stop = True

    def listenClients(self):
        self.remaining = self.maxConnection #remaining là số client còn lại chưa được kết nối
        self.stop = False
        while self.remaining > 0 or not self.stop:
            acceptParams = self.server_client.accept()

            # create new thread
            self.threadList.append(
                threading.Thread(target = self.onNewClient, 
                                 args = (acceptParams,)))
            self.threadList[-1].start()

            self.remaining -= 1
        
        self.server_client.close()
    #đọc tín hiệu từ client
    def onNewClient(self, acceptParam: tuple): # acceptParam: (client, addr)
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

serverIP = socket.gethostbyname(socket.gethostname())
print("Server address: ", serverIP)
server = Server(3, "./", serverSocket = (serverIP, 1234))
#server = Server(2, "./")

thread = threading.Thread(target = server.listenClients, args = ())
thread.start()

  
#input("press anything to continue..\n")
# server.discover("client1")
# server.discover("client2")
#server.ping("client1")
# server.ping("client2")