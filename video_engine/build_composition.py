"""Create illustrated, scene-specific Indian puppet-theatre visuals for a vertical Short."""
from __future__ import annotations
import html, json, sys
from pathlib import Path

def esc(v): return html.escape(str(v or ""), quote=True)

def kind_for(s):
    t=" ".join(str(s.get(k,"")) for k in ("visual_description","setting","action","on_screen_text")).lower()
    for words,k in [(("ocean","sea","water"),"ocean"),(("ashoka","garden","grove"),"garden"),(("palace","lanka","kingdom"),"palace"),(("mountain","hill"),"mountain"),(("battle","war"),"battle"),(("sky","cloud"),"sky"),(("forest","jungle"),"forest")]:
        if any(w in t for w in words): return k
    return "forest"

def character_for(s):
    t=" ".join(str(s.get(k,"")) for k in ("visual_description","characters","action","narration_segment")).lower()
    for n in ("hanuman","sita","ravana","rama","krishna","shiva"):
        if n in t: return n
    return "hero"

def scenery(k,i):
    palettes={"ocean":("#142f59","#167e9b","#f7b85c"),"garden":("#173d35","#3b8050","#f6c66b"),"forest":("#142e31","#34704e","#eab85c"),"palace":("#391d42","#8c4352","#f4c56c"),"mountain":("#182c49","#607b8c","#f5c66a"),"battle":("#321f3b","#8b3f45","#f5b45e"),"sky":("#182d55","#75518a","#f7c86d")}
    a,b,c=palettes[k]
    z=f'<defs><linearGradient id="g{i}" x2="0" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient><radialGradient id="r{i}"><stop stop-color="{c}" stop-opacity=".8"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient></defs><rect width="1080" height="1920" fill="url(#g{i})"/><circle cx="820" cy="350" r="330" fill="url(#r{i})"/><circle cx="820" cy="350" r="92" fill="{c}"/>'
    if k in ("ocean","battle"):
        z+='<path d="M0 1000 Q150 940 300 1000 T600 1000 T900 1000 T1200 1000 V1920 H0Z" fill="#12627b"/><path d="M0 1160 Q150 1090 300 1160 T600 1160 T900 1160 T1200 1160 M0 1340 Q150 1270 300 1340 T600 1340 T900 1340 T1200 1340" fill="none" stroke="#9be0d9" stroke-width="16" opacity=".55"/>'
    elif k in ("forest","garden"):
        for x,y,r in [(70,820,130),(260,700,105),(850,770,125),(1030,850,140),(650,920,90)]:
            z+=f'<path d="M{x} 1420 V{y+160}" stroke="#50352b" stroke-width="45"/><circle cx="{x}" cy="{y}" r="{r}" fill="#194a3b"/><circle cx="{x-35}" cy="{y-35}" r="{r*.62}" fill="#398252"/>'
        z+='<path d="M0 1400 Q270 1280 540 1400 T1080 1380 V1920 H0Z" fill="#173d34"/>'
        if k=="garden":
            for x in range(80,1080,160): z+=f'<circle cx="{x}" cy="1440" r="22" fill="#eaa3b4"/><circle cx="{x+22}" cy="1420" r="12" fill="#ffd77c"/>'
    elif k=="palace":
        z+='<path d="M120 1120 V620 H960 V1120Z" fill="#9b5a50" stroke="#f3c66e" stroke-width="16"/><path d="M80 640 L540 330 L1000 640Z" fill="#d99a52" stroke="#ffe0a0" stroke-width="18"/><path d="M430 1120 V780 Q540 650 650 780 V1120Z" fill="#40253d"/><path d="M190 760 H330 V960 H190Z M750 760 H890 V960 H750Z" fill="#f6d48b"/>'
    else:
        z+='<path d="M0 1190 L250 560 L430 960 L680 390 L1080 1210 V1920 H0Z" fill="#344c68"/><path d="M680 390 L610 600 L700 560 L770 660Z" fill="#e5e8e3"/><path d="M0 1300 Q300 1200 600 1320 T1080 1270 V1920 H0Z" fill="#243d4c" opacity=".8"/>'
    return z

def puppet(name,x,y,scale,pose,idx):
    skin={"hanuman":"#b86d43","sita":"#d99a70","rama":"#5886b8","ravana":"#9a5548","krishna":"#4e76b6","shiva":"#9ab9c8","hero":"#c78358"}[name]
    cloth={"hanuman":"#e4a52e","sita":"#c94f69","rama":"#2f8c79","ravana":"#6e3b83","krishna":"#e0a52e","shiva":"#e8e5dc","hero":"#a64d57"}[name]
    arms=("M-65 -185 Q-125 -260 -155 -340","M65 -185 Q130 -250 160 -325") if pose in ("leap","raise","fight") else ("M-65 -185 Q-130 -135 -150 -80","M65 -185 Q125 -135 145 -80")
    crown='<path d="M-62 -390 L-45 -480 L0 -425 L45 -480 L62 -390Z" fill="#f5c45d" stroke="#5b342b" stroke-width="10"/>' if name in ("rama","krishna","ravana","hanuman") else '<path d="M-55 -390 Q0 -490 55 -390Z" fill="#d9ad56" stroke="#653d32" stroke-width="8"/>'
    tail='<path d="M85 -275 Q190 -390 230 -300" stroke="#d89b35" stroke-width="24" fill="none"/>' if name=="hanuman" else ""
    return f'''<g class="puppet puppet-{idx}" transform="translate({x} {y}) scale({scale})"><ellipse cy="8" rx="180" ry="35" fill="#090d18" opacity=".35"/><path d="M-45 -75 L-80 30 M45 -75 L80 30" stroke="{skin}" stroke-width="38" stroke-linecap="round"/><path d="M-105 35 H-45 M45 35 H105" stroke="#f2c66f" stroke-width="26" stroke-linecap="round"/><path d="M-92 -300 Q-115 -250 -95 -90 Q0 -35 95 -90 Q115 -250 92 -300Z" fill="{cloth}" stroke="#43283a" stroke-width="14"/><path d="M-75 -245 L0 -155 L75 -245" fill="none" stroke="#f4d17b" stroke-width="15"/><g class="arms"><path d="{arms[0]}" stroke="#43283a" stroke-width="58" fill="none" stroke-linecap="round"/><path d="{arms[0]}" stroke="{skin}" stroke-width="38" fill="none" stroke-linecap="round"/><path d="{arms[1]}" stroke="#43283a" stroke-width="58" fill="none" stroke-linecap="round"/><path d="{arms[1]}" stroke="{skin}" stroke-width="38" fill="none" stroke-linecap="round"/></g><circle cy="-355" r="88" fill="{skin}" stroke="#43283a" stroke-width="13"/><path d="M-70 -390 Q-35 -470 35 -430 Q75 -410 70 -380" fill="#382536"/>{crown}<ellipse cx="-30" cy="-360" rx="10" ry="15" fill="#20192a"/><ellipse cx="30" cy="-360" rx="10" ry="15" fill="#20192a"/><path d="M-22 -315 Q0 -298 22 -315" fill="none" stroke="#7e3438" stroke-width="9"/>{tail}</g>'''

def main():
    sp=Path(sys.argv[1]) if len(sys.argv)>1 else Path("output/stories/latest.json")
    ap=Path(sys.argv[2]) if len(sys.argv)>2 else Path("video/assets/narration.wav")
    data=json.loads(sp.read_text(encoding="utf-8")); scenes=data["scenes"]; total=sum(float(s["duration_seconds"]) for s in scenes)
    if not 30<=total<=60: raise ValueError(f"Video duration must be 30–60 seconds; got {total}")
    blocks=[]; cursor=0
    for i,s in enumerate(scenes,1):
        dur=float(s["duration_seconds"]); start=cursor; cursor+=dur; k=kind_for(s); who=character_for(s)
        words=" ".join(str(s.get(q,"")) for q in ("action","visual_description","narration_segment")).lower()
        pose="leap" if any(w in words for w in ("leap","jump","fly","soar")) else "raise" if any(w in words for w in ("raise","lift","greet","bless")) else "fight" if any(w in words for w in ("fight","battle","attack")) else "rest"
        alltext=" ".join(str(s.get(q,"")) for q in ("visual_description","narration_segment")).lower()
        other=next((n for n in ("sita","rama","hanuman","ravana","krishna","shiva") if n!=who and n in alltext),None)
        figures=puppet(who,510,1390,1.2,pose,i)+(puppet(other,830,1430,.78,"raise",i+20) if other else "")
        title=esc(s.get("on_screen_text") or data["title"]); caption=esc(s.get("narration_segment","")); desc=esc(s.get("visual_description",""))
        blocks.append(f'''<section class="clip scene" id="scene-{i}" data-start="{start:.2f}" data-duration="{dur:.2f}" data-track-index="0"><svg class="art" viewBox="0 0 1080 1920" role="img" aria-label="{desc}">{scenery(k,i)}{figures}</svg><div class="topline">INDIAN EPIC • {i:02d}/{len(scenes):02d}</div><div class="copy"><div class="scene-title">{title}</div><div class="caption">{caption}</div></div><div class="scene-description">{desc}</div></section>''')
    question=esc(data.get("closing_question","What would you have done?"))
    doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
    *{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#101322;font-family:Georgia,serif}}#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#101322;color:#fff}}
    .scene{{position:absolute;inset:0;width:1080px;height:1920px;overflow:hidden;opacity:0}}.art{{position:absolute;inset:0;width:100%;height:100%;filter:saturate(1.1)}}
    .topline{{position:absolute;top:85px;left:70px;right:70px;text-align:center;font:700 22px Arial,sans-serif;letter-spacing:7px;color:#ffe2a0;text-shadow:0 3px 12px #111}}
    .copy{{position:absolute;left:65px;right:65px;bottom:300px;text-align:center;padding:34px 30px 40px;background:linear-gradient(180deg,#17132500,#171325e8 18%,#171325f2);border-top:2px solid #f2c66f}}
    .scene-title{{font:700 68px/1.08 Georgia,serif;color:#ffe2a0;margin-bottom:22px;text-shadow:0 4px 16px #000}}.caption{{font:29px/1.36 Arial,sans-serif;color:white;max-width:900px;margin:auto}}
    .scene-description{{position:absolute;left:85px;right:85px;bottom:165px;text-align:center;font:italic 21px/1.3 Arial,sans-serif;color:#f6dca8;opacity:.85}}
    .puppet{{filter:drop-shadow(0 18px 16px #070b1880);transform-box:fill-box;transform-origin:50% 85%;animation:bob 2.8s ease-in-out infinite alternate}}.puppet .arms{{transform-box:fill-box;transform-origin:50% 30%;animation:gesture 2.4s ease-in-out infinite alternate}}
    @keyframes bob{{from{{translate:0 0;rotate:-1deg}}to{{translate:0 -22px;rotate:1deg}}}}@keyframes gesture{{from{{rotate:-3deg}}to{{rotate:5deg}}}}
    .outro{{position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:100px;background:radial-gradient(circle at 50% 35%,#7e4058,#17152e 70%);font:700 66px/1.15 Georgia,serif;color:#ffe2a0}}
    </style></head><body><div id="root" data-composition-id="mythology-short" data-start="0" data-width="1080" data-height="1920">{''.join(blocks)}<div class="clip outro" id="outro" data-start="{max(0,total-4):.2f}" data-duration="4" data-track-index="4">{question}</div><audio id="narration" data-start="0" data-duration="{total:.2f}" data-track-index="5" src="assets/{ap.name}"></audio><script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});document.querySelectorAll('.scene').forEach(el=>{{const t=Number(el.dataset.start);tl.fromTo(el,{{opacity:0,scale:1.035}},{{opacity:1,scale:1,duration:.55,ease:'power2.out'}},t);tl.to(el,{{scale:1.035,duration:Number(el.dataset.duration)-.55,ease:'none'}},t+.55);}});window.__timelines=window.__timelines||{{}};window.__timelines['mythology-short']=tl;</script></div></body></html>'''
    out=Path("video/index.html"); out.parent.mkdir(parents=True,exist_ok=True); (out.parent/"assets").mkdir(parents=True,exist_ok=True); out.write_text(doc,encoding="utf-8")
    print(f"Created illustrated composition: {len(scenes)} scenes, {total:.1f}s")
if __name__=="__main__": main()
