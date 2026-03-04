# Content Schema

## Puzzles (`puzzles.json`)
```json
{
  "id": "string",
  "fen": "string",
  "sideToMove": "w" | "b",
  "goal": "string",
  "solutionMoves": ["uci_string"],
  "difficulty": "Easy" | "Medium" | "Hard"
}
```

## Openings (`openings.json`)
```json
{
  "id": "string",
  "name": "string",
  "moves": ["uci_string"], // Sequence of moves from start
  "playerColor": "white" | "black"
}
```
