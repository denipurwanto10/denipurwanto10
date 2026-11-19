#!/usr/bin/env python3
"""Generate the Bandung banner from live weather (Open-Meteo, no API key)."""
import json, random, sys, time, urllib.request

OUT = sys.argv[1] if len(sys.argv) > 1 else "bandung-night.svg"
URL = ("https://api.open-meteo.com/v1/forecast?latitude=-6.9175&longitude=107.6191"
       "&current=temperature_2m,weather_code,is_day"
       "&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FJakarta&forecast_days=1")

def fetch():
    for _ in range(3):
        try:
            with urllib.request.urlopen(URL, timeout=20) as r:
                d = json.load(r)
            return (round(d["current"]["temperature_2m"]), round(d["daily"]["temperature_2m_max"][0]),
                    round(d["daily"]["temperature_2m_min"][0]), int(d["current"]["weather_code"]),
                    bool(d["current"]["is_day"]))
        except Exception as e:
            print("fetch failed:", e, file=sys.stderr); time.sleep(3)
    sys.exit(1)  # API down -> keep the old banner

# test mode:  python banner.py out.svg TEMP HI LO WMO_CODE IS_DAY(0/1)
if len(sys.argv) > 6:
    TEMP, HI, LO, CODE = (int(x) for x in sys.argv[2:6]); DAY = bool(int(sys.argv[6]))
else:
    TEMP, HI, LO, CODE, DAY = fetch()

THUNDER = CODE >= 95
DRIZZLE = CODE in (51, 53, 55, 56, 57)
RAIN = DRIZZLE or CODE in (61, 63, 65, 66, 67, 80, 81, 82) or THUNDER
FOG = CODE in (45, 48)
CLEAR = CODE == 0
PARTLY = CODE in (1, 2)
NIGHT = not DAY
GRAY = RAIN or CODE >= 3
NRAIN = 0 if not RAIN else 45 if DRIZZLE else 150 if (CODE in (65, 67, 82) or THUNDER) else 95
NRIP = 14 if RAIN else 0
NSTARS = 0 if DAY else 46 if CLEAR else 24 if PARTLY else 0 if RAIN else 8
CLOUDS = CODE >= 2
SHOW_MOON = NIGHT and CODE <= 3
SHOW_SUN = DAY and CODE <= 2
LAMPS = (96, 300, 904, 1100) if (NIGHT or GRAY) else ()

if CLEAR: LABEL = "Cerah"
elif PARTLY: LABEL = "Cerah berawan"
elif FOG: LABEL = "Berkabut"
elif THUNDER: LABEL = "Hujan petir"
elif DRIZZLE: LABEL = "Gerimis"
elif RAIN: LABEL = "Hujan"
else: LABEL = "Berawan"
NOTE = ("// petir, save dulu kodenya" if THUNDER
        else "// gerimis tipis, cocok ngoding sambil ngopi" if DRIZZLE
        else "// hujan, cocok ngoding sambil ngopi" if RAIN
        else "// berkabut, khas Bandung" if FOG
        else "// langit cerah, semangat ngoding" if CLEAR and DAY
        else "// malam cerah, cocok ngoding santai" if CLEAR
        else "// adem, cocok ngoding sambil ngopi")

PAL = {}
if DAY:
    sky = ("#6a7c92", "#93a4b6", "#c3ced9") if GRAY else ("#4f9be8", "#8cc5f2", "#d6ecfb")
    PAL = {"#050813": sky[0], "#101734": sky[1], "#2b2c5e": sky[2],
           "#232b5a": "#5d86b8", "#141a3a": "#3f628f", "#1c2349": "#4a739f", "#10152f": "#34557f",
           "#2b3560": "#6f8fbd", "#141a35": "#3d5883", "#1a2145": "#7c9cc6", "#11162f": "#5b7ba4",
           "#2a3358": "#c9d2e6", "#363a62": "#b5bdd6", "#58476a": "#a6a3c0",
           "#1c2347": "#5a6788", "#121830": "#434e6e", "#121a30": "#3a4258", "#090d1a": "#262c3e",
           "#1b2442": "#4a5470", "#7c6bff": "#ffe2b0",
           "#5d678f": "#d3daf3", "#6f7aa8": "#d3daf3", "#8f9bc9": "#dfe5fa", 'fill="#0b1126" fill-opacity=".45"': 'fill="#0b1126" fill-opacity=".62"',
           ".wy{fill:#ffd98a;fill-opacity:.85}.wc{fill:#7dd3fc;fill-opacity:.8}.wp{fill:#c4b5fd;fill-opacity:.8}":
           ".wy{fill:#8fa6c9;fill-opacity:.55}.wc{fill:#7fa3cf;fill-opacity:.5}.wp{fill:#9aa3d0;fill-opacity:.5}",
           'stop-color="#a5b4fc" stop-opacity="0"/><stop offset="1" stop-color="#a5b4fc" stop-opacity=".2"':
           'stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".35"'}

random.seed(7)
B=236
o=[]
a=o.append

# ---------- helpers ----------
def win_cls():
    r=random.random()
    return ' a%d'%random.randint(1,6) if r<.14 else ''
def wcol():
    r=random.random()
    return 'wy' if r<.62 else ('wc' if r<.9 else 'wp')

def tower(x,w,top,style='flat',antenna=False):
    s=''
    if style=='slant':
        s+=f'<polygon points="{x},{top+16} {x+w},{top} {x+w},{B} {x},{B}" fill="url(#tw)"/>'
    elif style=='step':
        s+=f'<rect x="{x}" y="{top+14}" width="{w}" height="{B-top-14}" fill="url(#tw)"/><rect x="{x+8}" y="{top}" width="{w-16}" height="16" fill="url(#tw)"/>'
    else:
        s+=f'<rect x="{x}" y="{top}" width="{w}" height="{B-top}" rx="1.5" fill="url(#tw)"/>'
    s+=f'<rect x="{x}" y="{top}" width="1.4" height="{B-top}" fill="#9fb0ff" opacity=".28"/>'
    if antenna:
        cx=x+w/2
        s+=f'<rect x="{cx-.7}" y="{top-26}" width="1.4" height="26" fill="#6b7aa8"/><circle class="bc" cx="{cx}" cy="{top-27}" r="2.2" fill="#ff5c7a"/>'
    cols=max(1,(w-10)//10)
    start=top+(18 if style in('slant','step') else 10)
    y=start
    while y<B-14:
        for c in range(cols):
            if random.random()<.58:
                s+=f'<rect class="{wcol()}{win_cls()}" x="{x+6+c*10}" y="{y}" width="5" height="7" rx="1"/>'
        y+=14
    return s

o.append('''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="300" viewBox="0 0 1200 300" role="img" aria-label="Bandung malam hari, 22°C gerimis">
<title>Bandung at night — 22°C, gerimis</title>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050813"/><stop offset=".55" stop-color="#101734"/><stop offset="1" stop-color="#2b2c5e"/></linearGradient>
<radialGradient id="hz" cx=".5" cy="1" r=".6"><stop offset="0" stop-color="#7c6bff" stop-opacity=".35"/><stop offset="1" stop-color="#7c6bff" stop-opacity="0"/></radialGradient>
<radialGradient id="moonglow"><stop offset="0" stop-color="#c7d2fe" stop-opacity=".35"/><stop offset="1" stop-color="#c7d2fe" stop-opacity="0"/></radialGradient>
<radialGradient id="halo"><stop offset="0" stop-color="#ffc857" stop-opacity=".4"/><stop offset="1" stop-color="#ffc857" stop-opacity="0"/></radialGradient>
<radialGradient id="lamp"><stop offset="0" stop-color="#ffd98a" stop-opacity=".6"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient>
<radialGradient id="wash" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffc857" stop-opacity=".28"/><stop offset="1" stop-color="#ffc857" stop-opacity="0"/></radialGradient>
<linearGradient id="m1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232b5a"/><stop offset="1" stop-color="#141a3a"/></linearGradient>
<linearGradient id="m2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2349"/><stop offset="1" stop-color="#10152f"/></linearGradient>
<linearGradient id="tw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b3560"/><stop offset="1" stop-color="#141a35"/></linearGradient>
<linearGradient id="far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a2145"/><stop offset="1" stop-color="#11162f"/></linearGradient>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3358"/><stop offset=".65" stop-color="#363a62"/><stop offset="1" stop-color="#58476a"/></linearGradient>
<linearGradient id="roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2347"/><stop offset="1" stop-color="#121830"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff0b8"/><stop offset="1" stop-color="#ffb938"/></linearGradient>
<linearGradient id="arch" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe9a8"/><stop offset="1" stop-color="#ffb347"/></linearGradient>
<linearGradient id="mist" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a5b4fc" stop-opacity="0"/><stop offset="1" stop-color="#a5b4fc" stop-opacity=".2"/></linearGradient>
<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121a30"/><stop offset="1" stop-color="#090d1a"/></linearGradient>
<linearGradient id="rmg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="cone" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff3c4" stop-opacity=".55"/><stop offset="1" stop-color="#fff3c4" stop-opacity="0"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset="1" stop-color="#fff" stop-opacity=".04"/></linearGradient>
<mask id="rm"><rect x="0" y="238" width="1200" height="62" fill="url(#rmg)"/></mask>
<mask id="mm"><rect width="1200" height="300" fill="#fff"/><circle cx="1082" cy="52" r="19" fill="#000"/></mask>
<clipPath id="c"><rect width="1200" height="300" rx="22"/></clipPath>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.6"/></filter>
<filter id="cloudb" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
<style>
.tw{animation:tw 3.4s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.8}50%{opacity:.12}}
.wy{fill:#ffd98a;fill-opacity:.85}.wc{fill:#7dd3fc;fill-opacity:.8}.wp{fill:#c4b5fd;fill-opacity:.8}
.a1{animation:fl 6s steps(1) infinite}.a2{animation:fl 7.5s steps(1) infinite 1.2s}.a3{animation:fl 5s steps(1) infinite 2.1s}
.a4{animation:fl 8.5s steps(1) infinite .6s}.a5{animation:fl 6.5s steps(1) infinite 3s}.a6{animation:fl 9s steps(1) infinite 4s}
@keyframes fl{0%,62%{opacity:1}63%,100%{opacity:.12}}
.bc{animation:bc 1.8s ease-in-out infinite}
@keyframes bc{0%,100%{opacity:1}50%{opacity:.1}}
.sk{animation:sk 2.4s ease-in-out infinite}
@keyframes sk{0%,100%{opacity:.55}50%{opacity:1}}
.cl{animation:cl 70s linear infinite}
@keyframes cl{from{transform:translateX(-320px)}to{transform:translateX(1400px)}}
.ms{animation:ms 45s linear infinite}
@keyframes ms{from{transform:translateX(-260px)}to{transform:translateX(1360px)}}
.dash{animation:dash 1.2s linear infinite}
@keyframes dash{to{stroke-dashoffset:-48}}
.r{stroke:#b9c6ff;stroke-width:1;stroke-linecap:round;opacity:.3;animation:rn 1s linear infinite}
.r2{animation-duration:1.3s;animation-delay:-.4s}.r3{animation-duration:.8s;animation-delay:-.2s;opacity:.22}
.r4{animation-duration:1.15s;animation-delay:-.7s}.r5{animation-duration:.95s;animation-delay:-.5s;opacity:.2}
@keyframes rn{from{transform:translate(0,-20px)}to{transform:translate(-40px,330px)}}
.rp{fill:none;stroke:#cfd8ff;stroke-width:.8;transform-box:fill-box;transform-origin:center;animation:rp 2.4s ease-out infinite;opacity:0}
@keyframes rp{0%{transform:scale(.2);opacity:.6}100%{transform:scale(1.6);opacity:0}}
.dr{stroke:#93c5fd;stroke-width:1.6;stroke-linecap:round;animation:dr 1.2s ease-in infinite}
@keyframes dr{0%{opacity:0;transform:translateY(-3px)}40%{opacity:1}100%{opacity:0;transform:translateY(5px)}}
.pulse{animation:pu 3s ease-in-out infinite}
@keyframes fx{0%,90%,100%{opacity:0}92%{opacity:.35}94%{opacity:.05}96%{opacity:.3}}
.fx{animation:fx 7s linear infinite}
@keyframes pu{0%,100%{opacity:.75}50%{opacity:1}}
</style>
</defs>
<g clip-path="url(#c)">
<rect width="1200" height="300" fill="url(#sky)"/>
<rect width="1200" height="300" fill="url(#hz)"/>''')

# stars
for _ in range(NSTARS):
    x=random.randint(10,1190); y=random.randint(8,115)
    if x<390 and y<140: 
        if random.random()<.7: continue
    a(f'<circle class="tw" cx="{x}" cy="{y}" r="{random.choice([.8,1,1.3])}" fill="#dbe4ff" style="animation-delay:{random.random()*3.4:.2f}s"/>')

# moon
if SHOW_MOON:
    a('<circle cx="1082" cy="56" r="78" fill="url(#moonglow)"/><circle cx="1070" cy="60" r="22" fill="#eef2ff" mask="url(#mm)" opacity="%s"/>' % ('.9' if CODE<=1 else '.6'))
if SHOW_SUN:
    a('<circle cx="1070" cy="62" r="90" fill="url(#halo)"/><circle cx="1070" cy="62" r="24" fill="#fff4c2"/><circle cx="1070" cy="62" r="18" fill="#ffd45e"/>')

# clouds (rain clouds)
CLOUD_SVG=('<g filter="url(#cloudb)"><g class="cl" fill="#3a4272" fill-opacity=".55"><ellipse cx="120" cy="40" rx="110" ry="16"/><ellipse cx="210" cy="52" rx="80" ry="13"/></g>'
  '<g class="cl" style="animation-delay:-28s" fill="#2f3766" fill-opacity=".5"><ellipse cx="90" cy="86" rx="130" ry="14"/></g>'
  '<g class="cl" style="animation-delay:-50s" fill="#3a4272" fill-opacity=".45"><ellipse cx="60" cy="24" rx="100" ry="12"/></g></g>')
if CLOUDS:
    if NIGHT: a(CLOUD_SVG)
    else:
        gy = RAIN or CODE >= 3
        a(CLOUD_SVG.replace('#3a4272','#8a97a8' if gy else '#ffffff').replace('#2f3766','#7d8a9c' if gy else '#ffffff'))

# mountains
a('<path d="M0,196 C70,178 160,146 260,114 S380,86 410,84 L520,86 C566,92 620,112 700,122 S860,150 960,150 S1120,160 1200,176 V240 H0Z" fill="url(#m1)"/>')
a('<path d="M0,208 C120,192 220,172 330,162 S520,142 620,152 S800,176 900,178 S1100,188 1200,194 V240 H0Z" fill="url(#m2)"/>')

# far skyline
x=-10
while x<1200:
    w=random.randint(30,60); h=random.randint(24,56)
    a(f'<rect x="{x}" y="{B-h-6}" width="{w}" height="{h+6}" fill="url(#far)"/>')
    x+=w-2

# near towers
for t in [(0,52,152,'flat',False),(46,40,182,'slant',False),(82,58,140,'step',True),(136,44,170,'flat',False),(176,60,126,'slant',True),(232,42,162,'flat',False),(270,56,184,'step',False),(320,40,200,'flat',False)]:
    a(tower(*t))
for t in [(872,46,196,'flat',False),(914,46,166,'step',False),(956,62,134,'slant',True),(1014,40,176,'flat',False),(1050,58,122,'step',True),(1104,44,164,'flat',False),(1144,60,146,'slant',False)]:
    a(tower(*t))

# ---------- Gedung Sate (defs-like group, referenced twice) ----------
gs=[]
g=gs.append
g('<g id="gs">')
if NIGHT:
    g('<ellipse cx="600" cy="232" rx="300" ry="26" fill="url(#wash)"/>')
    g('<circle cx="600" cy="54" r="62" fill="url(#halo)"/>')
def mx(x): return 1200-x
# wings
for (x0,x1) in [(372,548),(652,828)]:
    g(f'<rect x="{x0}" y="196" width="{x1-x0}" height="{B-196}" fill="url(#wall)"/>')
    g(f'<rect x="{x0-6}" y="190" width="{x1-x0+12}" height="6" fill="url(#roof)"/>')
    g(f'<rect x="{x0}" y="213" width="{x1-x0}" height="1" fill="#ffc857" opacity=".3"/>')
    n=11; step=(x1-x0-12)/n
    for i in range(n):
        wx=x0+8+i*step
        g(f'<path d="M{wx:.1f} 233 V218 a3 3 0 0 1 6 0 V233Z" class="wy{win_cls()}"/>')
        g(f'<rect x="{wx:.1f}" y="200" width="6" height="8" rx="1" class="wy{win_cls()}" fill-opacity=".7"/>')
# end pavilions
for (x0,x1) in [(346,384),(816,854)]:
    g(f'<rect x="{x0}" y="170" width="{x1-x0}" height="{B-170}" fill="url(#wall)"/>')
    g(f'<polygon points="{x0-6},170 {x1+6},170 {x1-6},154 {x0+6},154" fill="url(#roof)"/>')
    for i in range(3):
        wx=x0+6+i*11
        g(f'<path d="M{wx} 233 V216 a3.5 3.5 0 0 1 7 0 V233Z" class="wy{win_cls()}"/>')
        g(f'<path d="M{wx} 206 V192 a3.5 3.5 0 0 1 7 0 V206Z" class="wy{win_cls()}" fill-opacity=".7"/>')
        g(f'<rect x="{wx}" y="176" width="7" height="9" rx="1" class="wc{win_cls()}"/>')
# central block
g(f'<rect x="536" y="160" width="128" height="{B-160}" fill="url(#wall)"/>')
g('<polygon points="526,160 674,160 652,132 548,132" fill="url(#roof)"/>')
g('<rect x="536" y="196" width="128" height="1.2" fill="#ffc857" opacity=".35"/>')
for i in range(6):
    ax=546+i*19.4
    g(f'<path d="M{ax:.1f} 236 V210 a5.5 5.5 0 0 1 11 0 V236Z" fill="url(#arch)" class="pulse" style="animation-delay:{i*.4:.1f}s"/>')
for i in range(7):
    wx=545+i*15.3
    g(f'<rect x="{wx:.1f}" y="172" width="6" height="13" rx="3" class="wy{win_cls()}" fill-opacity=".8"/>')
# tower tiers
g('<rect x="562" y="108" width="76" height="24" fill="url(#wall)"/><polygon points="554,108 646,108 630,92 570,92" fill="url(#roof)"/>')
for wx in (574,597,620): g(f'<rect x="{wx}" y="113" width="6" height="14" rx="3" class="wy{win_cls()}"/>')
g('<rect x="578" y="74" width="44" height="18" fill="url(#wall)"/><polygon points="572,74 628,74 616,62 584,62" fill="url(#roof)"/>')
for wx in (587,606): g(f'<rect x="{wx}" y="78" width="6" height="10" rx="3" class="wy"/>')
g('<rect x="590" y="52" width="20" height="10" fill="url(#wall)"/><polygon points="585,52 615,52 608,44 592,44" fill="url(#roof)"/>')
g('<rect x="597" y="55" width="6" height="5" rx="2.5" class="wy"/>')
# gold roof lines
g('<g filter="url(#glow)" fill="none" stroke="#ffc857" stroke-width="1.5" stroke-linecap="round">'
  '<path d="M366 190H554M646 190H834"/><path d="M552 132H648M570 92H630M584 62H616M592 44H608"/>'
  '<path d="M352 154H378M822 154H848"/><path d="M526 160H674" opacity=".7"/></g>')
# spire + six skewers
g('<rect x="599.2" y="8" width="1.6" height="36" fill="#cbd5ff" opacity=".8"/>')
g('<g filter="url(#glow)">'+''.join(f'<ellipse class="sk" cx="600" cy="{40-i*5.6:.1f}" rx="3.5" ry="2.5" fill="url(#gold)" style="animation-delay:{i*.25:.2f}s"/>' for i in range(6))+'</g>')
g('</g>')
a('<defs>'+''.join(gs)+'</defs>')
# plaza + road first
a('<rect x="0" y="236" width="1200" height="64" fill="url(#road)"/>')
a('<rect x="0" y="236" width="1200" height="7" fill="#1b2442"/><rect x="0" y="243" width="1200" height="1" fill="#ffc857" opacity=".25"/>')
# building
a('<use href="#gs" xlink:href="#gs"/>')
# reflection
a('<g mask="url(#rm)" opacity=".55" filter="url(#soft)"><use href="#gs" xlink:href="#gs" transform="translate(0 476) scale(1 -1)"/></g>')

# mist
a('<g class="ms"><ellipse cx="100" cy="224" rx="200" ry="14" fill="url(#mist)"/><ellipse cx="420" cy="214" rx="130" ry="10" fill="url(#mist)"/></g>')
a('<g class="ms" style="animation-delay:-22s"><ellipse cx="100" cy="228" rx="240" ry="12" fill="url(#mist)"/></g>')

# lamps
for lx in LAMPS:
    a(f'<circle cx="{lx}" cy="214" r="18" fill="url(#lamp)"/><rect x="{lx-.8}" y="214" width="1.6" height="22" fill="#4b5688"/><circle cx="{lx}" cy="213" r="2.2" fill="#fff1c1"/>')
    a(f'<ellipse cx="{lx}" cy="256" rx="14" ry="30" fill="#ffd98a" opacity=".07"/>')

# lane dash
a('<line x1="0" y1="270" x2="1200" y2="270" stroke="#3b4672" stroke-width="2" stroke-dasharray="24 24" class="dash"/>')
# ripples
for _ in range(NRIP):
    x=random.randint(10,1190); y=random.randint(247,296)
    a(f'<ellipse class="rp" cx="{x}" cy="{y}" rx="8" ry="2" style="animation-delay:{random.random()*2.4:.2f}s"/>')

# vehicles
def car(col,by,direction,dur,begin,w=64):
    cone=f'<polygon points="{w},{by+6} {w+70},{by-3} {w+70},{by+15}" fill="url(#cone)"/>'
    body=(f'<rect x="0" y="{by}" width="{w}" height="14" rx="6" fill="{col}"/>'
          f'<path d="M12 {by} L18 {by-8} H44 L52 {by} Z" fill="{col}"/>'
          f'<path d="M20 {by-1} L23 {by-6.5} H31 V{by-1}Z M34 {by-1} V{by-6.5} H42 L46 {by-1}Z" fill="#0b1020" opacity=".7"/>'
          f'<rect x="{w-4}" y="{by+4}" width="4" height="3.5" rx="1" fill="#fff6cf"/><rect x="0" y="{by+4}" width="3" height="3.5" rx="1" fill="#ff5c7a"/>'
          f'<circle cx="14" cy="{by+14}" r="4.4" fill="#05070f"/><circle cx="{w-14}" cy="{by+14}" r="4.4" fill="#05070f"/>')
    inner=cone+body
    if direction<0: inner=f'<g transform="translate({w} 0) scale(-1 1)">{inner}</g>'
    vals="-160 0;1260 0" if direction>0 else "1260 0;-160 0"
    return f'<g>{inner}<animateTransform attributeName="transform" type="translate" values="{vals}" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/></g>'
def bike(col,by,direction,dur,begin):
    inner=(f'<path d="M-30 {by} L-34 {by-4} L-26 {by-4}Z" fill="#fff6cf" opacity="0"/>'
           f'<polygon points="0,{by-2} 46,{by-8} 46,{by+4}" fill="url(#cone)" transform="translate(4 0)"/>'
           f'<circle cx="-12" cy="{by+5}" r="5" fill="none" stroke="#a5b4fc" stroke-width="1.8"/><circle cx="12" cy="{by+5}" r="5" fill="none" stroke="#a5b4fc" stroke-width="1.8"/>'
           f'<path d="M-12 {by+5} L-4 {by-3} H8 L12 {by+5}" fill="none" stroke="{col}" stroke-width="3" stroke-linejoin="round"/>'
           f'<circle cx="-2" cy="{by-12}" r="4.5" fill="{col}"/><rect x="14" y="{by-1}" width="3" height="3" fill="#fff6cf"/>')
    if direction<0: inner=f'<g transform="scale(-1 1)">{inner}</g>'
    vals="-120 0;1260 0" if direction>0 else "1260 0;-120 0"
    return f'<g>{inner}<animateTransform attributeName="transform" type="translate" values="{vals}" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/></g>'
a(car('#34d399',252,1,11,0)); a(car('#7c9bff',252,1,13,6.5)); a(car('#f59e0b',280,-1,12,3)); a(car('#f472b6',280,-1,15,10))
a(bike('#a78bfa',256,1,7,2.5)); a(bike('#fb7185',284,-1,8,5))

# rain
for i in range(NRAIN):
    x=random.randint(-10,1230); cls=random.choice(['r','r r2','r r3','r r4','r r5'])
    y=random.randint(-20,0)
    a(f'<line class="{cls}" x1="{x}" y1="{y}" x2="{x-3}" y2="{y+11}" style="animation-delay:-{random.random()*1.3:.2f}s"/>')

if FOG:
    a('<rect y="90" width="1200" height="150" fill="#dfe6f5" opacity=".22"/><g class="ms"><ellipse cx="300" cy="170" rx="320" ry="40" fill="#e6ecfa" opacity=".2"/></g>')
if THUNDER:
    a('<rect width="1200" height="300" fill="#fff" opacity="0" class="fx"/>')
# weather glass card
a('''<g>
<rect x="28" y="18" width="348" height="118" rx="18" fill="#0b1126" fill-opacity=".45"/>
<rect x="28" y="18" width="348" height="118" rx="18" fill="url(#glass)" stroke="#fff" stroke-opacity=".16"/>
<text x="46" y="42" font-family="'JetBrains Mono','SFMono-Regular',Consolas,Menlo,monospace" font-size="12.5" fill="#6f7aa8"><tspan fill="#a78bfa">❯</tspan> <tspan fill="#ffc857">curl</tspan> wttr.in/bandung</text>
<text x="46" y="98" font-family="Inter,'SF Pro Display','Segoe UI',system-ui,sans-serif" font-size="46" font-weight="700" fill="#fff">@@TEMP@@<tspan font-size="20" font-weight="500" fill="#a5b4fc" dy="-18">°C</tspan></text>
<text x="158" y="80" font-family="Inter,'Segoe UI',system-ui,sans-serif" font-size="17" font-weight="600" fill="#e8ecff">@@LABEL@@</text>
<text x="158" y="99" font-family="Inter,'Segoe UI',system-ui,sans-serif" font-size="12" fill="#8f9bc9">H @@HI@@° · L @@LO@@°</text>
@@ICON@@
<text x="46" y="122" font-family="'JetBrains Mono','SFMono-Regular',Consolas,Menlo,monospace" font-size="11.5" fill="#5d678f">@@NOTE@@</text>
</g>''')
a('</g><rect x=".5" y=".5" width="1199" height="299" rx="22" fill="none" stroke="#22d3ee" stroke-opacity=".55"/></svg>')
svg='\n'.join(o)
CLOUD_P='<path d="M8 24H27a7 7 0 0 0 .8-13.9A10 10 0 0 0 8 12.4 6 6 0 0 0 8 24Z" fill="#c7d2fe"/>'
DROPS='<line class="dr" x1="12" y1="29" x2="10" y2="34"/><line class="dr" style="animation-delay:.4s" x1="19" y1="29" x2="17" y2="34"/><line class="dr" style="animation-delay:.8s" x1="26" y1="29" x2="24" y2="34"/>'
SUN='<circle cx="18" cy="18" r="8" fill="#ffd45e"/><g stroke="#ffd45e" stroke-width="2" stroke-linecap="round"><path d="M18 3v4M18 29v4M3 18h4M29 18h4M7.4 7.4l2.8 2.8M25.8 25.8l2.8 2.8M7.4 28.6l2.8-2.8M25.8 10.2l2.8-2.8"/></g>'
MOON='<path d="M24 6a13 13 0 1 0 8 20 11 11 0 0 1-8-20Z" fill="#eef2ff"/>'
if RAIN: icon=CLOUD_P+DROPS
elif CLEAR: icon=SUN if DAY else MOON
elif PARTLY: icon='<g transform="translate(-6 -4) scale(.75)">'+(SUN if DAY else MOON)+'</g><g transform="translate(6 6)">'+CLOUD_P+'</g>'
else: icon=CLOUD_P
icon='<g transform="translate(322 62)">'+icon+'</g>'
for k,v in {'@@TEMP@@':TEMP,'@@LABEL@@':LABEL,'@@HI@@':HI,'@@LO@@':LO,'@@NOTE@@':NOTE,'@@ICON@@':icon}.items(): svg=svg.replace(k,str(v))
svg=svg.replace('aria-label="Bandung malam hari, 22°C gerimis"','aria-label="Bandung, %d°C, %s"'%(TEMP,LABEL.lower())).replace('<title>Bandung at night — 22°C, gerimis</title>','<title>Bandung — %d°C, %s</title>'%(TEMP,LABEL.lower()))
for k,v in PAL.items(): svg=svg.replace(k,v)
open(OUT,'w',encoding='utf-8').write(svg)
