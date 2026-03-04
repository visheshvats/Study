import { useState, useEffect } from "react";
import ChessboardWrapper from "@/components/Board/ChessboardWrapper";
import { useChessGame } from "@/chess/rules/useChessGame";
// import { StockfishEngine } from "@/chess/engine/stockfish";
import endgamesData from "@/content/endgames.json";

export default function EndgameTrainer() {
    const { state, makeMove, resetGame } = useChessGame();
    const [currentScenario, setCurrentScenario] = useState(endgamesData[0]);
    // Engine integration pending
    /*
    const [engine, setEngine] = useState<StockfishEngine | null>(null);

    useEffect(() => {
        const sf = new StockfishEngine();
        setEngine(sf);
        return () => sf.quit();
    }, []);
    */

    useEffect(() => {
        if (currentScenario) resetGame(currentScenario.fen);
    }, [currentScenario, resetGame]);

    // Engine response logic would go here (similar to PlayPage)
    // For brevity, we assume the user plays against themselves or we'd duplicate the engine hook logic.
    // Ideally, extract "useEngineOpponent" hook.

    return (
        <div className="p-8 flex flex-col items-center gap-6">
            <h1 className="text-2xl font-bold">Endgame Practice</h1>

            <div className="flex gap-2 bg-zinc-800 p-2 rounded overflow-x-auto max-w-full">
                {endgamesData.map(e => (
                    <button
                        key={e.id}
                        onClick={() => setCurrentScenario(e)}
                        className={`whitespace-nowrap px-4 py-2 rounded ${currentScenario.id === e.id ? 'bg-amber-600' : 'bg-zinc-700'}`}
                    >
                        {e.title}
                    </button>
                ))}
            </div>

            <div className="text-center">
                <h2 className="text-xl font-bold">{currentScenario.title}</h2>
                <p className="text-zinc-400">{currentScenario.objective}</p>
            </div>

            <ChessboardWrapper
                fen={state.fen}
                onMove={(from, to) => makeMove({ from, to, promotion: 'q' })}
                orientation={currentScenario.sideToMove === 'w' ? 'white' : 'black'}
            />

            <p className="text-xs text-zinc-500">Note: Engine opponent implementation required for auto-defense.</p>
        </div>
    );
}
