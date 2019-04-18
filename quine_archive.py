### Imports
## Standard library
import zlib
from datetime import datetime
import calendar
import io
import binascii

## External packages
import bitstring

### Main methods

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

    ### Create quine data
    data = _generic(head, '', zlib.compress(head), '')

    ### Write file
    _write_file(filename, 'gz', data)

### Helper methods

def _generic(head, tail, head_deflate, tail_deflate):
    """Implementation of Russ Cox's self-expanding Lempel-Ziv program"""

    ### Create self-expanding byte sequence
    ## Initialize buffer and program constants
    buf = QuineBuffer()
    UNIT = 5 # size of opcodes in bytes
    incremented_prefix_len = len(head) + UNIT
    incremented_suffix_len = len(tail) + UNIT

    ## P
    buf.write(head)

    ## L[P+1] P L[P+1]
    buf.lit(incremented_prefix_len)
    buf.write(head)
    buf.lit(incremented_prefix_len)

    ## R[P+1]
    buf.rep(incremented_prefix_len)

    ## L[1] R[P+1]
    buf.lit(UNIT)
    buf.rep(incremented_prefix_len)

    ## L[1] L[1]
    buf.lit(UNIT)
    buf.lit(UNIT)

	## L[4] R[P+1] L[1] L[1] L[4]
    buf.lit(4*UNIT)
    buf.rep(incremented_prefix_len)
    buf.lit(UNIT)
    buf.lit(UNIT)
    buf.lit(4*UNIT)

    ## R[4]
    buf.rep(4*UNIT)

    ## L[4] R[4] L[4] R[4] L[4]
    buf.lit(4*UNIT)
    buf.rep(4*UNIT)
    buf.lit(4*UNIT)
    buf.rep(4*UNIT)
    buf.lit(4*UNIT)

    ## R[4]
    buf.rep(4*UNIT)

    ## L[4] R[4] L[0] L[0] L[S+1]
    buf.lit(4*UNIT)
    buf.rep(4*UNIT)
    buf.lit(0)
    buf.lit(0)
    buf.lit(incremented_suffix_len)

    ## R[4]
    buf.rep(4*UNIT)

    ## L[0] L[0] L[S+1] R[S+1] S
    buf.lit(0)
    buf.lit(0)
    buf.lit(incremented_suffix_len)
    buf.rep(incremented_suffix_len)
    buf.lit(0)
    buf.write(tail_deflate)

    ## R[S+1]
    buf.rep(incremented_suffix_len)

    ## S
    buf.lit(0)
    buf.write(tail_deflate)

    return buf.bytes_array()

def _write_file(name, extension, data):
    filename = name + '.' + extension

    with open(filename, 'wb') as file:
        file.write(data)

### Utility class

class QuineBuffer:
    """Wrapper for bytes buffer that has utilities for creating quines"""

    def __init__(self):
        """Initialize bytes buffer and set final block to false"""

        self._bytes = io.BytesIO()
        self.final = False

    def write(self, data):
        """Write 8-bit int or bytes-like object to buffer"""

        if isinstance(data, int):
            if data < 2 ** 8:
                self._write(data.to_bytes(1, byteorder='big'))
            else:
                raise ValueError("Value given over a byte unsigned integer value")
        elif isinstance(data, bytes) or isinstance(data, bytearray):
            self._write(data)

    def _write(self, binary):
        """Write bytes-like object to buffer"""

        self._bytes.write(binary)

    def lit(self, n): # literal
        """Write a literal block to buffer"""

        ### Write block header
        ## Initialize bit array
        head = bitstring.BitArray()

        ## Define header
        head.append('0b1' if self.final else '0b0') # final block bit (BFINAL)
        head.append('0b00') # literal section (BTYPE)
        head = self._zero_pad(head) # zero padding to byte boundary

        ## Append header
        head_binary = head.int # integer representation
        self.write(head_binary)

        ### Write lengths
        ## Define data
        length = n.to_bytes(2, byteorder='big')
        nlength = self._ones_complement(length) # One's complement of len

        ## Write data
        self.write(length)
        self.write(nlength)

    def rep(self, n): # repeat
        """Write a repeat block to buffer"""

        ### Create block header
        ## Initialize bit array
        head = bitstring.BitArray()

        ## Define header
        head.append('0b1' if self.final else '0b0') # final block bit (BFINAL)
        head.append('0b01') # fixed huffman code (BTYPE)

        ### Create repeat opcodes
        ## Initialize bit array
        body = bitstring.BitArray()

        ## Get associated huffman code
        length = self._fixed_code(n / 2)
        distance = self._fixed_code(n)

        ## Append repeat opcode twice
        body.append(length)
        body.append(distance)
        body.append(length)
        body.append(distance)

        ### Write block
        ## Add everything together
        data = head + body
        data = self._zero_pad(data)

        ## Write to buffer
        self.write(data)

    def _ones_complement(self, binary):
        """Find one's complement of bytes given"""

        # Find number of bytes
        size = len(binary)

        # Convert binary to integer
        binary_int = int(binary.hex(), 16)

        # One's complement in integer form
        binary_int_swapped = binary_int ^ ((2 ** (size * 8))  - 1)

        # Return one's complement integer in bytes
        return binary_int_swapped.to_bytes(size, byteorder='big')

    def _fixed_code(self, length):
        """"Find respective fixed Huffman code for given length (Deflate RFC 3.2.6)"""

        if 0 <= length <= 143:
            literal = 0b00110000 + length
            bits = 8

        elif 144 <= length <= 255:
            literal = 0b110010000 + length - 144
            bits = 9

        elif 256 <= length <= 279:
            literal = 0b0000000 + length - 256
            bits = 7

        elif 280 <= length <= 287:
            literal = 0b11000000 + length - 280
            bits = 8

        else:
            raise ValueError("Only literal values between 0 and 287 are accepted")

        return bitstring.Bits(uint=int(literal), length=bits)

    def _zero_pad(self, binary):
        """Zero pad a given BitArray to byte boundary"""

        length = len(binary)
        zeroes_left = 8 - (length % 8)
        for _ in range(zeroes_left):
            binary.append('0b0')

        return binary

    def bytes_array(self):
        """Return bytes array"""

        return self._bytes.getvalue()
