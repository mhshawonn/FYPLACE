import PropTypes from "prop-types";
import { NavLink } from "react-router-dom";
import { lazy, Suspense, useEffect, useState } from "react";
import { motion } from "framer-motion";

const ThreeScene = lazy(() => import("../components/ThreeScene.jsx"));

const navLinks = [
  { to: "/", label: "Search" }
];

export default function MainLayout({ children }) {
  const [shouldRenderScene, setShouldRenderScene] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mediaQuery.matches) {
      return undefined;
    }

    const timer = window.setTimeout(() => setShouldRenderScene(true), 200);
    return () => window.clearTimeout(timer);
  }, []);

  return (
    <div className="relative min-h-screen bg-fy-dark text-white">
      {/* 3D butterflies floating in the background */}
      <div className="pointer-events-none fixed inset-0 -z-10 opacity-80">
        {shouldRenderScene && (
          <Suspense fallback={null}>
            <ThreeScene />
          </Suspense>
        )}
      </div>

      <header className="fixed top-0 z-50 w-full border-b border-white/5 bg-gradient-to-b from-black/70 via-black/40 to-transparent backdrop-blur-md">
        <nav className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
          <motion.div
            className="text-2xl font-bold tracking-[0.4em] text-white drop-shadow-[0_0_25px_rgba(147,51,234,0.8)]"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            FYPLACE 
          </motion.div>
          <div className="flex items-center gap-6 text-sm uppercase tracking-[0.2em] text-white/80">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `relative transition-colors duration-300 hover:text-white ${
                    isActive ? "text-white" : ""
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    {link.label}
                    {isActive && (
                      <motion.span
                        layoutId="nav-underline"
                        className="absolute -bottom-2 left-0 right-0 h-[2px] rounded-full bg-fy-primary shadow-neon"
                      />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </nav>
      </header>

      <main className="relative z-10 pt-24">{children}</main>
    </div>
  );
}

MainLayout.propTypes = {
  children: PropTypes.node
};
