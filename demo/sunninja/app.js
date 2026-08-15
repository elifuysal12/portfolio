/* ══════════════════════════════════════════════════════════════
   The day engine.
   Scroll drives one number: `progress` (0 → 1 = 05:50 → 21:30).
   Sky colour, the sun's arc, the ink, the clock and how hard the
   sea is running all read from it. One summer day, top to bottom.
   ══════════════════════════════════════════════════════════════ */

const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── six moments ──────────────────────────────────────────────
   sky1 = zenith, sky2 = horizon. ink = type. acc = the loud one. */
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

const DAY_START = 5 * 60 + 50;   // 05:50
const DAY_END   = 21 * 60 + 30;  // 21:30

/* ══════════════════════════════════════════════════════════════
   COLOUR MATHS

   These colours are crossfaded on every frame, so HOW they are
   mixed matters more than usual.

   Mixing straight in sRGB — which is what this did — walks a
   straight line through the colour cube, and between two hues on
   opposite sides of it that line passes through grey. Sunrise
   accent #0F7FA8 (teal) to morning accent #E0451F (coral) landed
   on #786264 halfway: a dusty brown. Every crossfade spent its
   middle washed out, and the italic in the headline is exactly
   where you noticed it.

   The fix is NOT to rotate hue. Rotating hue round the wheel does
   keep the chroma up, but it invents colours the palette does not
   contain — cream to cyan went through green, and the teal accent
   reached coral via violet. A green sky is a worse bug than a
   muted one.

   So: mix in OKLab. Same straight line between the two colours,
   but drawn in a perceptually uniform space, so the midpoint is
   the colour the eye expects to be halfway rather than the one
   the sRGB numbers average to. No hue is invented — every colour
   in a crossfade is one the two ends genuinely pass through.

   This fixes the muddiness that came from gamma. What it cannot
   fix is a palette whose neighbouring accents sit on opposite
   sides of the wheel: any straight path from teal to coral goes
   somewhere desaturated, in any colour space. If the italic still
   reads flat mid-scroll, the answer is to move those two accents
   closer together in the DAY table, not more colour maths.
   ══════════════════════════════════════════════════════════════ */
const hex2rgb = h => [1,3,5].map(i => parseInt(h.slice(i, i+2), 16));
const rgb2hex = c => '#' + c.map(v => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2,'0')).join('');

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
  return rgb2hex(oklab2rgb([
    A[0] + (B[0] - A[0]) * k,
    A[1] + (B[1] - A[1]) * k,
    A[2] + (B[2] - A[2]) * k,
  ]));
};

/* ══════════════════════════════════════════════════════════════
   THE CONTRAST FLOOR

   The day has a structural problem that no amount of nicer mixing
   fixes. Between golden hour and sundown the ink crossfades from
   #4A1E07 (nearly black) to #FFEDE2 (nearly white) — while the sky
   is crossfading underneath it. Halfway through, BOTH are mid
   tone, they pass through each other, and for a stretch of scroll
   the headlines sit at about 1.6:1 on their own background.

   That is why the type kept washing out in the middle of a
   transition and then coming back: it was not the colours, it was
   the fact that two independent fades crossed.

   So the palette's ink is treated as an intention rather than a
   final answer. Whatever it blends to, it is then pushed away
   from the sky — lighter if the sky is dark, darker if the sky is
   light — until it clears a real contrast ratio. In the middle of
   a crossfade that push is large; at the six defined moments,
   where the palette was already chosen properly, it does nothing
   at all.
   ══════════════════════════════════════════════════════════════ */
const relLum = ([r, g, b]) => 0.2126 * s2l(r) + 0.7152 * s2l(g) + 0.0722 * s2l(b);
const ratio  = (x, y) => { const a = relLum(x), b = relLum(y);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };

function floorContrast(inkHex, bgHex, target){
  const bg  = hex2rgb(bgHex);
  let ink   = hex2rgb(inkHex);
  if (ratio(ink, bg) >= target) return inkHex;

  /* Direction comes from the ink itself, not from a brightness
     threshold on the sky.

     Deciding by the sky meant that as the sky crossed one exact
     luminance the type flipped from near-black to white — the
     headline changed colour completely between two frames of the
     golden-hour rail, which is the opposite of continuous.

     Reading it off the ink instead means dark type is pushed
     darker and light type is pushed lighter. The palette already
     says which one this moment wants, so the type only ever
     deepens the choice that was made for it, and it changes sides
     exactly once — at sundown, where the palette itself does. */
  const lab = rgb2oklab(ink);
  const bgL = rgb2oklab(bg)[0];
  const end = lab[0] >= bgL ? 1 : 0;
  for (let i = 1; i <= 24; i++){
    const L = lab[0] + (end - lab[0]) * (i / 24);
    const c = oklab2rgb([L, lab[1] * (1 - i / 40), lab[2] * (1 - i / 40)]);
    if (ratio(c, bg) >= target) return rgb2hex(c);
    ink = c;
  }
  return rgb2hex(ink);
}
const num  = (a, b, k) => a + (b - a) * k;
const ease = k => k * k * (3 - 2 * k);   // linger in each moment, then move

function dayAt(p){
  let i = 0;
  while (i < DAY.length - 2 && p > DAY[i+1].t) i++;
  const a = DAY[i], b = DAY[i+1];
  const k = ease(Math.min(Math.max((p - a.t) / (b.t - a.t), 0), 1));
  return {
    sky1: mixc(a.sky1, b.sky1, k),
    sky2: mixc(a.sky2, b.sky2, k),
    ink:  mixc(a.ink,  b.ink,  k),
    acc:  mixc(a.acc,  b.acc,  k),
    pop:  mixc(a.pop,  b.pop,  k),
    panel:   mixc(a.panel,   b.panel,   k),
    onPanel: mixc(a.onPanel, b.onPanel, k),
    sunC: mixc(a.sunC, b.sunC, k),
    sunX: num(a.sunX, b.sunX, k),
    sunY: num(a.sunY, b.sunY, k),
    sunR: num(a.sunR, b.sunR, k),
    sunO: num(a.sunO, b.sunO, k),
    name: k < 0.5 ? a.name : b.name,
  };
}


/* ── loop ─────────────────────────────────────────────────── */
const root  = document.documentElement;
const railT = document.getElementById('railTime');
const railN = document.getElementById('railName');


let phase = 0, lastT = performance.now(), progress = 0;

function readProgress(){
  const max = document.documentElement.scrollHeight - innerHeight;
  progress = max > 0 ? Math.min(Math.max(scrollY / max, 0), 1) : 0;
}

function paint(now){
  const dt = Math.min((now - lastT) / 1000, 0.05);
  lastT = now;

  const d = dayAt(progress);

  root.style.setProperty('--sky-1', d.sky1);
  root.style.setProperty('--sky-2', d.sky2);

  /* the ground the type actually sits on is the middle of the sky
     gradient, so that is what ink and accent are held against */
  const ground = mixc(d.sky1, d.sky2, 0.5);
  root.style.setProperty('--ink',    floorContrast(d.ink, ground, 5.2));
  root.style.setProperty('--accent', floorContrast(d.acc, ground, 4.2));
  root.style.setProperty('--pop',    d.pop);
  root.style.setProperty('--panel',    d.panel);
  root.style.setProperty('--on-panel', d.onPanel);
  root.style.setProperty('--sun-x', d.sunX.toFixed(2) + '%');
  root.style.setProperty('--sun-y', d.sunY.toFixed(2) + '%');
  root.style.setProperty('--sun-r', d.sunR.toFixed(0) + 'px');
  root.style.setProperty('--sun-c', d.sunC);
  root.style.setProperty('--sun-o', d.sunO.toFixed(3));
  // how low the sun is sitting — drives the sky banding and the flattening
  root.style.setProperty('--lowness', Math.min(Math.max((d.sunY - 26) / 46, 0), 1).toFixed(3));

  // the clock ticks as you scroll
  const mins = Math.round(DAY_START + (DAY_END - DAY_START) * progress);
  if (railT) railT.textContent =
    String(Math.floor(mins / 60)).padStart(2,'0') + ':' + String(mins % 60).padStart(2,'0');
  if (railN) railN.textContent = d.name;


  requestAnimationFrame(paint);
}

readProgress();
addEventListener('scroll', readProgress, { passive:true });
addEventListener('resize', readProgress);
requestAnimationFrame(paint);

/* ── reveal on entry — a soft spring, never a slide-in ────── */
if (!REDUCED){
  const targets = document.querySelectorAll(
    '.hero-copy > *, .hero-product, .specbar li, .split-copy > *, .split-media, ' +
    '.noon-head > *, .size, .noon-foot > *, .golden-head > *, .scenes figure, ' +
    '.sunset-head > *, .quotes blockquote, .kit-head > *, .kit-grid a, .promises li, .night-head > *, .foot > *'
  );
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

/* ── the setup, one beat at a time ────────────────────────────
   The section is three screens tall but only one screen is ever
   visible. Scrolling through it advances the step rather than the
   page: the picture holds, the words change. */
(() => {
  const act   = document.querySelector('.act--pin');
  const steps = [...document.querySelectorAll('.step[data-step]')];
  const shots = [...document.querySelectorAll('[data-media] img[data-step]')];
  const dots  = [...document.querySelectorAll('.stepbar span')];
  const cap   = document.querySelector('[data-caption]');
  if (!act || !steps.length) return;
  const LABELS = ['01 — Spread', '02 — Anchor', '03 — Lift'];
  let active = -1;

  function pick(){
    const r    = act.getBoundingClientRect();
    const run  = act.offsetHeight - innerHeight;
    const p    = run > 0 ? Math.min(Math.max(-r.top / run, 0), 1) : 0;
    const i    = Math.min(Math.floor(p * steps.length + 0.0001), steps.length - 1);
    if (i === active) return;
    active = i;
    steps.forEach((el, n) => el.classList.toggle('is-active', n === i));
    shots.forEach((el, n) => el.classList.toggle('is-shown',  n === i));
    dots .forEach((el, n) => el.classList.toggle('is-on',     n === i));
    if (cap) cap.textContent = LABELS[i];
  }
  addEventListener('scroll', pick, { passive:true });
  addEventListener('resize', pick);
  pick();
})();

/* ── the buy bar shows up where buying happens ────────────────
   It has no business floating over a sunrise, and it used to run
   all the way to the reviews — which meant it hung over the
   golden-hour rail and the whole product grid, sitting on top of
   the captions and offering a tent while you were reading about
   everything that is not the tent.

   It belongs to one decision: which size. So it lives exactly as
   long as that decision is on screen, and leaves when the rail
   starts. */
(() => {
  const bar   = document.querySelector('[data-buybar]');
  const from  = document.querySelector('.panel');        // the sizes
  const until = document.querySelector('#golden');        // the rail — the tent question is over
  if (!bar || !from) return;
  const sync = () => {
    const start = from.getBoundingClientRect().top + scrollY - innerHeight * 0.65;
    const end   = until
      ? until.getBoundingClientRect().top + scrollY - innerHeight * 0.5
      : start + 3000;
    const on = scrollY > start && scrollY < end;
    bar.classList.toggle('is-up', on);
    bar.setAttribute('aria-hidden', String(!on));
  };
  addEventListener('scroll', sync, { passive:true });
  addEventListener('resize', sync);
  sync();
})();

/* ── fill the floor plans with the people they hold ───────── */
document.querySelectorAll('.plan-dots').forEach(el => {
  const n = +el.dataset.people || 0;
  el.innerHTML = '<i></i>'.repeat(n);
});

/* ── golden hour travels sideways while the page holds still ─
   Each tile has one exact translate that puts it in the middle of
   the screen. Scroll progress walks between those positions, so
   tile n is dead centre at n/(count-1) — no drift, no guessing. */
(() => {
  const act   = document.querySelector('.act--rail');
  const track = document.querySelector('[data-rail]');
  const segs  = [...document.querySelectorAll('.rail-prog i')];
  const idxEl = document.querySelector('[data-rail-index]');
  const nameEl= document.querySelector('[data-rail-name]');
  const noteEl= document.querySelector('[data-rail-note]');
  if (!act || !track) return;
  const tiles = [...track.children];
  if (tiles.length < 2) return;

  // Read where each tile actually renders with the track at zero, rather
  // than trusting offsetLeft — the sticky wrapper makes that unreliable.
  let stops = [];
  function measure(){
    const prev = track.style.transform;
    track.style.transform = 'translate3d(0px,0,0)';
    void track.offsetWidth;                        // force the layout to settle
    stops = tiles.map(t => {
      const b = t.getBoundingClientRect();
      return innerWidth / 2 - (b.left + b.width / 2);
    });
    track.style.transform = prev;
  }

  function move(){
    if (getComputedStyle(track).transform === 'none' && innerWidth <= 900) return;
    const r   = act.getBoundingClientRect();
    const run = act.offsetHeight - innerHeight;
    const p   = run > 0 ? Math.min(Math.max(-r.top / run, 0), 1) : 0;

    const f = p * (tiles.length - 1);
    const i = Math.min(Math.floor(f), tiles.length - 2);
    const k = f - i;
    const x = stops[i] + (stops[i + 1] - stops[i]) * k;

    track.style.transform = `translate3d(${x.toFixed(1)}px,0,0)`;

    const focus = Math.round(f);
    tiles.forEach((t, n) => t.classList.toggle('is-focus', n === focus));
    segs.forEach((s, n) => s.classList.toggle('is-on', n === focus));
    if (idxEl)  idxEl.textContent  = String(focus + 1).padStart(2, '0');
    // the tile's caption is not rendered any more — it is read from
    // here and shown once, under the heading, so the focused scene
    // is not named twice on the same screen
    if (nameEl) nameEl.textContent = tiles[focus].querySelector('figcaption b').textContent;
    if (noteEl) noteEl.textContent = tiles[focus].querySelector('figcaption span').textContent;
  }

  measure(); move();
  requestAnimationFrame(() => { measure(); move(); });   // after first paint
  addEventListener('scroll', move, { passive:true });
  addEventListener('resize', () => { measure(); move(); });
  addEventListener('load',   () => { measure(); move(); });
})();

/* the kit used to shrink, dim and blur as the reviews slid over it.
   That motion belonged to a different page — see the note in
   style.css — so the handover is now just the sky continuing. */
(() => {
  return;
})();
