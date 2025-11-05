import { Link, useNavigate } from 'react-router-dom';
import SearchBar from './SearchBar';

/**
 * Navbar Component
 * 
 * Main navigation bar with search
 */
export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className="bg-gray-800 border-b border-gray-700 sticky top-0 z-40">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center gap-6">
          {/* Logo / Home Link */}
          <Link to="/" className="text-xl font-bold text-white hover:text-blue-400 transition-colors whitespace-nowrap">
            Arc Raiders Wiki
          </Link>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl">
            <SearchBar />
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-4 whitespace-nowrap">
            <Link
              to="/items"
              className="text-gray-300 hover:text-white transition-colors px-3 py-2"
            >
              Items
            </Link>
            <Link
              to="/tasks?type=quest"
              className="text-gray-300 hover:text-white transition-colors px-3 py-2"
            >
              Quests
            </Link>
            <Link
              to="/tasks?type=expedition"
              className="text-gray-300 hover:text-white transition-colors px-3 py-2"
            >
              Expeditions
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-gray-300 hover:text-white"
            onClick={() => {/* TODO: Add mobile menu */}}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
}
