#!/usr/bin/env python3
"""Render an honest walkthrough of live MCP tool responses.

No account, private data, platform approval or ChatGPT UI is represented.
Each frame is derived from the adjacent live JSON-RPC capture. Fonts are
system dependencies and are never distributed with the resulting video.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
W,H=1280,720
BG="#0e1712"
SURFACE="#18241b"
INK="#e8f3e6"
MUTED="#9caf9e"
LINE="#3b5340"
ACCENT="#b6e881"
FONT_DIR=Path("/usr/share/fonts/truetype/dejavu")
def font(size,bold=False,mono=False):
    name=("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf") if mono else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(str(FONT_DIR/name),size)

def rounded(draw,rect,fill,outline=None,r=18,width=1):
    draw.rounded_rectangle(rect,radius=r,fill=fill,outline=outline,width=width)

def clip_text(draw,text,x,y,available,font_,fill,max_lines=3,leading=13):
    text=" ".join(str(text).split())
    words=text.split(" ")
    lines=[]
    line=""
    for word in words:
        candidate=word if not line else line+" "+word
        if draw.textbbox((0,0),candidate,font=font_)[2]<=available:
            line=candidate
        elif not line:
            # Narrow break for unspaced URLs and filenames.
            fragments=[word[j:j+35] for j in range(0,len(word),35)]
            if lines:lines[-1]+=" ..."
            lines.extend(fragments[:-1]);line=fragments[-1]
        else:
            lines.append(line);line=word
    if line:lines.append(line)
    for i,part in enumerate(lines[:max_lines]):
        if i==max_lines-1 and len(lines)>max_lines:
            while draw.textbbox((0,0),part+"…",font=font_)[2]>available and part:
                part=part[:-1]
            part+="…"
        draw.text((x,y+i*(font_.size+leading)),part,font=font_,fill=fill)
    return len(lines[:max_lines])*(font_.size+leading)

def render(scene,index,count,captured):
    image=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(image)
    # Atmospheric gridded field, no stock assets and no imitation of vendor UI.
    for x in range(0,W,54):d.line((x,0,x,H),fill="#15241a",width=1)
    for y in range(0,H,54):d.line((0,y,W,y),fill="#15241a",width=1)
    d.rectangle((0,0,W,88),fill="#101d15")
    logo=Image.open(ROOT/"assets/docsy-icon-192.png").convert("RGBA")
    logo.thumbnail((42,42))
    image.paste(logo,(52,22),logo)
    d.text((104,28),"docsy",font=font(30,True),fill=INK)
    d.text((213,37),"/  PLUGIN REVIEW WALKTHROUGH",font=font(13,True,True),fill=MUTED)
    rounded(d,(950,23,1227,63),"#263a25",r=14)
    d.ellipse((970,39,981,50),fill=ACCENT)
    d.text((995,35),"REAL LIVE MCP RESPONSES",font=font(13,True),fill=ACCENT)
    # vertical stepping nav
    d.text((53,112),"PUBLIC MCP · 9 VERIFICATIONS",font=font(14,True,True),fill=MUTED)
    labels=["CONNECT","RESOLVE","RETRIEVE","VERSIONS","SEARCH","FETCH","FASTIFY","SAFETY","READY"]
    for j,name in enumerate(labels):
        y=155+j*48
        active=j==index
        if active:rounded(d,(43,y-7,250,y+34),"#29422a",r=10)
        d.text((55,y),f"{j+1:02d}",font=font(18,True,True),fill=ACCENT if active else "#6d866e")
        d.text((92,y+2),name,font=font(15,True,True),fill=INK if active else MUTED)
    # right content
    rounded(d,(291,111,1226,604),SURFACE,outline=LINE,r=23)
    d.text((330,143),scene["tag"],font=font(18,True,True),fill=ACCENT)
    d.text((329,181),scene["title"],font=font(34,True),fill=INK)
    d.text((329,237),"MCP REQUEST",font=font(12,True,True),fill=MUTED)
    rounded(d,(328,260,1190,321),"#0e1912",outline="#2d4931",r=11)
    clip_text(d,scene["command"],345,276,827,font(15,False,True),ACCENT,max_lines=2,leading=8)
    d.text((329,340),"LIVE RESULT",font=font(12,True,True),fill=MUTED)
    y=372
    for line in scene["outputLines"][:6]:
        if y>558:break
        d.ellipse((330,y+8,338,y+16),fill="#6aa866")
        taken=clip_text(d,line,355,y,822,font(16,False,True),INK,max_lines=2,leading=6)
        y+=max(34,taken)+3
    # Lower separator/footer
    d.line((49,636,1230,636),fill=LINE,width=1)
    d.text((52,659),scene["caption"],font=font(15),fill=INK)
    d.text((52,685),"DATA: "+captured[:10]+"  ·  https://docsy.remcp.site/mcp/registry",font=font(10,False,True),fill=MUTED)
    d.text((1073,658),f"STEP {index+1:02d} / {count:02d}",font=font(14,True,True),fill=ACCENT)
    # bounded progress
    d.rectangle((0,H-4,int(W*(index+1)/count),H),fill=ACCENT)
    return image

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("data",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--seconds",type=int,default=5)
    args=parser.parse_args()
    report=json.loads(args.data.read_text())
    scenes=report["scenes"]
    assert len(scenes)==9
    assert 3<=args.seconds<=15
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="docsy-demo-") as tmp:
        playlist=[]
        for i,scene in enumerate(scenes):
            path=Path(tmp)/f"step-{i:02d}.png"
            render(scene,i,len(scenes),report["capturedAt"]).save(path,optimize=True)
            playlist.append(f"file '{path}'\nduration {args.seconds}\n")
        playlist.append(f"file '{Path(tmp)/f'step-{len(scenes)-1:02d}.png'}'\n")
        listing=Path(tmp)/"frames.txt"
        listing.write_text("".join(playlist))
        command=[
            "ffmpeg","-hide_banner","-loglevel","error","-y",
            "-f","concat","-safe","0","-i",str(listing),
            "-vf","fps=12,format=yuv420p",
            "-c:v","libx264","-preset","medium","-crf","22",
            "-movflags","+faststart",str(args.output)
        ]
        subprocess.run(command,check=True,timeout=150)
    print("Rendered",args.output,round(args.output.stat().st_size/1024/1024,2),"MiB")
if __name__=="__main__":
    main()
