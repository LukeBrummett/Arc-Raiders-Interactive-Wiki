import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchAPI } from '../services/api';
import { addToSearchHistory } from '../utils/cookies';

/**
 * SearchBar Component
 * 
 * Main search interface with autocomplete suggestions
 */
export default function SearchBar({ className = '' }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState({ items: [], tasks: [], total_results: 0 });
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const navigate = useNavigate();
  const searchRef = useRef(null);
  const debounceRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (query.trim().length < 2) {
      setResults({ items: [], tasks: [], total_results: 0 });
      setIsOpen(false);
      return;
    }

    // Clear previous timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new timeout
    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const data = await searchAPI.search(query, 10);
        setResults(data);
        setIsOpen(true);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Search error:', error);
        setResults({ items: [], tasks: [], total_results: 0 });
      } finally {
        setIsLoading(false);
      }
    }, 300); // 300ms debounce

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query]);

  // Handle keyboard navigation
  function handleKeyDown(e) {
    const allResults = [...results.items, ...results.tasks];
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev < allResults.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && allResults[selectedIndex]) {
        handleSelect(allResults[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setSelectedIndex(-1);
    }
  }

  // Handle result selection
  function handleSelect(result) {
    const isItem = 'category' in result; // Items have category, tasks don't
    const type = isItem ? 'item' : 'task';
    
    addToSearchHistory(result.name);
    setQuery('');
    setIsOpen(false);
    setSelectedIndex(-1);
    
    navigate(`/${type}s/${result.id}`);
  }

  return (
    <div ref={searchRef} className={`relative w-full ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.trim().length >= 2 && setIsOpen(true)}
          placeholder="Search items, quests, expeditions..."
          className="w-full px-4 py-3 pl-12 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
        
        {/* Search Icon */}
        <svg
          className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>

        {/* Loading Spinner */}
        {isLoading && (
          <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && results.total_results > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl max-h-96 overflow-y-auto">
          {/* Items Section */}
          {results.items.length > 0 && (
            <div>
              <div className="px-4 py-2 text-sm font-semibold text-gray-400 bg-gray-900">
                Items ({results.items.length})
              </div>
              {results.items.map((item, index) => {
                const globalIndex = index;
                return (
                  <button
                    key={`item-${item.id}`}
                    onClick={() => handleSelect(item)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center gap-3 border-b border-gray-700 ${
                      selectedIndex === globalIndex ? 'bg-gray-700' : ''
                    }`}
                  >
                    {item.image_url && (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        className="w-10 h-10 object-contain rounded"
                      />
                    )}
                    <div className="flex-1">
                      <div className="font-medium text-white">{item.name}</div>
                      <div className="text-sm text-gray-400">
                        {item.category} {item.rarity && `• ${item.rarity}`}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {/* Tasks Section */}
          {results.tasks.length > 0 && (
            <div>
              <div className="px-4 py-2 text-sm font-semibold text-gray-400 bg-gray-900">
                Quests & Expeditions ({results.tasks.length})
              </div>
              {results.tasks.map((task, index) => {
                const globalIndex = results.items.length + index;
                return (
                  <button
                    key={`task-${task.id}`}
                    onClick={() => handleSelect(task)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center gap-3 border-b border-gray-700 last:border-b-0 ${
                      selectedIndex === globalIndex ? 'bg-gray-700' : ''
                    }`}
                  >
                    <div className="flex-1">
                      <div className="font-medium text-white">{task.name}</div>
                      <div className="text-sm text-gray-400">
                        {task.type} {task.trader && `• ${task.trader}`}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* No Results */}
      {isOpen && query.trim().length >= 2 && results.total_results === 0 && !isLoading && (
        <div className="absolute z-50 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-4 text-center text-gray-400">
          No results found for "{query}"
        </div>
      )}
    </div>
  );
}
