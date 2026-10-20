/**
 * Shared, dependency-free helpers for the hand-rolled SVG charts.
 *
 * Everything here is pure math: log/linear scales, tick generation, and
 * number formatting. Charts render on the server, so there are no hooks,
 * no state, and no client bundle cost.
 */

export type Scale = (value: number) => number;

/** Build a linear map from a numeric domain onto a pixel range. */
export function linearScale(
  d0: number,
  d1: number,
  r0: number,
  r1: number,
): Scale {
  const span = d1 - d0 || 1;
  return (value: number) => r0 + ((value - d0) / span) * (r1 - r0);
}

/**
 * Build a base-10 log map. Values must be strictly positive; callers clip or
 * skip non-positive inputs before mapping.
 */
export function log10Scale(
  d0: number,
  d1: number,
  r0: number,
  r1: number,
): Scale {
  const l0 = Math.log10(d0);
  const l1 = Math.log10(d1);
  return (value: number) => linearScale(l0, l1, r0, r1)(Math.log10(value));
}

/** Decade boundaries (10^k) within [d0, d1], ascending. */
export function logDecades(d0: number, d1: number): number[] {
  const k0 = Math.ceil(Math.log10(d0));
  const k1 = Math.floor(Math.log10(d1));
  const out: number[] = [];
  for (let k = k0; k <= k1; k += 1) out.push(10 ** k);
  return out;
}

/** Evenly spaced values across [d0, d1]; useful for linear axes. */
export function linspace(d0: number, d1: number, count: number): number[] {
  if (count <= 1) return [d0];
  const out: number[] = [];
  for (let i = 0; i < count; i += 1) {
    out.push(d0 + ((d1 - d0) * i) / (count - 1));
  }
  return out;
}

/** n evenly spaced samples of `f` across [d0, d1], ready for a polyline. */
export function samplePath(
  f: (x: number) => number,
  d0: number,
  d1: number,
  n: number,
): XY[] {
  return linspace(d0, d1, n).map((x) => ({ x, y: f(x) }));
}

/** A single point in an already-projected path. */
export type XY = { x: number; y: number };

/**
 * `M x,y L x,y ...` for a list of projected points.
 *
 * Points outside `[lo, hi]` are dropped and each surviving run is emitted as
 * its own subpath, so values past the axis window are simply clipped away
 * instead of leaking an `Infinity` coordinate into the SVG.
 */
export function toPolyline(
  points: XY[],
  sx: Scale,
  sy: Scale,
  lo = 0,
  hi = Number.POSITIVE_INFINITY,
): string {
  const subpaths: string[] = [];
  let run: string[] = [];

  const flush = () => {
    if (run.length > 1) subpaths.push(run.join(" "));
    run = [];
  };

  for (const p of points) {
    const cx = sx(p.x);
    const cy = sy(p.y);
    if (!Number.isFinite(cx) || !Number.isFinite(cy) || cy < lo || cy > hi) {
      flush();
      continue;
    }
    run.push(`${run.length === 0 ? "M" : "L"}${cx.toFixed(2)},${cy.toFixed(2)}`);
  }
  flush();

  return subpaths.join(" ");
}

/** Scientific notation with a Unicode multiplication sign, e.g. `3.9 × 10⁻¹⁰`. */
export function sci(value: number, digits = 3): string {
  if (!Number.isFinite(value)) return "—";
  if (value === 0) return "0";
  const exponent = Math.floor(Math.log10(Math.abs(value)));
  const mantissa = value / 10 ** exponent;
  const sup = String(exponent)
    .split("")
    .map((ch) => (ch === "-" ? "⁻" : "⁰¹²³⁴⁵⁶⁷⁸⁹"[Number(ch)]))
    .join("");
  return `${mantissa.toFixed(digits)} × 10${sup}`;
}

/** Compact log-axis tick label, e.g. `10⁻⁶`. */
export function decadeLabel(value: number): string {
  const exponent = Math.round(Math.log10(value));
  const sup = String(exponent)
    .split("")
    .map((ch) => (ch === "-" ? "⁻" : "⁰¹²³⁴⁵⁶⁷⁸⁹"[Number(ch)]))
    .join("");
  return `10${sup}`;
}

/** Fixed-precision decimal without exponent surprises at small magnitudes. */
export function fixed(value: number, digits = 4): string {
  return value.toFixed(digits);
}

/** Palette shared by every chart so the legend colors stay consistent. */
export const palette = {
  green: "#4ade80",
  greenSoft: "rgba(74, 222, 128, 0.12)",
  blue: "#60a5fa",
  purple: "#c084fc",
  grid: "#374151",
  axis: "#6b7280",
  ink: "#d1d5db",
} as const;
