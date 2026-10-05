# SPDX-License-Identifier: MIT
"""Small fixed-memory forest-green/gold layout. Approved PNG assets are read-only."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

R=Path(__file__).resolve().parents[1]
W,H,FPS=960,720,24
FONT=os.environ.get('MAPLE_FONT_DIR','/usr/share/fonts/truetype/dejavu').rstrip('/')+'/'
def font(size,bold=False):
    return ImageFont.truetype(FONT+'DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)
F={k:font(size,bold) for k,size,bold in [
    ('title',32,True),('subtitle',13,False),('label',15,True),
    ('card',27,True),('body',20,False),('small',13,False),('caption',28,True)]}
GOLD=(238,210,149); CREAM=(245,239,218); SAGE=(164,189,163)
# Titles and card words summarize the exact approved fictional introduction.
CARDS={
 'welcome':('COME GET COMFORTABLE',['Hello, there.'],['A little warmth.','A little feline mischief.']),
 'name':('MAPLE NEKOKAMI',['Maple / Koyou'],['She / they','Excellent ears.']),
 'tail':('EXACTLY ONE TAIL',['6 foot 2'],['We have to draw','the line somewhere.']),
 'lore':('IN THE STORY',['Nagaoka','Kami of plenty'],['Nourishment','Agriculture','Continuity']),
 'nourishment':('THE HEART OF THE STORY',['Enough for','one more.'],['Warm rice.','Seeds for next year.']),
 'compute':('FOOD + COMPUTE',['Grow things.','Build things.'],['Make useful things','go further.']),
 'satiation':('SATIATION',['Enough.'],['To eat.','To keep going.','To be curious.']),
 'design':('THE VIRTUAL FORM',['Autumn warmth.'],['Blonde hair, green eyes.','A little cyberpunk.','A little feline mischief.']),
 'linux':('TANGENT INCOMING',['Linux'],['Which shell?','How are you finding it?']),
 'foss':('FREE + OPEN SOURCE',['Make. Share.','Build on it.'],['That moment','when something clicks.']),
 'research':('AI RESEARCH',['Stay curious.'],['How was it tested?','What did it measure?','Where did it fall over?']),
 'ai':('A LITTLE CLARITY',['AI character.','Synthetic voice.'],['The kami story is fiction.','Question me.','Check the facts.']),
 'warmth':('A WARM PLACE TO LAND',['Bring your','enthusiasm.'],['Ask the beginner question.','Choose your own way.']),
 'backup':('A VERY LOVING EYEBROW',['Saved your work?'],['How are those backups?']),
 'end':('THANKS FOR STOPPING BY',['What are you','working on?'],['I want to hear','about your project.'])}

def wrap(text,ft,maxw):
    d=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[];line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if d.textlength(candidate,font=ft)>maxw and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines

def make_base():
    y=np.arange(H)[:,None];x=np.arange(W)[None,:];v=y/H*.5+x/W*.12
    arr=np.stack([12+v*12,27+v*17,23+v*12],axis=-1).astype('uint8')
    im=Image.fromarray(arr,'RGB');d=ImageDraw.Draw(im)
    d.text((29,19),'MAPLE  /  come get comfortable.',font=F['title'],fill=GOLD)
    d.text((30,66),'KOYOU · AI CHARACTER + SYNTHETIC VOICE · RENDERED PNGTUBER PROOF OF CONCEPT',font=F['subtitle'],fill=SAGE)
    d.line((28,93,931,93),fill=(66,87,61),width=1)
    # A quiet warm halo sits behind the unchanged transparent avatar.
    d.ellipse((68,126,565,623),fill=(28,44,31))
    return im

BASE=make_base()
IMAGES={s:Image.open(R.parents[1]/'assets/aligned'/f'maple-{s}.png').convert('RGBA').resize((610,610),Image.Resampling.LANCZOS) for s in ('idle','speaking','blink','speaking-blink')}

def draw_card(im,key):
    d=ImageDraw.Draw(im);label,big,body=CARDS[key];x,y=621,191
    d.rounded_rectangle((x,y,933,525),radius=18,fill=(12,24,20),outline=(77,100,68),width=2)
    d.line((x+20,y+28,x+70,y+28),fill=(194,150,72),width=2)
    d.ellipse((x+76,y+24,x+84,y+32),fill=(194,150,72))
    d.text((x+20,y+48),label,font=F['label'],fill=GOLD)
    yy=y+86
    for t in big:
        ft=F['card'] if d.textlength(t,font=F['card'])<=274 else font(24,True)
        assert d.textlength(t,font=ft)<=274,(key,t)
        d.text((x+20,yy),t,font=ft,fill=CREAM);yy+=38
    yy=max(y+184,yy+15)
    for t in body:
        ft=F['body'] if d.textlength(t,font=F['body'])<=274 else font(18)
        assert d.textlength(t,font=ft)<=274,(key,t)
        d.text((x+20,yy),t,font=ft,fill=SAGE);yy+=29
    d.text((x+20,552),'A fictional introduction, with Maple.',font=F['small'],fill=(161,174,143))

def frame(state,scene,caption,progress=0):
    im=BASE.copy();im.paste(IMAGES[state],(4,72),IMAGES[state]);draw_card(im,scene)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((24,586,936,704),radius=15,fill=(8,20,16),outline=(65,87,61),width=1)
    ft=F['caption'];lines=wrap(caption,ft,868);lh=36
    if len(lines)>2:
        ft=font(24,True);lines=wrap(caption,ft,868);lh=31
    assert len(lines)<=3,(caption,lines)
    yy=641-len(lines)*lh/2
    for line in lines:
        d.text(((W-d.textlength(line,font=ft))/2,yy),line,font=ft,fill=CREAM);yy+=lh
    if progress>0:d.line((30,699,30+900*min(1,progress),699),fill=(201,160,78),width=3)
    return im

if __name__=='__main__':
    for key in CARDS:
        frame('idle',key,'Oh, hello there. Come get comfortable.').save(R/'build/evidence'/f'layout-{key}.png')
    print('All layout cards fit.')
