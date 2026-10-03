/* chess-oracle · vortex_view.js — the visual storm of T16.

   Renders the vortex field of the current position over the board:

     particles    advected by the visual field (smooth attraction of the
                  currents + fixed-circulation vortices at the pieces +
                  in-basin damping); inside a current basin the swirl is
                  suppressed — the eye of the storm collapses onto the
                  sink, captured trajectories spiral in;
     currents     tapered arrows, coloured by tag:
                    descent gold / neutral faint gold / trap crimson /
                    escape silver dashed (the drawing resource);
     vortex rings dashed circles around the pieces (rotation direction
                  of the swirl).

   A DRAWN position renders as pure rotation: the currents carry no
   strength, the particles orbit the pieces forever.  A WON/LOSS position
   renders as the net: everything bends into the mating targets.

   Honours prefers-reduced-motion: a single static frame is drawn. */

(function (global) {
  'use strict';

  var V = global.ChessOracle.vortex;

  var COLORS = {
    descent: 'rgba(242, 181, 68, 0.85)',
    neutral: 'rgba(242, 181, 68, 0.30)',
    trap: 'rgba(228, 87, 76, 0.85)',
    escape: 'rgba(154, 164, 180, 0.75)',
    particle: '255, 224, 150',
    ring: 'rgba(154, 164, 180, 0.35)'
  };

  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function VortexView(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.field = null;
    this.flip = false;
    this.parts = null;          // {x, y, vx, vy, alive}
    this.phase = 0;
    this.raf = null;
    this.last = 0;
    this.reduced = global.matchMedia &&
      global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  VortexView.prototype.resize = function () {
    var box = this.canvas.parentNode;
    var s = Math.min(box.clientWidth, box.clientHeight);
    if (s > 0) {
      this.canvas.width = s;
      this.canvas.height = s;
    }
  };

  /* board-plane coords [0,8]^2 -> canvas px, honouring the flip */
  VortexView.prototype.map = function (px, py) {
    var s = this.canvas.width;
    var qx = this.flip ? 8 - px : px;
    var qy = this.flip ? 8 - py : py;
    return { x: qx / 8 * s, y: qy / 8 * s };
  };

  VortexView.prototype.setField = function (field, flip) {
    this.field = field;
    this.flip = !!flip;
    this.resize();
    this.seed();
    this.drawFrame(0);
  };

  VortexView.prototype.seed = function () {
    var rng = mulberry32(0x6001);                // deterministic ensemble
    var n = V.FROZEN.view_particles, a = [];
    for (var i = 0; i < n; i++) {
      a.push({ x: rng() * 8, y: rng() * 8,
               vx: 0, vy: 0, life: 0.5 + rng() * 0.5 });
    }
    this.parts = a;
  };

  /* the visual acceleration field (smooth currents + gated swirl) */
  VortexView.prototype.accel = function (x, y, out) {
    var f = this.field, i, cur, c;
    var ax = 0, ay = 0, basin = 0;
    if (f) {
      for (i = 0; i < f.currents.length; i++) {
        cur = f.currents[i];
        if (cur.J <= 0) continue;
        c = V.sqCenter(cur.to);
        var dx = c.x - x, dy = c.y - y;
        var r2 = 1 + dx * dx + dy * dy, inv = 1 / r2;
        ax += cur.J * dx * inv;
        ay += cur.J * dy * inv;
        basin += cur.J * inv;
      }
      for (i = 0; i < f.vortices.length; i++) {
        c = V.sqCenter(f.vortices[i].sq);
        var ux = x - c.x, uy = y - c.y;
        var r2c = 1 + ux * ux + uy * uy;
        var swirl = 1 / (1 + V.FROZEN.swirl_gate * basin);
        ax += swirl * f.vortices[i].g * (-uy) / r2c;
        ay += swirl * f.vortices[i].g * (ux) / r2c;
      }
    }
    out.ax = ax; out.ay = ay; out.zeta = V.FROZEN.zeta * basin;
  };

  VortexView.prototype.step = function (dt) {
    if (!this.parts || !this.field) return;
    var out = { ax: 0, ay: 0, zeta: 0 };
    for (var i = 0; i < this.parts.length; i++) {
      var p = this.parts[i];
      this.accel(p.x, p.y, out);
      p.vx += (out.ax - out.zeta * p.vx) * dt;
      p.vy += (out.ay - out.zeta * p.vy) * dt;
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      if (p.x < 0) p.x = 0; if (p.x > 8) p.x = 8;
      if (p.y < 0) p.y = 0; if (p.y > 8) p.y = 8;
      p.life -= dt * 0.05;
      if (p.life <= 0) {                     // respawn at the edges
        p.x = Math.random() * 8; p.y = Math.random() * 8;
        p.vx = 0; p.vy = 0; p.life = 0.5 + Math.random() * 0.5;
      }
    }
    this.phase += dt;
  };

  VortexView.prototype.drawCurrents = function (ctx) {
    var f = this.field;
    if (!f) return;
    for (var i = 0; i < f.currents.length; i++) {
      var cur = f.currents[i];
      var from = this.map((cur.from & 7) + 0.5, (cur.from >> 4) + 0.5);
      var to = this.map((cur.to & 7) + 0.5, (cur.to >> 4) + 0.5);
      ctx.strokeStyle = COLORS[cur.tag] || COLORS.neutral;
      ctx.lineWidth = cur.tag === 'descent' ? 2.4 : 1.4;
      ctx.setLineDash(cur.tag === 'escape' ? [5, 5] : []);
      if (cur.J <= 0 && cur.tag === 'neutral') continue;   // too faint
      ctx.beginPath();
      var mx = (from.x + to.x) / 2, my = (from.y + to.y) / 2;
      ctx.moveTo(from.x, from.y);
      ctx.quadraticCurveTo(mx + (to.y - from.y) * 0.12,
                           my - (to.x - from.x) * 0.12, to.x, to.y);
      ctx.stroke();
      if (cur.J > 0) {                       // arrowhead at the target
        var ang = Math.atan2(to.y - my, to.x - mx);
        ctx.beginPath();
        ctx.moveTo(to.x, to.y);
        ctx.lineTo(to.x - 7 * Math.cos(ang - 0.42),
                   to.y - 7 * Math.sin(ang - 0.42));
        ctx.lineTo(to.x - 7 * Math.cos(ang + 0.42),
                   to.y - 7 * Math.sin(ang + 0.42));
        ctx.closePath();
        ctx.fillStyle = COLORS[cur.tag];
        ctx.fill();
      }
    }
    ctx.setLineDash([]);
  };

  VortexView.prototype.drawRings = function (ctx) {
    var f = this.field;
    if (!f) return;
    var rot = this.phase * 0.8;
    for (var i = 0; i < f.vortices.length; i++) {
      var c = this.map(V.sqCenter(f.vortices[i].sq).x,
                       V.sqCenter(f.vortices[i].sq).y);
      ctx.strokeStyle = COLORS.ring;
      ctx.lineWidth = 1.2;
      ctx.setLineDash([4, 7]);
      ctx.lineDashOffset = -rot * 12 * (i % 2 ? 1 : -1);
      ctx.beginPath();
      ctx.arc(c.x, c.y, this.canvas.width / 8 * 0.42, 0, 6.2832);
      ctx.stroke();
    }
    ctx.setLineDash([]);
  };

  VortexView.prototype.drawParticles = function (ctx) {
    var s = this.canvas.width / 8;
    ctx.globalCompositeOperation = 'lighter';
    for (var i = 0; i < this.parts.length; i++) {
      var p = this.map(this.parts[i].x, this.parts[i].y);
      var a = Math.max(0, Math.min(1, this.parts[i].life)) * 0.85;
      var grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, s * 0.16);
      grad.addColorStop(0, 'rgba(' + COLORS.particle + ',' + (a * 0.9) + ')');
      grad.addColorStop(1, 'rgba(' + COLORS.particle + ',0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(p.x, p.y, s * 0.16, 0, 6.2832);
      ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';
  };

  VortexView.prototype.drawFrame = function () {
    var ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    if (!this.field) return;
    this.drawCurrents(ctx);
    this.drawRings(ctx);
    this.drawParticles(ctx);
  };

  VortexView.prototype.tick = function (ts) {
    var dt = Math.min(0.05, (ts - this.last) / 1000 || 0.016);
    this.last = ts;
    this.step(dt * 1.6);
    this.drawFrame();
    this.raf = global.requestAnimationFrame(this.tickBound);
  };

  VortexView.prototype.start = function () {
    if (this.raf || this.reduced) { this.drawFrame(); return; }
    this.tickBound = this.tick.bind(this);
    this.raf = global.requestAnimationFrame(this.tickBound);
  };

  VortexView.prototype.stop = function () {
    if (this.raf) { global.cancelAnimationFrame(this.raf); this.raf = null; }
  };

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.vortexView = { VortexView: VortexView };
})(window);
