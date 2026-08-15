/* ══════════════════════════════════════════════════════════════
   SUN NINJA — Product page

   The home page's day engine, unchanged, running a much shorter
   slice of the day. The home page spends 05:50 → 21:30 on you
   because the whole day is the story. A product page has no
   business being a sunrise, so this one holds around noon: the sun
   is up, the sky is blue, and it only breathes.

   The two brand accents are pinned in product.css rather than
   drifting with the hour — see the note there.
   ══════════════════════════════════════════════════════════════ */

const clamp = (v,a,b) => Math.min(Math.max(v,a),b);
const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── the day, and the slice of it this page gets ───────────── */
const DAY = [
  { t:0.00, name:'Sunrise',     sky1:'#FFE0AE', sky2:'#FF8A66', ink:'#20366C', acc:'#0F7FA8', sea:'#E8674C', pop:'#E0361F', foam:'#FFE6D2', panel:'#173B5D', onPanel:'#F1FAFF',
    sunX:74, sunY:52, sunR:1240, sunC:'#FFF2CC', sunO:0.95 },
  { t:0.18, name:'Morning swim',sky1:'#63D9F2', sky2:'#D9F7EC', ink:'#20366C', acc:'#E0451F', sea:'#2FC3DE', pop:'#20366C', foam:'#FFFFFF', panel:'#FFF2DC', onPanel:'#20366C',
    sunX:58, sunY:26, sunR:330, sunC:'#FFF6D4', sunO:0.90 },
  { t:0.40, name:'High noon',   sky1:'#0193CE', sky2:'#74E2F8', ink:'#0C2C57', acc:'#0C2C57', sea:'#0179B8', pop:'#FFDD33', foam:'#FFFFFF', panel:'#FFF1D2', onPanel:'#20366C',
    sunX:50, sunY:8, sunR:340, sunC:'#FFFEF2', sunO:1.00 },
  /* ── afternoon ────────────────────────────────────────────────
     This stop exists to stop the sky going green.

     Noon's zenith is #0193CE and golden hour's is #FFC246 — a
     blue and an amber, near enough opposite that ANY straight
     interpolation between them lands on sage: the sRGB midpoint
     is #80AA98. That was not a colour anyone chose, it was just
     what sat halfway, and for a whole scroll the beach turned
     green.

     A real afternoon does not go from blue to amber directly
     either. It pales first — the zenith washes out and the
     horizon warms — and only then does the whole thing turn gold.
     So that is the stop: pale blue above, warm sand below. Now
     both halves of the journey stay in colours the sky actually
     has. */
  { t:0.50, name:'Afternoon',   sky1:'#5FC4E8', sky2:'#FFE0B4', ink:'#123056', acc:'#0E5C74', sea:'#2E9FCC', pop:'#FF8A3C', foam:'#FFFFFF', panel:'#FFF0D8', onPanel:'#20366C',
    sunX:42, sunY:18, sunR:370, sunC:'#FFF6D0', sunO:1.00 },
  { t:0.60, name:'Golden hour', sky1:'#FFC246', sky2:'#FF7A3C', ink:'#4A1E07', acc:'#20366C', sea:'#E3641F', pop:'#E8431C', foam:'#FFF2DA', panel:'#12365E', onPanel:'#EAF6FF',
    sunX:34, sunY:30, sunR:400, sunC:'#FFE9A8', sunO:1.00 },
  /* ── sundown ──────────────────────────────────────────────
     Re-cut twice, and the second time for a measurable reason.

     The first version had a mid-tone sky (#6B2448 over #FF6A3C,
     blending to #B2474A). Nothing reads on a mid tone: dark type
     got pushed all the way to black and still only reached
     3.1:1, and the solid CTA — which is ink-filled — disappeared
     into the background entirely.

     So the sky actually darkens, the way a sunset does. Deep plum
     above, ember below, blending to #7F2A35. Light type on that
     is 8:1 and the gold accent is 6.4:1, and the filled button is
     light-on-dark, which is visible. */
  { t:0.80, name:'Sundown',     sky1:'#4A1836', sky2:'#B83A28', ink:'#FFEDE2', acc:'#FFD24A', sea:'#4B1E63', pop:'#FFD24A', foam:'#FFC7A2', panel:'#FFE7CB', onPanel:'#4A1E07',
    sunX:12, sunY:76, sunR:560, sunC:'#FFB35A', sunO:1.00 },
  { t:1.00, name:'After dark',  sky1:'#04101F', sky2:'#16375F', ink:'#CFEAF5', acc:'#2BE0C8', sea:'#061428', pop:'#2BE0C8', foam:'#7FF0DC', panel:'#0C2742', onPanel:'#CFEAF5',
    sunX:24, sunY:18, sunR:140, sunC:'#DDEEFA', sunO:0.80 },
];

/* Late morning to just past noon, and no further. Past 0.50 the
   zenith starts for golden hour, and every straight line between a
   blue zenith and an amber one passes through sage — the sky went
   green at the foot of the page. Stopping here means the whole
   scroll stays in one hour of one colour. */
const SLICE = [0.33, 0.42];

/* ── colour maths ─────────────────────────────────────────────
   Crossfading in sRGB walks a straight line through the colour
   cube, and between two hues on opposite sides of it that line
   passes through grey. OKLab draws the same straight line in a
   perceptually uniform space, so the midpoint is the colour the
   eye expects halfway. No hue is invented on the way. */
const hex2rgb = h => [1,3,5].map(i => parseInt(h.slice(i, i+2), 16));
const rgb2hex = c => '#' + c.map(v => Math.round(clamp(v,0,255)).toString(16).padStart(2,'0')).join('');
const s2l = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
const l2s = v => 255 * (v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055);

function rgb2oklab([R, G, B]){
  const r = s2l(R), g = s2l(G), b = s2l(B);
  const l = Math.cbrt(0.4122214708*r + 0.5363325363*g + 0.0514459929*b);
  const m = Math.cbrt(0.2119034982*r + 0.6806995451*g + 0.1073969566*b);
  const s = Math.cbrt(0.0883024619*r + 0.2817188376*g + 0.6299787005*b);
  return [
    0.2104542553*l + 0.7936177850*m - 0.0040720468*s,
    1.9779984951*l - 2.4285922050*m + 0.4505937099*s,
    0.0259040371*l + 0.7827717662*m - 0.8086757660*s,
  ];
}
function oklab2rgb([L, A, B]){
  const l = (L + 0.3963377774*A + 0.2158037573*B) ** 3;
  const m = (L - 0.1055613458*A - 0.0638541728*B) ** 3;
  const s = (L - 0.0894841775*A - 1.2914855480*B) ** 3;
  return [
    l2s( 4.0767416621*l - 3.3077115913*m + 0.2309699292*s),
    l2s(-1.2684380046*l + 2.6097574011*m - 0.3413193965*s),
    l2s(-0.0041960863*l - 0.7034186147*m + 1.7076147010*s),
  ];
}
const mixc = (a, b, k) => {
  const A = rgb2oklab(hex2rgb(a)), B = rgb2oklab(hex2rgb(b));
  return rgb2hex(oklab2rgb(A.map((v, i) => v + (B[i] - v) * k)));
};
const numi = (a, b, k) => a + (b - a) * k;
const ease = k => k * k * (3 - 2 * k);

function dayAt(p){
  let i = 0;
  while (i < DAY.length - 2 && p > DAY[i+1].t) i++;
  const a = DAY[i], b = DAY[i+1];
  const k = ease(clamp((p - a.t) / (b.t - a.t), 0, 1));
  return {
    sky1: mixc(a.sky1, b.sky1, k),
    sky2: mixc(a.sky2, b.sky2, k),
    ink:  mixc(a.ink,  b.ink,  k),
    sunC: mixc(a.sunC, b.sunC, k),
    sunX: numi(a.sunX, b.sunX, k),
    sunY: numi(a.sunY, b.sunY, k),
    sunR: numi(a.sunR, b.sunR, k),
    sunO: numi(a.sunO, b.sunO, k),
  };
}

const root = document.documentElement;
let queued = false;
function paintSky(){
  queued = false;
  const max = root.scrollHeight - innerHeight;
  const p = max > 0 ? clamp(scrollY / max, 0, 1) : 0;
  const d = dayAt(SLICE[0] + p * (SLICE[1] - SLICE[0]));
  root.style.setProperty('--sky-1', d.sky1);
  root.style.setProperty('--sky-2', d.sky2);
  root.style.setProperty('--ink',   d.ink);
  root.style.setProperty('--sun-x', d.sunX.toFixed(2) + '%');
  root.style.setProperty('--sun-y', d.sunY.toFixed(2) + '%');
  root.style.setProperty('--sun-r', d.sunR.toFixed(0) + 'px');
  root.style.setProperty('--sun-c', d.sunC);
  root.style.setProperty('--sun-o', d.sunO.toFixed(3));
  root.style.setProperty('--lowness', '0');
}
const queueSky = () => { if (!queued){ queued = true; requestAnimationFrame(paintSky); } };
paintSky();
addEventListener('scroll', queueSky, { passive:true });
addEventListener('resize', queueSky);

/* the footer logo is the nav logo, cloned rather than pasted, so
   there is one copy of that path data in the file */
const logoSrc = $('[data-logo] svg');
if (logoSrc) $('[data-logo-copy]').appendChild(logoSrc.cloneNode(true));

/* ══════════════════════════════════════════════════════════════
   PRODUCT DATA
   Photography, sizes and specs are the brand's own — 1.32 / 2.11
   gallon, 6.88 ft of coiled hose, seven spray modes, one-year
   warranty.
   ══════════════════════════════════════════════════════════════ */
const STYLES = [
  { key:'Multi-Color',
    chip:{ src:'img/ps_multi_c.webp', size:'420%', pos:'50% 56%' },
    shots:[
      { src:'img/ps_multi_a.webp', alt:'Sun Ninja portable shower in Multi-Color, spraying' },
      { src:'img/ps_multi_c.webp', alt:'The Multi-Color shower with its shoulder strap and coiled hose' },
      { src:'img/ps_multi_b.webp', alt:'The Multi-Color shower with the hose coiled beside it' },
    ] },
  { key:'Camo',
    chip:{ src:'img/ps_camo_c.webp', size:'420%', pos:'50% 56%' },
    shots:[
      { src:'img/ps_camo_a.webp', alt:'Sun Ninja portable shower in Camo, spraying' },
      { src:'img/ps_camo_c.webp', alt:'The Camo shower with its shoulder strap and coiled hose' },
      { src:'img/ps_camo_b.webp', alt:'The Camo shower with the hose coiled beside it' },
    ] },
];

const SIZES = [
  { key:'1.32 gal', price:60, note:'Two people, 2–3 minutes of spray', scale:74 },
  { key:'2.11 gal', price:80, note:'Four people, 3–4 minutes of spray', scale:97, flag:'Most picked' },
];

let style = STYLES[0], size = SIZES[0], qty = 1;
const money = n => '$' + n;

/* ── gallery ──────────────────────────────────────────────── */
const stage  = $('[data-frames]');
const thumbs = $('[data-thumbs]');

function buildGallery(){
  stage.innerHTML = '';
  thumbs.innerHTML = '';
  style.shots.forEach((s, i) => {
    const fig = document.createElement('figure');
    fig.className = 'gal-slide';
    const img = document.createElement('img');
    img.src = s.src; img.alt = s.alt;
    if (i > 0) img.loading = 'lazy';
    fig.appendChild(img);
    stage.appendChild(fig);

    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('role', 'tab');
    b.setAttribute('aria-label', s.alt);
    const t = document.createElement('img');
    t.src = s.src; t.alt = ''; t.loading = 'lazy';
    b.appendChild(t);
    b.addEventListener('click', () => showFrame(i));
    thumbs.appendChild(b);
  });
  showFrame(0);
}
function showFrame(i){
  $$('.gal-slide').forEach((s, n) => s.classList.toggle('is-on', n === i));
  $$('[data-thumbs] button').forEach((b, n) => b.setAttribute('aria-selected', String(n === i)));
}

/* ── the decision ─────────────────────────────────────────── */
function buildSizes(){
  const row = $('[data-sizes]');
  SIZES.forEach(s => {
    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('role', 'radio');
    b.innerHTML = `<b>${s.key}</b><span>${money(s.price)}</span>`;
    b.addEventListener('click', () => { size = s; sync(); });
    row.appendChild(b);
  });
}

function buildStyles(){
  const row = $('[data-styles]');
  STYLES.forEach(s => {
    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('role', 'radio');
    b.setAttribute('aria-label', s.key);
    b.style.backgroundImage = `url(${s.chip.src})`;
    b.style.backgroundSize = s.chip.size;
    b.style.backgroundPosition = s.chip.pos;
    b.addEventListener('click', () => { style = s; buildGallery(); sync(); });
    row.appendChild(b);
  });
}

function sync(){
  $$('[data-sizes] button').forEach((b, i) =>
    b.setAttribute('aria-checked', String(SIZES[i] === size)));
  $$('[data-styles] button').forEach((b, i) =>
    b.setAttribute('aria-checked', String(STYLES[i] === style)));
  $('[data-stylename]').textContent = style.key;
  $('[data-qtyval]').textContent = qty;
  $('[data-total]').textContent = money(size.price * qty);
  $('[data-barprice]').textContent = money(size.price);
}

$$('[data-qty]').forEach(b => b.addEventListener('click', () => {
  qty = clamp(qty + Number(b.dataset.qty), 1, 9);
  sync();
}));

buildGallery();
buildSizes();
buildStyles();
sync();

/* ══════════════════════════════════════════════════════════════
   THE RIG
   Seven modes, filed by the job rather than the name. `spread`,
   `reach`, `bite` and `flow` are what the drawing actually runs
   on — they are tuned so each mode behaves the way that mode
   behaves. Mist barely moves the sand. Jet clears it. Full empties
   the bottle fastest, and you watch the pressure fall while you
   hold it, which is the one thing a photograph cannot show.
   ══════════════════════════════════════════════════════════════ */
const NOZZLES = [
  { name:'Shower', job:'the everyday rinse',  spread:22,  reach:520, bite:1.00, flow:7,  rate:2.2,
    desc:'Wide and soft — about as close to a real shower as a bottle gets. <b>This is the one you will actually use.</b>' },
  { name:'Jet',    job:'stuck-on sand',       spread:2.4, reach:640, bite:3.60, flow:6,  rate:1.1,
    desc:'One hard line. For the tow hitch, the sand in the tread, <b>the thing that will not let go.</b>' },
  { name:'Mist',   job:'cooling kids down',   spread:30,  reach:420, bite:0.16, flow:3,  rate:3.4,
    desc:'Barely there — and you can feel that here. <b>It cools a toddler down; it does not clean anything.</b>' },
  { name:'Flat',   job:'boards and wetsuits', spread:34,  reach:470, bite:1.30, flow:9,  rate:1.5,
    desc:'A blade of water. <b>Wipes a board down in two passes instead of ten.</b>' },
  { name:'Full',   job:'emptying it fast',    spread:27,  reach:500, bite:1.15, flow:15, rate:3.0,
    desc:'Everything at once. Empties the bottle fastest — <b>watch the pressure drop.</b>' },
  { name:'Cone',   job:'around a thing',      spread:26,  reach:520, bite:0.95, flow:8,  rate:1.8, hollow:true,
    desc:'A hollow ring. <b>Goes around a bike frame or a chair leg</b> rather than straight at it.' },
  { name:'Center', job:'filling and clearing',spread:5,   reach:560, bite:1.90, flow:5,  rate:1.2,
    desc:'Tight and central. Fills a bottle, clears a mask, <b>refuses to spray your legs.</b>' },
];

const rig = (() => {
  const cv = $('[data-rinse]');
  if (!cv) return null;
  const ctx = cv.getContext('2d');
  const W = 1000, H = 667, GROUND = 604;
  /* both read off the photograph: the nozzle is where the real
     spray disc sits in the frame, and the feet stand in the empty
     sand between the bottle and the head — which is the direction
     the real head is pointing. */
  const NOZ = { x:818, y:254 };
  const LEG = { x:565 };
  /* the head in the photograph cannot turn, so the water is not
     allowed to leave it backwards. Everything from a little
     down-right, through straight down, round to the left. */
  const AIM_MIN = 70 * Math.PI/180, AIM_MAX = 175 * Math.PI/180;
  function aimAngle(){
    const a = Math.atan2(aim.y - NOZ.y, aim.x - NOZ.x);
    return clamp(a < -Math.PI/2 ? Math.PI : a, AIM_MIN, AIM_MAX);
  }

  /* the drawing is dark on light now, because the stage is glass
     over a bright sky rather than a navy rectangle */
  const LINE = 'rgba(12,44,87,.88)';
  const FAINT = 'rgba(12,44,87,.22)';

  let head = NOZZLES[0];
  let psi = 45, spraying = false, pumping = false;
  let aim = { x:720, y:400 };
  let drops = [], sand = [], total = 0;
  let running = false, last = 0;

  function seedSand(){
    sand = [];
    let s = 20;
    const rnd = () => (s = (s*1103515245 + 12345) % 2147483648) / 2147483648;
    const band = (x0, w, y0, h, n) => {
      for (let i = 0; i < n; i++)
        sand.push({ x:x0 + rnd()*w, y:y0 + rnd()*h, r:1.6 + rnd()*2.2 });
    };
    band(LEG.x - 11, 24, 406, 160, 95);   // left shin
    band(LEG.x + 41, 24, 406, 160, 95);   // right shin
    band(LEG.x - 26, 59, 578, 24,  78);   // left foot
    band(LEG.x + 34, 59, 578, 24,  78);   // right foot
    total = sand.length;
  }

  function drawTarget(){
    ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(LEG.x,      400); ctx.lineTo(LEG.x - 4,  570);
    ctx.moveTo(LEG.x + 52,  400); ctx.lineTo(LEG.x + 56, 570);
    ctx.moveTo(LEG.x - 4,  570); ctx.lineTo(LEG.x - 24, GROUND); ctx.lineTo(LEG.x + 31, GROUND);
    ctx.moveTo(LEG.x + 56, 570); ctx.lineTo(LEG.x + 36, GROUND); ctx.lineTo(LEG.x + 91, GROUND);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(LEG.x,     400, 10, 0, 7); ctx.moveTo(LEG.x + 62, 400);
    ctx.arc(LEG.x + 52, 400, 10, 0, 7);
    ctx.stroke();
  }


  function emit(dt){
    const power = clamp(psi / 45, 0, 1);
    if (power < .07) return;
    const a = aimAngle();
    const half = head.spread * Math.PI / 180;
    const n = Math.round(head.rate * 26 * dt * (0.45 + power * 0.55));
    for (let i = 0; i < n; i++){
      const off = head.hollow
        ? (Math.random() < .5 ? -1 : 1) * half * (0.82 + Math.random()*0.18)
        : (Math.random()*2 - 1) * half;
      const sp = head.reach * (0.55 + power * 0.45) * 1.7 * (0.85 + Math.random()*0.3);
      drops.push({
        x: NOZ.x + Math.cos(a)*18, y: NOZ.y + Math.sin(a)*18,
        vx: Math.cos(a + off) * sp, vy: Math.sin(a + off) * sp,
        life: 0.45 + Math.random()*0.25, age: 0,
        r: head.name === 'Mist' ? 1.2 : (head.name === 'Jet' ? 2.6 : 1.9),
      });
    }
  }

  /* the sand does not need particle collision to behave right —
     what matters is that the cone, the range and the mode's bite
     decide how fast it clears */
  function scrub(dt){
    const power = clamp(psi / 45, 0, 1);
    if (power < .07) return;
    const a = aimAngle();
    const half = head.spread * Math.PI / 180;
    const range = head.reach * (0.45 + power * 0.55);
    for (let i = sand.length - 1; i >= 0; i--){
      const g = sand[i];
      const dx = g.x - NOZ.x, dy = g.y - NOZ.y;
      const d = Math.hypot(dx, dy);
      if (d > range) continue;
      let da = Math.atan2(dy, dx) - a;
      while (da >  Math.PI) da -= Math.PI*2;
      while (da < -Math.PI) da += Math.PI*2;
      const inCone = head.hollow
        ? Math.abs(Math.abs(da) - half*0.9) < half*0.22
        : Math.abs(da) < half;
      if (!inCone) continue;
      const falloff = 1 - (d / range) * 0.55;
      if (Math.random() < head.bite * power * falloff * dt * 7) sand.splice(i, 1);
    }
  }

  function paintMeters(){
    const cleanPct = Math.round((1 - sand.length / total) * 100);
    $('[data-psi]').textContent = Math.round(psi) + ' PSI';
    $('[data-psibar]').style.width = (psi / 45 * 100) + '%';
    $('[data-clean]').textContent = cleanPct + '%';
    $('[data-cleanbar]').style.width = cleanPct + '%';
    $('[data-done]').classList.toggle('is-on', cleanPct >= 99);
  }

  function step(now){
    if (!running) return;
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;

    if (pumping) psi = clamp(psi + 26*dt, 0, 45);
    if (spraying){
      psi = clamp(psi - head.flow*dt, 0, 45);
      emit(dt); scrub(dt);
    }

    for (let i = drops.length - 1; i >= 0; i--){
      const d = drops[i];
      d.age += dt;
      if (d.age > d.life){ drops.splice(i,1); continue; }
      d.x += d.vx*dt; d.y += d.vy*dt; d.vy += 740*dt;
      if (d.y > GROUND) drops.splice(i,1);
    }
    if (drops.length > 900) drops.splice(0, drops.length - 900);

    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = FAINT; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(120, GROUND); ctx.lineTo(W - 90, GROUND); ctx.stroke();
    drawTarget();
    ctx.fillStyle = '#C9954A';
    sand.forEach(g => { ctx.beginPath(); ctx.arc(g.x, g.y, g.r, 0, 7); ctx.fill(); });
    ctx.fillStyle = 'rgba(255,255,255,.85)';
    drops.forEach(d => { ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, 7); ctx.fill(); });

    paintMeters();
    requestAnimationFrame(step);
  }

  function toWorld(e){
    const r = cv.getBoundingClientRect();
    return { x:(e.clientX - r.left) / r.width * W, y:(e.clientY - r.top) / r.height * H };
  }
  cv.addEventListener('pointerdown', e => {
    try { cv.setPointerCapture(e.pointerId); } catch {}
    aim = toWorld(e); spraying = true; wake();
    $('[data-cue]').classList.add('is-off');
  });
  cv.addEventListener('pointermove', e => { aim = toWorld(e); });
  const stop = () => { spraying = false; };
  ['pointerup','pointercancel','pointerleave'].forEach(ev => cv.addEventListener(ev, stop));

  const pumpBtn = $('[data-pump]');
  pumpBtn.addEventListener('pointerdown', () => { pumping = true; wake(); });
  ['pointerup','pointerleave','pointercancel'].forEach(ev =>
    pumpBtn.addEventListener(ev, () => { pumping = false; }));

  $('[data-reset]').addEventListener('click', () => {
    seedSand(); psi = 45; drops = [];
    $('[data-done]').classList.remove('is-on');
  });

  function setHead(name){
    head = NOZZLES.find(n => n.name === name);
    $('[data-rigsay]').innerHTML = head.desc;
    $$('[data-righeads] button').forEach(b =>
      b.setAttribute('aria-selected', String(b.dataset.name === name)));
  }
  function buildHeads(){
    const ul = $('[data-righeads]');
    NOZZLES.forEach(n => {
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.type = 'button'; b.setAttribute('role','tab'); b.dataset.name = n.name;
      b.innerHTML = `<b>${n.name}</b><span>${n.job}</span>`;
      b.addEventListener('click', () => setHead(n.name));
      li.appendChild(b); ul.appendChild(li);
    });
  }

  function fit(){
    const dpr = Math.min(devicePixelRatio || 1, 2);
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function wake(){
    if (running) return;
    running = true; last = performance.now();
    requestAnimationFrame(step);
  }

  fit(); buildHeads(); setHead('Shower'); seedSand();
  addEventListener('resize', fit);
  return { wake, sleep(){ running = false; } };
})();

/* it only runs while it is on screen — a canvas loop four screens
   up is nobody's idea of a good time */
if (rig){
  new IntersectionObserver(([e]) => {
    e.isIntersecting ? rig.wake() : rig.sleep();
  }, { threshold:0.05 }).observe($('.rig-stage'));
}

/* ══════════════════════════════════════════════════════════════
   THE SECOND BAR
   It arrives once the buy column has gone past, and it says which
   section you are in by weight rather than by drawing a line under
   anything.
   ══════════════════════════════════════════════════════════════ */
(() => {
  const bar = $('[data-subnav]');
  const hero = $('#buy');
  if (!bar || !hero) return;

  new IntersectionObserver(([e]) => {
    bar.classList.toggle('is-up', !e.isIntersecting);
  }, { rootMargin:'-40% 0px 0px 0px' }).observe(hero);

  const links = $$('.subnav-links a');
  const marks = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const spy = new IntersectionObserver(entries => {
    for (const e of entries){
      if (!e.isIntersecting) continue;
      links.forEach(a => a.classList.toggle('is-on',
        a.getAttribute('href') === '#' + e.target.id));
    }
  }, { rootMargin:'-45% 0px -50% 0px' });
  marks.forEach(m => spy.observe(m));
})();

/* ── reveal on entry — a soft spring, never a slide-in ────── */
if (!REDUCED){
  const targets = $$('.pbuy > *, .gal, .act > .wrap > *, .box-grid li, .quotes blockquote, .foot > *');
  targets.forEach(el => el.classList.add('reveal'));
  const io = new IntersectionObserver(entries => {
    for (const e of entries){
      if (!e.isIntersecting) continue;
      const peers = e.target.parentElement
        ? [...e.target.parentElement.children].filter(c => c.classList.contains('reveal'))
        : [e.target];
      e.target.style.transitionDelay = Math.max(peers.indexOf(e.target), 0) * 70 + 'ms';
      e.target.classList.add('is-in');
      io.unobserve(e.target);
    }
  }, { rootMargin:'0px 0px -10% 0px', threshold:0.1 });
  targets.forEach(el => io.observe(el));
}
