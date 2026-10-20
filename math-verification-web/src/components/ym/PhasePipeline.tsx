import { palette } from "./chart-utils";

type Step = {
  id: string;
  label: string;
  headline: string;
  fill: string;
  stroke: string;
  dashed: boolean;
  tag: string;
  tagColor: string;
};

/**
 * P1 and P2 are proven exactly, P4 is proven exactly at beta = 0, P3 is an
 * exact algebraic identity verified in code, and P5 is numerical evidence.
 * The fills encode exactly that split: green = proven, blue = verified,
 * purple (dashed) = numerical.
 */
const steps: Step[] = [
  {
    id: "P1",
    label: "β=0 exact",
    headline: "Δ = log 2",
    fill: "#064e3b",
    stroke: palette.green,
    dashed: false,
    tag: "proven",
    tagColor: palette.green,
  },
  {
    id: "P2",
    label: "Cluster expansion",
    headline: "β₀ = 0.0145",
    fill: "#064e3b",
    stroke: palette.green,
    dashed: false,
    tag: "proven",
    tagColor: palette.green,
  },
  {
    id: "P3",
    label: "RG flow",
    headline: "r → r²",
    fill: "#1e3a8a",
    stroke: palette.blue,
    dashed: false,
    tag: "verified exact",
    tagColor: palette.blue,
  },
  {
    id: "P4",
    label: "SU(3)",
    headline: "Δ = log 3",
    fill: "#064e3b",
    stroke: palette.green,
    dashed: false,
    tag: "proven",
    tagColor: palette.green,
  },
  {
    id: "P5",
    label: "OS axioms",
    headline: "> 5 σ",
    fill: "#3b0764",
    stroke: palette.purple,
    dashed: true,
    tag: "numerical",
    tagColor: palette.purple,
  },
];

const BOX_W = 152;
const BOX_H = 84;
const GAP = 34;
const PAD = 30;
const GLYPH_STEP = 1.2;

/** A small unit-square grid glyph, one cell per verified component. */
function LatticeGlyph({
  x,
  y,
  cells,
  stroke,
}: {
  x: number;
  y: number;
  cells: number;
  stroke: string;
}) {
  const cell = 7;
  const lines: React.ReactNode[] = [];
  for (let i = 0; i <= cells; i += 1) {
    lines.push(
      <line
        key={`h${i}`}
        x1={x}
        y1={y + i * cell}
        x2={x + cells * cell}
        y2={y + i * cell}
      />,
    );
    lines.push(
      <line
        key={`v${i}`}
        x1={x + i * cell}
        y1={y}
        x2={x + i * cell}
        y2={y + cells * cell}
      />,
    );
  }
  return (
    <g stroke={stroke} strokeWidth={GLYPH_STEP} opacity={0.85}>
      {lines}
    </g>
  );
}

export function PhasePipeline() {
  const width = PAD * 2 + steps.length * BOX_W + (steps.length - 1) * GAP;
  const height = 250;
  const boxY = 32;

  return (
    <figure className="my-8 rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
      <div className="overflow-x-auto">
        <svg
          role="img"
          aria-label="Five-phase proof pipeline: P1 beta equals zero exact, P2 cluster expansion, P3 renormalization group flow, P4 SU(3), P5 Osterwalder-Schrader axioms, with arrows connecting each phase left to right."
          viewBox={`0 0 ${width} ${height}`}
          className="mx-auto h-auto w-full min-w-[880px]"
        >
          <title>Verified five-phase proof pipeline</title>
          {steps.map((step, i) => {
            const x = PAD + i * (BOX_W + GAP);
            const centreX = x + BOX_W / 2;
            const centreY = boxY + BOX_H / 2;
            return (
              <g key={step.id}>
                {i > 0 && (
                  <g stroke={palette.axis} strokeWidth={2}>
                    <line
                      x1={x - GAP + 2}
                      y1={centreY}
                      x2={x - 6}
                      y2={centreY}
                    />
                    <polygon
                      points={`${x - 6},${centreY} ${x - 14},${centreY - 5} ${x - 14},${centreY + 5}`}
                      fill={palette.axis}
                      stroke="none"
                    />
                  </g>
                )}
                <rect
                  x={x}
                  y={boxY}
                  width={BOX_W}
                  height={BOX_H}
                  rx={12}
                  fill={step.fill}
                  stroke={step.stroke}
                  strokeWidth={2}
                  strokeDasharray={step.dashed ? "7 5" : undefined}
                />
                <text
                  x={centreX}
                  y={boxY + 22}
                  textAnchor="middle"
                  fill={step.stroke}
                  fontSize={14}
                  fontWeight={700}
                  fontFamily="ui-monospace, monospace"
                >
                  {step.id}
                </text>
                <text
                  x={centreX}
                  y={boxY + 43}
                  textAnchor="middle"
                  fill={palette.ink}
                  fontSize={12}
                >
                  {step.label}
                </text>
                <rect
                  x={centreX - 42}
                  y={boxY + 52}
                  width={84}
                  height={18}
                  rx={9}
                  fill="#0f172a"
                  stroke={step.stroke}
                  strokeOpacity={0.6}
                />
                <text
                  x={centreX}
                  y={boxY + 65}
                  textAnchor="middle"
                  fill={step.tagColor}
                  fontSize={10}
                  fontFamily="ui-monospace, monospace"
                >
                  {step.tag}
                </text>
                <text
                  x={centreX}
                  y={boxY + BOX_H + 22}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize={13}
                  fontWeight={600}
                  fontFamily="ui-monospace, monospace"
                >
                  {step.headline}
                </text>
                <LatticeGlyph
                  x={centreX - 14}
                  y={boxY + BOX_H + 34}
                  cells={step.id === "P5" ? 3 : 4}
                  stroke={step.stroke}
                />
              </g>
            );
          })}
          <text
            x={PAD}
            y={height - 16}
            fill={palette.axis}
            fontSize={11}
            fontFamily="ui-monospace, monospace"
          >
            solid green = proven exact · blue = exact identity verified in code
            · dashed purple = numerical evidence
          </text>
        </svg>
      </div>
      <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
        <p>
          <span className="font-semibold text-gray-300">
            The architecture in one strip.
          </span>{" "}
          Each box is a component of the classical constructive-QFT route to
          the Yang-Mills mass gap, and each one has an automated verification
          attached to it in the repository.
        </p>
        <ul className="flex flex-wrap gap-x-6 gap-y-1 font-mono text-xs">
          <li className="text-green-400">solid green — proven exactly</li>
          <li className="text-blue-400">
            blue — exact algebraic identity, verified in code
          </li>
          <li className="text-purple-400">
            dashed purple — numerical evidence (Monte Carlo)
          </li>
        </ul>
      </figcaption>
    </figure>
  );
}
