import { useRef } from "react";
import { motion, useMotionValue, useTransform } from "framer-motion";
import PropTypes from "prop-types";

export default function CarouselRow({ title, movies }) {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between px-2">
        <motion.h2
          className="text-xl font-semibold uppercase tracking-[0.35em] text-white md:text-2xl"
          initial={{ opacity: 0, x: -40 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.6 }}
        >
          {title}
        </motion.h2>
        <motion.span
          className="hidden text-xs uppercase tracking-[0.3em] text-white/50 md:block"
          initial={{ opacity: 0, x: 40 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.6 }}
        >
          Scroll →
        </motion.span>
      </div>
      <motion.div
        className="flex gap-5 overflow-x-auto pb-4 pl-2 pr-6"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.6 }}
      >
        {movies.map((movie, index) => (
          <PosterCard key={movie.id} movie={movie} index={index} />
        ))}
      </motion.div>
    </section>
  );
}

CarouselRow.propTypes = {
  title: PropTypes.string.isRequired,
  movies: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      thumbnail: PropTypes.string.isRequired,
      year: PropTypes.number,
      genre: PropTypes.string
    })
  ).isRequired
};

function PosterCard({ movie, index }) {
  const cardRef = useRef(null);
  const rotateX = useMotionValue(0);
  const rotateY = useMotionValue(0);

  const glowOpacity = useTransform(rotateY, [-12, 12], [0.5, 1]);

  const handleMouseMove = (event) => {
    const rect = cardRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const midX = rect.width / 2;
    const midY = rect.height / 2;

    const rotateAmountX = ((y - midY) / midY) * -8;
    const rotateAmountY = ((x - midX) / midX) * 10;

    rotateX.set(rotateAmountX);
    rotateY.set(rotateAmountY);
  };

  const resetTilt = () => {
    rotateX.set(0);
    rotateY.set(0);
  };

  return (
    <motion.div
      ref={cardRef}
      className="group relative h-56 w-40 shrink-0 cursor-pointer overflow-hidden rounded-2xl border border-white/10 bg-black/40 shadow-[0_20px_45px_rgba(0,0,0,0.55)] backdrop-blur-md md:h-64 md:w-48"
      style={{
        rotateX,
        rotateY,
        transformPerspective: "900px"
      }}
      whileHover={{
        scale: 1.12,
        boxShadow: "0px 30px 80px rgba(229, 9, 20, 0.4)"
      }}
      transition={{
        hover: { type: "spring", stiffness: 260, damping: 20 },
        animate: {
          duration: 0.5,
          delay: index * 0.05,
          type: "spring",
          stiffness: 120,
          damping: 18
        }
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={resetTilt}
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
    >
      <img
        src={movie.thumbnail}
        alt={movie.title}
        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
        loading="lazy"
      />
      <motion.div
        className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent"
        style={{ opacity: glowOpacity }}
      />
      <div className="absolute inset-x-0 bottom-0 flex flex-col gap-1 p-3">
        <p className="text-sm font-semibold text-white drop-shadow-[0_0_15px_rgba(229,9,20,0.6)]">
          {movie.title}
        </p>
        <p className="text-xs uppercase tracking-[0.3em] text-white/60">
          {movie.genre} • {movie.year}
        </p>
      </div>
    </motion.div>
  );
}

PosterCard.propTypes = {
  movie: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    thumbnail: PropTypes.string.isRequired,
    year: PropTypes.number,
    genre: PropTypes.string
  }).isRequired,
  index: PropTypes.number.isRequired
};
