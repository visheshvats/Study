import plansData from "@/content/plans.json";
import { Play, Clock } from "lucide-react";

export default function PracticePlans() {
    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Daily Practice Plans</h1>

            <div className="grid gap-6">
                {plansData.map(plan => (
                    <div key={plan.id} className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-2xl font-bold text-amber-500">{plan.title}</h2>
                                <div className="flex items-center gap-2 text-zinc-400 mt-1">
                                    <Clock size={16} />
                                    <span>Total time: {plan.tasks.reduce((acc, t) => acc + t.duration, 0)} mins</span>
                                </div>
                            </div>
                            <button className="bg-amber-600 hover:bg-amber-500 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2">
                                <Play size={18} /> Start
                            </button>
                        </div>

                        <div className="space-y-3">
                            {plan.tasks.map((task, i) => (
                                <div key={i} className="flex items-center gap-4 bg-zinc-800/50 p-3 rounded-lg">
                                    <div className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center font-mono text-sm">
                                        {i + 1}
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-bold">{task.label}</div>
                                        <div className="text-xs text-zinc-500 uppercase tracking-wider">{task.module}</div>
                                    </div>
                                    <div className="text-zinc-400 font-mono">
                                        {task.duration}m
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
