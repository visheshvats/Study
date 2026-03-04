# Architecture

## Overview
The Chess Simulator is a React-based SPA (Single Page Application) built with Vite.

## Key Components
- **Game Engine**: Custom `useChessGame` hook wrapping `chess.js` logic.
- **AI**: Stockfish run in a Web Worker (via `StockfishEngine` class).
- **State**: Local component state mostly, with specific keys persisted to `localStorage`.
- **UI**: Tailwind CSS with modular components.

## Directory Structure
- `src/chess/`: Core chess logic.
- `src/components/`: Reusable UI.
- `src/pages/`: Route views.
- `src/content/`: Static JSON data for training modules.
