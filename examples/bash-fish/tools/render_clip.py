# SPDX-License-Identifier: MIT
"""Offline audio-driven PNGtuber render. Never invokes native avatar software."""
from pathlib import Path
import argparse, json, math, random, wave, subprocess, os
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
(R/'build/evidence').mkdir(parents=True,exist_ok=True)
A=R.parents[1]/'assets/aligned'
W,H,FPS=960,720,30
fonts=os.environ.get('MAPLE_FONT_DIR','/usr/share/fonts/truetype/dejavu').rstrip('/')+'/'
def font(size,bold=False,mono=False):return ImageFont.truetype(fonts+('DejaVuSansMono' if mono else 'DejaVuSans')+('-Bold' if bold else '')+'.ttf',size)
F={n:font(s,b,m) for n,s,b,m in [('title',32,True,False),('label',16,True,False),('small',13,False,False),('card',22,False,False),('code',25,False,True),('caption',28,True,False)]}
meta=json.loads((R/'timing.json').read_text());rows=meta['segments']
audio_file=R/meta['audio_file']
with wave.open(str(audio_file),'rb') as w:
 rate=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
parser=argparse.ArgumentParser()
parser.add_argument('--limit-seconds',type=float,help='Render only a short smoke test')
args=parser.parse_args()
assert args.limit_seconds is None or args.limit_seconds>0
nframes=math.ceil(min(len(a)/rate,args.limit_seconds or len(a)/rate)*FPS)
images={s:Image.open(A/f'maple-{s}.png').convert('RGBA').resize((610,610),Image.Resampling.LANCZOS) for s in ['idle','speaking','blink','speaking-blink']}
base=Image.new('RGB',(W,H));p=base.load()
for y in range(H):
 for x in range(W):
  v=y/H*.55+x/W*.15;p[x,y]=(int(12+v*14),int(27+v*20),int(25+v*13))
d=ImageDraw.Draw(base)
d.line((28,94,930,94),fill=(65,89,67),width=1)
d.text((29,20),'MAPLE  /  bash vs fish',font=F['title'],fill=(246,223,166))
d.text((30,67),'AI CHARACTER + SYNTHETIC VOICE · RENDERED PNGTUBER PROOF OF CONCEPT',font=F['small'],fill=(166,188,165))
# Quiet terminal card, with exact syntax examples when spoken.
cards={
'intro':('tiny terminal rabbit hole',['bash  +  fish'],['Different grammar.','Shared terminal.']),
'bash':('BASH',['Bourne Again','Shell'],['Yes, it is a pun.']),
'fish':('FISH',['autosuggestions','syntax highlighting'],['Built in.','Very cozy.']),
'syntax':('VARIABLES',['bash','name=Maple','','fish','set name Maple'],[]),
'compat':('DIFFERENT GRAMMAR',['fish ≠ POSIX'],['Bash syntax will not','always work in fish.']),
'launch':('FROM A FISH PROMPT',['bash script.sh'],['Bash interprets','the Bash script.']),
'choice':('COZY SETUP',['fish → interactive','bash → Bash scripts'],['Bash scripts are not','automatically portable.']),
'end':('THE TAKEAWAY',['Two shells.','One terminal.'],['No custody battle.'])}

def wrap(text,ft,maxw):
 out=[];line=''
 for word in text.split():
  candidate=(line+' '+word).strip()
  if d.textlength(candidate,font=ft)>maxw and line:out.append(line);line=word
  else:line=candidate
 if line:out.append(line)
 return out

def scene_at(t):
 # Hold the current scene through pauses, never jump to the end card.
 selected=rows[0]
 for row in rows:
  if row['start_s']>t:break
  selected=row
 return selected

def draw_card(im,key):
 dr=ImageDraw.Draw(im);title,codes,lines=cards[key]
 x,y=623,210
 dr.rounded_rectangle((x,y,930,515),radius=18,fill=(13,24,23),outline=(72,94,69),width=2)
 for i,c in enumerate([(184,79,56),(230,178,93),(118,167,115)]):dr.ellipse((x+19+i*18,y+17,x+27+i*18,y+25),fill=c)
 dr.text((x+18,y+47),title,font=F['label'],fill=(222,191,126))
 yy=y+91
 for text in codes:
  size=25 if len(text)<17 else 20;ft=font(size,False,True)
  if text in ('bash','fish'):ft=F['small']
  dr.text((x+18,yy),text,font=ft,fill=(168,225,168) if text not in ('bash','fish') else (150,178,155));yy+=31 if text else 7
 yy=max(yy+19,y+190)
 for text in lines:dr.text((x+18,yy),text,font=font(19),fill=(211,217,201));yy+=28

rng=random.Random(305);blink_times=[];t=2.25
while t<len(a)/rate-.85:
 t+=rng.uniform(2.7,4.8)
 if t<len(a)/rate-.85:blink_times.append(t)
# Independent, short two-state gate measured on actual final waveform.
rms=np.array([math.sqrt(np.mean(a[round(f*rate/FPS):min(len(a),round((f+1)*rate/FPS))]**2)) if round(f*rate/FPS)<len(a) else 0 for f in range(nframes)])
voiced_rms=rms[rms>.008]
assert len(voiced_rms)>0,'Audio is silent'
threshold=max(.008,float(np.percentile(voiced_rms,23))*.7)
state_events=[];frames_meta=[];last_open=-100;end=rows[-1]['end_s']
log=open(R/'build/evidence/encode.log','w')
video=R/'build'/'maple-bash-vs-fish-elevenlabs-voice1.mp4'
proc=subprocess.Popen(['ffmpeg','-y','-v','info','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(audio_file),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','1','-preset','fast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart','-t',str(nframes/FPS),str(video)],stdin=subprocess.PIPE,stderr=log)
for f in range(nframes):
 t=f/FPS;row=scene_at(t)
 if rms[f]>threshold:last_open=f
 speaking=(f-last_open<=1) and t>=rows[0]['start_s'] and t<end
 blink=any(b<=t<b+.13334 for b in blink_times)
 state='speaking-blink' if speaking and blink else 'speaking' if speaking else 'blink' if blink else 'idle'
 im=base.copy();dr=ImageDraw.Draw(im)
 bob=round(1.5*math.sin(t*math.pi*3)) if speaking else 0
 im.paste(images[state],(4,72+bob),images[state]);draw_card(im,row['scene'])
 dr=ImageDraw.Draw(im);dr.rounded_rectangle((24,585,936,704),radius=15,fill=(9,20,19),outline=(62,87,66),width=1)
 caption=row['text'] if row['start_s']<=t<row['end_s'] else ('A tiny terminal rabbit hole, with Maple.' if t<rows[0]['start_s'] or t>=end+.1 else '')
 lines=wrap(caption,F['caption'],866)
 assert len(lines)<=3,(caption,lines)
 ft=F['caption'];line_h=36
 if len(lines)==3:ft=font(24,True);lines=wrap(caption,ft,866);line_h=31
 yy=643-len(lines)*line_h/2
 for line in lines:
  dr.text(((W-dr.textlength(line,font=ft))/2,yy),line,font=ft,fill=(245,239,217));yy+=line_h
 progress=min(1,t/end);dr.rounded_rectangle((30,697,30+900*progress,700),radius=1,fill=(202,163,86))
 proc.stdin.write(im.tobytes())
 if not state_events or state!=state_events[-1]['state']:state_events.append({'frame':f,'time_s':t,'state':state})
 frames_meta.append({'frame':f,'rms':float(rms[f]),'state':state,'segment':row['index']})
proc.stdin.close();rc=proc.wait();log.close()
if rc:raise RuntimeError('ffmpeg failed')
(R/'build/evidence/animation-checks.json').write_text(json.dumps({'fps':FPS,'frames':nframes,'duration_s':nframes/FPS,'native_capture':False,'mouth_control':'RMS of actual final speech; 1-frame hold; exact end reset','phoneme_alignment':False,'rms_threshold':threshold,'blink_times_s':blink_times,'state_events':state_events,'final_state':state_events[-1]['state'],'asset_states':list(images),'caption_timing':meta['alignment_method']},indent=2)+'\n')
(R/'build/evidence/frame-state-timing.json').write_text(json.dumps(frames_meta)+'\n')
# SRT uses the same segment starts and ends as the burned captions.
def stamp(t):
 ms=round(t*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60);return f'{h:02}:{m:02}:{s:02},{ms:03}'
srt='\n\n'.join(f"{i+1}\n{stamp(r['start_s'])} --> {stamp(r['end_s'])}\n{r['text']}" for i,r in enumerate(rows))+'\n'
(R/'build'/'captions.srt').write_text(srt)
print(video)
