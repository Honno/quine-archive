import io
import binascii
import bitstring

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
        data = head.append(body)
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
        """"Find respective fixed Huffman code for given length (RFC section 3.2.6.)"""

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

        return bitstring.Bits(uint=literal, length=bits)

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
