export class StockfishEngine {
    private worker: Worker | null = null;

    onMessage: (message: string) => void = () => { };

    constructor() {
        // Try to initialize worker
        try {
            this.worker = new Worker("/engine/stockfish.js");

            this.worker.onmessage = (e) => {
                const msg = e.data;
                // if (msg === "uciok") {}
                this.onMessage(msg);
            };

            this.sendCommand("uci");
        } catch (e) {
            console.error("Failed to load Stockfish worker", e);
        }
    }

    sendCommand(cmd: string) {
        if (this.worker) {
            this.worker.postMessage(cmd);
        }
    }

    evaluate(fen: string, depth: number = 10) {
        this.sendCommand(`position fen ${fen}`);
        this.sendCommand(`go depth ${depth}`);
    }

    getBestMove(fen: string, depth: number = 10) {
        this.sendCommand(`position fen ${fen}`);
        this.sendCommand(`go depth ${depth}`);
    }

    setSkillLevel(level: number) { // 0-20
        this.sendCommand(`setoption name Skill Level value ${level}`);
    }

    quit() {
        this.sendCommand("quit");
        if (this.worker) {
            this.worker.terminate();
            this.worker = null;
        }
    }
}
