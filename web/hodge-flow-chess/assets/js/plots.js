/* ════════════════════════════════════════════════════════════════════
   Hodge Flow — Шахматная Лаборатория / Chess Flow Laboratory
   plots.js — 600 dpi PNG exports via offscreen 4800×4800 canvas +
   toBlob; mobile fallback 2400×2400. window.HFPlots
   ════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const FULL = 4800;   // 8 in × 600 dpi
  const FALLBACK = 2400;

  function download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  /*
    exportPNG(filename, logicalSize, drawFn, onDone, onError)
    drawFn(ctx, size, scale) must render the full square.
  */
  function exportPNG(filename, logicalSize, drawFn, onDone, onError) {
    let size = FULL;
    let cv = null;
    try {
      cv = document.createElement('canvas');
      cv.width = size; cv.height = size;
      const tctx = cv.getContext('2d');
      if (!tctx) throw new Error('2d context unavailable');
      tctx.fillStyle = '#0A1120';
      tctx.fillRect(0, 0, size, size);
    } catch (e) {
      // memory-constrained device: retry at fallback resolution
      size = FALLBACK;
      try {
        cv = document.createElement('canvas');
        cv.width = size; cv.height = size;
      } catch (e2) {
        if (onError) onError(e2);
        return;
      }
    }
    const ctx = cv.getContext('2d');
    try {
      drawFn(ctx, size, size / logicalSize, size === FULL);
    } catch (e3) {
      if (onError) onError(e3);
      return;
    }
    if (cv.toBlob) {
      cv.toBlob(function (blob) {
        if (!blob) { if (onError) onError(new Error('toBlob returned null')); return; }
        download(blob, filename);
        if (onDone) onDone(size);
      }, 'image/png');
    } else {
      // very old engines: dataURL path
      try {
        const bin = atob(cv.toDataURL('image/png').split(',')[1]);
        const buf = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
        download(new Blob([buf], { type: 'image/png' }), filename);
        if (onDone) onDone(size);
      } catch (e4) {
        if (onError) onError(e4);
      }
    }
  }

  /* Board export: flow snapshot → 600 dpi square */
  function exportBoard(snap, caption, captionSub, lang, onDone, onError) {
    const logical = 1200;
    exportPNG('hodge_flow_board_600dpi.png', logical, function (ctx, size, scale) {
      window.HFBoard.draw(ctx, logical, logical, scale, snap, {
        now: performance.now(),
        caption: caption,
        captionSub: captionSub,
        showDpi: true,
        fontScale: scale,
      });
    }, onDone, onError);
  }

  /* Formula grid export */
  function exportFormula(job, scan, caption, captionSub, legendLabels, onDone, onError) {
    const logical = 1200;
    exportPNG('hodge_flow_formula_grid_600dpi.png', logical, function (ctx, size, scale) {
      window.HFBoard.renderFormula(ctx, logical, logical, scale, job, 1, {
        caption: caption,
        captionSub: captionSub,
        showDpi: true,
        legend: true,
        legendQ: legendLabels.q,
        legendLow: legendLabels.low,
        legendHigh: legendLabels.high,
        fontScale: scale,
      });
    }, onDone, onError);
  }

  /* Spectrum export: top band = Kronecker levels, bottom band = Gram O(1/N) */
  function exportSpectrum(levels, docEdge, caption, captionSub, gramRows, gramCaption, onDone, onError) {
    const logical = 1200;
    exportPNG('hodge_flow_tower_spectrum_600dpi.png', logical, function (ctx, size, scale) {
      const split = 0.62;
      window.HFBoard.renderSpectrum(ctx, logical, logical * split, scale, levels, {
        caption: caption,
        captionSub: captionSub,
        showDpi: true,
        docEdge: docEdge,
        fontScale: scale,
      });
      if (gramRows && gramRows.length) {
        window.HFBoard.renderGram(ctx, logical, logical * (1 - split), scale, gramRows, {
          offsetPx: size * split,
          caption: gramCaption,
          note: 'Gram towers G_N · CSR density O(1/N) · ~39 MB @ 220000 (documented)',
        });
      }
    }, onDone, onError);
  }

  window.HFPlots = {
    exportPNG: exportPNG,
    exportBoard: exportBoard,
    exportFormula: exportFormula,
    exportSpectrum: exportSpectrum,
    FULL: FULL,
    FALLBACK: FALLBACK,
  };
})();
