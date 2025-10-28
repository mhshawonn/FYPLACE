import { motion } from "framer-motion";

export default function LoadingIntro() {
  return (
    <motion.div
      className="fixed inset-0 z-[999] flex items-center justify-center bg-black"
      initial={{ opacity: 1 }}
      animate={{ opacity: 0 }}
      transition={{ delay: 0.8, duration: 0.4, ease: "easeInOut" }}
    >
      <motion.div
        className="flex flex-col items-center gap-3"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <motion.div
          className="h-24 w-24 rounded-full border-4 border-fy-primary border-t-transparent"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 0.9, ease: "linear" }}
        />
        <motion.h1
          className="text-4xl font-semibold tracking-[0.35em] text-white drop-shadow-[0_0_20px_rgba(229,9,20,0.85)]"
          animate={{ opacity: [0.35, 1, 0.35] }}
          transition={{ repeat: Infinity, duration: 1.2, ease: "easeInOut" }}
        >
          FYPLACE
        </motion.h1>
      </motion.div>
    </motion.div>
  );
}
