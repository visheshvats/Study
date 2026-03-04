// Curriculum Type Definitions

export interface Module {
    id: string;
    title: string;
    description: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    lessons: Lesson[];
    exerciseCount: number;
    estimatedHours: number;
    icon: string;
    order: number;
}

export interface Lesson {
    id: string;
    moduleId: string;
    title: string;
    content: string; // Markdown content
    positions: FENPosition[]; // Diagrams to show
    drills: string[]; // Practice recommendations
    nextLesson?: string;
    prevLesson?: string;
    estimatedMinutes: number;
}

export interface FENPosition {
    fen: string;
    description: string;
    orientation?: 'white' | 'black';
    arrows?: Arrow[];
    highlights?: string[]; // Squares to highlight
}

export interface Arrow {
    from: string;
    to: string;
    color?: string;
}

export interface Exercise {
    id: string;
    moduleId: string;
    type: 'multiple-choice' | 'position' | 'notation' | 'calculation' | 'text';
    question: string;
    fen?: string; // For position-based exercises
    options?: string[]; // For multiple choice
    correctAnswer: string | string[];
    explanation: string;
    difficulty: 1 | 2 | 3 | 4 | 5;
    hints?: string[];
}

export interface ExerciseResult {
    exerciseId: string;
    correct: boolean;
    attempts: number;
    timestamp: Date;
    timeSpent: number; // seconds
}

export interface UserProgress {
    completedLessons: string[];
    completedExercises: Record<string, ExerciseResult>;
    currentModule: string;
    currentLesson: string;
    studyStreak: number;
    lastStudyDate: string; // ISO date string
    skillLevel: 'beginner' | 'intermediate' | 'advanced';
    assessmentScores: Record<string, AssessmentScore>;
    totalStudyTime: number; // minutes
}

export interface AssessmentScore {
    level: 'beginner' | 'intermediate' | 'advanced';
    score: number;
    maxScore: number;
    percentage: number;
    date: string;
    weakAreas: string[];
    recommendations: string[];
}

export interface StudyPlan {
    id: string;
    title: string;
    description: string;
    weeks: Week[];
    totalDays: number;
}

export interface Week {
    weekNumber: number;
    title: string;
    days: Day[];
}

export interface Day {
    dayNumber: number;
    dayOfWeek: string;
    topic: string;
    activities: Activity[];
    estimatedMinutes: number;
}

export interface Activity {
    type: 'read' | 'practice' | 'play' | 'solve' | 'review';
    description: string;
    moduleId?: string;
    lessonId?: string;
    completed?: boolean;
}

export interface ModuleMetadata {
    modules: Module[];
    totalLessons: number;
    totalExercises: number;
}
