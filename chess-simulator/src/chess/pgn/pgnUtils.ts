import { Chess } from "chess.js";

export function exportPGN(game: Chess): string {
    return game.pgn();
}

export function importPGN(pgn: string): Chess | null {
    try {
        const game = new Chess();
        game.loadPgn(pgn);
        return game;
    } catch (e) {
        console.error("Invalid PGN", e);
        return null;
    }
}

export function validateFen(fen: string): boolean {
    const game = new Chess();
    try {
        game.load(fen);
        return true;
    } catch {
        return false;
    }
}
