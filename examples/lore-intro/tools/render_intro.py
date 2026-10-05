# SPDX-License-Identifier: MIT
"""Fixed-memory streaming quality-targeted H.264 PNGtuber renderer.

Uses only the downloaded new voice waveform and unchanged approved art.
Requires FFmpeg, Pillow and NumPy already installed locally. Two encoder
threads maximum; no parallel render or per-frame image archive.
"""
from pathlib import Path
import argparse, bisect, hashlib, json, math, random, subprocess, wave
import numpy as np
from layout import R,W,H,FPS,frame,wrap,F

p=argparse.ArgumentParser();p.add_argument('--crf',type=int,default=22);p.add_argument('--limit-seconds',type=float,help='Render only a short smoke test');args=p.parse_args()
assert args.limit_seconds is None or args.limit_seconds>0
(R/'build/evidence').mkdir(parents=True,exist_ok=True)
meta=json.loads((R/'timing.json').read_text());rows=meta['segments'];duration=meta['duration_s'];master=R/meta['audio_file']
nframes=math.ceil(min(duration,args.limit_seconds or duration)*FPS);audio_kbps=128
# Leave room for MP4 muxing and mild bitrate variability; hard validated later.
video_kbps=int((7_500_000*8/duration-6_000)/1000-audio_kbps)
assert video_kbps>=75
# Validate every caption fits before starting encoding.
for r in rows:
 lines=wrap(r['text'],F['caption'],868)
 assert len(lines)<=3,(r['index'],r['text'])
with wave.open(str(master),'rb') as w:
 rate=w.getframerate();assert rate==48000
 rms=np.zeros(nframes,dtype='float32')
 for f in range(nframes):
  raw=w.readframes(round((f+1)*rate/FPS)-round(f*rate/FPS))
  aa=np.frombuffer(raw,'<i2').astype('float32')/32768
  if len(aa):rms[f]=math.sqrt(float(np.mean(aa*aa)))
voiced=rms[rms>.008];assert len(voiced)
threshold=max(.008,float(np.percentile(voiced,23))*.7)
rng=random.Random(51005);blink_times=[];t=2.1
while True:
 t+=rng.uniform(2.8,5.7)
 if t>=duration-1.2:break
 blink_times.append(t)
starts=[r['start_s'] for r in rows];last_open=-100;states=[];events=[];frame_meta=[]
speech_start=meta['lead_s'];speech_end=meta['lead_s']+meta['source_duration_s']
# Mouth gate follows only actual audio. Captions never open the mouth.
for f in range(nframes):
 t=f/FPS
 if rms[f]>threshold:last_open=f
 speaking=(f-last_open<=1) and speech_start<=t<speech_end
 blink=any(b<=t<b+.125 for b in blink_times) and t<duration-1.05
 state='speaking-blink' if speaking and blink else 'speaking' if speaking else 'blink' if blink else 'idle'
 if t>=duration-1.0:state='idle'
 states.append(state)
 if not events or state!=events[-1]['state']:events.append({'frame':f,'time_s':t,'state':state})
 ix=max(0,bisect.bisect_right(starts,t)-1)
 frame_meta.append({'frame':f,'rms':round(float(rms[f]),7),'state':state,'segment':rows[ix]['index']})
video=R/'build'/'maple-lore-introduction-elevenlabs-voice1.mp4';passlog=R/'build/evidence/x264-pass'
passes=[2]  # Static composition compresses better with a stable quality target.
for passno in passes:
 log=open(R/'build/evidence'/f'encode-pass-{passno}.log','w')
 cmd=['ffmpeg','-y','-hide_banner','-v','info','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-']
 if passno==2:cmd+=['-threads','1','-i',str(master)]
 cmd+=['-map','0:v:0','-c:v','libx264','-threads','2','-preset','fast','-crf',str(args.crf),'-pix_fmt','yuv420p','-g','240','-keyint_min','24','-sc_threshold','20']
 if passno==1:cmd+=['-an','-f','null','-']
 else:cmd+=['-map','1:a:0','-c:a','aac','-b:a',f'{audio_kbps}k','-movflags','+faststart','-t',str(nframes/FPS),'-metadata','title=Maple / Come get comfortable','-metadata','comment=AI character and synthetic voice; rendered PNGtuber proof of concept; approximate captions',str(video)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
 last_key=None;payload=None
 try:
  for f in range(nframes):
   t=f/FPS;idx=max(0,bisect.bisect_right(starts,t)-1);row=rows[idx]
   caption=row['text'] if row['start_s']<=t<row['end_s'] else ''
   if t<rows[0]['start_s']:caption='Come get comfortable.'
   if t>=speech_end+.15:caption='Thanks for stopping by.'
   # Once-per-second progress avoids spending the small budget on decoration.
   progress=min(1,int(t)/speech_end) if t<speech_end else 1.
   key=(states[f],row['scene'],caption,progress)
   if key!=last_key:
    payload=frame(*key).tobytes();last_key=key
   proc.stdin.write(payload)
   if f%1200==0:print(f'pass {passno}: {f}/{nframes} frames',flush=True)
 finally:
  proc.stdin.close();rc=proc.wait();log.close()
 if rc:raise RuntimeError(f'FFmpeg pass {passno} failed; see log')
 print(f'Pass {passno} completed.',flush=True)
(R/'build/evidence/animation-checks.json').write_text(json.dumps({'fps':FPS,'frames':nframes,'duration_s':nframes/FPS,'native_capture':False,'mouth_control':'RMS of actual new final speech, one-frame hold; hard reset in trailing silence','phoneme_alignment':False,'rms_threshold':threshold,'blink_times_s':blink_times,'state_events':events,'final_state':states[-1],'asset_states':['idle','speaking','blink','speaking-blink'],'caption_timing':meta['alignment_method'],'encoding':{'estimated_video_budget_kbps':video_kbps,'audio_kbps':audio_kbps,'passes':1,'crf':args.crf,'threads':2,'maximum_bytes':8_000_000}},indent=2)+'\n')
(R/'build/evidence/frame-state-timing.json').write_text(json.dumps(frame_meta)+'\n')
def stamp(t):
 ms=round(t*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60);return f'{h:02}:{m:02}:{s:02},{ms:03}'
srt='\n\n'.join(f"{i+1}\n{stamp(r['start_s'])} --> {stamp(r['end_s'])}\n{r['text']}" for i,r in enumerate(rows))+'\n'
(R/'build'/'captions.srt').write_text(srt)
print(json.dumps({'video':str(video),'bytes':video.stat().st_size if video.exists() else None,'duration_s':duration,'estimated_video_budget_kbps':video_kbps,'audio_kbps':audio_kbps},indent=2))
