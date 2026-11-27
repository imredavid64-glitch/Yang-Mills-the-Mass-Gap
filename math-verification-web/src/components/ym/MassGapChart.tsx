import {
  log10Scale,
  logDecades,
  decadeLabel,
  palette,
  samplePath,
  toPolyline,
} from "./chart-utils";
import { phase2, LOG2 } from "@/data/ym";
const M = { top: 24, right: 28, bottom: 56, left: 78 };
const W = 780;
const H = 420;

const Y_MIN = 0.3;
const Y_MAX = 30;
const X_MIN = 0;
const X_MAX = 0.03;

/** deltaBeta = log 2 - beta^2/4 — cited, not derived; shown for reference only. */
const deltaBeta = (beta: number) => LOG2 - (beta * beta) / 4;

export function MassGapChart() {
  const { beta, gap } = phase2.gapBound;
  const beta0 = phase2.beta0rig;

  const plotW = W - M.left - M.right;
  const plotH = H - M.top - M.bottom;
  const x = (b: number) => M.left + ((b - X_MIN) / (X_MAX - X_MIN)) * plotW;
  const y = log10Scale(Y_MIN, Y_MAX, M.top + plotH, M.top);

  const deltaCurve = samplePath(deltaBeta, X_MIN + 0.0002, X_MAX, 160);

  return (
    <figure className="my-8 rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
      <div className="overflow-x-auto">
        <svg
          role="img"
          aria-label="Chart comparing torus-only bound (superseded), certified interval-arithmetic domain beta <= 0.0167 (mu >= 0.0063), and the cited analytic asymptote 4 ln(4/beta) shown for reference only"
          viewBox={`0 0 ${W} ${H}`}
          className="mx-auto h-auto w-full min-w-[640px]"
        >
          <title>Rigorous gap bound versus the analytic mass gap</title>

          {/* certified region shading */}
          <rect
            x={M.left}
            y={M.top}
            width={Math.max(0, x(0.0167) - M.left)}
            height={plotH}
            fill={palette.greenSoft}
          />
          <text
            x={M.left + 10}
            y={M.top + 18}
            fill={palette.green}
            fontSize={12}
            fontWeight={600}
            fontFamily="ui-monospace, monospace"
          >
            certified region β {"<"} 0.0167 (μ ≥ 0.0063)
          </text>

          {logDecades(Y_MIN, Y_MAX).map((tick) => (
            <g key={tick}>
              <line
                x1={M.left}
                y1={y(tick)}
                x2={M.left + plotW}
                y2={y(tick)}
                stroke={palette.grid}
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
            β
          </text>
          <text
            x={18}
            y={M.top + plotH / 2}
            textAnchor="middle"
            fill={palette.ink}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
            transform={`rotate(-90 18 ${M.top + plotH / 2})`}
          >
            gap (log scale)
          </text>

          {/* Delta(beta): nearly flat analytic curve */}
          <path
            d={toPolyline(deltaCurve, x, y, M.top, M.top + plotH)}
            fill="none"
            stroke={palette.blue}
            strokeWidth={2.5}
          />
          <text
            x={x(X_MAX) - 8}
            y={y(deltaBeta(X_MAX)) - 12}
            textAnchor="end"
            fill={palette.blue}
            fontSize={12}
            fontWeight={600}
            fontFamily="ui-monospace, monospace"
          >
            cited asymptote Δ(β) = log 2 − β²/4
          </text>

          {/* torus-only KP bound (superseded by certified result) */}
          <path
            d={beta
              .map(
                (b, i) =>
                  `${i === 0 ? "M" : "L"}${x(b).toFixed(2)},${y(gap[i]).toFixed(2)}`,
              )
              .join(" ")}
            fill="none"
            stroke={palette.green}
            strokeWidth={2.5}
          />
          {beta.map((b, i) => (
            <circle
              key={i}
              cx={x(b)}
              cy={y(gap[i])}
              r={2.5}
              fill={palette.green}
            />
          ))}
          <text
            x={x(beta[4])}
            y={y(gap[4]) - 10}
            fill={palette.green}
            fontSize={12}
            fontWeight={600}
            fontFamily="ui-monospace, monospace"
          >
            −log(A + tail) ≥ Δ
          </text>

          {/* beta_0 vertical */}
          <line
            x1={x(beta0)}
            y1={M.top}
            x2={x(beta0)}
            y2={M.top + plotH}
            stroke={palette.blue}
            strokeDasharray="6 4"
            strokeWidth={1.6}
          />
          <text
            x={x(beta0) + 6}
            y={M.top + 40}
            fill={palette.blue}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
          >
            β₀ʳⁱᵍ = 0.01452 (superseded)
          </text>
        </svg>
      </div>

      <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-xs">
          <span className="text-blue-400">
            — torus-only KP bound −log(A + tail), 38 points (superseded)
          </span>
          <span className="text-green-400">— certified domain β {"<"} 0.0167</span>
        </p>
        <p className="mt-2 text-yellow-300">
          Superseded: the green curve uses incorrect Catalan-moment weights; the
          certified interval-arithmetic domain is β {"<"} 0.0167 with μ ≥ 0.0063
          (proof/rigorous_check.py). The analytic estimate log 2 − β²/4 is cited,
          not derived.
        </p>
      </figcaption>
    </figure>
  );
}
