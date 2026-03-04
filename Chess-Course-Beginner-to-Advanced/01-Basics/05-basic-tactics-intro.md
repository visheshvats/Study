# 05. Basic Tactics Intro

Tactics are short-term sequences of moves that result in a tangible gain (winning a piece or checkmate). 99% of games under 1500 Elo are decided by tactics.

## The Most Basic Tactic: "Hanging Pieces"
A piece is "hanging" if it is unprotected and being attacked.
- **Rule**: Always look at what your opponent's last move attacked.
- **Rule**: Before you move, check if your square is safe.

## Counting Attackers vs Defenders
If you want to capture something, count first.
- **Attackers**: Pieces trying to eat the target.
- **Defenders**: Pieces protecting the target.
- **Rule**: You can only win "material" if Attackers > Defenders.
- *Exception*: If your Attacker is lower value than the Defender (e.g., Pawn attacks Queen), you can trade even if equal count.

## The Checkmate Patterns (Introduction)

### Back Rank Mate
The King is trapped behind his own pawns.
```
  8 | . . R . . . K .
  7 | . . . . . P P P
  6 | . . . . . . . .
```
White plays `Ra8#` (assuming the King is on g8 and pawns on f7, g7, h7).

### Kiss of Death
The Queen is right next to the King, supported by another piece.
White Q on g7, Black K on g8. White King or Bishop protects Q.

## Key Ideas
- **Undefended Pieces Drop Off.** (John Nunn)
- Checks, Captures, Threats (CCT). Always look for these first.

## Drills (10 Mins)
1.  Set up random positions. Instantly point to every "Hanging Piece" for both sides.
2.  Practice checking "Is it safe?" before every move in a game against a computer.
