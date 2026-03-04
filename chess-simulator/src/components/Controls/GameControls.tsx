import { RotateCcw, ChevronLeft, ChevronRight, FlipHorizontal } from "lucide-react";

interface GameControlsProps {
    onReset: () => void;
    onUndo: () => void;
    onFlip: () => void;
    canUndo: boolean;
}

export default function GameControls({ onReset, onUndo, onFlip, canUndo }: GameControlsProps) {
    return (
        <div className="flex gap-2 justify-center bg-zinc-900 p-2 rounded-lg border border-zinc-700">
            <button
                onClick={onReset}
                className="p-2 hover:bg-zinc-700 rounded text-zinc-400 hover:text-white transition"
                title="New Game"
            >
                <RotateCcw size={20} />
            </button>
            <button
                onClick={onFlip}
                className="p-2 hover:bg-zinc-700 rounded text-zinc-400 hover:text-white transition"
                title="Flip Board"
            >
                <FlipHorizontal size={20} />
            </button>
            <div className="w-px bg-zinc-700 mx-1"></div>
            <button
                onClick={onUndo}
                disabled={!canUndo}
                className="p-2 hover:bg-zinc-700 rounded text-zinc-400 hover:text-white transition disabled:opacity-50 disabled:cursor-not-allowed"
                title="Undo Move"
            >
                <ChevronLeft size={20} />
            </button>
            {/* Redo is harder with chess.js unless we track it manually */}
            <button
                disabled
                className="p-2 hover:bg-zinc-700 rounded text-zinc-400 hover:text-white transition disabled:opacity-30"
            >
                <ChevronRight size={20} />
            </button>
        </div>
    );
}
