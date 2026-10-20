import { palette } from "./chart-utils";
import { phase2 } from "@/data/ym";

const M = { top: 28, right: 24, bottom: 48, left: 56 };
const W = 420;
const H = 240;

const SIZES = [3, 4, 5, 6];
const MAX_COUNT = 70;

/** A 4x4 block of plaquettes with one closed loop of four highlighted. */
function FourCycleSchematic() {
  const cell = 22;
  const ox = 12;
  const oy = 30;
  const cells = 4;
  const squares: React.ReactNode[] = [];
  const loop = new Set(["1,1", "1,2", "2,1", "2,2"]);
  for (let r = 0; r < cells; r += 1) {
    for (let c = 0; c < cells; c += 1) {
      const highlighted = loop.has(`${r},${c}`);
      squares.push(
        <rect
          key={`${r}-${c}`}
          x={ox + c * cell}
          y={oy + r * cell}
          width={cell}
          height={cell}
          fill={highlighted ? palette.greenSoft : "transparent"}
          stroke={highlighted ? palette.green : palette.grid}
          strokeWidth={highlighted ? 2 : 1}
        />,
      );
    }
  }
  return (
    <svg
      role="img"
      aria-label="Schematic of a four by four grid of plaquettes with a closed loop of four squares in the middle highlighted in green, labelled four-cycle zeta equals r to the fourth."
      viewBox="0 0 120 150"
      className="h-40 w-auto"
    >
      <title>4-cycle polymer</title>
      {squares}
      <text
        x={ox + (cells * cell) / 2}
        y={22}
        textAnchor="middle"
        fill={palette.ink}
        fontSize={11}
        fontFamily="ui-monospace, monospace"
      >
        4-cycle: ζ = r⁴
      </text>
      <text
        x={ox + (cells * cell) / 2}
        y={140}
        textAnchor="middle"
        fill={palette.axis}
        fontSize={10}
        fontFamily="ui-monospace, monospace"
      >
        24 of these exist
      </text>
    </svg>
  );
}

/** A cube wireframe: the smallest closed surface on the infinite lattice. */
function CubeSchematic() {
  // Isometric projection of a unit cube.
  const s = 26;
  const ax = Math.cos(Math.PI / 6) * s; // ~22.5
  const ay = Math.sin(Math.PI / 6) * s; // ~13
  const oz = 34;
  const px = (a: number, b: number, c: number) => ({
    x: 60 + (a - b) * ax,
    y: 62 + (a + b) * ay - c * oz,
  });
  const corners: Array<[number, number, number]> = [
    [0, 0, 0],
    [1, 0, 0],
    [0, 1, 0],
    [1, 1, 0],
    [0, 0, 1],
    [1, 0, 1],
    [0, 1, 1],
    [1, 1, 1],
  ];
  const edges: Array<[number, number]> = [
    [0, 1],
    [0, 2],
    [1, 3],
    [2, 3],
    [4, 5],
    [4, 6],
    [5, 7],
    [6, 7],
    [0, 4],
    [1, 5],
    [2, 6],
    [3, 7],
  ];
  return (
    <svg
      role="img"
      aria-label="Wireframe cube schematic labelled six-cycle, zeta equals r to the sixth, showing the smallest closed surface of six plaquettes."
      viewBox="0 0 120 150"
      className="h-40 w-auto"
    >
      <title>6-cycle (cube) polymer</title>
      <g stroke={palette.green} strokeWidth={1.8} fill="none">
        {edges.map(([a, b]) => {
          const p = px(...corners[a]);
          const q = px(...corners[b]);
          return (
            <line key={`${a}-${b}`} x1={p.x} y1={p.y} x2={q.x} y2={q.y} />
          );
        })}
      </g>
      <g fill={palette.green}>
        {corners.map((c, i) => {
          const p = px(...c);
          return <circle key={i} cx={p.x} cy={p.y} r={2.2} />;
        })}
      </g>
      <text
        x={60}
        y={22}
        textAnchor="middle"
        fill={palette.ink}
        fontSize={11}
        fontFamily="ui-monospace, monospace"
      >
        6-cycle (cube): ζ = r⁶
      </text>
      <text
        x={60}
        y={140}
        textAnchor="middle"
        fill={palette.axis}
        fontSize={10}
        fontFamily="ui-monospace, monospace"
      >
        64 of these exist
      </text>
    </svg>
  );
}

export function PolymerViz() {
  const sizes = phase2.polymerSizes.size;
  const counts = phase2.polymerSizes.count;
  const countOf = (size: number) => {
    const i = sizes.indexOf(size);
    return i === -1 ? 0 : counts[i];
  };

  const plotW = W - M.left - M.right;
  const plotH = H - M.top - M.bottom;
  const bandW = plotW / SIZES.length;
  const y = (v: number) => M.top + plotH - (v / MAX_COUNT) * plotH;

  return (
    <div className="my-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
      <figure className="rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6 lg:col-span-2">
        <div className="overflow-x-auto">
          <svg
            role="img"
            aria-label="Bar chart of enumerated closed polymers by size: zero polymers of size 3, 24 of size 4, zero of size 5, and 64 of size 6, for 88 in total."
            viewBox={`0 0 ${W} ${H}`}
            className="mx-auto h-auto w-full min-w-[380px]"
          >
            <title>Closed polymers enumerated up to size six</title>

            {[0, 20, 40, 60].map((tick) => (
              <g key={tick}>
                <line
                  x1={M.left}
                  y1={y(tick)}
                  x2={M.left + plotW}
                  y2={y(tick)}
                  stroke={palette.grid}
                />
                <text
                  x={M.left - 8}
                  y={y(tick) + 4}
                  textAnchor="end"
                  fill={palette.axis}
                  fontSize={11}
                  fontFamily="ui-monospace, monospace"
                >
                  {tick}
                </text>
              </g>
            ))}

            {SIZES.map((size, i) => {
              const count = countOf(size);
              const cx = M.left + i * bandW + bandW / 2;
              const barW = bandW * 0.5;
              const empty = count === 0;
              return (
                <g key={size}>
                  {empty ? (
                    <g>
                      <line
                        x1={cx - barW / 2}
                        y1={y(0)}
                        x2={cx + barW / 2}
                        y2={y(0)}
                        stroke={palette.axis}
                        strokeWidth={2}
                        strokeDasharray="4 3"
                      />
                      <text
                        x={cx}
                        y={y(0) - 12}
                        textAnchor="middle"
                        fill={palette.axis}
                        fontSize={12}
                        fontFamily="ui-monospace, monospace"
                      >
                        0
                      </text>
                    </g>
                  ) : (
                    <g>
                      <rect
                        x={cx - barW / 2}
                        y={y(count)}
                        width={barW}
                        height={y(0) - y(count)}
                        rx={4}
                        fill={palette.green}
                        fillOpacity={0.35}
                        stroke={palette.green}
                        strokeWidth={1.5}
                      />
                      <text
                        x={cx}
                        y={y(count) - 8}
                        textAnchor="middle"
                        fill="#ffffff"
                        fontSize={13}
                        fontWeight={700}
                        fontFamily="ui-monospace, monospace"
                      >
                        {count}
                      </text>
                    </g>
                  )}
                  <text
                    x={cx}
                    y={M.top + plotH + 20}
                    textAnchor="middle"
                    fill={empty ? palette.axis : palette.ink}
                    fontSize={12}
                    fontFamily="ui-monospace, monospace"
                  >
                    |γ| = {size}
                  </text>
                </g>
              );
            })}

            <line
              x1={M.left}
              y1={y(0)}
              x2={M.left + plotW}
              y2={y(0)}
              stroke={palette.axis}
            />
            <line
              x1={M.left}
              y1={M.top}
              x2={M.left}
              y2={y(0)}
              stroke={palette.axis}
            />
            <text
              x={M.left + plotW / 2}
              y={H - 12}
              textAnchor="middle"
              fill={palette.ink}
              fontSize={11}
              fontFamily="ui-monospace, monospace"
            >
              polymer size |γ| (plaquettes)
            </text>
            <text
              x={14}
              y={M.top + plotH / 2}
              textAnchor="middle"
              fill={palette.ink}
              fontSize={11}
              fontFamily="ui-monospace, monospace"
              transform={`rotate(-90 14 ${M.top + plotH / 2})`}
            >
              count
            </text>
          </svg>
        </div>
        <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
          <p>
            Exhaustive enumeration of every closed connected polymer up to size
            6 on the <span className="font-mono text-gray-300">L = 2</span>{" "}
            torus: <span className="font-mono text-green-400">88 in total</span>{" "}
            — 24 four-cycles and 64 six-cycles.
          </p>
          <p className="text-gray-500">
            The grey dashed markers at sizes 3 and 5 are genuinely zero, not
            missing data: the closure condition forces every link to be touched
            an even number of times, so no closed surface has an odd plaquette
            count. The smallest odd-sized polymer simply does not exist.
          </p>
        </figcaption>
      </figure>

      <figure className="rounded-xl border border-gray-800 bg-gray-900 p-4 sm:p-6">
        <div className="flex flex-wrap items-start justify-center gap-4">
          <FourCycleSchematic />
          <CubeSchematic />
        </div>
        <figcaption className="mt-4 space-y-2 text-sm text-gray-400">
          <p>
            A polymer is a connected set of plaquettes whose boundary links are
            all touched twice, and its weight factorises as{" "}
            <span className="font-mono text-gray-300">
              ζ(γ) = r^|γ| ∏_ℓ Cat(k_ℓ/2)
            </span>
            . On the tiny torus the cheapest object is the planar four-cycle,
            weight <span className="font-mono text-green-400">r⁴</span>; on an
            infinite lattice the cheapest closed surface is the cube, weight{" "}
            <span className="font-mono text-green-400">r⁶</span>.
          </p>
          <p className="text-gray-500">
            Those two shapes are why the leading correction is{" "}
            <span className="font-mono">O(β⁸)</span>, and why truncating the
            enumeration at size 6 is exact through{" "}
            <span className="font-mono">O(β¹⁰)</span>.
          </p>
        </figcaption>
      </figure>
    </div>
  );
}
