import io
import binascii
import bitstring

### Wrapper for bytes buffer that has utilities for creating quines
class QuineBuffer:
    def __init__(self):
        self._bytes = io.BytesIO()
        self.final = False

    def write(self, data):
        if isinstance(data, int):
            if data < 2 ** 8:
                self._write(data.to_bytes(1, byteorder='big'))
            else:
                raise ValueError("Value given over a byte unsigned integer value")
        elif isinstance(data, bytes) or isinstance(data, bytearray):
            self._write(data)

    def _write(self, binary):
        self._bytes.write(binary)

    def lit(self, n): # literal
        """Write a literal block to buffer"""

        ### Write block header
        ## Initialize bit array
        head = bitstring.BitArray()

        ## Define header
        head.append('0b1' if self.final else '0b0') # final block bit (BFINAL)
        head.append('0b00') # literal section (BTYPE)
        head.append('0b00000') # zero padding to byte boundary

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

        ### Write block header
        ## Initialize bit array
        head = BitArray()

        ## Define header
        head.append('0b1' if self.final else '0b0') # final block bit (BFINAL)
        head.append('0b01') # fixed huffman code (BTYPE)

    def _ones_complement(self, binary):
        """Find one's complement of bytes given"""

        size = len(binary)
        binary_int = int(binary.hex(), 16)
        binary_int_swapped = binary_int ^ ((2 ** (size * 8))  - 1)
        return binary_int_swapped.to_bytes(size, byteorder='big')

    def bytes_array(self):
        return self._bytes.getvalue()
