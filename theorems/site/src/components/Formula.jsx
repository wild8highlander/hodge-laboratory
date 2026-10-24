import React, { useMemo } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

/** Render a KaTeX formula (display or inline) into a span. */
export default function Formula({ tex, display = false, className = '' }) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(tex, {
        displayMode: display,
        throwOnError: false,
        trust: true,
        colorIsTextColor: true,
      });
    } catch (e) {
      return `<span style="color:#f472b6">${tex}</span>`;
    }
  }, [tex, display]);
  return <span className={className} dangerouslySetInnerHTML={{ __html: html }} />;
}
