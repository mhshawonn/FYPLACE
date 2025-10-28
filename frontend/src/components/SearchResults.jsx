import { useState } from "react";
import { motion } from "framer-motion";

const categoryIcons = {
  school: "🏫",
  college: "🎓",
  hospital: "🏥",
  hotel: "🏨"
};

const PlaceCard = ({ place }) => (
  <motion.div
    className="bg-black/20 backdrop-blur-sm rounded-lg p-4 hover:bg-black/30 transition-colors"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ scale: 1.02 }}
  >
    <div className="flex items-start gap-3">
      <span className="text-2xl" role="img" aria-label={place.category}>
        {categoryIcons[place.category]}
      </span>
      <div className="flex-1">
        <h3 className="text-lg font-semibold text-white">{place.name || 'Unnamed Location'}</h3>
        <p className="text-gray-300 text-sm">{place.address || 'No address available'}</p>
        
        <div className="mt-2 space-y-1">
          {place.phone && (
            <p className="text-sm text-gray-300">
              📞 <a href={`tel:${place.phone}`} className="hover:text-purple-400">{place.phone}</a>
            </p>
          )}
          {place.email && (
            <p className="text-sm text-gray-300">
              ✉️ <a href={`mailto:${place.email}`} className="hover:text-purple-400">{place.email}</a>
            </p>
          )}
          {place.website && (
            <p className="text-sm text-gray-300">
              🌐 <a href={place.website} target="_blank" rel="noopener noreferrer" className="hover:text-purple-400">
                Website
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  </motion.div>
);

export default function SearchResults({ results, locationLabel, radiusKm, searchParams }) {
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState(null);

  const handleExport = async () => {
    if (!searchParams) {
      return;
    }

    setExportLoading(true);
    setExportError(null);

    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchParams),
      });

      if (!response.ok) {
        let message = 'Export failed';
        try {
          const errorPayload = await response.json();
          if (errorPayload?.detail) {
            message = Array.isArray(errorPayload.detail)
              ? errorPayload.detail[0]?.msg || message
              : errorPayload.detail;
          }
        } catch (parseError) {
          // Ignore JSON parse issues and keep the generic error message.
        }
        throw new Error(message);
      }

      const blob = await response.blob();
      const disposition = response.headers.get('Content-Disposition') || response.headers.get('content-disposition');
      let filename = 'findyourplace_results.csv';
      if (disposition) {
        const match = disposition.match(/filename[^;=\n]*=\s*"?([^";\n]*)"?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      const downloadUrl = window.URL.createObjectURL(blob);
      const tempLink = document.createElement('a');
      tempLink.href = downloadUrl;
      tempLink.download = filename;
      document.body.appendChild(tempLink);
      tempLink.click();
      document.body.removeChild(tempLink);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Export error:', error);
      setExportError(error.message || 'Export failed');
    } finally {
      setExportLoading(false);
    }
  };

  if (!results || results.length === 0) {
    return (
      <div className="text-center text-gray-300 py-8">
        No places found in this area. Try expanding your search radius or changing categories.
      </div>
    );
  }

  // Group results by category
  const groupedResults = results.reduce((acc, place) => {
    if (!acc[place.category]) {
      acc[place.category] = [];
    }
    acc[place.category].push(place);
    return acc;
  }, {});

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-white">
          Results for {locationLabel}
        </h2>
        <p className="text-gray-300">Within {radiusKm} km radius</p>
      </div>

      {Object.entries(groupedResults).map(([category, places]) => (
        <section key={category} className="space-y-4">
          <h3 className="text-xl font-semibold text-white capitalize">
            {categoryIcons[category]} {category.replace('_', ' ')}s
          </h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {places.map((place) => (
              <PlaceCard key={place.osm_id} place={place} />
            ))}
          </div>
        </section>
      ))}

      <div className="flex justify-center mt-6">
        <button
          type="button"
          onClick={handleExport}
          disabled={exportLoading || !searchParams}
          className="bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          {exportLoading ? 'Exporting...' : 'Export to CSV'}
        </button>
      </div>

      {exportError && (
        <p className="text-center text-sm text-red-400">
          {exportError}
        </p>
      )}
    </div>
  )
}
