"""Build a portrait HyperFrames composition from the validated story JSON."""
from __future__ import annotations
import html, json, sys
from pathlib import Path

def esc(value: str) -> str:
    return html.escape(str(value), quote=True)

def main() -> int:
    story_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/stories/latest.json")
    audio_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("video/assets/narration.wav")
    out = Path("video/index.html")
    data = json.loads(story_path.read_text(encoding="utf-8"))
    scenes = data["scenes"]
    total = sum(float(s["duration_seconds"]) for s in scenes)
    if not 30 <= total <= 60:
        raise ValueError(f"Video duration must be 30–60 seconds; got {total}")

    chunks = []
    cursor = 0.0
    for i, scene in enumerate(scenes, 1):
        duration = float(scene["duration_seconds"])
        start = cursor
        cursor += duration
        title = esc(scene.get("on_screen_text") or data["title"])
        description = esc(scene.get("visual_description") or "")
        # Reusable stylized puppet silhouette: distinct colors and simple expressive face.
        hue = (i * 47 + 18) % 360
        chunks.append(f'''
<section id="scene-{i}" class="clip scene" data-start="{start:.2f}" data-duration="{duration:.2f}" data-track-index="0">
  <div class="stars"></div>
  <div class="sun-halo"></div>
  <div class="puppet" style="--hue:{hue}">
    <div class="crown"><span>✦</span></div>
    <div class="head"><div class="eye left"></div><div class="eye right"></div><div class="smile"></div></div>
    <div class="body"><div class="ornament">✦</div></div>
    <div class="arm arm-left"></div><div class="arm arm-right"></div>
  </div>
  <div class="scene-copy">
    <div class="eyebrow">AN INDIAN MYTHOLOGY STORY</div>
    <h1>{title}</h1>
    <p>{description}</p>
  </div>
  <div class="scene-number">{i:02d} / {len(scenes):02d}</div>
</section>''')

    title = esc(data["title"])
    tradition = esc(data["tradition"])
    question = esc(data.get("closing_question", "What would you have done?"))
    audio_src = "assets/" + audio_path.name
    html_doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{box-sizing:border-box}} html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#100b27;font-family:Georgia,serif}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(ellipse at 50% 35%,#382052 0%,#17112f 48%,#090817 100%);color:#fff}}
.scene{{position:absolute;inset:0;width:1080px;height:1920px;overflow:hidden;padding:100px 82px}}
.stars{{position:absolute;inset:0;background-image:radial-gradient(#ffe9a6 1.5px,transparent 2px),radial-gradient(#fff 1px,transparent 1.5px);background-size:113px 127px,173px 191px;background-position:10px 20px,70px 90px;opacity:.5}}
.sun-halo{{position:absolute;width:730px;height:730px;left:175px;top:180px;border-radius:50%;background:radial-gradient(circle,#f6c45b55 0%,#b84b6940 48%,transparent 70%);border:2px solid #f6c45b44}}
.puppet{{position:absolute;left:50%;top:650px;width:370px;height:620px;transform:translateX(-50%);filter:drop-shadow(0 18px 22px #0008)}}
.crown{{position:absolute;left:126px;top:0;width:118px;height:110px;background:linear-gradient(135deg,#ffe58b,#c77b20);clip-path:polygon(50% 0,62% 34%,100% 10%,82% 100%,18% 100%,0 10%,38% 34%);display:grid;place-items:center;color:#6b2b19;font-size:42px}}
.head{{position:absolute;left:105px;top:85px;width:160px;height:170px;border-radius:48% 48% 45% 45%;background:linear-gradient(135deg,#f6c58d,#b76a45);border:9px solid #26142a}}
.eye{{position:absolute;top:65px;width:17px;height:24px;border-radius:50%;background:#211329}}.eye.left{{left:40px}}.eye.right{{right:40px}}
.smile{{position:absolute;left:61px;top:112px;width:32px;height:14px;border-bottom:5px solid #762e34;border-radius:50%}}
.body{{position:absolute;left:58px;top:240px;width:255px;height:300px;background:linear-gradient(140deg,hsl(var(--hue),65%,62%),hsl(var(--hue),70%,30%));clip-path:polygon(25% 0,75% 0,100% 100%,0 100%);border:5px solid #f6c45b}}
.ornament{{position:absolute;left:103px;top:70px;font-size:65px;color:#ffe7a0}}
.arm{{position:absolute;top:270px;width:48px;height:250px;border-radius:30px;background:#d99b69;border:8px solid #28162d;transform-origin:top center}}
.arm-left{{left:45px;transform:rotate(22deg)}}.arm-right{{right:42px;transform:rotate(-22deg)}}
.scene-copy{{position:absolute;left:80px;right:80px;bottom:210px;text-align:center}}
.eyebrow{{font:700 22px Arial,sans-serif;letter-spacing:7px;color:#f7d98a;margin-bottom:28px}}
h1{{font-size:76px;line-height:1.08;margin:0 auto 28px;color:#ffe4a0;text-shadow:0 5px 22px #0009;max-width:900px}}
p{{font:30px/1.35 Arial,sans-serif;color:#f2e7df;max-width:850px;margin:0 auto}}
.scene-number{{position:absolute;bottom:80px;right:80px;font:700 20px Arial,sans-serif;letter-spacing:4px;color:#e9c77b}}
.brand{{position:absolute;top:65px;left:0;right:0;text-align:center;font:700 20px Arial,sans-serif;letter-spacing:8px;color:#f6d58a}}
</style></head><body>
<div id="root" data-composition-id="mythology-short" data-start="0" data-width="1080" data-height="1920">
<div class="brand clip" id="brand" data-start="0" data-duration="{total:.2f}" data-track-index="3">MYTHOLOGY • STORIES</div>
{''.join(chunks)}
<div class="clip" id="outro" data-start="{max(0,total-4):.2f}" data-duration="4" data-track-index="4" style="position:absolute;left:60px;right:60px;top:130px;text-align:center;font:700 30px Arial,sans-serif;color:#ffe4a0;text-shadow:0 3px 12px #000">{question}</div>
<audio id="narration" data-start="0" data-duration="{total:.2f}" data-track-index="5" src="{audio_src}"></audio>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script>
const tl=gsap.timeline({{paused:true}});
document.querySelectorAll(".scene").forEach((el)=>{{
 const id=el.id;
 tl.fromTo("#"+id,{{opacity:0,scale:0.97}},{{opacity:1,scale:1,duration:0.55,ease:"power2.out"}},Number(el.dataset.start));
 tl.fromTo("#"+id+" .puppet",{{y:30,rotation:-2}},{{y:-18,rotation:2,duration:2.2,yoyo:true,repeat:Math.max(0,Math.floor(Number(el.dataset.duration)/2)-1),ease:"sine.inOut"}},Number(el.dataset.start)+0.2);
 tl.fromTo("#"+id+" h1",{{y:35,opacity:0}},{{y:0,opacity:1,duration:0.6}},Number(el.dataset.start)+0.25);
}});
window.__timelines=window.__timelines||{{}};
window.__timelines["mythology-short"]=tl;
</script>
</div></body></html>'''
    out.parent.mkdir(parents=True, exist_ok=True)
    (out.parent / "assets").mkdir(parents=True, exist_ok=True)
    out.write_text(html_doc, encoding="utf-8")
    print(f"Created {out} ({total:.1f}s), story={title}, tradition={tradition}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
