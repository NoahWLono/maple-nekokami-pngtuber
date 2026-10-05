#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render a clearly labeled offline frame-state review, not a native capture."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,os
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/qa').mkdir(parents=True,exist_ok=True)
OUT=ROOT/'build/preview';OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS,SECONDS=960,720,30,9
fontpath=str(Path(os.environ.get('MAPLE_FONT_DIR','/usr/share/fonts/truetype/dejavu'))/'DejaVuSans.ttf')
font=ImageFont.truetype(fontpath,24);small=ImageFont.truetype(fontpath,15);statefont=ImageFont.truetype(fontpath,18)
images={n:Image.open(ROOT/'assets/aligned'/('maple-'+n+'.png')).convert('RGBA') for n in ['idle','speaking','blink','speaking-blink']}
video=OUT/'maple-aligned-2d-offline-preview.mp4'
p=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
selected={};events=[]
for f in range(FPS*SECONDS):
 t=f/FPS;speaking=1.7<=t<6.7
 openmouth=speaking and ((t-1.7)%0.34<0.24)
 blink=any(start<=t<start+.1334 for start in (1.15,4.1,7.6))
 state='speaking-blink' if openmouth and blink else 'speaking' if openmouth else 'blink' if blink else 'idle'
 im=Image.new('RGB',(W,H),(22,32,34));d=ImageDraw.Draw(im)
 d.text((35,24),'Maple | 2D comparison',font=font,fill=(238,220,180))
 d.text((35,59),'Offline frame preview · original artwork + local eye/mouth patches',font=small,fill=(178,190,183))
 art=images[state];im.paste(art,(160,75),art)
 label='SPEAKING' if speaking else 'IDLE'
 d.rounded_rectangle((760,24,924,59),radius=12,fill=(61,83,64) if speaking else (46,60,59))
 d.text((783,31),label,font=statefont,fill=(234,231,203))
 d.text((35,687),'Silent preview. Final native playback / live AI control is not yet verified.',font=small,fill=(174,185,180))
 p.stdin.write(im.tobytes())
 if f in (20,64,123,231):selected[f]=im.copy()
 if f==0 or state!=events[-1]['state']:events.append({'frame':f,'time':round(t,4),'state':state})
p.stdin.close();err=p.stderr.read().decode();rc=p.wait()
(ROOT/'build/qa/preview-encode.log').write_text(err)
if rc:raise RuntimeError(f'ffmpeg failed: {rc}')
# One contact sheet for decoded representative video frames (quality verified separately).
for f in selected:
 subprocess.run(['ffmpeg','-y','-i',str(video),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(OUT/f'preview-frame-{f:03d}.png')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
board=Image.new('RGB',(960,720),(0,0,0))
for i,f in enumerate(selected):board.paste(Image.open(OUT/f'preview-frame-{f:03d}.png').resize((480,360)),((i%2)*480,(i//2)*360))
board.save(OUT/'maple-preview-contact-sheet.png')
(ROOT/'build/qa/offline-preview-events.json').write_text(json.dumps({'native_capture':False,'audio':False,'fps':FPS,'seconds':SECONDS,'frames':FPS*SECONDS,'events':events},indent=2)+'\n')
print(video)
