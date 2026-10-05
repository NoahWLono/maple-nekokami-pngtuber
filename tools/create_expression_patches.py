#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authorized precise mouth/eye patch assembly; originals remain immutable.
Use approved imagegen expression references only inside explicit face masks.
All RGBA pixels outside the selected edit mask remain byte-exact. Source alpha
is retained everywhere, including within the patches. No body/hair redraw.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/qa').mkdir(parents=True,exist_ok=True)
OUT=ROOT/'assets/aligned';OUT.mkdir(parents=True,exist_ok=True)
base=Image.open(ROOT/'assets/maple-original-unchanged.png').convert('RGBA')
a=np.array(base)
def source(name):
 return np.array(Image.open(ROOT/'assets/references'/name).convert('RGBA').resize(base.size,Image.Resampling.LANCZOS))
refs={'mouth':source('maple-talking-redraw-proposal.png'),'blink':source('maple-blink-redraw-proposal.png')}
polys={
 'mouth':[(304,212),(311,210),(330,210),(338,215),(339,227),(332,234),(311,234),(303,227)],
 'eye_left':[(258,173),(268,168),(278,163),(289,163),(299,168),(307,174),(314,181),(310,191),(301,199),(282,199),(270,194),(264,184)],
 'eye_right':[(332,175),(337,168),(347,163),(362,160),(371,163),(383,171),(381,180),(373,191),(363,198),(345,198),(335,190),(329,182)]}
masks={}
for name,poly in polys.items():
 m=Image.new('L',base.size);ImageDraw.Draw(m).polygon(poly,fill=255)
 # Feather inward only, so support never grows beyond the documented polygon.
 eroded=m.filter(ImageFilter.MinFilter(3))
 feather=np.minimum(np.array(m,dtype=np.float32),np.array(eroded.filter(ImageFilter.GaussianBlur(1.15)),dtype=np.float32))/255
 feather[np.array(m)==0]=0
 masks[name]=(np.array(m)>0,feather)
 m.save(OUT/(name+'-edit-mask.png'))

def apply_patch(result,ref,name):
 hard,alpha=masks[name]
 # Neutralize the modest reference skin tint using a robust ring estimate.
 hm=Image.fromarray((hard*255).astype('uint8'))
 inner=np.array(hm.filter(ImageFilter.MinFilter(7)))>0
 ring=hard & ~inner
 rgb=a[:,:,:3].astype(float); rr=ref[:,:,:3].astype(float)
 skin=(rgb[:,:,0]>160)&(rgb[:,:,0]>=rgb[:,:,1])&((rgb[:,:,1]-rgb[:,:,2])<52)&(rr[:,:,0]>160)&((rr[:,:,1]-rr[:,:,2])<52)
 samples=(rgb-rr)[ring&skin]
 offset=np.clip(np.median(samples,axis=0) if len(samples)>4 else np.zeros(3),-18,18)
 corrected=np.clip(rr+offset,0,255)
 mixed=np.rint(result[:,:,:3]*(1-alpha[:,:,None])+corrected*alpha[:,:,None]).astype('uint8')
 result[:,:,:3]=np.where(hard[:,:,None],mixed,result[:,:,:3])
 return {'mask':name,'polygon':polys[name],'skin_rgb_offset':[round(float(x),2) for x in offset]}
frames={};reports={}
for filename,names in [('idle',[]),('speaking',['mouth']),('blink',['eye_left','eye_right']),('speaking-blink',['mouth','eye_left','eye_right'])]:
 result=a.copy();history=[];allowed=np.zeros(base.size[::-1],dtype=bool)
 for name in names:
  history.append(apply_patch(result,refs['mouth' if name=='mouth' else 'blink'],name));allowed|=masks[name][0]
 assert np.array_equal(result[~allowed],a[~allowed])
 assert np.array_equal(result[:,:,3],a[:,:,3])
 out=OUT/('maple-'+filename+'.png');Image.fromarray(result).save(out)
 frames[filename]=Image.fromarray(result)
 changed=np.any(result!=a,axis=2)
 reports[filename]={'file':str(out.relative_to(ROOT)),'dimensions':[640,640],'changed_pixels':int(changed.sum()),'changed_pixels_outside_masks':int((changed&~allowed).sum()),'alpha_unchanged_everywhere':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'patches':history}
# Exact idle RGBA pixels; byte-identical original is also supplied separately.
# Review sheet: full frames plus enlarged eye/mouth context, neutral background.
board=Image.new('RGB',(1280,1050),(36,42,48));d=ImageDraw.Draw(board)
labels={'idle':'IDLE | original pixels','speaking':'SPEAKING | mouth patch','blink':'BLINK | eye patches','speaking-blink':'SPEAKING + BLINK'}
for i,(name,im) in enumerate(frames.items()):
 x=(i%2)*640;y=(i//2)*525
 d.text((x+20,y+10),labels[name],fill=(244,227,199))
 thumb=im.resize((440,440),Image.Resampling.LANCZOS);board.paste(thumb,(x+10,y+45),thumb)
 face=im.crop((254,156,385,238)).resize((262,164),Image.Resampling.NEAREST)
 # Face inset intentionally overlaps some right-side blank area, not artwork.
 board.paste(face,(x+365,y+125),face)
board.save(ROOT/'build/qa/aligned-expression-review.png')
(ROOT/'build/qa/expression-pixel-validation.json').write_text(json.dumps({'original_sha256':hashlib.sha256((ROOT/'assets/maple-original-unchanged.png').read_bytes()).hexdigest(),'method':'Imagegen expression reference; Lanczos normalized to640; local feathered RGB patches only; original alpha retained everywhere','mask_policy':'No changes outside documented polygons; all source files retained','frames':reports},indent=2)+'\n')
print(json.dumps(reports,indent=2))
