### Imports
## Standard library
import zlib
from datetime import datetime
import calendar

## Internal
from . import flate
from . import buffers

def gz(filename = 'quine'):
    """Create a gzip quine"""

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
    head = bytearray(head)

    import pdb; pdb.set_trace()
    ### Create quine data
    data = _generic(head, '', flate.deflate(head), '')

    ### Write file
    _write_file(filename, 'gz', data)

def _generic(head, tail, head_deflate, tail_deflate):
    """Implementation of Russ Cox's self-expanding Lempel-Ziv program"""

    ### Create self-expanding byte sequence
    ## Initialize buffer and program constants
    buf = buffers.QuineBuffer()
    UNIT = 5 # size of opcodes in bytes
    incremented_prefix_len = len(head) + UNIT
    incremented_suffix_len = len(tail) + UNIT
    import pdb; pdb.set_trace()

    ## P
    buf.write(head)

    ## L[P+1] P L[P+1]
    buf.lit(incremented_prefix_len)
    buf.write(head)
    buf.lit(incremented_prefix_len)

    ## R[P+1]
    buf.rep(incremented_prefix_len)

    ## L[1] R[P+1]
    buf.lit(unit)
    buf.rep(incremented_prefix_len)

    ## L[1] L[1]
    buf.lit(unit)
    buf.lit(unit)

	## L[4] R[P+1] L[1] L[1] L[4]
    buf.lit(4*unit)
    buf.rep(incremented_prefix_len)
    buf.lit(unit)
    buf.lit(unit)
    buf.lit(4*unit)

    ## R[4]
    buf.rep(4*unit)

    ## L[4] R[4] L[4] R[4] L[4]
    buf.lit(4*unit)
    buf.rep(4*unit)
    buf.lit(4*unit)
    buf.rep(4*unit)
    buf.lit(4*unit)

    ## R[4]
    buf.rep(4*unit)

    ## L[4] R[4] L[0] L[0] L[S+1]
    buf.lit(4*unit)
    buf.rep(4*unit)
    buf.lit(0)
    buf.lit(0)
    buf.lit(incremented_suffix_len)

    ## R[4]
    buf.rep(4*unit)

    ## L[0] L[0] L[S+1] R[S+1] S
    buf.lit(0)
    buf.lit(0)
    buf.lit(incremented_suffix_len)
    buf.rep(incremented_suffix_len)
    buf.lit(0)
    buf.write(ztail)

    ## R[S+1]
    buf.rep(incremented_suffix_len)

    ## S
    buf.lit(0)
    buf.write(ztail)

    return buf.toBytesArray()

def _write_file(name, extension, data):
    filename = name + '.' + extension

    with open(filename, 'wb') as file:
        file.write(data)
