// The deck player shared by the audience page (index.html) and the presenter page (presenter.html).
//
// A slide is a <section> in the claude.ai Slides format, laid out on a fixed 1920x1080 canvas that is scaled to fit
// its host. The player covers what the deck uses of the format's motion:
// - data-transition on a slide: how it leaves for the next one. fade, push, none, and magic: children with the same
//   id on both slides move from their old place and size to their new one, the rest fade out or in.
// - data-build-in="fade N" on a pinned child: it appears on the slide's Nth click.
// A position in the show is (slide index, step): step 0 shows no builds, step N the builds up to N.

const W = 1920, H = 1080;
const MAGIC = 800, FADE = 500, PUSH = 600, BUILD = 400;  // durations, ms
const EASE = "cubic-bezier(0.4, 0, 0.2, 1)";

function buildOrder(el) {
  const m = /(\d+)/.exec(el.getAttribute("data-build-in") || "");
  return m ? Number(m[1]) : 1;
}

// The deck from the server: every slide as a <section> template, with its notes, transition and number of steps.
async function loadDeck() {
  const response = await fetch("deck.json", {cache: "no-store"});
  const deck = await response.json();
  const slides = [];
  for (const s of deck.slides) {
    const t = document.createElement("template");
    t.innerHTML = s.html.trim();
    const section = t.content.querySelector("section");
    if (section === null || section.hasAttribute("hidden")) continue;  // hidden = skipped
    const aside = section.querySelector(":scope > aside");
    const notes = aside ? aside.textContent.trim() : "";
    if (aside) aside.remove();
    const builds = [...section.querySelectorAll("[data-build-in]")].map(buildOrder);
    slides.push({id: s.id, section, notes, transition: section.getAttribute("data-transition") || "fade",
                 steps: builds.length ? Math.max(...builds) : 0,
                 title: (section.querySelector("h1, h2, h3") || {}).textContent || ""});
  }
  return {title: deck.title, slides};
}

// Positions in the show.
function nextPos(deck, {i, step}) {
  if (step < deck.slides[i].steps) return {i, step: step + 1};
  if (i + 1 < deck.slides.length) return {i: i + 1, step: 0};
  return null;
}
function prevPos(deck, {i, step}) {
  if (step > 0) return {i, step: step - 1};
  if (i > 0) return {i: i - 1, step: deck.slides[i - 1].steps};
  return null;
}
function clampPos(deck, {i, step}) {
  i = Math.max(0, Math.min(deck.slides.length - 1, i | 0));
  return {i, step: Math.max(0, Math.min(deck.slides[i].steps, step | 0))};
}

// A slide at a step, as a layer (a 1920x1080 box holding the section) ready to put on a canvas.
function makeLayer(slide, step) {
  const layer = document.createElement("div");
  layer.className = "layer";
  const section = slide.section.cloneNode(true);
  for (const el of section.querySelectorAll("[data-build-in]")) {
    el.dataset.opacity = el.style.opacity;
    if (buildOrder(el) > step) el.style.opacity = "0";
  }
  layer.append(section);
  return layer;
}

function builtHidden(el) {
  return el.hasAttribute("data-build-in") && el.style.opacity === "0";
}

// A 1920x1080 canvas scaled to fit its host, showing one position at a time and animating between neighbours.
class Stage {
  constructor(host) {
    this.host = host;
    this.canvas = document.createElement("div");
    this.canvas.className = "canvas";
    host.append(this.canvas);
    this.pos = null;
    this.busy = Promise.resolve();
    new ResizeObserver(() => this.fit()).observe(host);
    this.fit();
  }

  fit() {
    const w = this.host.clientWidth, h = this.host.clientHeight;
    const s = Math.min(w / W, h / H) || 0;
    this.canvas.style.transform = `translate(${(w - W * s) / 2}px, ${(h - H * s) / 2}px) scale(${s})`;
  }

  // Ends any animation at once, in its final state.
  async settle() {
    for (const a of this.canvas.getAnimations({subtree: true})) a.finish();
    await this.busy;
  }

  show(deck, pos) {
    for (const a of this.canvas.getAnimations({subtree: true})) a.cancel();
    this.canvas.replaceChildren(pos ? makeLayer(deck.slides[pos.i], pos.step) : this.endLayer());
    this.pos = pos;
  }

  endLayer() {
    const layer = document.createElement("div");
    layer.className = "layer end";
    layer.textContent = "End of the deck";
    return layer;
  }

  // Moves to pos: animated when it's the next click from here (a build, or the slide's transition), else at once.
  go(deck, pos, animate = true) {
    const from = this.pos;
    this.busy = this.settle().then(() => {
      if (animate && from && pos) {
        const slide = deck.slides[from.i];
        if (pos.i === from.i && pos.step === from.step + 1) return this.build(pos);
        if (pos.i === from.i + 1 && pos.step === 0 && from.step === slide.steps)
          return this.transition(deck, pos, slide.transition);
      }
      this.show(deck, pos);
    });
    return this.busy;
  }

  async build(pos) {
    const section = this.canvas.querySelector(".layer:last-child section");
    const shown = [];
    for (const el of section.querySelectorAll("[data-build-in]")) {
      if (buildOrder(el) !== pos.step) continue;
      el.style.opacity = el.dataset.opacity;
      const to = getComputedStyle(el).opacity;
      shown.push(el.animate([{opacity: 0}, {opacity: to}], {duration: BUILD, easing: EASE}).finished);
    }
    this.pos = pos;
    await Promise.all(shown).catch(() => {});
  }

  async transition(deck, pos, kind) {
    const oldLayer = this.canvas.lastElementChild;
    const newLayer = makeLayer(deck.slides[pos.i], pos.step);
    this.pos = pos;
    if (kind === "none" || !oldLayer) {
      this.canvas.replaceChildren(newLayer);
      return;
    }
    let anims;
    if (kind === "push") {
      this.canvas.append(newLayer);
      anims = [newLayer.animate([{transform: `translateX(${W}px)`}, {transform: "none"}], {duration: PUSH, easing: EASE}),
               oldLayer.animate([{transform: "none"}, {transform: `translateX(${-W}px)`}], {duration: PUSH, easing: EASE})];
    } else if (kind === "magic") {
      anims = this.magic(oldLayer, newLayer);
    } else {  // fade: the new slide over the old; what's the same on both stays still
      this.canvas.append(newLayer);
      anims = [newLayer.animate([{opacity: 0}, {opacity: 1}], {duration: FADE, easing: EASE})];
    }
    await Promise.all(anims.map(a => a.finished)).catch(() => {});
    oldLayer.remove();
  }

  // Magic move. The old slide stays on top with a transparent background: its children that the new slide doesn't
  // have fade out, while the new slide's own fade in below. Children with the same id on both move and resize from
  // their old box to their new one; children that are identical on both (the timeline, an unchanged heading) stay.
  magic(oldLayer, newLayer) {
    this.canvas.insertBefore(newLayer, oldLayer);
    const os = oldLayer.firstElementChild, ns = newLayer.firstElementChild;
    os.style.background = "transparent";
    const scale = ns.getBoundingClientRect().width / W || 1;
    const box = (el, s) => {
      const r = el.getBoundingClientRect(), base = s.getBoundingClientRect();
      return {x: (r.left - base.left) / scale, y: (r.top - base.top) / scale, w: r.width / scale, h: r.height / scale};
    };
    const oldById = new Map([...os.children].filter(c => c.id).map(c => [c.id, c]));
    const matched = new Set(), anims = [];
    const newRest = [];
    for (const nc of ns.children) {
      const oc = nc.id ? oldById.get(nc.id) : undefined;
      if (oc === undefined || builtHidden(nc) || builtHidden(oc)) {
        if (!builtHidden(nc)) newRest.push(nc);
        continue;
      }
      matched.add(oc);
      const a = box(oc, os), b = box(nc, ns);
      const own = nc.style.transform || "";
      const from = {transform: `translate(${a.x - b.x}px, ${a.y - b.y}px) ${own}`.trim()};
      const to = {transform: own || "none"};
      const resize = !(nc instanceof SVGElement) && (Math.abs(a.w - b.w) > 0.5 || Math.abs(a.h - b.h) > 0.5);
      if (resize) {
        Object.assign(from, {width: `${a.w}px`, height: `${a.h}px`});
        Object.assign(to, {width: `${b.w}px`, height: `${b.h}px`});
      }
      const oo = getComputedStyle(oc).opacity, no = getComputedStyle(nc).opacity;
      if (oo !== no) Object.assign(from, {opacity: oo}), Object.assign(to, {opacity: no});
      oc.style.visibility = "hidden";
      anims.push(nc.animate([from, to], {duration: MAGIC, easing: EASE}));
    }
    // What's identical on both slides stays put; the rest of the old slide fades out, the rest of the new fades in.
    const oldRest = new Map();
    for (const oc of os.children) {
      if (matched.has(oc) || builtHidden(oc)) continue;
      const key = oc.outerHTML;
      if (!oldRest.has(key)) oldRest.set(key, []);
      oldRest.get(key).push(oc);
    }
    const fading = [];
    for (const nc of newRest) {
      const same = oldRest.get(nc.outerHTML);
      if (same && same.length) {
        same.shift().style.visibility = "hidden";
        continue;
      }
      fading.push(nc);
    }
    const oldLeft = [...oldRest.values()].flat();
    // Something new without an id where something of the same kind was (a heading, the timeline's amber mark) is
    // there at once, under the old one fading out on top: a crossfade that doesn't dim. Anything else, the code that's
    // new in particular, fades in after the moves start.
    const overlap = (a, b) => {
      const w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x), h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
      return w > 0 && h > 0 && w * h > 0.5 * Math.min(a.w * a.h, b.w * b.h);
    };
    const replaced = new Set();
    for (const nc of fading) {
      const b = box(nc, ns);
      const oc = nc.id ? undefined
        : oldLeft.find(o => !o.id && !replaced.has(o) && o.tagName === nc.tagName && overlap(box(o, os), b));
      if (oc) {
        replaced.add(oc);
        continue;
      }
      const to = getComputedStyle(nc).opacity;
      anims.push(nc.animate([{opacity: 0}, {opacity: to}],
                            {duration: MAGIC * 0.6, delay: MAGIC * 0.4, easing: EASE, fill: "backwards"}));
    }
    for (const oc of oldLeft) {
      const from = getComputedStyle(oc).opacity;
      const timing = replaced.has(oc) ? {duration: MAGIC * 0.7} : {duration: MAGIC * 0.5};
      anims.push(oc.animate([{opacity: from}, {opacity: 0}], {...timing, easing: EASE, fill: "forwards"}));
    }
    return anims;
  }
}

// Keeps the open pages of a show in step: each page applies a move itself and tells the others.
class Link {
  constructor(onMessage) {
    this.channel = "BroadcastChannel" in window ? new BroadcastChannel("palindrome-deck") : null;
    if (this.channel) this.channel.onmessage = e => onMessage(e.data);
  }
  post(message) {
    if (this.channel) this.channel.postMessage(message);
  }
}

// The keys both pages share. Returns the new position, or undefined when the key isn't a move.
function keyMove(deck, pos, e) {
  if (e.metaKey || e.ctrlKey || e.altKey) return undefined;
  switch (e.key) {
    case "ArrowRight": case "ArrowDown": case "PageDown": case " ": case "Enter": case "n":
      return nextPos(deck, pos) || pos;
    case "ArrowLeft": case "ArrowUp": case "PageUp": case "Backspace": case "p":
      return prevPos(deck, pos) || pos;
    case "Home":
      return {i: 0, step: 0};
    case "End":
      return {i: deck.slides.length - 1, step: deck.slides[deck.slides.length - 1].steps};
  }
  return undefined;
}

// Test hook for headless checks: ?at=I.S shows slide I (0-based) at step S; with &next=1 it then makes the next
// move, and with &freeze=MS it stops every animation MS milliseconds in, so a screenshot shows the middle of it.
function testParams() {
  const q = new URLSearchParams(location.search);
  const at = q.get("at");
  if (at === null) return null;
  const [i, step] = at.split(".").map(Number);
  return {pos: {i, step: step || 0}, next: q.get("next") === "1", freeze: q.has("freeze") ? Number(q.get("freeze")) : null};
}

function freezeAll(root, ms) {
  for (const a of root.getAnimations({subtree: true})) {
    a.pause();
    a.currentTime = ms;
  }
}
