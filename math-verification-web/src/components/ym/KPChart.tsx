import {
  decadeLabel,
  log10Scale,
  logDecades,
  palette,
  sci,
} from "./chart-utils";
import { phase2 } from "@/data/ym";

const M = { top: 24, right: 28, bottom: 56, left: 74 };
const W = 760;
const H = 400;

/** Data-space window: one decade below the smallest sampled value. */
const Y_MIN = 1e-13;
const Y_MAX = 1e0;
const X_MIN = 0;
const X_MAX = 0.03;

export function KPChart() {
  const { beta, kp } = phase2.kpScan;
  const beta0 = phase2.beta0rig;

  const plotW = W - M.left - M.right;
  const plotH = H - M.top - M.bottom;
  const x = (b: number) => M.left + ((b - X_MIN) / (X_MAX - X_MIN)) * plotW;
  const y = log10Scale(Y_MIN, Y_MAX, M.top + plotH, M.top);

  // Split the curve wherever the bound is null (vacuous beyond index 38).
  const segments: Array<Array<{ x: number; y: number }>> = [];
  let current: Array<{ x: number; y: number }> = [];
  for (let i = 0; i < beta.length; i += 1) {
    const value = kp[i];
    if (value === null || value === undefined) {
      if (current.length > 1) segments.push(current);
      current = [];
      continue;
    }
    if (!(value > 0) || value > Y_MAX) {
      // Outside the drawn window: beta = 0 has the exact value A + tail = 0,
      // which a log axis cannot represent (log10(0) = -Infinity), so the path
      // breaks there instead of emitting a non-finite coordinate.
      if (current.length > 1) segments.push(current);
      current = [];
      continue;
    }
    current.push({ x: x(beta[i]), y: y(value) });
  }
  if (current.length > 1) segments.push(current);

  const validCount = kp.filter((v) => v !== null && v !== undefined).length;
  const lastValid = kp[validCount - 1];
  // The first sample is A + tail = 0 (the exact integer value at β = 0), which
  // is off the bottom of a log axis. The curve therefore starts at the second
  // sample, and the caption states this explicitly.
  const firstPlotted = beta[1];

  return (
    <figure className="my-8 rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
      <div className="overflow-x-auto">
        <svg
          role="img"
          aria-label={`Log-scale plot of the Kadanoff-Pfeuty polymer norm A(beta) plus analytic tail versus beta from 0 to 0.03. The curve rises from about 1.9e-13 to ${sci(
            lastValid as number,
          )} at its last sampled point and is undefined beyond beta 0.0148, where the criterion becomes vacuous. A horizontal line marks the convergence criterion value 1.`}
          viewBox={`0 0 ${W} ${H}`}
          className="mx-auto h-auto w-full min-w-[620px]"
        >
          <title>Kadanoff-Pfeuty norm A(β) + tail(β)</title>

          {/* horizontal grid at each decade */}
          {logDecades(Y_MIN, Y_MAX).map((tick) => (
            <g key={tick}>
              <line
                x1={M.left}
                y1={y(tick)}
                x2={M.left + plotW}
                y2={y(tick)}
                stroke={palette.grid}
                strokeWidth={1}
              />
              <text
                x={M.left - 10}
                y={y(tick) + 4}
                textAnchor="end"
                fill={palette.axis}
                fontSize={11}
                fontFamily="ui-monospace, monospace"
              >
                {decadeLabel(tick)}
              </text>
            </g>
          ))}

          {/* x axis ticks */}
          {[0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03].map((tick) => (
            <g key={`x${tick}`}>
              <line
                x1={x(tick)}
                y1={M.top + plotH}
                x2={x(tick)}
                y2={M.top + plotH + 6}
                stroke={palette.axis}
              />
              <text
                x={x(tick)}
                y={M.top + plotH + 22}
                textAnchor="middle"
                fill={palette.axis}
                fontSize={11}
                fontFamily="ui-monospace, monospace"
              >
                {tick.toFixed(3)}
              </text>
            </g>
          ))}

          {/* axes */}
          <line
            x1={M.left}
            y1={M.top}
            x2={M.left}
            y2={M.top + plotH}
            stroke={palette.axis}
          />
          <line
            x1={M.left}
            y1={M.top + plotH}
            x2={M.left + plotW}
            y2={M.top + plotH}
            stroke={palette.axis}
          />
          <text
            x={M.left + plotW / 2}
            y={H - 18}
            textAnchor="middle"
            fill={palette.ink}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
          >
            β (inverse coupling squared)
          </text>
          <text
            x={16}
            y={M.top + plotH / 2}
            textAnchor="middle"
            fill={palette.ink}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
            transform={`rotate(-90 16 ${M.top + plotH / 2})`}
          >
            A(β) + tail(β)
          </text>

          {/* Kadanoff-Pfeuty criterion line */}
          <line
            x1={M.left}
            y1={y(1)}
            x2={M.left + plotW}
            y2={y(1)}
            stroke="#f87171"
            strokeWidth={2}
            strokeDasharray="8 5"
          />
          <text
            x={M.left + 8}
            y={y(1) - 8}
            fill="#f87171"
            fontSize={12}
            fontWeight={600}
            fontFamily="ui-monospace, monospace"
          >
            Kadanoff-Pfeuty criterion: A + tail {"<"} 1
          </text>

          {/* the curve, broken at the nulls */}
          {segments.map((segment, i) => (
            <path
              key={i}
              d={segment
                .map(
                  (p, j) =>
                    `${j === 0 ? "M" : "L"}${p.x.toFixed(2)},${p.y.toFixed(2)}`,
                )
                .join(" ")}
              fill="none"
              stroke={palette.green}
              strokeWidth={2.5}
              strokeLinecap="round"
            />
          ))}
          {segments.flat().map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r={2.6} fill={palette.green} />
          ))}

          {/* beta_0 vertical */}
          <line
            x1={x(beta0)}
            y1={M.top}
            x2={x(beta0)}
            y2={M.top + plotH}
            stroke={palette.blue}
            strokeWidth={1.6}
            strokeDasharray="6 4"
          />
          <text
            x={x(beta0) - 6}
            y={M.top + 16}
            textAnchor="end"
            fill={palette.blue}
            fontSize={12}
            fontWeight={600}
            fontFamily="ui-monospace, monospace"
          >
            β₀ʳⁱᵍ = 0.01452
          </text>
        </svg>
      </div>

      <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-xs">
          <span className="text-green-400">
            — A(β) + tail(β), {validCount} sampled values
          </span>
          <span className="text-red-400">— convergence criterion (value 1)</span>
          <span className="text-blue-400">- - β₀ʳⁱᵍ bisection root</span>
        </p>
        <p>
          The quantity plotted is the root-plaquette polymer norm{" "}
          <span className="font-mono text-gray-300">A(β)</span> summed over all
          88 enumerated closed polymers, plus the rigorously dominating
          analytic tail <span className="font-mono text-gray-300">
            b x⁶/(1 − x)
          </span>{" "}
          for everything beyond size 6. Convergence of the cluster expansion
          needs this total to stay below 1, and it does all the way up to{" "}
          <span className="font-mono text-green-400">
            β₀ʳⁱᵍ = 0.0145206
          </span>{" "}
          (bisection; the sum equals 0.99671 there).
        </p>
        <p className="text-gray-500">
          The curve starts at β = {firstPlotted.toFixed(6)}, not at β = 0: at β =
          0 the exact value of A + tail is 0, which no logarithmic axis can
          draw, so the first visible point ({sci(1.94e-13, 3)}) is the second
          sample.
        </p>
        <p className="text-gray-500">
          Past β ≈ 0.0148 the sampled values stop: the enumeration only covers
          88 polymers, and the analytic tail alone exceeds 1, so the bound
          becomes vacuous there. The gap in the curve is that honesty cut-off —
          no data point has been invented to fill it.
        </p>
      </figcaption>
    </figure>
  );
}
