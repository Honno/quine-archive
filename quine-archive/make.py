import binascii
from datetime import datetime
import calendar

MAGIC_NUM = 0x1f8b
COMPRESSION_METHOD = 0x08 # defalte
FILE_FLAGS = 0x08 # accepts filename as extra field
COMPRESSION_FLAGS = 0x00
OS_TYPE = 0xff # unknown

def gz(filename = 'q'):
    ### Creating header data
    ## Find current time for date modified field
    current_time = datetime.utcnow()
    unix_time = calendar.timegm(current_time.utctimetuple()) # integer representation

    ## Concat members together by byte
    # Split members that are over a byte
    magic_num_bin = MAGIC_NUM.to_bytes(2, byteorder='big')
    unix_time_bin = unix_time.to_bytes(4, byteorder='little')

    # Initialize standard header format
    head = [
        magic_num_bin[0],
        magic_num_bin[1],
        COMPRESSION_METHOD,
        FILE_FLAGS,
        unix_time_bin[0],
        unix_time_bin[1],
        unix_time_bin[2],
        unix_time_bin[3],
        COMPRESSION_FLAGS,
        OS_TYPE
    ]

    # Append filename data
    for byte in filename.encode('utf-8'):
        head.append(byte)
    head.append(0x00) # zero terminate filename field

    print(head)

    return head

gz()
