#!/usr/bin/env python3

"""
A partial implementation of RFC 6455
http://tools.ietf.org/pdf/rfc6455.pdf
Brian Thorne 2012

TODO:
 - support long messages and multipacket frames
 - closing handshake
 - ping/pong
"""

import socket
import threading
import time
import base64
import hashlib
import textwrap
import select

# for python2:
import struct

def calculate_websocket_hash(key):
    magic_websocket_string = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    result_string = key + magic_websocket_string
    sha1_digest = hashlib.sha1(result_string).digest()
    response_data = base64.encodestring(sha1_digest).strip()
    response_string = response_data.decode('utf8')
    return response_string

def is_bit_set(int_type, offset):
    """
    >>> is_bit_set(1, 0)
    True
    >>> is_bit_set(2, 0)
    False
    >>> is_bit_set(0xFF, 2)
    True
    
    """
    mask = 1 << offset
    return not 0 == (int_type & mask)

def set_bit(int_type, offset):
    """
    >>> set_bit(2, 0)
    3
    """
    return int_type | (1 << offset)

def bytes_to_int(data):
    """Convert a bytes/str/list to int.
    
    >>> bytes_to_int(b"a0")
    24880
        
    Passed a list with null bytes:
        
    >>> bytes_to_int([97, 48])
    24880

    Passed a string:
    
    >>> bytes_to_int("a")
    97
    """
    # note big-endian is the standard network byte order
    try:
        return int.from_bytes(data, byteorder='big')
    except:
        # PYTHON2 HACK...
        if type(data) == str:
            return sum(ord(c) << (i * 8) for i, c in enumerate(data[::-1]))
        else:
            return sum(c << (i * 8) for i, c in enumerate(data[::-1]))


def int_to_bytes(number, bytesize):
    """Convert an integer to a bytearray. 
    
    The integer is represented as an array of bytesize. An OverflowError 
    is raised if the integer is not representable with the given number
    of bytes.
    
    >>> int_to_bytes(97, 1)
    bytearray(b'a')

    >>> int_to_bytes(159487778, 2)
    Traceback (most recent call last):
    ...
    OverflowError: Need more bytes to represent that number
    
    >>> int_to_bytes(159487778, 4) == bytearray([9, 129, 151, 34])
    True
    
    """
    try:
        return bytearray(number.to_bytes(bytesize, byteorder='big'))
    except:
        # PYTHON2 HACK...
        d = bytearray(bytesize)
        # Use big endian byteorder
        fmt = '!' + {1: 'b', 2: 'H', 4: 'L', 8: 'Q'}[bytesize]
        try:
            struct.pack_into(fmt, d, 0, number)
        except:
            raise OverflowError("Need more bytes to represent that number")
        return d


def pack(data):
    """pack bytes for sending to client"""
    frame_head = bytearray(2)

    # set final fragment
    frame_head[0] = set_bit(frame_head[0], 7)

    # set opcode 1 = text
    frame_head[0] = set_bit(frame_head[0], 0)

    # payload length
    if len(data) < 126:
        frame_head[1] = len(data)
    elif len(data) < ((2**16) - 1):
        # First byte must be set to 126 to indicate the following 2 bytes
        # interpreted as a 16-bit unsigned integer are the payload length
        frame_head[1] = 126
        frame_head += int_to_bytes(len(data), 2)
    elif len(data) < (2**64) -1:
        # Use 8 bytes to encode the data length
        # First byte must be set to 127
        frame_head[1] = 127
        frame_head += int_to_bytes(len(data), 8)

    # add data
    frame = frame_head + data.encode('utf-8')
    #print(list(hex(b) for b in frame))
    return frame

def receive(s):
    """blocking call to receive data from client"""
    
    # read the first two bytes
    frame_head = s.recv(2)
    
    # On severed connection
    if frame_head == '' or frame_head == b'':
        return
    
    # PYTHON2 HACK
    frame_head = bytearray(frame_head)

    # very first bit indicates if this is the final fragment
    #print("final fragment: ", is_bit_set(frame_head[0], 7))

    # bits 4-7 are the opcode (0x01 -> text)
    #print("opcode: ", frame_head[0] & 0x0f)

    # mask bit, from client will ALWAYS be 1
    #assert is_bit_set(frame_head[1], 7)

    # length of payload
    # 7 bits, or 16 bits, 64 bits
    payload_length = frame_head[1] & 0x7F
    if payload_length == 126:
        raw = s.recv(2)
        payload_length = bytes_to_int(raw)
    elif payload_length == 127:
        raw = s.recv(8)
        payload_length = bytes_to_int(raw)
    #print('Payload is {} bytes'.format(payload_length))

    """masking key
    All frames sent from the client to the server are masked by a
    32-bit nounce value that is contained within the frame
    """
    # PYTHON2 HACK
    masking_key = bytearray(s.recv(4))
    #print("mask: ", masking_key, bytes_to_int(masking_key))
    
    # finally get the payload data:
    bytes_received = 0
    masked_data_in = bytearray(payload_length)
    while bytes_received < payload_length:
        data_in = bytearray(s.recv(payload_length))
        #print "Received {} bytes".format(len(data_in))
        masked_data_in[bytes_received:bytes_received+len(data_in)] = data_in
        
        bytes_received += len(data_in)
    #print "Done received {} bytes".format(len(masked_data_in))
        
    data = bytearray(payload_length)

    # The ith byte is the XOR of byte i of the data with
    # masking_key[i % 4]
    for i, b in enumerate(masked_data_in):
        data[i] = b ^ masking_key[i%4]

    return data
    
class Websocket(object):
    """

    """

    def __init__(self, port, new_client_callback=None):
        self.port = port
        self.callback = new_client_callback
        

    def serve_forever(self, end=None):
        """
        end is an optional event to trigger server shutdown
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('', self.port))
        self.s.listen(1)

        # because socket.accept is blocking we use select for its timeout
        # so every second we check if "forever" is over.
    
        while True:
            r, w, e = select.select((self.s,), (), (), 1)
            for l in r:
                t, address = self.s.accept()
                print("Accepting connection from {}:{}".format(*address))
                threading.Thread(target=self.handle_connection, args = (t, )).start()
            else:
                # should we quit?
                if end is not None and end.is_set():
                    return
                    
    
    def transmit(self, msg_str):
        self.s.send(pack(msg_str))

    def handle_connection(self, s):
        client_request = s.recv(4096)
        key = None
        # get to the key
        for line in client_request.splitlines():
            #print(line.strip())
            if b'Sec-WebSocket-Key:' in line:
                key = line.split(b': ')[1]
                break
        if key is None:
            raise IOError("Couldn't find the key?\n\n", client_request)
        
        response_string = calculate_websocket_hash(key)

        header = '''HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: {}\r
\r
'''.format(response_string)
        
        s.send(header.encode())

        if self.callback is not None:
            self.callback(s)
        

    def __del__(self):
        self.s.close()


if __name__ == "__main__":
    import doctest
    doctest.testmod()