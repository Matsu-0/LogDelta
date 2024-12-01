import lzma
import gzip
import zstandard as zstd

class newOutArray:
    def __init__(self):
        self.byte_length: int = 8
        self.byte_stream: bytearray = bytearray()
        self.current_bits: int = 0
        self.bit_count: int = 0
    
    def flush(self):
        while self.bit_count >= self.byte_length:
            self.byte_stream.append(self.current_bits >> (self.bit_count - self.byte_length))
            self.current_bits &= (1 << (self.bit_count - self.byte_length)) - 1
            self.bit_count -= self.byte_length


    def encode(self, data: int, bit_len: int = 8):
        data &= (1 << bit_len) - 1
        self.current_bits << bit_len
        self.current_bits |= data
        self.bit_count += bit_len
        self.flush()
    
    def pack(self):
        self.flush()
        if self.bit_count > 0:
            self.byte_stream.append(self.current_bits << (self.byte_length - self.bit_count))
            self.current_bits = 0
            self.bit_count = 0
    
    def length(self):
        self.pack()
        return len(self.byte_stream)
    
    def write(self, file_path: str, mode="wb", compressor = "none"):
        self.pack()
        # print(self.length())
        with open(file_path, mode) as handle:
            if compressor == "lzma":
                comp_stream = lzma.compress(self.byte_stream)
            elif compressor == "gzip":
                comp_stream = gzip.compress(self.byte_stream)
            elif compressor == "zstd":
                comp_stream = zstd.compress(self.byte_stream)
            elif compressor == "none":
                comp_stream = self.byte_stream
            else:
                print("This general compressor is not currently supported, or the compressor name is wrong. lzma is automatically used for compression.")
                comp_stream = lzma.compress(self.byte_stream)
            handle.write(comp_stream)
            # print(len(comp_stream))


class newInArray:
    def __init__(self):
        self.byte_length: int = 8
        