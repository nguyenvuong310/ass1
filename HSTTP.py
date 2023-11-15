MAX_HEADERS_SIZE = 10 # max header size for length

# get data length in bytes, then padding its size to MAX_HEADERS_SIZE,
# finally, return
def getDataLengthInBytes(data) -> bytes:
    if not isinstance(data, bytes):
        raise TypeError("data need to be in bytes!")
    
    length = bytes(str(len(data)), "utf8") # get length of data in bytes
    len_diff = MAX_HEADERS_SIZE - len(length) # get different
    length +=  bytes("\0" * len_diff, "utf8") # then padding
    #print("length: ", length)
    return length

class HSTTP:
    # Type:
    # 0: open connection, 1: inform, 2: fetch, 3: response fetch, 4: request file, 
    # 5: send file, 6: end file, 7: discover, 8: ping, 9: online
    def __init__(self):
        pass

    def encode(self, hostname, type, source = None, payload = None, p1 = None, p2 = None):
        self.hostname = hostname
        self.sourceSocket = source
        self.type = type
        self.p1 = p1
        self.p2 = p2
        self.payload = payload

    def openConnection(self, data = "", sender = "", source: tuple = None):
        # this packet contains socket instance between client-server
        self.encode(hostname = sender, type = 0,
                    source = source, payload = data)

    def inform(self, data, sender = "", source: tuple = None): #thông báo cho server client có những file nào
        self.encode(hostname = sender, type = 1, 
                    source = source, payload = data)

    def fetch(self, fname, sender = "", source: tuple = None):
        self.encode(hostname = sender, type = 2, 
                    source = source, payload = fname)

    def responseFetch(self, peerAddr, targetPeerName: str = "unknown", sender = "", source: tuple = None):
        self.encode(hostname = sender, type = 3, 
                    source = source, payload = [targetPeerName, peerAddr])
        pass

    def requestFile(self, fname, sender = "", source: tuple = None):
        self.encode(hostname = sender, type = 4, 
                    source = source, payload = fname)

    def sendFile(self, data, sender = "", source = None):
        self.encode(hostname = sender, type = 5, 
                    source = source, payload = data)
    
    def endFile(self, sender = "", source = None):
        self.encode(hostname = sender, type = 6)

    def discover(self, sender = "", source = None):
        self.encode(hostname = sender, type = 7)

    def ping(self, sender = "", source = None):
        self.encode(hostname = sender, type = 8)

    def responsePing(self, sender = "", source = None):
        self.encode(hostname = sender, type = 9)