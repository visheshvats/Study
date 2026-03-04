export default function EvalBar({ evaluation }: { evaluation: string }) {
    // evaluation expected format: "+1.5", "-0.3", "M3" (mate in 3)

    // Simple visualizer: 
    // score is 0-100% height for white.
    // 0.0 -> 50%
    // +10 -> 100%
    // -10 -> 0%

    let percent = 50;
    let text = evaluation;

    if (evaluation.startsWith("M")) {
        // Mate
        if (evaluation.includes("-")) {
            percent = 0; // Black mates
            text = "#" + evaluation.replace("M-", "");
        } else {
            percent = 100; // White mates
            text = "#" + evaluation.replace("M", "");
        }
    } else {
        const score = parseFloat(evaluation);
        // specific formula sigmoid
        // percent = 50 + (score * 5) // simple linear
        // cap at +/- 5
        const capped = Math.max(-5, Math.min(5, score));
        percent = 50 + (capped * 10);
    }

    return (
        <div className="w-6 h-[400px] bg-zinc-800 rounded overflow-hidden flex flex-col relative border border-zinc-600">
            {/* Black bar (top) is the 'background', White bar (bottom) is the fill from bottom */}
            <div
                className="absolute bottom-0 left-0 right-0 bg-white transition-all duration-500"
                style={{ height: `${percent}%` }}
            ></div>
            <div className={`absolute w-full text-center text-xs font-bold z-10 ${percent > 50 ? 'top-1 text-black' : 'bottom-1 text-white'}`}>
                {text}
            </div>
        </div>
    );
}
