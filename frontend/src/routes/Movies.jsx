import { useMemo } from "react";
import { motion } from "framer-motion";
import { newReleases, trendingMovies, topRated } from "../data/movies.js";

export default function Movies() {
  const collection = useMemo(() => [...trendingMovies, ...newReleases, ...topRated], []);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-6 pb-20">
      <motion.header
        className="mt-8 flex flex-col gap-2 text-white"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-3xl font-semibold uppercase tracking-[0.35em] md:text-4xl">
          Library
        </h1>
        <p className="text-sm text-white/70 md:text-base">
          Browse the entire catalog and dive into crystalline, neon-lit universes.
        </p>
      </motion.header>

      <motion.div
        className="grid gap-6 md:grid-cols-3 lg:grid-cols-4"
        initial="hidden"
        animate="visible"
        variants={{
          hidden: {},
          visible: {
            transition: {
              staggerChildren: 0.05
            }
          }
        }}
      >
        {collection.map((movie) => (
          <motion.div
            key={movie.id}
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
            whileHover={{ scale: 1.04 }}
            className="group relative aspect-[2/3] overflow-hidden rounded-3xl border border-white/10 bg-black/40 shadow-[0_20px_45px_rgba(0,0,0,0.55)]"
          >
            <img
              src={movie.thumbnail}
              alt={movie.title}
              loading="lazy"
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
            <div className="absolute inset-x-0 bottom-0 space-y-1 bg-gradient-to-t from-black via-black/40 to-transparent p-4">
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-white">
                {movie.title}
              </p>
              <p className="text-xs uppercase tracking-[0.3em] text-white/60">
                {movie.genre} • {movie.year}
              </p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
