import { createBrowserRouter } from "react-router-dom";
import Layout from "./layout/Layout";
// Placeholder imports for now, we will create these pages next
import HomePage from "@/pages/Home/HomePage";
import PlayPage from "@/pages/Play/PlayPage";
import AnalyzePage from "@/pages/Analyze/AnalysisPage";
import TrainingHub from "@/pages/Train/TrainingHub";
import ModulePage from "@/pages/Train/ModulePage";
import BasicsModule from "@/pages/Train/modules/Basics/BasicsTrainer";
import TacticsModule from "@/pages/Train/modules/Tactics/TacticsTrainer";
import OpeningsModule from "@/pages/Train/modules/Openings/OpeningTrainer";
import EndgamesModule from "@/pages/Train/modules/Endgames/EndgameTrainer";
import PlansModule from "@/pages/Train/modules/Plans/PracticePlans";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Layout />,
        children: [
            { path: "/", element: <HomePage /> },
            { path: "/play", element: <PlayPage /> },
            { path: "/analyze", element: <AnalyzePage /> },
            {
                path: "/train",
                children: [
                    { index: true, element: <TrainingHub /> },
                    { path: "module/:moduleId", element: <ModulePage /> },
                    { path: "basics", element: <BasicsModule /> },
                    { path: "tactics", element: <TacticsModule /> },
                    { path: "openings", element: <OpeningsModule /> },
                    { path: "endgames", element: <EndgamesModule /> },
                    { path: "plans", element: <PlansModule /> },
                ]
            },
        ],
    },
]);
