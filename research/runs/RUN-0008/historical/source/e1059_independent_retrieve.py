#!/usr/bin/env python3
"""Independent clean-room reimplementation of the frozen OutGuess 0.13 retrieval path.

This module intentionally does not import or call e1058_retrieve.py.  It uses a
separate RC4 state representation and generator-based position scheduler.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

MASK=0xff

def md5(data: bytes) -> bytes:
    return hashlib.md5(data).digest()

class StreamCipher:
    def __init__(self, label: bytes, key: bytes):
        self.box = bytearray(range(256))
        self.x = 0
        self.y = 0
        self._mix(md5(label + key))

    def clone(self):
        c = object.__new__(StreamCipher)
        c.box = self.box.copy(); c.x=self.x; c.y=self.y
        return c

    def _next(self) -> int:
        self.x=(self.x+1)&MASK
        a=self.box[self.x]
        self.y=(self.y+a)&MASK
        b=self.box[self.y]
        self.box[self.x],self.box[self.y]=b,a
        return self.box[(a+b)&MASK]

    def _mix(self, material: bytes) -> None:
        self.x=(self.x-1)&MASK
        L=len(material)
        for t in range(256):
            self.x=(self.x+1)&MASK
            a=self.box[self.x]
            self.y=(self.y+a+material[t%L])&MASK
            self.box[self.x],self.box[self.y]=self.box[self.y],a

    def word_be(self) -> int:
        return (self._next()<<24)|(self._next()<<16)|(self._next()<<8)|self._next()

    def xor(self, data: bytes) -> bytes:
        return bytes(b ^ self._next() for b in data)

    def reseed16le(self, value: int) -> None:
        self._mix(bytes((value & 255, (value >> 8) & 255)))

class PositionSchedule:
    def __init__(self, key: bytes):
        self.modulus=32
        self.prng=StreamCipher(b'Seeding',key)
        self.position=self.prng.word_be()%self.modulus

    def advance(self) -> int:
        self.position += self.prng.word_be()%self.modulus + 1
        return self.position

    def add_seed(self, seed: int) -> None:
        self.prng.reseed16le(seed)

    def retune(self, total_bits: int, bytes_left: int) -> None:
        x=total_bits
        y=x-self.position
        x32=x//32
        factor=2.0 if y>x32 else 2.0-(x32-y)/float(x32)
        self.modulus=max(1,int(factor*y/(8*bytes_left)))

def get_bitmap_bit(buf: bytes, index: int) -> int:
    return (buf[index//8] >> (index%8)) & 1

def extract_little_endian_byte(buf: bytes, nbits: int, schedule: PositionSchedule) -> int:
    result=0
    pos=schedule.position
    for bitno in range(8):
        if pos>=nbits:
            raise EOFError({'position':pos,'usable_bits':nbits})
        result |= get_bitmap_bit(buf,pos)<<bitno
        pos=schedule.advance()
    return result

def retrieve(bitmap_path: Path):
    packed=bitmap_path.read_bytes()
    nbits=int(Path(str(bitmap_path)+'.meta').read_text().strip())
    key=b'Default key'
    crypt=StreamCipher(b'Encryption',key)
    body_decoder=crypt.clone()
    schedule=PositionSchedule(key)

    raw_header=bytes(extract_little_endian_byte(packed,nbits,schedule) for _ in range(4))
    decoded_header=crypt.xor(raw_header)
    seed=int.from_bytes(decoded_header[:2],'little')
    requested=int.from_bytes(decoded_header[2:],'little')
    schedule.add_seed(seed)

    raw_body=bytearray()
    err=None
    left=requested
    while left:
        try:
            schedule.retune(nbits,left)
            raw_body.append(extract_little_endian_byte(packed,nbits,schedule))
        except Exception as exc:
            err=repr(exc)
            break
        left-=1
    output=body_decoder.xor(bytes(raw_body))
    meta={
      'bitmap':bitmap_path.name,'usable_bits':nbits,
      'raw_header_hex':raw_header.hex(),'decoded_header_hex':decoded_header.hex(),
      'seed':seed,'declared_length':requested,'recovered_length':len(output),
      'missing_bytes':requested-len(output),'complete':len(output)==requested,
      'final_iterator_offset':schedule.position,'capacity_margin_bits':nbits-schedule.position,
      'error':err,'output_sha256':hashlib.sha256(output).hexdigest(),
      'raw_sha256':hashlib.sha256(raw_body).hexdigest()
    }
    return output,bytes(raw_body),meta

def main():
    ap=argparse.ArgumentParser();ap.add_argument('bitmap',type=Path);ap.add_argument('--page',type=int,required=True);ap.add_argument('--outdir',type=Path,required=True)
    a=ap.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    out,raw,meta=retrieve(a.bitmap)
    stem=f'page_{a.page:02d}'; suffix='' if meta['complete'] else '.partial'
    (a.outdir/f'{stem}{suffix}.out').write_bytes(out)
    (a.outdir/f'{stem}{suffix}.raw').write_bytes(raw)
    (a.outdir/f'{stem}.extraction.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta,sort_keys=True))
if __name__=='__main__': main()
