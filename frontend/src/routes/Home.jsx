import { useState } from 'react';
import { motion } from "framer-motion";
import SearchForm from "../components/SearchForm";
import SearchResults from "../components/SearchResults";
import LoadingIntro from "../components/LoadingIntro";

export default function Home() {
  const [searchResults, setSearchResults] = useState(null);
  const [searchParams, setSearchParams] = useState(null);
  
  const handleSearch = (results, params) => {
    setSearchResults(results);
    setSearchParams(params);
    // Scroll to results smoothly
    window.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
  };

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-16 px-6 pb-20">
      <div className="min-h-screen flex flex-col items-center justify-center">
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Find Your Place
          </h1>
          <p className="text-gray-300 text-lg">
            Discover schools, colleges, hospitals, and hotels near you
          </p>
        </motion.div>

        <SearchForm onSearch={handleSearch} />
      </div>

      {searchResults && (
        <motion.section
          className="grid gap-16"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <SearchResults 
            results={searchResults.results}
            locationLabel={searchResults.location_label}
            radiusKm={searchResults.radius_km}
            searchParams={searchParams}
          />
        </motion.section>
      )}
    </div>
  );
}
