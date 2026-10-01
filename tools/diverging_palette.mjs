// Generates the map's color ramps: the diverging ramp for zero-centered measures (decline <-> growth) and the
// six-step sequential ramp that overrides chicago.css's --seq-* on the map page (see site/sequential.css).
//   node tools/diverging_palette.mjs          -> prints the CSS custom properties
// Hues come from the Chicago School chart tokens (--s1 lake blue, --s2 terra cotta) so the ramp belongs to the
// same system. Seven steps, equal count per arm, neutral gray midpoint, lightness moves monotonically outward
// from the neutral (lighter outward on dark, darker outward on light). Validate with the dataviz validator;
// see the results recorded in site/diverging.css.

const toLin = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const toSrgb = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055);
const hex2rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
function rgb2oklab([r, g, b]) {
  const [R, G, B] = [r, g, b].map(toLin);
  const l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B);
  const m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B);
  const s = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B);
  return [0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s];
}
function oklab2rgb([L, a, b]) {
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3,
    s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
    -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s].map(toSrgb);
}
export const hueOf = (hex) => { const [, a, b] = rgb2oklab(hex2rgb(hex)); return Math.atan2(b, a); };
const inGamut = (rgb) => rgb.every((v) => v >= -1e-4 && v <= 1 + 1e-4);
const toHex = (rgb) => "#" + rgb.map((v) => Math.round(Math.min(1, Math.max(0, v)) * 255).toString(16).padStart(2, "0")).join("");
function lch(L, C, h) {
  for (let c = C; c >= 0; c -= 0.002) { const rgb = oklab2rgb([L, c * Math.cos(h), c * Math.sin(h)]); if (inGamut(rgb)) return toHex(rgb); }
  return toHex(oklab2rgb([L, 0, 0]));
}

// mode -> chart tokens whose hues we reuse, neutral lightness, step lightness, chroma schedule
const MODES = {
  dark: { blue: "#2f9bd4", terra: "#cf6236", neutral: [0.46, 0.012], L: [0.57, 0.66, 0.76], C: [0.10, 0.13, 0.15] },
  light: { blue: "#2483bb", terra: "#c1541f", neutral: [0.74, 0.012], L: [0.60, 0.52, 0.44], C: [0.10, 0.13, 0.15] },
};
export function ramp(mode) {
  const m = MODES[mode], hb = hueOf(m.blue), ht = hueOf(m.terra);
  const arm = (h) => m.L.map((L, i) => lch(L, m.C[i], h));
  const decline = arm(ht), growth = arm(hb);
  // div-1 = largest decline ... div-4 = about flat ... div-7 = largest growth
  return { steps: [...decline.slice().reverse(), lch(m.neutral[0], m.neutral[1], hb), ...growth], decline, growth };
}
// sequential: one hue (--s1 lake blue), six steps, lightness monotone and every step at least 3:1 against
// --page so the palest/darkest bin still reads as a mark (WCAG 1.4.11). Light on dark: low values dim, high bright.
const SEQ = {
  dark: { page: "#0c0e10", L: [0.52, 0.60, 0.68, 0.76, 0.84, 0.92], C: [0.09, 0.105, 0.115, 0.115, 0.095, 0.06] },
  light: { page: "#f2efe9", L: [0.61, 0.54, 0.47, 0.40, 0.33, 0.26], C: [0.10, 0.115, 0.12, 0.11, 0.095, 0.075] },
};
const lum = (h) => { const [r, g, b] = hex2rgb(h).map(toLin); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
export const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => p - q); return (y + 0.05) / (x + 0.05); };
export function seqRamp(mode) { const m = SEQ[mode], h = hueOf("#2f9bd4"); return m.L.map((L, i) => lch(L, m.C[i], h)); }
if (process.argv[1] && process.argv[1].endsWith("diverging_palette.mjs")) {
  for (const mode of ["dark", "light"]) {
    const { steps } = ramp(mode);
    console.log(`${mode}: ${steps.map((h, i) => `--div-${i + 1}: ${h};`).join(" ")}`);
  }
  for (const mode of ["dark", "light"]) {
    const s = seqRamp(mode);
    console.log(`${mode}: ${s.map((h, i) => `--seq-${i + 1}: ${h};`).join(" ")}`);
    console.log(`  contrast vs page: ${s.map((h) => contrast(h, SEQ[mode].page).toFixed(2)).join(" ")}`);
  }
}
