import SearchBar from '../components/SearchBar';
import Footer from '../components/Footer';
import { getProgress } from '../utils/cookies';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

/**
 * HomePage Component
 * 
 * Main landing page with search and recent activity
 */
export default function HomePage() {
  const [progress, setProgress] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    setProgress(getProgress());
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-center mb-2">
            Arc Raiders Interactive Wiki
          </h1>
          <p className="text-gray-400 text-center">
            Your comprehensive guide to items, quests, and expeditions
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Search Section */}
        <div className="max-w-3xl mx-auto mb-12">
          <SearchBar className="mb-4" />
          <p className="text-sm text-gray-400 text-center">
            Search for any item, quest, or expedition to get started
          </p>
        </div>

        {/* Quick Links */}
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
          <button
            onClick={() => navigate('/items')}
            className="bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg p-6 text-center transition-colors"
          >
            <div className="text-3xl mb-2">📦</div>
            <h3 className="text-xl font-semibold mb-1">Items</h3>
            <p className="text-gray-400 text-sm">Browse all loot and equipment</p>
          </button>

          <button
            onClick={() => navigate('/tasks?type=quest')}
            className="bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg p-6 text-center transition-colors"
          >
            <div className="text-3xl mb-2">📜</div>
            <h3 className="text-xl font-semibold mb-1">Quests</h3>
            <p className="text-gray-400 text-sm">Track your quest progress</p>
          </button>

          <button
            onClick={() => navigate('/tasks?type=expedition')}
            className="bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg p-6 text-center transition-colors"
          >
            <div className="text-3xl mb-2">🗺️</div>
            <h3 className="text-xl font-semibold mb-1">Expeditions</h3>
            <p className="text-gray-400 text-sm">Plan your expeditions</p>
          </button>
        </div>

        {/* Recent Activity */}
        {progress && progress.lastVisited && progress.lastVisited.length > 0 && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">Recently Viewed</h2>
            <div className="bg-gray-800 border border-gray-700 rounded-lg divide-y divide-gray-700">
              {progress.lastVisited.slice(0, 5).map((item) => (
                <button
                  key={`${item.type}-${item.id}`}
                  onClick={() => navigate(`/${item.type}s/${item.id}`)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-700 transition-colors flex items-center justify-between"
                >
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-sm text-gray-400 capitalize">{item.type}</div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(item.timestamp).toLocaleDateString()}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Stats */}
        {progress && (
          <div className="max-w-4xl mx-auto mt-8 grid md:grid-cols-2 gap-4">
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Quest Progress</h3>
              <div className="text-2xl font-bold">{progress.completedQuests.length} Completed</div>
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Expedition Progress</h3>
              <div className="text-2xl font-bold">{progress.completedExpeditions.length} Completed</div>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
