import {
  decadeLabel,
  linspace,
  log10Scale,
  logDecades,
  palette,
  sci,
} from "./chart-utils";
import { phase3, LOG2 } from "@/data/ym";

const M = { top: 28, right: 78, bottom: 52, left: 82 };
const W = 760;
const H = 400;

const Y_MIN = 1e-10;
const Y_MAX = 1e0;
const GAP_MIN = 0.62;
const GAP_MAX = 0.7;

export function RGFlowChart() {
  const { step, beta, gap } = phase3.trajectory;

  const plotW = W - M.left - M.right;
  const plotH = H - M.top - M.bottom;

  const x = (s: number) =>
    M.left + (step.length <= 1 ? 0 : (s / (step.length - 1)) * plotW);
  const yBeta = log10Scale(Y_MIN, Y_MAX, M.top + plotH, M.top);
  const yGap = (g: number) =>
    M.top + plotH - ((g - GAP_MIN) / (GAP_MAX - GAP_MIN)) * plotH;

  const barW = plotW / (step.length * 2.4);

  return (
    <figure className="my-8 rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
      <div className="overflow-x-auto">
        <svg
          role="img"
          aria-label={`Renormalization group trajectory over five blocking steps. The coupling beta falls on a log scale from 0.5 to ${sci(
            beta[beta.length - 1],
          )}, while the mass gap on the right axis rises from 0.6306 to log 2 equals 0.693147, shown as a dashed asymptote.`}
          viewBox={`0 0 ${W} ${H}`}
          className="mx-auto h-auto w-full min-w-[620px]"
        >
          <title>Exact character-space RG trajectory</title>

          {logDecades(Y_MIN, Y_MAX).map((tick) => (
            <g key={tick}>
              <line
                x1={M.left}
                y1={yBeta(tick)}
                x2={M.left + plotW}
                y2={yBeta(tick)}
                stroke={palette.grid}
              />
              <text
                x={M.left - 10}
                y={yBeta(tick) + 4}
                textAnchor="end"
                fill={palette.axis}
                fontSize={11}
                fontFamily="ui-monospace, monospace"
              >
                {decadeLabel(tick)}
              </text>
            </g>
          ))}

          {linspace(GAP_MIN, GAP_MAX, 5).map((tick) => (
            <text
              key={tick}
              x={M.left + plotW + 10}
              y={yGap(tick) + 4}
              fill={palette.green}
              fontSize={11}
              fontFamily="ui-monospace, monospace"
            >
              {tick.toFixed(2)}
            </text>
          ))}

          {/* log 2 asymptote */}
          <line
            x1={M.left}
            y1={yGap(LOG2)}
            x2={M.left + plotW}
            y2={yGap(LOG2)}
            stroke={palette.green}
            strokeDasharray="7 5"
            strokeWidth={1.6}
          />
          <text
            x={M.left + 10}
            y={yGap(LOG2) - 8}
            fill={palette.green}
            fontSize={12}
            fontWeight={600}
            fontFamily="ui-monospace, monospace"
          >
            asymptote Δ = log 2 = 0.69315
          </text>

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
          <line
            x1={M.left + plotW}
            y1={M.top}
            x2={M.left + plotW}
            y2={M.top + plotH}
            stroke={palette.axis}
          />

          <text
            x={M.left - 62}
            y={M.top + plotH / 2}
            textAnchor="middle"
            fill={palette.purple}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
            transform={`rotate(-90 ${M.left - 62} ${M.top + plotH / 2})`}
          >
            βₙ (log scale)
          </text>
          <text
            x={M.left + plotW + 62}
            y={M.top + plotH / 2}
            textAnchor="middle"
            fill={palette.green}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
            transform={`rotate(90 ${M.left + plotW + 62} ${M.top + plotH / 2})`}
          >
            Δ(βₙ) (linear)
          </text>
          <text
            x={M.left + plotW / 2}
            y={H - 14}
            textAnchor="middle"
            fill={palette.ink}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
          >
            blocking step n
          </text>

          {/* beta bars; the last step falls below the drawn range and is floored */}
          {step.map((s, i) => {
            const onScale = beta[i] >= Y_MIN;
            const value = onScale ? beta[i] : Y_MIN;
            const top = yBeta(value);
            return (
              <rect
                key={s}
                x={x(s) - barW / 2}
                y={top}
                width={barW}
                height={M.top + plotH - top}
                rx={3}
                fill={palette.purple}
                fillOpacity={onScale ? 0.35 : 0.18}
                stroke={palette.purple}
                strokeDasharray={onScale ? undefined : "4 3"}
              />
            );
          })}

          {/* gap curve on the right axis */}
          <path
            d={step
              .map(
                (s, i) =>
                  `${i === 0 ? "M" : "L"}${x(s).toFixed(2)},${yGap(gap[i]).toFixed(2)}`,
              )
              .join(" ")}
            fill="none"
            stroke={palette.green}
            strokeWidth={2.5}
          />
          {step.map((s, i) => (
            <circle
              key={`g${s}`}
              cx={x(s)}
              cy={yGap(gap[i])}
              r={4}
              fill={palette.green}
            />
          ))}

          {/* step labels with beta values */}
          {step.map((s, i) => (
            <g key={`l${s}`}>
              <text
                x={x(s)}
                y={M.top + plotH + 20}
                textAnchor="middle"
                fill={palette.ink}
                fontSize={12}
                fontFamily="ui-monospace, monospace"
              >
                n = {s}
              </text>
              <text
                x={x(s)}
                y={M.top + plotH + 36}
                textAnchor="middle"
                fill={palette.purple}
                fontSize={10}
                fontFamily="ui-monospace, monospace"
              >
                {i === 4 ? "3.95×10⁻¹⁰" : beta[i].toPrecision(4)}
              </text>
            </g>
          ))}

          <text
            x={M.left + 10}
            y={M.top + 16}
            fill={palette.axis}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            each step squares the coupling: r → r²
          </text>
        </svg>
      </div>

      <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-xs">
          <span className="text-purple-400">
            ▮ βₙ — effective coupling (left, log)
          </span>
          <span className="text-green-400">— Δ(βₙ) mass gap (right, linear)</span>
          <span className="text-green-400">- - asymptote at log 2</span>
          <span className="text-purple-400">dashed bar — below the axis range</span>
        </p>
        <p>
          Five blocking steps starting from{" "}
          <span className="font-mono text-gray-300">β₀ = 0.5</span>. The
          coupling collapses by roughly nine orders of magnitude while the mass
          gap climbs monotonically to{" "}
          <span className="font-mono text-green-400">log 2 = 0.693147</span> —
          the gap at β = 0 is an attractor, reached along the exact trajectory{" "}
          <span className="font-mono text-gray-300">Δ(βₙ) = log 2 − βₙ²/4</span>.
        </p>
        <p className="text-gray-500">
          The purple bar at step 4 is dashed: its true coupling (3.95 × 10⁻¹⁰)
          lies below the lowest decade drawn, so the bar marks where the
          trajectory has gone rather than its exact height. Exact values are in
          the table below.
        </p>
      </figcaption>
    </figure>
  );
}
