#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Package approved aligned Maple frames into native veadotube mini2.2.
Source pixels are serialized losslessly as RAW.; art editing is performed only
by create_expression_patches.py. Format references are linked in the README.
"""
from pathlib import Path
import struct,hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/qa').mkdir(parents=True,exist_ok=True)
def vi(n):
 out=bytearray()
 while n>=128:out.append((n&127)|128);n>>=7
 out.append(n);return bytes(out)
def string(x):
 b=x.encode('utf-8');return vi(len(b))+b
def chunk(i,t,b):return struct.pack('<I4sI',i,t,len(b))+b
def effects(entries):
 return vi(len(entries))+b''.join(string(n)+b'\x01'+vi(len(v))+struct.pack('<'+'d'*len(v),*v) for n,v in entries)
def state(name,images,fx):
 return string(name)+struct.pack('<I8I3d',2,*(images+images),.13,3.5,6.0)+effects(fx)+effects(fx)+b'\x00\x00\x00PRES'
images=[('idle',10,11),('speaking',20,21),('blink',30,31),('speaking-blink',40,41)]
states=[
 ('Maple Idle',[10,10,30,30],[]),
 ('Maple Speaking',[20,20,40,40],[('jump',[0.,.009,2.6])]),
 ('Maple Blink',[30]*4,[]),
 ('Maple Speaking Blink',[40]*4,[('jump',[0.,.009,2.6])])]
blob=b'VEADOTUBE'+chunk(1,b'META',string('Maple aligned-state builder for veadotube mini 2.2')+string('')+string('Original artwork preserved outside approved eye/mouth masks.'))
blob+=chunk(2,b'MLST',struct.pack('<4I',3,4,5,6))
for i,(name,im,fx) in enumerate(states,3):blob+=chunk(i,b'MSTA',state(name,im,fx))
expected={};asfd=b'MINI'
for name,i,t in images:
 p=ROOT/'assets/aligned'/('maple-'+name+'.png');im=Image.open(p).convert('RGBA');w,h=im.size;px=im.tobytes();row=w*4
 bottom=b''.join(px[y*row:(y+1)*row] for y in range(h-1,-1,-1));expected[t]=(px,w,h)
 blob+=chunk(i,b'AIMG',struct.pack('<II',w,h)+vi(1)+struct.pack('<IIId',t,0,0,0.))
 blob+=chunk(t,b'ABMP',struct.pack('<II4s',w,h,b'RAW.')+bottom)
 asfd+=string('image'+f'{i:08X}')+struct.pack('<I',i)+b'\x00'
blob+=chunk(50,b'ASFD',asfd)+bytes(12)
out=ROOT/'project/maple-pngtuber.veado';out.write_bytes(blob)
# Read back every texture payload; verify dimensions and pixel equality.
pos=9;read={}
while pos+12<=len(blob):
 i,t,n=struct.unpack_from('<I4sI',blob,pos);pos+=12
 if not i:break
 read[i]=(t,blob[pos:pos+n]);pos+=n
checks=[]
for tid,(px,w,h) in expected.items():
 t,d=read[tid];rw,rh,fmt=struct.unpack_from('<II4s',d);assert(t,rw,rh,fmt)==(b'ABMP',w,h,b'RAW.')
 row=w*4;b=d[12:];restored=b''.join(b[y*row:(y+1)*row] for y in range(h-1,-1,-1));assert restored==px
 checks.append({'texture_id':tid,'dimensions':[w,h],'rgba_pixel_exact':True})
report={'avatar':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(blob).hexdigest(),'states':[s[0] for s in states],'image_count':4,'textures':checks,'native_status':'Original-only import was verified. Final four-state live playback has not been verified.','controller_status':'Mock tests only; live switching unverified','limitations':['PNG frame switching, not Cubism deformation','No live AI/TTS hookup, microphone, webcam, gaze or gesture integration verified']}
(ROOT/'build/qa/container-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
