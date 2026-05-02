#!/usr/bin/env node
// Render an ECharts option JSON to an SVG file, headless.
//
// Usage:
//   node scripts/render_echarts_svg.mjs <option.json> <out.svg> [width] [height]
//
// Defaults: 800 x 900. Used by build_graphical_toc.py for Panel B and is
// generic enough for any ECharts JSON in this repo.

import { readFileSync, writeFileSync } from 'node:fs';
import { JSDOM } from 'jsdom';
import * as echarts from 'echarts';

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node scripts/render_echarts_svg.mjs <option.json> <out.svg> [width] [height]');
  process.exit(2);
}
const [optionPath, outPath, w = '800', h = '900'] = args;

const opt = JSON.parse(readFileSync(optionPath, 'utf-8'));
// Strip render hints if present (they're advisory only).
delete opt._render_hints;

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
const root = dom.window.document.createElement('div');
root.style.width = `${w}px`;
root.style.height = `${h}px`;
dom.window.document.body.appendChild(root);

const chart = echarts.init(root, null, {
  renderer: 'svg',
  ssr: true,
  width: parseInt(w, 10),
  height: parseInt(h, 10),
});

chart.setOption(opt);

const svg = chart.renderToSVGString();
writeFileSync(outPath, svg, 'utf-8');
console.log(`  wrote ${outPath}  (${Buffer.byteLength(svg)} bytes)`);
chart.dispose();
