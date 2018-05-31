import collections
from metainfo import Metainfo

EOF_CHAR = '\0'
STRING   = 0
INTEGER  = 1
D        = 2
E        = 3
L        = 4
EOF      = 5

NAMES   = [
    "STRING", "INTEGER", "D", "E",
    "L", "EOF"
]

class Token:
    def __init__(self, text, token_type):
        self.text = text
        self.type = token_type

class Parser:
    def __init__(self, program):
        self.program = program
        self.raw_info = None
        self.pos = -1
        self.nextch()

    def get_token(self):
        self.token = self.next_token()

    def match_token(self, type, message, it=True):
        if self.token.type != type:
            raise TypeError("%s. Found '%s'" % (message,
                            NAMES[self.token.type]))
        if it: self.get_token()
        

    def metainfo(self):
        self.token = self.next_token()
        if self.token.type == EOF:
            return
        bdict = collections.OrderedDict(self.bdict())
        # Save the raw bencoded info dictionary aswell as
        # the parsed one.
        bdict["raw_info"] = self.raw_info
        # Change the pieces string into a list.
        pieces = bdict["info"]["pieces"]
        pieces_list = []
        i = 0
        while i < len(pieces):
            pieces_list.append(pieces[i:i+20])
            i += 20
        bdict["info"]["pieces"] = pieces_list
        self.match_token(EOF, "expected end of file")
        return bdict
        
    def bdict(self):
        self.get_token()
        bdict = collections.OrderedDict()
        while True:
            if self.token.type == E:
                self.get_token()
                break
            self.match_token(STRING, "expected key(string)", False)
            key   = self.token.text
            self.get_token()
            value = self.value()
            bdict[key] = value
        return bdict

    def blist(self):
        self.get_token()
        blist = []
        while True:
            if self.token.type == E:
                self.get_token()
                break
            blist.append(self.value())
        return blist

    def value(self):
        if self.token.type == L:
            retval = self.blist()
        elif self.token.type == D:
            retval = self.bdict()
        elif self.token.type == STRING:
            retval = self.token.text
            self.get_token()
        elif self.token.type == INTEGER:
            retval = int(self.token.text)
            self.get_token()
        else:
            raise TypeError("expected value. Found '%s'" % (
                            NAMES[self.token.type]))
        return retval

    def nextch(self):
        self.pos += 1
        if self.pos >= len(self.program):
            self.ch = EOF_CHAR
        else:
            self.ch = chr(self.program[self.pos])
        return self.ch

    def next_token(self):
        if self.ch != EOF_CHAR:
            # self.skipws()
            if self.ch >= '0' and self.ch <= '9':
                return self.parse_string()
            if self.ch == 'i':
                return self.parse_integer()
            if self.ch == 'l':
                self.nextch()
                return Token('l', L)
            if self.ch == 'd':
                self.nextch()
                return Token('d', D)
            if self.ch == 'e':
                self.nextch()
                return Token('e', E)
            raise ValueError("unrecognized character: '%s'" % self.ch)
        return Token("EOF", EOF)

    
    def parse_string(self):
        buf = ""
        num = int(self.number())
        pos = 0
        self.nextch()
        while pos < num:
            buf += self.ch
            self.nextch()
            pos += 1
        if buf == "info":
            self.raw_info = self.program[self.pos:-1]
        return Token(buf, STRING)

    def parse_integer(self):
        self.nextch()
        token = Token(self.number(), INTEGER)
        self.nextch()
        return token

    def number(self):
        buf = ""
        while self.ch >= '0' and self.ch <= '9':
            buf += self.ch
            self.nextch()
        return buf

    """
    def skipws(self):
        while self.ch == '\t' or self.ch == ' ' or \
              self.ch == '\r' or self.ch == '\n': self.nextch()
    """
