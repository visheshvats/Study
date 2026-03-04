import { expect, test } from 'vitest'
import { importPGN, exportPGN, validateFen } from '../src/chess/pgn/pgnUtils'

test('validates correct FEN', () => {
    const startFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    expect(validateFen(startFen)).toBe(true)
})

test('invalidates bad FEN', () => {
    expect(validateFen('invalid FEN string')).toBe(false)
})

test('imports valid PGN', () => {
    const pgn = '1. e4 e5 2. Nf3 Nc6';
    const game = importPGN(pgn);
    expect(game).not.toBeNull();
    expect(game?.history().length).toBe(4);
})
