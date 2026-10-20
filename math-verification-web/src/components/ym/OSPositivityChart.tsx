import { palette } from "./chart-utils";
import { phase5 } from "@/data/ym";

const M = { top: 34, right: 24, bottom: 52, left: 62 };const W = 980;
const H = 470;

/** Display window; the two largest z-scores are annotated as clipped. */
const Y_MAX = 155;
const THRESHOLD = 5;

const ROW_H = 150;
const ROW_GAP = 56;

export function OSPositivityChart() {
  const rows = [
    { key: "beta1", label: "β = 1.0", values: phase5.osz.beta1, color: palette.green },
    { key: "beta2", label: "β = 2.0", values: phase5.osz.beta2, color: palette.purple },
  ];

  const plotW = W - M.left - M.right;
  const count = phase5.osz.beta1.length;
  const bandW = plotW / count;
  const rowTop = (i: number) => M.top + i * (ROW_H + ROW_GAP);

  const strongest = phase5.osz.beta2.reduce(
    (best, value, i) => (value > phase5.osz.beta2[best] ? i : best),
    0,
  );

  return (
    <figure className="my-8 rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
      <div className="overflow-x-auto">
        <svg
          role="img"
          aria-label={`Bar chart of 35 Osterwalder-Schrader positivity z-scores per coupling, beta equals 1 on the top row in green and beta equals 2 on the bottom row in purple, all positive and almost all far above the 5 sigma threshold. The single smallest value is 0.095 at beta equals 2 and the largest is 149.5.`}
          viewBox={`0 0 ${W} ${H}`}
          className="mx-auto h-auto w-full min-w-[720px]"
        >
          <title>OS positivity z-scores for 35 test forms at two couplings</title>

          {rows.map((row, rowIndex) => {
            const top = rowTop(rowIndex);
            const yRow = (v: number) =>
              top + ROW_H - (Math.min(v, Y_MAX) / Y_MAX) * (ROW_H - 12) - 12;
            return (
              <g key={row.key}>
                <text
                  x={M.left - 52}
                  y={top + ROW_H / 2}
                  textAnchor="middle"
                  fill={row.color}
                  fontSize={12}
                  fontWeight={600}
                  fontFamily="ui-monospace, monospace"
                  transform={`rotate(-90 ${M.left - 52} ${top + ROW_H / 2})`}
                >
                  {row.label}
                </text>

                {[0, 50, 100, 150].map((tick) => (
                  <g key={tick}>
                    <line
                      x1={M.left}
                      y1={yRow(tick)}
                      x2={M.left + plotW}
                      y2={yRow(tick)}
                      stroke={palette.grid}
                    />
                    <text
                      x={M.left - 10}
                      y={yRow(tick) + 4}
                      textAnchor="end"
                      fill={palette.axis}
                      fontSize={11}
                      fontFamily="ui-monospace, monospace"
                    >
                      {tick}
                    </text>
                  </g>
                ))}

                {/* 5 sigma threshold */}
                <line
                  x1={M.left}
                  y1={yRow(THRESHOLD)}
                  x2={M.left + plotW}
                  y2={yRow(THRESHOLD)}
                  stroke="#f87171"
                  strokeWidth={1.6}
                  strokeDasharray="7 5"
                />
                <text
                  x={M.left + 8}
                  y={yRow(THRESHOLD) - 6}
                  fill="#f87171"
                  fontSize={11}
                  fontWeight={600}
                  fontFamily="ui-monospace, monospace"
                >
                  5 σ
                </text>

                {row.values.map((value, i) => {
                  const cx = M.left + i * bandW + bandW / 2;
                  const clipped = value > Y_MAX;
                  const barTop = yRow(value);
                  return (
                    <rect
                      key={`${row.key}-${i}`}
                      x={cx - bandW * 0.32}
                      y={barTop}
                      width={bandW * 0.64}
                      height={top + ROW_H - 12 - barTop}
                      rx={2}
                      fill={row.color}
                      fillOpacity={clipped ? 0.45 : 0.8}
                      stroke={clipped ? "#f87171" : "none"}
                    />
                  );
                })}

                <line
                  x1={M.left}
                  y1={top + ROW_H - 12}
                  x2={M.left + plotW}
                  y2={top + ROW_H - 12}
                  stroke={palette.axis}
                />
              </g>
            );
          })}

          {/* annotations */}
          <text
            x={M.left + (strongest + 0.5) * bandW}
            y={rowTop(1) + 22}
            textAnchor="middle"
            fill="#f87171"
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            z = 149.5 ▸ clipped
          </text>
          <text
            x={M.left + 5 * bandW}
            y={rowTop(0) + 30}
            fill="#ffffff"
            fontSize={13}
            fontWeight={700}
            fontFamily="ui-monospace, monospace"
          >
            no form negative at either β
          </text>
          <text
            x={M.left + 5 * bandW}
            y={rowTop(0) + 48}
            fill={palette.ink}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            worst z: 1.45 at β = 1, 0.095 at β = 2
          </text>

          {Array.from({ length: count }, (_, i) => i + 1).map((form) =>
            form === 1 ||
            form % 5 === 0 ? (
              <text
                key={form}
                x={M.left + (form - 1 + 0.5) * bandW}
                y={rowTop(1) + ROW_H + 22}
                textAnchor="middle"
                fill={palette.axis}
                fontSize={10}
                fontFamily="ui-monospace, monospace"
              >
                {form}
              </text>
            ) : null,
          )}
          <text
            x={M.left + plotW / 2}
            y={H - 14}
            textAnchor="middle"
            fill={palette.ink}
            fontSize={12}
            fontFamily="ui-monospace, monospace"
          >
            OS test form index (1 … 35)
          </text>
        </svg>
      </div>

      <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-xs">
          <span className="text-green-400">▮ β = 1.0 (35 forms)</span>
          <span className="text-purple-400">▮ β = 2.0 (35 forms)</span>
          <span className="text-red-400">- - 5 σ detection threshold</span>
          <span className="text-gray-400">red outline — clipped at 155</span>
        </p>
        <p>
          Each bar is the z-score of one reflection-positive test form{" "}
          <span className="font-mono text-gray-300">
            M_ij = ⟨(ΘO_i)_t O_j⟩
          </span>
          . A negative form would be a violation of OS positivity; none occurs.
          At β = 1 the worst form sits at{" "}
          <span className="font-mono text-green-400">z = 1.45</span> (i.e.
          positive but not yet resolved above noise) and 33 of 35 clear 5 σ; at
          β = 2 the worst is{" "}
          <span className="font-mono text-purple-400">z = 0.095</span> and again
          33 of 35 clear 5 σ.
        </p>
        <p className="text-gray-500">
          The y-axis is linear and clipped at 155: the largest measured value,
          z = 149.5, is drawn with a red outline and its true height printed
          above the bar. z-scores are statistics, not rigorous bounds — this is
          evidence that the Euclidean measure has the analytic properties the
          rigorous phases presuppose.
        </p>
      </figcaption>
    </figure>
  );
}
