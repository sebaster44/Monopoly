export type Cell = { row: number; column: number };

/** Number of cells per side of the square grid that lays the board out as a ring. */
export function gridSize(squareCount: number): number {
  return Math.ceil(squareCount / 4) + 1;
}

/**
 * Grid cell (1-based) of a board position. Position 0 sits in the bottom-right corner and
 * the path runs clockwise: bottom row leftwards, left column upwards, top row, right column.
 */
export function cellOf(position: number, size: number): Cell {
  const side = size - 1;
  const offset = position % side;
  switch (Math.floor(position / side)) {
    case 0:
      return { row: size, column: size - offset };
    case 1:
      return { row: size - offset, column: 1 };
    case 2:
      return { row: 1, column: 1 + offset };
    default:
      return { row: 1 + offset, column: size };
  }
}
