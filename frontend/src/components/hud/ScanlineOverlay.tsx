import React from 'react';

/**
 * CRT scanline + sweep overlay. Mounted once at the root of the layout.
 * Pure CSS — driven by `.scanlines` and `.scanline-sweep` in index.css.
 */
export const ScanlineOverlay: React.FC = () => (
  <>
    <div className="scanlines" aria-hidden="true" />
    <div className="scanline-sweep" aria-hidden="true" />
  </>
);
