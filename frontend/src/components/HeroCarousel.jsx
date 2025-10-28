import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const media = [
  {
    type: "video",
    src: "https://storage.googleapis.com/coverr-main/mp4/Mt_Baker.mp4",
    title: "Beyond the Horizon",
    description: "Experience breathtaking journeys through cinematic worlds."
  },
  {
    type: "image",
    src: "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?auto=format&fit=crop&w=1600&q=80",
    title: "Neon City Dreams",
    description: "Lose yourself in stories that bend reality and pulse with neon."
  },
  {
    type: "image",
    src: "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1600&q=80",
    title: "Echoes of Tomorrow",
    description: "Mystery and adventure collide in a battle for the future."
  }
];

export default function HeroCarousel() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActive((prev) => (prev + 1) % media.length);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative h-[65vh] w-full overflow-hidden rounded-3xl border border-white/10 bg-black/60 shadow-[0_60px_120px_rgba(10,10,30,0.55)]">
      <div className="absolute inset-0 z-0 overflow-hidden">
        <AnimatePresence>
          {media.map((item, index) =>
            index === active ? (
              <motion.div
                key={index}
                className="absolute inset-0"
                initial={{ opacity: 0, scale: 1.05 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.05 }}
                transition={{ duration: 1.2, ease: "easeInOut" }}
              >
                {item.type === "video" ? (
                  <motion.video
                    className="h-full w-full object-cover"
                    src={item.src}
                    autoPlay
                    loop
                    muted
                    playsInline
                  />
                ) : (
                  <motion.img
                    src={item.src}
                    alt={item.title}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                )}
              </motion.div>
            ) : null
          )}
        </AnimatePresence>
        <div className="absolute inset-0 bg-gradient-to-r from-black/85 via-black/55 to-black/30" />
      </div>

      <div className="relative z-10 flex h-full flex-col justify-center gap-6 px-12 py-10 md:px-16">
        <motion.span
          className="inline-flex w-fit items-center gap-2 rounded-full bg-white/10 px-5 py-2 text-xs uppercase tracking-[0.4em]"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          Featured Story
        </motion.span>
        <motion.h1
          key={media[active].title}
          className="text-4xl font-bold uppercase tracking-[0.3em] text-white drop-shadow-[0_0_35px_rgba(229,9,20,0.6)] md:text-6xl"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {media[active].title}
        </motion.h1>
        <motion.p
          key={media[active].description}
          className="max-w-2xl text-base text-white/80 md:text-lg"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
        >
          {media[active].description}
        </motion.p>
        <div className="flex items-center gap-4">
          <motion.button
            className="rounded-full bg-fy-primary px-6 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white shadow-neon"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.96 }}
          >
            Play Now
          </motion.button>
          <motion.button
            className="rounded-full border border-white/25 px-6 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white/80 transition-colors hover:border-white hover:text-white"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.96 }}
          >
            More Info
          </motion.button>
        </div>

        <div className="mt-auto flex items-center gap-2">
          {media.map((_, index) => (
            <motion.span
              key={index}
              className={`h-1 flex-1 rounded-full ${
                index === active ? "bg-white" : "bg-white/30"
              }`}
              layout
            />
          ))}
        </div>
      </div>
    </section>
  );
}
