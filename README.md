<div align="center">

# Conway's Game of War

_Joshua Davidov, Neola Low, Hannah Mandel, Alja-Forcey Rodriguez_ **|** Cooper Union

</div>

Welcome to Conway's Game of War, a game produced for Cooper Union's ME-211 course.


This project starts from the classic Game of Life and extends it with:
- an interactive GUI
- clickable cell placement
- configurable grid size from the command line
- labeled rows and columns
- manual timestep advancement
- an optional two-player ruleset with territorial conversion mechanics

---

## Features

### Base GUI features
- Launches in a separate Tkinter window
- Displays an `n x n` square grid
- Grid size is configurable via CLI
- Default grid size is `8 x 8`
- Rows are labeled with letters: `A, B, C, ...`
- Columns are labeled with numbers: `1, 2, 3, ...`
- Current timestep is displayed in the window
- Cells can be toggled by mouse click
- Time advances manually with:
  - `Enter`
  - the on-screen `R Enter` button

### Two-Player Mode Features
- Optional two-player mode enabled by CLI flag
- Player 1 cells are shown in **crimson**
- Player 2 cells are shown in **blue**
- Dead cells are shown in **white**
- Active placement player is selected with:
  - `1` for Player 1
  - `2` for Player 2
- Mouse clicks place or toggle the currently selected player's cells

---

## Requirements


- Python 3.x
- Tkinter

Tkinter is included with most standard Python installations.

---

## Setup

### Single-Player Mode
```bash
python ConwaysGOW.py
```

### Single-Player Mode With Custom Grid Size

```bash
python ConwaysGOW.py --size 12
```

### Two-Player Mode

```bash
python ConwaysGOW.py --two-player
```

### Two-Player Mode With Custom Grid Size

```bash
python ConwaysGOW.py --two-player --size 12
```

---

## Command-line arguments

| Argument       | Description                         | Default |
| -------------- | ----------------------------------- | ------- |
| `-n`, `--size` | Grid size for an `n x n` board      | `8`     |
| `--two-player` | Enables competitive two-player mode | off     |

---

## Controls

### Single-Player Mode

* **Left click**: toggle a cell on/off
* **R**: advance one timestep
* **Enter**: advance one timestep
* **R Enter button**: advance one timestep

### Two-Player Mode

* **1**: select Player 1 for placement
* **2**: select Player 2 for placement
* **Left click**:

  * on an empty cell: place the active player's cell
  * on your own cell: remove it
  * on the other player's cell: convert it to the active player
* **Enter**: advance one timestep

---

## Game of War Rules

This repository preserves the original Conway rules as the base simulation logic, then extends them in two-player mode.

### Standard Conway's Game of Life Behavior:

In two-player mode, both Player 1 and Player 2 cells count as **live** for the purposes of ordinary Game of Life survival and birth.

That means:

* a live cell survives with 2 or 3 live neighbors
* a live cell dies otherwise
* a dead cell is born with exactly 3 live neighbors

### Board State in Two-Player Mode

Each cell may be:

* `0`: dead
* `1`: owned by Player 1
* `2`: owned by Player 2

### Newborn Cells Receive an Owner

When a dead cell becomes alive in two-player mode, ownership is assigned by the **majority owner among the 3 live neighboring parent cells**.

Examples:

* 2 Player 1 neighbors + 1 Player 2 neighbor → newborn belongs to Player 1
* 2 Player 2 neighbors + 1 Player 1 neighbor → newborn belongs to Player 2
* 3 Player 1 neighbors → newborn belongs to Player 1
* 3 Player 2 neighbors → newborn belongs to Player 2

### Encirclement

For any cell owned by Player A:

* if it has **5 or more adjacent cells owned by Player B**, then on the next turn it is converted into a Player B cell

This acts like territorial capture by surrounding pressure.

### Degree-Duel 

For any cell owned by Player A:

* if it is adjacent to one or more Player B cells,
* compare the degree of the Player A cell to the degree of the adjacent Player B cell(s)

Here, **degree** means:

> If all cells of one player are viewed as a graph, each cell is a vertex, and edges connect adjacent same-player cells. The degree of a cell is the number of adjacent same-player cells connected to it.

The rule used in this implementation is:

* if an adjacent enemy cell has a **strictly greater same-team degree** than the current cell, then the current cell is converted to the enemy player on the next turn
* if the degrees are equal, no conversion occurs
* if the current cell has the greater degree, no conversion occurs

This makes stronger connected structures more likely to overtake weak frontier cells.

### Rule Precedence

In two-player mode, competitive conversion rules override ordinary Conway survival for currently occupied cells.

That means:

* standard Conway birth/survival is computed first
* competitive takeover is then applied
* takeover has priority when a live cell is forced to convert

### Conflicting Cells

A natural ambiguity can occur in competitive cellular automata:

> What should happen if both players could claim the same cell on the next turn?

This implementation resolves ordinary births by assigning ownership via **majority among the 3 parent neighbors**.

A good general-purpose precedence order is:

1. encirclement takeover
2. degree-based takeover
3. standard Conway birth/survival
4. if a true tie still occurs, keep the previous owner for occupied cells or leave the cell dead for empty cells

This keeps the simulation predictable and avoids arbitrary coin-flip behavior.

---

## Implementation Notes

* The grid does **not** wrap around at the edges
* Neighbor checks use the 8 surrounding cells
* Timestep updates are synchronous
* The GUI is built with `tkinter`
* The game is manually stepped rather than continuously animated

---

## File structure

```text
.
├── ConwaysGOW.py
└── README.md
```

---



## Future Improvements

Possible extensions include:

* reset button
* random board generation
* save/load board states
* autoplay mode
* support for >2 players
* support for enhanced cells (as per powerups in game)
* wraparound boundary option
* score tracking by number of living cells per player
* alternate tie-breaking rules for births and takeovers


