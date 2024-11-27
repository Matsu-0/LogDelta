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
    
    def write(self, file_path: str, mode="wb", compressor = "lzma"):
        self.pack()
        with open(file_path, mode) as handle:
            if compressor == "lzma":
                self.byte_stream = lzma.compress(self.byte_stream)
            elif compressor == "gzip":
                self.byte_stream = gzip.compress(self.byte_stream)
            elif compressor == "zstd":
                self.byte_stream = zstd.compress(self.byte_stream)
            handle.write(self.byte_stream)


class newInArray:
    def __init__(self):
        self.byte_length: int = 8
        