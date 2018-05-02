from datetime import datetime
import calendar

def gz(filename = 'quine'):
    ### Create header data
    ## Static member data
    magic_num = 0x1f8b
    compression_method = 0x08 # defalte
    file_flags = 0x08 # accepts filename as extra field
    compression_flags = 0x00
    os_type = 0xff # unknown

    ## Find current time for date modified field
    current_time = datetime.utcnow()
    unix_time = calendar.timegm(current_time.utctimetuple())

    ## Concat members together by byte
    # Split members that are over a byte
    magic_num_bin = magic_num.to_bytes(2, byteorder='big')
    unix_time_bin = unix_time.to_bytes(4, byteorder='little')

    # Initialize standard header format
    head = [
        magic_num_bin[0],
        magic_num_bin[1],
        compression_method,
        file_flags,
        unix_time_bin[0],
        unix_time_bin[1],
        unix_time_bin[2],
        unix_time_bin[3],
        compression_flags,
        os_type
    ]

    # Append filename data
    for byte in filename.encode('utf-8'):
        head.append(byte)
    head.append(0x00) # zero terminate filename field

    ## Create header
    head_bytes = bytearray(head)

    return head_bytes

print(gz())
