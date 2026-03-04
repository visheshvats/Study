import { useEffect, useRef } from "react";

interface MoveListProps {
    history: string[];
}

export default function MoveList({ history }: MoveListProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history]);

    const moves = [];
    for (let i = 0; i < history.length; i += 2) {
        moves.push({
            num: Math.floor(i / 2) + 1,
            white: history[i],
            black: history[i + 1] || "",
        });
    }

    return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg flex flex-col h-full max-h-[300px]">
            <div className="p-2 border-b border-zinc-700 font-bold bg-zinc-800 rounded-t-lg">Moves</div>
            <div ref={scrollRef} className="overflow-y-auto p-2 flex-1 scrollbar-thin scrollbar-thumb-zinc-700">
                <table className="w-full text-sm">
                    <tbody>
                        {moves.map((m) => (
                            <tr key={m.num} className="even:bg-zinc-800/50">
                                <td className="p-1 text-zinc-500 w-8">{m.num}.</td>
                                <td className="p-1 font-medium text-zinc-200">{m.white}</td>
                                <td className="p-1 font-medium text-zinc-200">{m.black}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {history.length === 0 && (
                    <div className="text-zinc-600 text-center italic mt-4">Game started</div>
                )}
            </div>
        </div>
    );
}
