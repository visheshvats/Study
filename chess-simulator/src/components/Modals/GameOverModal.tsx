import { RotateCcw } from "lucide-react";

interface GameOverModalProps {
    isOpen: boolean;
    reason: string;
    winner: "white" | "black" | "draw";
    onRematch: () => void;
    onClose: () => void;
}

export default function GameOverModal({ isOpen, reason, winner, onRematch, onClose }: GameOverModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
            <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-8 max-w-sm w-full text-center shadow-xl">
                <h2 className="text-3xl font-bold mb-2">
                    {winner === "white" && "White Wins!"}
                    {winner === "black" && "Black Wins!"}
                    {winner === "draw" && "It's a Draw!"}
                </h2>
                <p className="text-zinc-400 mb-6">{reason}</p>

                <div className="flex gap-4 justify-center">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition"
                    >
                        Analyze
                    </button>
                    <button
                        onClick={onRematch}
                        className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 font-bold flex items-center gap-2"
                    >
                        <RotateCcw size={18} /> Rematch
                    </button>
                </div>
            </div>
        </div>
    );
}
