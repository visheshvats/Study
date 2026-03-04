import { useState, useEffect, useCallback } from 'react';
import type { UserProgress, ExerciseResult } from '@/types/curriculum';

const STORAGE_KEY = 'chess-simulator-progress';

const defaultProgress: UserProgress = {
    completedLessons: [],
    completedExercises: {},
    currentModule: '01-basics',
    currentLesson: '',
    studyStreak: 0,
    lastStudyDate: '',
    skillLevel: 'beginner',
    assessmentScores: {},
    totalStudyTime: 0,
};

export function useCurriculum() {
    const [progress, setProgress] = useState<UserProgress>(defaultProgress);
    const [loading, setLoading] = useState(true);

    // Load progress from localStorage
    useEffect(() => {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                const parsed = JSON.parse(saved);
                setProgress(parsed);

                // Update streak
                const today = new Date().toISOString().split('T')[0];
                const lastDate = parsed.lastStudyDate;

                if (lastDate) {
                    const daysDiff = Math.floor(
                        (new Date(today).getTime() - new Date(lastDate).getTime()) / (1000 * 60 * 60 * 24)
                    );

                    if (daysDiff === 1) {
                        // Consecutive day - increment streak
                        setProgress(prev => ({ ...prev, studyStreak: prev.studyStreak + 1, lastStudyDate: today }));
                    } else if (daysDiff > 1) {
                        // Streak broken
                        setProgress(prev => ({ ...prev, studyStreak: 1, lastStudyDate: today }));
                    }
                }
            }
        } catch (error) {
            console.error('Failed to load progress:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    // Save progress to localStorage
    useEffect(() => {
        if (!loading) {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
            } catch (error) {
                console.error('Failed to save progress:', error);
            }
        }
    }, [progress, loading]);

    const completeLesson = useCallback((lessonId: string) => {
        setProgress(prev => {
            if (prev.completedLessons.includes(lessonId)) {
                return prev;
            }

            const today = new Date().toISOString().split('T')[0];
            return {
                ...prev,
                completedLessons: [...prev.completedLessons, lessonId],
                lastStudyDate: today,
            };
        });
    }, []);

    const recordExerciseResult = useCallback((result: ExerciseResult) => {
        setProgress(prev => ({
            ...prev,
            completedExercises: {
                ...prev.completedExercises,
                [result.exerciseId]: result,
            },
        }));
    }, []);

    const setCurrentLesson = useCallback((moduleId: string, lessonId: string) => {
        setProgress(prev => ({
            ...prev,
            currentModule: moduleId,
            currentLesson: lessonId,
        }));
    }, []);

    const addStudyTime = useCallback((minutes: number) => {
        setProgress(prev => ({
            ...prev,
            totalStudyTime: prev.totalStudyTime + minutes,
        }));
    }, []);

    const recordAssessment = useCallback((score: UserProgress['assessmentScores'][string]) => {
        setProgress(prev => ({
            ...prev,
            assessmentScores: {
                ...prev.assessmentScores,
                [score.level]: score,
            },
            skillLevel: score.level,
        }));
    }, []);

    const getModuleProgress = useCallback((moduleId: string, totalLessons: number) => {
        const completed = progress.completedLessons.filter(id => id.startsWith(moduleId)).length;
        return {
            completed,
            total: totalLessons,
            percentage: totalLessons > 0 ? Math.round((completed / totalLessons) * 100) : 0,
        };
    }, [progress.completedLessons]);

    const getExerciseAccuracy = useCallback(() => {
        const results = Object.values(progress.completedExercises);
        if (results.length === 0) return 0;

        const correct = results.filter(r => r.correct).length;
        return Math.round((correct / results.length) * 100);
    }, [progress.completedExercises]);

    const resetProgress = useCallback(() => {
        setProgress(defaultProgress);
        localStorage.removeItem(STORAGE_KEY);
    }, []);

    return {
        progress,
        loading,
        completeLesson,
        recordExerciseResult,
        setCurrentLesson,
        addStudyTime,
        recordAssessment,
        getModuleProgress,
        getExerciseAccuracy,
        resetProgress,
    };
}
