"""Build a deterministic, Reel-inspired 2D vector cut-out composition for HyperFrames."""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

W, H = 1080, 1920
PALETTE = {
    "hanuman": ("#c9794c", "#e7a72e", "#713f32"),
    "krishna": ("#5487e8", "#e8b52e", "#263b78"),
    "rama": ("#5487d0", "#2e8b79", "#293c6e"),
    "sita": ("#d99b79", "#c95168", "#713c48"),
    "ravana": ("#a9574d", "#6e3b83", "#4a263d"),
    "shiva": ("#9bbbc9", "#e8e4d9", "#42566b"),
    "yudhishthira": ("#bd805d", "#397d70", "#60403a"),
    "bhima": ("#bd805d", "#b64b39", "#60403a"),
    "arjuna": ("#bd805d", "#3d6da8", "#60403a"),
    "duryodhana": ("#bd805d", "#7d477e", "#60403a"),
    "hero": ("#c78358", "#b64d55", "#57372e"),
}
ALIASES = {
    "dharmaraja": "yudhishthira", "yudhishthira": "yudhishthira",
    "bheema": "bhima", "bheem": "bhima", "arjun": "arjuna",
    "hanuman": "hanuman", "anjaneya": "hanuman",
    "krishna": "krishna", "rama": "rama", "sita": "sita",
    "ravana": "ravana", "shiva": "shiva",
}

def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)

def norm(value: object) -> str:
    return re.sub(r"[^a-z]", "", str(value or "").lower())

def canonical_character(value: object) -> str:
    key = norm(value)
    for alias, canonical in ALIASES.items():
        if alias in key:
            return canonical
    return "hero"

def scene_text(scene: dict) -> str:
    return " ".join(str(scene.get(k, "")) for k in (
        "visual_description", "setting", "action", "narration_segment",
        "props", "characters", "on_screen_text"
    )).lower()

def setting_for(scene: dict) -> str:
    text = scene_text(scene)
    for words, kind in (
        (("ocean", "sea", "wave", "water"), "ocean"),
        (("palace", "court", "hall", "kingdom", "throne"), "palace"),
        (("yagna", "yajna", "fire altar", "homam", "sacred fire"), "courtyard"),
        (("garden", "ashoka", "grove"), "garden"),
        (("mountain", "hill", "peak", "cliff"), "mountain"),
        (("battle", "war", "army"), "battle"),
        (("forest", "jungle", "hermitage"), "forest"),
        (("sky", "cloud", "heaven"), "sky"),
    ):
        if any(word in text for word in words):
            return kind
    return "palace"

def background(kind: str, index: int) -> str:
    palettes = {
        "palace": ("#f8dc91", "#e7ad58", "#fff0bd"),
        "courtyard": ("#f5d98c", "#d99a50", "#fff1c5"),
        "garden": ("#d6d99a", "#7eaa76", "#fff0b8"),
        "forest": ("#b9c98e", "#4e846c", "#f6d78e"),
        "ocean": ("#b9dce0", "#4a9eae", "#ffe0a0"),
        "mountain": ("#d6d8cf", "#718c9b", "#ffe3a0"),
        "battle": ("#e4b27f", "#a65f55", "#ffe2a0"),
        "sky": ("#a8c9e5", "#7d8db8", "#fff0bc"),
    }
    top, bottom, sun = palettes[kind]
    parts = [
        f'<defs><linearGradient id="bg{index}" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient><radialGradient id="halo{index}"><stop stop-color="{sun}" stop-opacity=".95"/><stop offset="1" stop-color="{sun}" stop-opacity="0"/></radialGradient></defs>',
        f'<rect width="{W}" height="{H}" fill="url(#bg{index})"/>',
        f'<circle cx="540" cy="600" r="500" fill="url(#halo{index})"/>',
        '<g class="sun-rays" opacity=".24" transform="translate(540 600)">',
    ]
    for n in range(24):
        parts.append(f'<path d="M-24 -145 L0 -490 L24 -145Z" fill="#fff5cf" transform="rotate({n*15})"/>')
    parts.append('</g>')
    if kind in ("palace", "courtyard"):
        parts += [
            '<path d="M0 260 Q540 -20 1080 260 V1380 H0Z" fill="#fff0c9" opacity=".55"/>',
            '<path d="M105 1210 V430 Q540 80 975 430 V1210" fill="none" stroke="#fff4d6" stroke-width="58" opacity=".95"/>',
            '<path d="M170 1190 V490 Q540 180 910 490 V1190" fill="none" stroke="#b97842" stroke-width="24" opacity=".7"/>',
        ]
        for x in (90, 880):
            parts.append(f'<rect x="{x}" y="450" width="110" height="850" rx="34" fill="#fff0c9" stroke="#bd834d" stroke-width="14"/><path d="M{x-28} 465 H{x+138} M{x-28} 1280 H{x+138}" stroke="#b97842" stroke-width="24"/>')
        parts.append('<path d="M0 1390 L1080 1390 L1080 1920 L0 1920Z" fill="#bd8451" opacity=".45"/>')
        for x in range(-500, 1600, 180):
            parts.append(f'<path d="M540 1390 L{x} 1920" stroke="#fff0c8" stroke-width="5" opacity=".45"/>')
        if kind == "courtyard":
            parts.append('<ellipse cx="540" cy="1350" rx="180" ry="90" fill="#8e5140"/><ellipse cx="540" cy="1320" rx="130" ry="65" fill="#f7a83b"/><path d="M480 1300 Q540 1170 600 1300 Q540 1260 480 1300Z" fill="#ffdf69"/>')
    elif kind in ("ocean", "battle"):
        parts.append('<path d="M0 980 Q150 900 300 980 T600 980 T900 980 T1200 980 V1920 H0Z" fill="#318b9a"/><path d="M0 1120 Q150 1050 300 1120 T600 1120 T900 1120 T1200 1120 M0 1330 Q150 1260 300 1330 T600 1330 T900 1330 T1200 1330" fill="none" stroke="#d4f1e6" stroke-width="18" opacity=".65"/>')
        if kind == "battle":
            parts.append('<path d="M0 1020 L180 720 L300 1020 L480 650 L650 1020 L830 740 L1080 1040 V1450 H0Z" fill="#7d5b56" opacity=".6"/>')
    elif kind in ("forest", "garden"):
        for x, y, r in ((90, 780, 150), (300, 650, 120), (820, 710, 145), (1030, 820, 150), (610, 860, 95)):
            parts.append(f'<path d="M{x} 1450 V{y+90}" stroke="#76533d" stroke-width="48"/><circle cx="{x}" cy="{y}" r="{r}" fill="#39795a"/><circle cx="{x-35}" cy="{y-35}" r="{r*.62}" fill="#6eaa68"/>')
        parts.append('<path d="M0 1400 Q270 1260 540 1400 T1080 1380 V1920 H0Z" fill="#527d4e"/>')
        if kind == "garden":
            for x in range(80, 1080, 140):
                parts.append(f'<circle cx="{x}" cy="1440" r="20" fill="#e99aa7"/><circle cx="{x+18}" cy="1422" r="11" fill="#ffe08a"/>')
    else:
        parts.append('<path d="M0 1250 L230 600 L410 980 L650 420 L1080 1240 V1920 H0Z" fill="#758e9b"/><path d="M650 420 L600 590 L670 555 L725 650Z" fill="#f7f4e9"/>')
    return "".join(parts)

def prop_svg(text: str, x: int, y: int, scale: float = 1.0) -> str:
    t = text.lower()
    if any(w in t for w in ("banana leaf", "leaf plate", "engili", "plate", "meal")):
        art = '<path d="M-120 0 Q0 -95 120 0 Q0 85 -120 0Z" fill="#5b9a4a" stroke="#245a3c" stroke-width="10"/><path d="M-100 0 Q0 5 100 0" stroke="#d6e69a" stroke-width="8"/><circle cx="0" cy="-10" r="25" fill="#f1c16c"/>'
    elif any(w in t for w in ("coin", "gold", "treasure", "wealth")):
        art = '<g fill="#f4c64f" stroke="#9e682b" stroke-width="8"><circle cx="-45" cy="0" r="43"/><circle cx="35" cy="-25" r="43"/><circle cx="65" cy="38" r="43"/></g><path d="M-45 -20 V20 M35 -45 V-5" stroke="#fff0a4" stroke-width="8"/>'
    elif any(w in t for w in ("scroll", "letter", "message", "script")):
        art = '<rect x="-75" y="-100" width="150" height="200" rx="14" fill="#fff0c6" stroke="#a86c3e" stroke-width="12"/><path d="M-42 -45 H42 M-42 0 H42 M-42 45 H20" stroke="#a86c3e" stroke-width="9"/>'
    elif any(w in t for w in ("mace", "gada")):
        art = '<path d="M0 15 L0 175" stroke="#8b5a34" stroke-width="24"/><path d="M0 -100 C-85 -100 -90 20 0 40 C90 20 85 -100 0 -100Z" fill="#e5b23f" stroke="#8b5a34" stroke-width="12"/>'
    elif any(w in t for w in ("bow", "arrow")):
        art = '<path d="M-70 -120 Q100 0 -70 120" fill="none" stroke="#8a4d2d" stroke-width="18"/><path d="M-70 -120 L-70 120" stroke="#f4d47e" stroke-width="8"/><path d="M-70 0 L95 0" stroke="#8a4d2d" stroke-width="7"/>'
    elif any(w in t for w in ("pot", "cooking", "kitchen")):
        art = '<path d="M-90 -40 H90 L70 100 Q0 145 -70 100Z" fill="#b65d3d" stroke="#743e32" stroke-width="12"/><path d="M-55 -65 Q0 -130 55 -65" fill="none" stroke="#fff0c5" stroke-width="13"/>'
    elif any(w in t for w in ("fire", "yagna", "yajna", "homam")):
        art = '<path d="M0 100 Q-100 20 -25 -90 Q-20 -10 15 -30 Q75 -150 80 -25 Q155 55 0 100Z" fill="#f28d32" stroke="#a84c2d" stroke-width="9"/><path d="M0 65 Q-35 15 8 -35 Q12 5 38 18 Q52 55 0 65Z" fill="#ffe27a"/>'
    else:
        art = '<path d="M-60 55 L0 -70 L60 55Z" fill="#e9bd57" stroke="#8c5c37" stroke-width="10"/>'
    return f'<g class="prop" transform="translate({x} {y}) scale({scale})">{art}</g>'

def puppet(name: str, x: int, y: int, scale: float, idx: int, emotion: str, action: str) -> str:
    skin, cloth, outline = PALETTE.get(name, PALETTE["hero"])
    hair = "#332638"
    if name == "hanuman":
        head = '<path d="M-72 -365 Q-115 -440 -45 -455 Q30 -490 78 -410 L65 -355Z" fill="#9c593b"/>'
        crest = '<path d="M42 -430 Q75 -520 108 -465 Q70 -430 42 -430Z" fill="#248c68"/><circle cx="95" cy="-470" r="22" fill="#2c9c72"/>'
        tail = '<path d="M82 -220 Q190 -310 205 -205 Q215 -135 155 -145" fill="none" stroke="#b86c42" stroke-width="24" stroke-linecap="round"/>'
    elif name == "krishna":
        head = '<path d="M-70 -385 Q-30 -465 55 -425 Q85 -395 70 -355Z" fill="#263c78"/>'
        crest = '<path d="M25 -430 Q-10 -535 60 -515 Q105 -490 45 -440Z" fill="#268c65"/><circle cx="50" cy="-500" r="18" fill="#2ca06e"/>'
        tail = ""
    else:
        head = f'<path d="M-70 -390 Q-35 -455 35 -430 Q75 -410 70 -370Z" fill="{hair}"/>'
        crest = '<path d="M-62 -395 L-42 -485 L0 -430 L42 -485 L62 -395Z" fill="#e9b943" stroke="#9b682f" stroke-width="9"/>'
        tail = ""
    if emotion in ("surprised", "shock", "afraid"):
        eyes = '<ellipse cx="-30" cy="-350" rx="17" ry="24" fill="white"/><ellipse cx="30" cy="-350" rx="17" ry="24" fill="white"/><circle cx="-30" cy="-348" r="8" fill="#201b2a"/><circle cx="30" cy="-348" r="8" fill="#201b2a"/>'
        mouth = '<ellipse cx="0" cy="-292" rx="17" ry="24" fill="#512c36"/>'
    elif emotion in ("happy", "joy", "laughing"):
        eyes = '<path d="M-48 -350 Q-30 -372 -12 -350 M12 -350 Q30 -372 48 -350" fill="none" stroke="#211b29" stroke-width="12" stroke-linecap="round"/>'
        mouth = '<path d="M-24 -300 Q0 -270 24 -300" fill="none" stroke="#743c3a" stroke-width="12" stroke-linecap="round"/>'
    elif emotion in ("determined", "angry", "focused"):
        eyes = '<ellipse cx="-30" cy="-350" rx="13" ry="17" fill="white"/><ellipse cx="30" cy="-350" rx="13" ry="17" fill="white"/><circle cx="-30" cy="-350" r="7" fill="#201b2a"/><circle cx="30" cy="-350" r="7" fill="#201b2a"/><path d="M-52 -380 L-10 -365 M10 -365 L52 -380" stroke="#332638" stroke-width="11"/>'
        mouth = '<path d="M-22 -295 H22" stroke="#743c3a" stroke-width="11" stroke-linecap="round"/>'
    else:
        eyes = '<ellipse cx="-30" cy="-350" rx="14" ry="19" fill="white"/><ellipse cx="30" cy="-350" rx="14" ry="19" fill="white"/><circle cx="-30" cy="-348" r="7" fill="#201b2a"/><circle cx="30" cy="-348" r="7" fill="#201b2a"/>'
        mouth = '<path d="M-22 -300 Q0 -282 22 -300" fill="none" stroke="#743c3a" stroke-width="10" stroke-linecap="round"/>'
    if any(w in action for w in ("fold", "pray", "bow", "namaste", "respect")):
        left_arm = 'M-65 -190 Q-25 -275 0 -240'
        right_arm = 'M65 -190 Q25 -275 0 -240'
    elif any(w in action for w in ("leap", "jump", "fly", "soar", "raise", "lift")):
        left_arm = 'M-65 -190 Q-130 -285 -155 -355'
        right_arm = 'M65 -190 Q130 -285 155 -355'
    elif any(w in action for w in ("point", "gesture", "show", "offer", "speak", "ask")):
        left_arm = 'M-65 -190 Q-125 -145 -160 -95'
        right_arm = 'M65 -190 Q125 -245 175 -285'
    else:
        left_arm = 'M-65 -190 Q-120 -135 -145 -65'
        right_arm = 'M65 -190 Q120 -135 145 -65'
    ident = f"char-{idx}"
    return f'''<g id="{ident}" class="character" transform="translate({x} {y}) scale({scale})">
      <ellipse cy="15" rx="150" ry="28" fill="#543d2d" opacity=".22"/>
      <g class="legs"><path d="M-45 -100 L-65 30 M45 -100 L65 30" stroke="{outline}" stroke-width="44" stroke-linecap="round"/><path d="M-45 -100 L-65 30 M45 -100 L65 30" stroke="{skin}" stroke-width="29" stroke-linecap="round"/><path d="M-95 32 H-35 M35 32 H95" stroke="#e7b75b" stroke-width="24" stroke-linecap="round"/></g>
      <path d="M-94 -300 Q-115 -245 -88 -100 Q0 -48 88 -100 Q115 -245 94 -300Z" fill="{cloth}" stroke="{outline}" stroke-width="12"/>
      <path d="M-76 -255 L0 -160 L76 -255" fill="none" stroke="#f5d27c" stroke-width="13"/>
      <path d="M-58 -115 Q0 -82 58 -115" fill="none" stroke="#f8dc8e" stroke-width="12"/>
      <g class="arm-left" transform="translate(-65 -205)"><path d="{left_arm}" transform="translate(65 205)" stroke="{outline}" stroke-width="53" fill="none" stroke-linecap="round"/><path d="{left_arm}" transform="translate(65 205)" stroke="{skin}" stroke-width="34" fill="none" stroke-linecap="round"/><circle cx="-80" cy="-85" r="20" fill="{skin}" stroke="{outline}" stroke-width="8"/></g>
      <g class="arm-right" transform="translate(65 -205)"><path d="{right_arm}" transform="translate(-65 205)" stroke="{outline}" stroke-width="53" fill="none" stroke-linecap="round"/><path d="{right_arm}" transform="translate(-65 205)" stroke="{skin}" stroke-width="34" fill="none" stroke-linecap="round"/><circle cx="110" cy="-80" r="20" fill="{skin}" stroke="{outline}" stroke-width="8"/></g>
      <circle cy="-355" r="88" fill="{skin}" stroke="{outline}" stroke-width="12"/>
      {head}{crest}{eyes}{mouth}{tail}
      <path d="M-40 -260 Q0 -235 40 -260" stroke="#f6d47b" stroke-width="10" fill="none"/>
    </g>'''

def main() -> None:
    story_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/stories/latest.json")
    audio_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("video/assets/narration.wav")
    data = json.loads(story_path.read_text(encoding="utf-8"))
    scenes = data["scenes"]
    total = sum(float(s["duration_seconds"]) for s in scenes)
    if not 30 <= total <= 60:
        raise ValueError(f"Video duration must be 30–60 seconds; got {total}")
    blocks: list[str] = []
    timeline: list[str] = []
    cursor = 0.0
    for i, scene in enumerate(scenes, 1):
        duration = float(scene["duration_seconds"])
        start = cursor
        cursor += duration
        kind = setting_for(scene)
        text = scene_text(scene)
        raw_chars = scene.get("characters") or []
        names = [canonical_character(n) for n in raw_chars if str(n).strip()]
        if not names:
            names = [canonical_character(text)]
        names = list(dict.fromkeys(names))[:3]
        emotion = str(scene.get("emotion") or ("determined" if any(w in text for w in ("fight", "battle", "leap", "promise")) else "happy" if any(w in text for w in ("smile", "laugh", "joy")) else "calm")).lower()
        action = str(scene.get("action") or text).lower()
        positions = [(380, 1430, 1.0), (730, 1460, .78), (540, 1190, .68)]
        figures = "".join(puppet(name, *positions[j], i * 10 + j, emotion, action) for j, name in enumerate(names))
        # Use the scene's actual setting/action/props to select a visible story prop.
        prop_text = " ".join(str(scene.get(k, "")) for k in ("props", "action", "visual_description", "narration_segment"))
        prop = prop_svg(prop_text, 790 if len(names) == 1 else 540, 1110, .9)
        title = esc(scene.get("on_screen_text") or data.get("title", "An Indian Epic"))
        caption = esc(scene.get("narration_segment", ""))
        visual = esc(scene.get("visual_description", ""))
        camera = str(scene.get("camera") or "gentle_push").lower()
        sid = f"scene-{i}"
        blocks.append(f'''<section class="clip scene" id="{sid}" data-start="{start:.3f}" data-duration="{duration:.3f}" data-track-index="0">
          <svg class="art" viewBox="0 0 {W} {H}" role="img" aria-label="{visual}">{background(kind, i)}<g class="stage">{prop}{figures}</g></svg>
          <div class="top-card">{title}</div><div class="caption">{caption}</div>
        </section>''')
        timeline.append(f'''
          const scene{i}=document.querySelector("#{sid}");
          const stage{i}=scene{i}.querySelector(".stage");
          const chars{i}=scene{i}.querySelectorAll(".character");
          tl.fromTo(scene{i},{{opacity:0}},{{opacity:1,duration:0.22,ease:"none"}},{start});
          tl.fromTo(stage{i},{{scale:{1.035 if camera in ("gentle_push","push_in","zoom_in") else 1.0},x:{-18 if camera=="pan_right" else 18 if camera=="pan_left" else 0}}},{{scale:1,x:0,duration:{max(0.7, duration-0.2):.3f},ease:"power1.out"}},{start});
          chars{i}.forEach((ch,j)=>{{
            tl.fromTo(ch,{{y:24,rotation:-2}},{{y:0,rotation:0,duration:0.45,ease:"back.out(1.5)"}},{start+0.08}+j*0.09);
            tl.to(ch,{{y:-10,duration:0.65,yoyo:true,repeat:Math.max(0,Math.floor(({duration}-1.0)/1.3)) ,ease:"sine.inOut"}},{start+0.65});
          }});
          tl.to(scene{i}.querySelector(".sun-rays"),{{rotation:5,duration:{duration:.3f},ease:"none"}},{start});
          tl.fromTo(scene{i}.querySelector(".top-card"),{{y:-65,opacity:0,rotation:-2}},{{y:0,opacity:1,rotation:0,duration:0.45,ease:"back.out(1.7)"}},{start+0.12});
          tl.fromTo(scene{i}.querySelector(".caption"),{{y:55,opacity:0}},{{y:0,opacity:1,duration:0.35,ease:"power2.out"}},{start+0.3});
          tl.fromTo(scene{i}.querySelector(".prop"),{{scale:0.55,opacity:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,duration:0.45,ease:"back.out(1.8)"}},{start+0.35});
        ''')
    question = esc(data.get("closing_question") or "What would you have done?")
    outro_start = max(0.0, total - 3.5)
    blocks.append(f'''<section class="clip outro" id="outro" data-start="{outro_start:.3f}" data-duration="3.5" data-track-index="4"><div class="outro-halo"></div><div class="outro-copy">{question}</div></section>''')
    root = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
      *{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#f5d58b;font-family:Arial,sans-serif}}
      #root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#f5d58b;color:#34271f}}
      .clip{{position:absolute;inset:0;width:{W}px;height:{H}px;overflow:hidden}}.scene{{opacity:0}}.art{{position:absolute;inset:0;width:100%;height:100%}}
      .sun-rays{{transform-origin:540px 600px}}
      .top-card{{position:absolute;top:80px;left:110px;right:110px;min-height:92px;padding:18px 30px;background:#fffdf4;border:5px solid #9f4b43;box-shadow:0 12px 0 #5b342c35;transform:rotate(-1.5deg);text-align:center;color:#963d3e;font:italic 700 36px/1.2 Georgia,serif}}
      .caption{{position:absolute;left:60px;right:60px;bottom:100px;min-height:150px;padding:28px 35px;background:#fffdf0;border:4px solid #8a5b3d;border-radius:24px;box-shadow:0 12px 0 #53372735;text-align:center;color:#35271f;font:700 36px/1.25 Arial,sans-serif}}
      .character{{transform-box:fill-box;transform-origin:50% 85%;filter:drop-shadow(0 10px 8px #563d2b35)}}.arm-left,.arm-right{{transform-box:fill-box;transform-origin:50% 15%}}
      .prop{{transform-box:fill-box;transform-origin:50% 50%;filter:drop-shadow(0 9px 8px #4b332b30)}}
      .outro{{display:grid;place-items:center;background:radial-gradient(circle at 50% 42%,#ffe8a6,#dca65a 75%);opacity:0}}
      .outro-halo{{position:absolute;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,#fff9dc 0%,#f5d47f 45%,#e6b45e 70%,transparent 71%);opacity:.9}}
      .outro-copy{{position:relative;margin:100px;padding:70px 55px;background:#fffdf2;border:5px solid #a34e40;border-radius:32px;text-align:center;color:#773c36;font:700 62px/1.15 Georgia,serif;box-shadow:0 18px 0 #5b342c35}}
    </style></head><body><div id="root" data-composition-id="mythology-short" data-start="0" data-duration="{total:.3f}" data-width="{W}" data-height="{H}">
      {''.join(blocks)}
      <audio class="clip" id="narration" data-start="0" data-duration="{total:.3f}" data-track-index="5" src="assets/{esc(audio_path.name)}"></audio>
      <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
      <script>
        window.__timelines=window.__timelines||{{}};
        const tl=gsap.timeline({{paused:true}});
        {''.join(timeline)}
        tl.fromTo("#outro",{{opacity:0,scale:0.94}},{{opacity:1,scale:1,duration:0.45,ease:"back.out(1.5)"}},{outro_start});
        window.__timelines["mythology-short"]=tl;
      </script>
    </div></body></html>'''
    out = Path("video/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    (out.parent / "assets").mkdir(parents=True, exist_ok=True)
    out.write_text(root, encoding="utf-8")
    print(f"Created Reel-inspired vector composition: {len(scenes)} scenes, {total:.1f}s, characters and props generated per scene.")

if __name__ == "__main__":
    main()
