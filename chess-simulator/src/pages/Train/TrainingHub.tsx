import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { useCurriculum } from "@/hooks/useCurriculum";
import modulesData from "@/content/curriculum/modules.json";
import type { Module } from "@/types/curriculum";

export default function TrainingHub() {
    const { progress, getModuleProgress } = useCurriculum();
    const [modules, setModules] = useState<Module[]>([]);

    useEffect(() => {
        setModules(modulesData.modules as Module[]);
    }, []);

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner': return 'text-green-500';
            case 'intermediate': return 'text-amber-500';
            case 'advanced': return 'text-red-500';
            default: return 'text-zinc-500';
        }
    };

    const getDifficultyBadge = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner': return '🌱 Beginner';
            case 'intermediate': return '⚡ Intermediate';
            case 'advanced': return '🚀 Advanced';
            default: return difficulty;
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold mb-3">Training Hub</h1>
                <p className="text-zinc-400 text-lg">
                    Master chess from beginner to advanced with our comprehensive curriculum
                </p>
            </div>

            {/* Progress Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-800">
                    <div className="text-3xl font-bold text-amber-500 mb-1">
                        {progress.completedLessons.length}
                    </div>
                    <div className="text-sm text-zinc-400">Lessons Completed</div>
                </div>
                <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-800">
                    <div className="text-3xl font-bold text-green-500 mb-1">
                        {progress.studyStreak}
                    </div>
                    <div className="text-sm text-zinc-400">Day Streak</div>
                </div>
                <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-800">
                    <div className="text-3xl font-bold text-blue-500 mb-1">
                        {progress.totalStudyTime}m
                    </div>
                    <div className="text-sm text-zinc-400">Total Study Time</div>
                </div>
            </div>

            {/* Curriculum Modules */}
            <div className="mb-6">
                <h2 className="text-2xl font-bold mb-4">Curriculum Modules</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {modules.map((module) => {
                        const moduleProgress = getModuleProgress(module.id, 5); // Assuming 5 lessons per module for now

                        return (
                            <Link
                                key={module.id}
                                to={`/train/module/${module.id}`}
                                className="bg-zinc-900 border border-zinc-800 rounded-xl hover:bg-zinc-800 transition group overflow-hidden"
                            >
                                {/* Progress Bar */}
                                <div className="h-1 bg-zinc-800">
                                    <div
                                        className="h-full bg-amber-500 transition-all duration-300"
                                        style={{ width: `${moduleProgress.percentage}%` }}
                                    />
                                </div>

                                <div className="p-6">
                                    {/* Icon & Title */}
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="text-4xl mb-2">{module.icon}</div>
                                        <span className={`text-xs font-bold px-2 py-1 rounded ${getDifficultyColor(module.difficulty)} bg-zinc-800`}>
                                            {getDifficultyBadge(module.difficulty)}
                                        </span>
                                    </div>

                                    <h3 className="text-xl font-bold mb-2 group-hover:text-amber-500 transition">
                                        {module.title}
                                    </h3>
                                    <p className="text-zinc-400 text-sm mb-4">
                                        {module.description}
                                    </p>

                                    {/* Stats */}
                                    <div className="flex items-center gap-4 text-xs text-zinc-500">
                                        <span>📚 {module.estimatedHours}h</span>
                                        <span>•</span>
                                        <span>✏️ {module.exerciseCount} exercises</span>
                                    </div>

                                    {/* Progress Text */}
                                    {moduleProgress.percentage > 0 && (
                                        <div className="mt-3 text-sm text-amber-500 font-bold">
                                            {moduleProgress.percentage}% Complete
                                        </div>
                                    )}
                                </div>
                            </Link>
                        );
                    })}
                </div>
            </div>

            {/* Legacy Training Modules */}
            <div className="mt-12">
                <h2 className="text-2xl font-bold mb-4">Interactive Training</h2>
                <p className="text-zinc-400 mb-4 text-sm">
                    Additional interactive training modules for hands-on practice
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                        {
                            title: "Vision Trainer",
                            description: "Improve board visualization",
                            path: "/train/basics",
                            icon: "👁️",
                        },
                        {
                            title: "Tactics Puzzles",
                            description: "Solve tactical positions",
                            path: "/train/tactics",
                            icon: "⚡",
                        },
                        {
                            title: "Opening Explorer",
                            description: "Study opening lines",
                            path: "/train/openings",
                            icon: "🏁",
                        },
                        {
                            title: "Endgame Scenarios",
                            description: "Practice endgame positions",
                            path: "/train/endgames",
                            icon: "👑",
                        },
                        {
                            title: "Study Plans",
                            description: "Structured learning paths",
                            path: "/train/plans",
                            icon: "📋",
                        },
                    ].map((item) => (
                        <Link
                            key={item.title}
                            to={item.path}
                            className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl hover:bg-zinc-800 transition group"
                        >
                            <div className="text-3xl mb-3">{item.icon}</div>
                            <h3 className="text-lg font-bold mb-2 group-hover:text-amber-500 transition">
                                {item.title}
                            </h3>
                            <p className="text-zinc-400 text-sm">{item.description}</p>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
}
