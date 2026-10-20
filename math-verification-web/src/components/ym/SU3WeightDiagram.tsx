import { linearScale, palette } from "./chart-utils";
import { phase4, LOG3 } from "@/data/ym";

const W = 460;
const H = 420;
const CX = W / 2;
const CY = 218;
const R = 120;

/** The six non-zero weights of the SU(3) adjoint (1,1) hexagon. */
const WEIGHTS: Array<[number, number]> = [
  [1, -1],
  [1, 0],
  [0, 1],
  [-1, 1],
  [-1, 0],
  [0, -1],
];

export function SU3WeightDiagram() {
  // Weight coordinates: x-axis is the first weight component, y the second.
  // Both span [-1.6, 1.6] so the origin sits middle-left of the hexagon.
  const sx = linearScale(-1.7, 1.7, CX - R, CX + R);
  const sy = linearScale(-1.7, 1.7, CY + R, CY - R);

  const hexPoints = WEIGHTS.map(([a, b]) => `${sx(a)},${sy(b)}`).join(" ");

  return (
    <figure className="my-8 rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
      <div className="overflow-x-auto">
        <svg
          role="img"
          aria-label="Weight diagram of the SU(3) adjoint representation: a regular hexagon with vertices at the six non-zero weights one minus one, one zero, zero one, minus one one, minus one zero and zero minus one, plus the origin. A caption reads SU(3) adjoint weights, Delta equals log 3 equals 1.0986 at beta equals 0. An arrow points to a fundamental triangle pair of dimension 3."
          viewBox={`0 0 ${W} ${H}`}
          className="mx-auto h-auto w-full min-w-[360px]"
        >
          <title>SU(3) adjoint weight hexagon</title>

          {/* axes in weight coordinates */}
          <g stroke={palette.grid}>
            <line x1={sx(-1.7)} y1={sy(0)} x2={sx(1.7)} y2={sy(0)} />
            <line x1={sx(0)} y1={sy(-1.7)} x2={sx(0)} y2={sy(1.7)} />
          </g>
          <text
            x={sx(1.62)}
            y={sy(0) - 8}
            fill={palette.axis}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            λ₁
          </text>
          <text
            x={sx(0) + 8}
            y={sy(1.62)}
            fill={palette.axis}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            λ₂
          </text>

          {[-1, 1].map((tick) => (
            <g key={`${tick}`}>
              <line
                x1={sx(tick)}
                y1={sy(0) - 4}
                x2={sx(tick)}
                y2={sy(0) + 4}
                stroke={palette.axis}
              />
              <text
                x={sx(tick)}
                y={sy(0) + 18}
                textAnchor="middle"
                fill={palette.axis}
                fontSize={10}
                fontFamily="ui-monospace, monospace"
              >
                {tick > 0 ? "1" : "−1"}
              </text>
            </g>
          ))}
          {[-1, 1].map((tick) => (
            <g key={`y${tick}`}>
              <line
                x1={sx(0) - 4}
                y1={sy(tick)}
                x2={sx(0) + 4}
                y2={sy(tick)}
                stroke={palette.axis}
              />
              <text
                x={sx(0) - 10}
                y={sy(tick) + 4}
                textAnchor="end"
                fill={palette.axis}
                fontSize={10}
                fontFamily="ui-monospace, monospace"
              >
                {tick > 0 ? "1" : "−1"}
              </text>
            </g>
          ))}

          {/* the hexagon through the six non-zero weights */}
          <polygon
            points={hexPoints}
            fill="rgba(192, 132, 252, 0.12)"
            stroke={palette.purple}
            strokeWidth={2}
          />

          {/* weights */}
          {WEIGHTS.map(([a, b]) => (
            <g key={`${a},${b}`}>
              <circle
                cx={sx(a)}
                cy={sy(b)}
                r={7}
                fill={palette.purple}
                stroke="#0f172a"
                strokeWidth={1.5}
              />
              <text
                x={sx(a) + (a === 0 ? 14 : a > 0 ? 14 : -14)}
                y={sy(b) + (b > 0 ? -10 : 18)}
                textAnchor={a === 0 ? "start" : a > 0 ? "start" : "end"}
                fill={palette.ink}
                fontSize={11}
                fontFamily="ui-monospace, monospace"
              >
                ({a > 0 ? "1" : a < 0 ? "−1" : "0"},{" "}
                {b > 0 ? "1" : b < 0 ? "−1" : "0"})
              </text>
            </g>
          ))}

          {/* origin */}
          <circle cx={sx(0)} cy={sy(0)} r={7} fill="#ffffff" />
          <text
            x={sx(0) + 12}
            y={sy(0) + 20}
            fill={palette.ink}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            (0, 0) — multiplicity 2
          </text>

          {/* fundamental pair marker */}
          <g stroke={palette.blue} strokeWidth={1.6} fill="none">
            <polygon
              points={`${sx(0.42)},${sy(0.34)} ${sx(0.62)},${sy(0.62)} ${sx(0.34)},${sy(0.5)}`}
            />
          </g>
          <line
            x1={sx(0.5)}
            y1={sy(0.5)}
            x2={sx(1.15)}
            y2={sy(1.15)}
            stroke={palette.blue}
            strokeWidth={1.2}
          />
          <text
            x={sx(1.2)}
            y={sy(1.2)}
            fill={palette.blue}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            3 and 3̄ (dim 3): the triangle pairs
          </text>

          <text
            x={CX}
            y={54}
            textAnchor="middle"
            fill="#ffffff"
            fontSize={15}
            fontWeight={700}
            fontFamily="ui-monospace, monospace"
          >
            SU(3) adjoint weights — Δ = log 3 = {LOG3.toFixed(4)} at β = 0
          </text>
          <text
            x={CX}
            y={76}
            textAnchor="middle"
            fill={palette.axis}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            adjoint (1, 1): dimension 8, zero weight of multiplicity 2
          </text>
          <text
            x={CX}
            y={H - 22}
            textAnchor="middle"
            fill={palette.ink}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            axes: Dynkin / weight coordinates (λ₁, λ₂)
          </text>
          <text
            x={CX}
            y={H - 6}
            textAnchor="middle"
            fill={palette.axis}
            fontSize={10}
            fontFamily="ui-monospace, monospace"
          >
            multiplicities: dim 1, 3, 3, 6, 6, 8, 10, 10, 15, 15, 15, 24, 27
          </text>
        </svg>
      </div>

      <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-xs">
          <span className="text-purple-400">
            ● adjoint (1,1) weights — six vertices
          </span>
          <span className="text-gray-200">● origin, multiplicity 2</span>
          <span className="text-blue-400">▲ fundamentals 3 and 3̄ (dim 3)</span>
        </p>
        <p>
          At β = 0 the Boltzmann weight is the Haar measure, so the transfer
          matrix in the character basis simply multiplies by{" "}
          <span className="font-mono text-gray-300">1/d</span> per link. The
          ground state is the trivial representation (d = 1); the first
          excitation is a single link in a fundamental or conjugate of{" "}
          <span className="font-mono text-blue-400">dimension 3</span>, which
          sits just off the centre as one of the blue triangle pairs.
        </p>
        <p>
          Hence the exact SU(3) gap{" "}
          <span className="font-mono text-green-400">
            Δ_SU(3) = log 3 = {LOG3.toFixed(6)}
          </span>{" "}
          — the QCD analogue of the SU(2) result Δ = log 2.
        </p>
        <p className="text-gray-500">
          Low-lying SU(3) multiplicities computed exactly by the code, in
          ascending dimension:{" "}
          <span className="font-mono">
            {phase4.dims.join(", ")}
          </span>
          .
        </p>
      </figcaption>
    </figure>
  );
}
