class ClaimData:

##signer doesnt change
    def __init__(self, v, r, s, msgHash, value, time, signer):
        self.v = v
        self.r = r
        self.s = s
        self.msgHash = msgHash
        self.value = value
        self.time = time
        self.signer = signer

        self.start_message = "["
        self.end_message = "]"

    def generate_string(self):

        return self.start_message + self.v + "," + self.r + "," + self.s + "," \
                   + self.msgHash + "," + str(self.value) + ","\
                   + str(self.time) + "," + self.signer + self.end_message
    


data = ClaimData("ox1c", "rrrrr", "ssssssssss", "hashhash", 12.2, 123123, "signersigner")
