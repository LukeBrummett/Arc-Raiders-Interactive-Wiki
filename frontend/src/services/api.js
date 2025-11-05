/**
 * API Client for Arc Raiders Wiki Backend
 * 
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Items API
 */
export const itemsAPI = {
  /**
   * Get paginated list of items
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (default: 1)
   * @param {number} params.page_size - Items per page (default: 20)
   * @param {string} params.search - Search term
   * @param {string} params.category - Filter by category
   * @param {string} params.type - Filter by type
   * @param {string} params.rarity - Filter by rarity
   */
  getAll: (params = {}) => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    return fetchAPI(`/api/items?${queryParams}`);
  },

  /**
   * Get single item by ID
   * @param {number} id - Item ID
   */
  getById: (id) => fetchAPI(`/api/items/${id}`),

  /**
   * Get single item by name
   * @param {string} name - Item name
   */
  getByName: (name) => fetchAPI(`/api/items/name/${encodeURIComponent(name)}`),
};

/**
 * Tasks API (Quests, Expeditions, Workshops)
 */
export const tasksAPI = {
  /**
   * Get paginated list of tasks
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number
   * @param {number} params.page_size - Tasks per page
   * @param {string} params.search - Search term
   * @param {string} params.type - Filter by type (quest, expedition, workshop_station)
   * @param {string} params.trader - Filter by trader
   * @param {string} params.station_type - Filter by station type
   */
  getAll: (params = {}) => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    return fetchAPI(`/api/tasks?${queryParams}`);
  },

  /**
   * Get single task by ID
   * @param {number} id - Task ID
   */
  getById: (id) => fetchAPI(`/api/tasks/${id}`),

  /**
   * Get single task by name
   * @param {string} name - Task name
   */
  getByName: (name) => fetchAPI(`/api/tasks/name/${encodeURIComponent(name)}`),
};

/**
 * Search API
 */
export const searchAPI = {
  /**
   * Search across items and tasks
   * @param {string} query - Search query
   * @param {number} limit - Max results per category (default: 10)
   */
  search: (query, limit = 10) => {
    const params = new URLSearchParams({ q: query, limit });
    return fetchAPI(`/api/search?${params}`);
  },
};

/**
 * Health Check API
 */
export const healthAPI = {
  /**
   * Check API health and get statistics
   */
  check: () => fetchAPI('/api/health'),
};

export default {
  items: itemsAPI,
  tasks: tasksAPI,
  search: searchAPI,
  health: healthAPI,
};
