import { Link, Outlet, useLocation } from "react-router-dom";
import { Home, Gamepad2, Microscope, GraduationCap, Menu, X } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

export default function Layout() {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const location = useLocation();

    const navItems = [
        { label: "Home", path: "/", icon: Home },
        { label: "Play", path: "/play", icon: Gamepad2 },
        { label: "Analyze", path: "/analyze", icon: Microscope },
        { label: "Train", path: "/train", icon: GraduationCap },
    ];

    return (
        <div className="flex h-screen w-full bg-zinc-950 text-zinc-100 overflow-hidden">
            {/* Sidebar (Desktop) */}
            <aside className="hidden md:flex flex-col w-64 border-r border-zinc-800 bg-zinc-900 p-4">
                <div className="flex items-center gap-2 mb-8 px-2">
                    <div className="w-8 h-8 bg-amber-600 rounded flex items-center justify-center font-bold text-xl">♔</div>
                    <h1 className="text-xl font-bold tracking-tight">Chess Sim</h1>
                </div>

                <nav className="flex flex-col gap-2 flex-1">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={clsx(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
                                    isActive
                                        ? "bg-amber-600/10 text-amber-500 font-medium"
                                        : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100"
                                )}
                            >
                                <Icon size={20} />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                <div className="mt-auto px-2 pt-4 border-t border-zinc-800">
                    <p className="text-xs text-zinc-500">v1.0.0 • Offline Ready</p>
                </div>
            </aside>

            {/* Mobile Header */}
            <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between px-4 z-50">
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-amber-600 rounded flex items-center justify-center font-bold">♔</div>
                    <span className="font-bold">Chess Sim</span>
                </div>
                <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2">
                    {isMobileMenuOpen ? <X /> : <Menu />}
                </button>
            </div>

            {/* Main Content */}
            <main className="flex-1 h-full overflow-auto pt-16 md:pt-0 bg-black/20">
                <div className="h-full max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>

            {/* Mobile Menu Overlay */}
            {isMobileMenuOpen && (
                <div className="md:hidden fixed inset-0 top-16 bg-zinc-950 z-40 p-4">
                    <nav className="flex flex-col gap-4">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className="flex items-center gap-4 p-4 rounded-xl bg-zinc-900 border border-zinc-800"
                                >
                                    <Icon className="text-amber-500" />
                                    <span className="text-lg font-medium">{item.label}</span>
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            )}
        </div>
    );
}
