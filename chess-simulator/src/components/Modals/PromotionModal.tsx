interface PromotionModalProps {
    isOpen: boolean;
    color: "w" | "b";
    onPromote: (piece: "q" | "r" | "b" | "n") => void;
}

export default function PromotionModal({ isOpen, onPromote }: PromotionModalProps) {
    if (!isOpen) return null;

    const pieces = [
        { type: "q", label: "Queen" },
        { type: "r", label: "Rook" },
        { type: "b", label: "Bishop" },
        { type: "n", label: "Knight" },
    ];

    return (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-40 rounded">
            <div className="bg-zinc-800 p-2 rounded-lg shadow-lg flex gap-2">
                {pieces.map((p) => (
                    <button
                        key={p.type}
                        onClick={() => onPromote(p.type as any)}
                        className="p-4 bg-zinc-700 hover:bg-zinc-600 rounded text-xl font-bold"
                    >
                        {/* In a real app we'd use piece icons */}
                        {p.type.toUpperCase()}
                    </button>
                ))}
            </div>
        </div>
    );
}
