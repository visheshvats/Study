# Chess Simulator

A polished, offline-capable Chess Simulator and Training Hub.

## Features
- **Play**: Vs Friend or Stockfish (Adjustable Level).
- **Train**: Tactics, Endgames, Openings, and Vision.
- **Analyze**: Engine evaluation and line exploration.

## Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Download Engine**
   Download `stockfish.js` and `stockfish.wasm` and place them in `public/engine/`.
   Check `public/engine/README.md` for details.

3. **Run Development Server**
   ```bash
   npm run dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   ```

## Tech Stack
- React + Vite + TypeScript
- Tailwind CSS
- Chess.js & Stockfish
