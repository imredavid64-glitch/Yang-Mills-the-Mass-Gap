import { linearScale, palette, toPolyline } from "./chart-utils";
import { phase5 } from "@/data/ym";

const M = { top: 28, right: 24, bottom: 56, left: 62 };
const W = 780;
const H = 380;

/** Plot t = 1..3; C(0) = 1 is off the top of this window. */
const T_MIN = 0.7;
const T_MAX = 3.3;
const Y_MIN = -0.03;
const Y_MAX = 0.055;

export function OSCorrelationChart() {
  const { t, beta1, beta1_se, beta2, beta2_se } = phase5.corr;

  const plotW = W - M.left - M.right;
  const plotH = H - M.top - M.bottom;
  const x = linearScale(T_MIN, T_MAX, M.left, M.left + plotW);
  const y = linearScale(Y_MIN, Y_MAX, M.top + plotH, M.top);

  const series = [
    {
      key: "beta1",
      label: "β = 1.0",
      color: palette.green,
      values: beta1,
      errors: beta1_se,
    },
    {
      key: "beta2",
      label: "β = 2.0",
      color: palette.purple,
      values: beta2,
      errors: beta2_se,
    },
  ];

  const jitter: Record<string, number> = { beta1: -0.06, beta2: 0.06 };

  return (
    <figure className="my-8 rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
      <div className="overflow-x-auto">
        <svg
          role="img"
          aria-label="Connected correlator C of t with plus minus one standard error bars for beta equals 1 in green and beta equals 2 in purple, over t from 1 to 3. The beta equals 1 points are all within errors of zero, while beta equals 2 has C of 1 equal to 0.0332 plus or minus 0.0102."
          viewBox={`0 0 ${W} ${H}`}
          className="mx-auto h-auto w-full min-w-[620px]"
        >
          <title>Connected correlator C(t) with standard-error bars</title>

          {[-0.02, 0, 0.02, 0.04].map((tick) => (
            <g key={tick}>
              <line
                x1={M.left}
                y1={y(tick)}
                x2={M.left + plotW}
                y2={y(tick)}
                stroke={tick === 0 ? palette.axis : palette.grid}
                strokeWidth={tick === 0 ? 1.6 : 1}
              />
              <text
                x={M.left - 10}
                y={y(tick) + 4}
                textAnchor="end"
                fill={palette.axis}
                fontSize={11}
                fontFamily="ui-monospace, monospace"
              >
                {tick.toFixed(2)}
              </text>
            </g>
          ))}

          {[1, 2, 3].map((tick) => (
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
                fill={palette.ink}
                fontSize={12}
                fontFamily="ui-monospace, monospace"
              >
                t = {tick}
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
            y={H - 16}
            textAnchor="middle"
            fill={palette.ink}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
          >
            Euclidean time separation t
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
            C(t)
          </text>

          {series.map((s) => (
            <g key={s.key}>
              {t.map((time, i) => {
                if (time === 0) return null;
                const cx = x(time) + jitter[s.key];
                const value = s.values[i];
                const err = s.errors[i];
                return (
                  <g key={`${s.key}-${time}`}>
                    <line
                      x1={cx}
                      y1={y(value - err)}
                      x2={cx}
                      y2={y(value + err)}
                      stroke={s.color}
                      strokeWidth={1.6}
                    />
                    <line
                      x1={cx - 5}
                      y1={y(value - err)}
                      x2={cx + 5}
                      y2={y(value - err)}
                      stroke={s.color}
                      strokeWidth={1.6}
                    />
                    <line
                      x1={cx - 5}
                      y1={y(value + err)}
                      x2={cx + 5}
                      y2={y(value + err)}
                      stroke={s.color}
                      strokeWidth={1.6}
                    />
                    <circle cx={cx} cy={y(value)} r={4} fill={s.color} />
                  </g>
                );
              })}
            </g>
          ))}

          {series.map((s) => (
            <path
              key={`line-${s.key}`}
              d={toPolyline(
                s.values
                  .map((value, i) => ({ x: t[i] + jitter[s.key], y: value }))
                  .filter((p) => p.x > T_MIN),
                x,
                y,
                0,
                H,
              )}
              fill="none"
              stroke={s.color}
              strokeWidth={1.4}
              strokeOpacity={0.5}
            />
          ))}

          <text
            x={x(1) + jitter.beta2 + 10}
            y={y(beta2[1]) - 14}
            fill={palette.purple}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            C(1) = 0.0332 ± 0.0102
          </text>
          <text
            x={x(1) + jitter.beta1 - 10}
            y={y(beta1[1]) - 14}
            textAnchor="end"
            fill={palette.green}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            consistent with 0
          </text>
          <text
            x={M.left + 12}
            y={M.top + 14}
            fill={palette.axis}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            C(0) = 1.000 for both β (off scale)
          </text>
        </svg>
      </div>

      <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-xs">
          <span className="text-green-400">● β = 1.0</span>
          <span className="text-purple-400">● β = 2.0</span>
          <span className="text-gray-300">— ± 1 standard error</span>
          <span className="text-gray-500">solid line at C = 0</span>
        </p>
        <p>
          The plot starts at t = 1 so the error bars are legible: at both
          couplings <span className="font-mono text-gray-300">C(0) = 1</span>{" "}
          by normalisation and would flatten everything else.
        </p>
        <p>
          At <span className="font-mono text-green-400">β = 1.0</span> the
          correlator is zero within errors from t = 1 onward (C = −0.0020 ±
          0.0046), i.e. the correlation length is below one lattice spacing — the
          strong-coupling picture. At{" "}
          <span className="font-mono text-purple-400">β = 2.0</span> the leading
          value is genuinely non-zero,{" "}
          <span className="font-mono text-purple-400">
            C(1) = 0.0332 ± 0.0102
          </span>
          , a 3.2 σ signal that the correlation length is growing as the coupling
          increases — exactly where the rigorous β {"<"} 0.0145 region ends and
          Monte Carlo takes over.
        </p>
        <p className="text-gray-500">
          The decay significance from C(0) to C(1) is 125.6 σ at β = 1 and
          114.2 σ at β = 2 (OS4, table below).
        </p>
      </figcaption>
    </figure>
  );
}
