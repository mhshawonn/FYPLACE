import { motion } from "framer-motion";

export default function MyList() {
  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-5xl flex-col items-center justify-center gap-6 px-6 text-center text-white">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="flex flex-col items-center gap-4"
      >
        <div className="rounded-full border border-white/10 bg-white/10 px-6 py-2 text-xs uppercase tracking-[0.4em] text-white/60">
          Coming Soon
        </div>
        <h1 className="text-3xl font-semibold uppercase tracking-[0.3em] md:text-4xl">
          Your Personal Stage Awaits
        </h1>
        <p className="max-w-xl text-base text-white/70">
          Save titles across devices and build your own cinematic universe. Add movies to
          your list from the home page to see them appear here with full sync.
        </p>
      </motion.div>
    </div>
  );
}
