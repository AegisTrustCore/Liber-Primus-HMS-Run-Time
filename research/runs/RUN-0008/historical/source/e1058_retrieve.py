#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json

class ARC4:
    def __init__(self): self.s=list(range(256)); self.i=0; self.j=0
    def copy(self):
        o=ARC4();o.s=self.s.copy();o.i=self.i;o.j=self.j;return o
    def getbyte(self):
        self.i=(self.i+1)&255;si=self.s[self.i];self.j=(self.j+si)&255;sj=self.s[self.j]
        self.s[self.i],self.s[self.j]=sj,si;return self.s[(si+sj)&255]
    def getword(self):return (self.getbyte()<<24)|(self.getbyte()<<16)|(self.getbyte()<<8)|self.getbyte()
    def addrandom(self,dat:bytes):
        self.i=(self.i-1)&255
        for n in range(256):
            self.i=(self.i+1)&255;si=self.s[self.i];self.j=(self.j+si+dat[n%len(dat)])&255
            self.s[self.i],self.s[self.j]=self.s[self.j],si
    @classmethod
    def initkey(cls,typ:bytes,key:bytes):
        import hashlib
        a=cls();a.addrandom(hashlib.md5(typ+key).digest());return a

def bit_at(buf:bytes,i:int):return (buf[i>>3]>>(i&7))&1
class Iterator:
    def __init__(self,key:bytes):
        self.skipmod=32;self.arc=ARC4.initkey(b'Seeding',key);self.off=self.arc.getword()%self.skipmod
    def next(self):self.off+=self.arc.getword()%self.skipmod+1;return self.off
    def seed(self,seed:int):self.arc.addrandom(bytes((seed&255,(seed>>8)&255)))
    def adapt(self,total_bits:int,datalen:int):
        x=total_bits;y=total_bits-self.off;x32=x//32
        adj=2.0 if y>x32 else 2.0-(x32-y)/float(x32)
        self.skipmod=max(1,int(adj*y/(8*datalen)))
def retrbyte(bits:bytes,total:int,it:Iterator,n=8):
    i=it.off;v=0
    for where in range(n):
        if i>=total:raise EOFError((i,total))
        v|=bit_at(bits,i)<<where;i=it.next()
    return v

def retrieve(bitmap:Path):
    bits=bitmap.read_bytes();total=int(Path(str(bitmap)+'.meta').read_text());key=b'Default key'
    enc=ARC4.initkey(b'Encryption',key);decode=enc.copy();it=Iterator(key)
    raw_header=bytes(retrbyte(bits,total,it) for _ in range(4));header=bytes(x^enc.getbyte() for x in raw_header)
    seed=header[0]|header[1]<<8;declared=header[2]|header[3]<<8;it.seed(seed)
    raw=bytearray();remaining=declared;error=None
    while remaining:
        try:it.adapt(total,remaining);raw.append(retrbyte(bits,total,it))
        except Exception as exc:error=repr(exc);break
        remaining-=1
    out=bytes(x^decode.getbyte() for x in raw)
    return out,bytes(raw),{
      'bitmap':bitmap.name,'usable_bits':total,'raw_header_hex':raw_header.hex(),'decoded_header_hex':header.hex(),
      'seed':seed,'declared_length':declared,'recovered_length':len(out),'missing_bytes':declared-len(out),
      'complete':len(out)==declared,'final_iterator_offset':it.off,'capacity_margin_bits':total-it.off,
      'error':error,'output_sha256':hashlib.sha256(out).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('bitmap',type=Path);ap.add_argument('--page',required=True,type=int);ap.add_argument('--outdir',required=True,type=Path)
    a=ap.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    out,raw,meta=retrieve(a.bitmap);stem=f'page_{a.page:02d}'
    suffix='' if meta['complete'] else '.partial'
    (a.outdir/f'{stem}{suffix}.out').write_bytes(out);(a.outdir/f'{stem}{suffix}.raw').write_bytes(raw)
    (a.outdir/f'{stem}.extraction.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta))
if __name__=='__main__':main()
