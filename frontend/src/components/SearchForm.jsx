import { useState } from 'react';
import { motion } from "framer-motion";

const categories = {
  school: "Schools",
  college: "Colleges & Universities",
  hospital: "Hospitals & Clinics",
  hotel: "Hotels & Accommodations"
};

export default function SearchForm({ onSearch }) {
  const [location, setLocation] = useState("");
  const [radius, setRadius] = useState(5);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const requestPayload = {
      location,
      radius_km: radius,
      categories: selectedCategories.length > 0 ? selectedCategories : null,
    };
    
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });
      
      if (!response.ok) {
        let message = 'Search failed';
        try {
          const errorPayload = await response.json();
          if (errorPayload?.detail) {
            message = Array.isArray(errorPayload.detail)
              ? errorPayload.detail[0]?.msg || message
              : errorPayload.detail;
          }
        } catch (parseError) {
          // Keep fallback message if body is not JSON.
        }
        throw new Error(message);
      }

      const data = await response.json();
      onSearch(data, requestPayload);
    } catch (error) {
      console.error('Search error:', error);
      setError(error.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.form 
      onSubmit={handleSubmit}
      className="bg-black/20 backdrop-blur-sm rounded-xl p-6 max-w-2xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-4">
        <div>
          <label htmlFor="location" className="block text-sm font-medium text-white mb-1">
            Location
          </label>
          <input
            type="text"
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter city, address, or location"
            className="w-full px-4 py-2 bg-black/40 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          />
        </div>
        
        <div>
          <label htmlFor="radius" className="block text-sm font-medium text-white mb-1">
            Search Radius (km): {radius}
          </label>
          <input
            type="range"
            id="radius"
            min="1"
            max="20"
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
            className="w-full"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-white mb-2">
            Categories
          </label>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(categories).map(([value, label]) => (
              <label key={value} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  value={value}
                  checked={selectedCategories.includes(value)}
                  onChange={(e) => {
                    setSelectedCategories(
                      e.target.checked
                        ? [...selectedCategories, value]
                        : selectedCategories.filter(c => c !== value)
                    );
                  }}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-white">{label}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>

        {error && (
          <p className="text-sm text-red-400 text-center">
            {error}
          </p>
        )}
      </div>
    </motion.form>
  );
}
