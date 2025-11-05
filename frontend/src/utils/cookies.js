/**
 * Cookie Management Utilities
 * 
 * Handles user progress tracking via browser cookies (no server-side storage)
 */

const COOKIE_NAME = 'arcraiders_progress';
const COOKIE_EXPIRY_DAYS = 365;

/**
 * Get a cookie value by name
 */
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return null;
}

/**
 * Set a cookie value
 */
function setCookie(name, value, days = COOKIE_EXPIRY_DAYS) {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = `expires=${date.toUTCString()}`;
  document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
}

/**
 * Get user progress data
 * Returns the progress object or creates a new one
 */
export function getProgress() {
  const cookie = getCookie(COOKIE_NAME);
  
  if (cookie) {
    try {
      return JSON.parse(decodeURIComponent(cookie));
    } catch (e) {
      console.error('Error parsing progress cookie:', e);
    }
  }
  
  // Default progress structure
  return {
    completedQuests: [],
    completedExpeditions: [],
    searchHistory: [],
    lastVisited: [],
    preferences: {
      theme: 'dark',
    },
  };
}

/**
 * Save user progress data
 */
export function saveProgress(progressData) {
  const jsonString = JSON.stringify(progressData);
  setCookie(COOKIE_NAME, encodeURIComponent(jsonString));
}

/**
 * Mark a quest as completed
 */
export function markQuestComplete(questId) {
  const progress = getProgress();
  
  if (!progress.completedQuests.includes(questId)) {
    progress.completedQuests.push(questId);
    saveProgress(progress);
  }
  
  return progress;
}

/**
 * Mark a quest as incomplete
 */
export function markQuestIncomplete(questId) {
  const progress = getProgress();
  
  progress.completedQuests = progress.completedQuests.filter(id => id !== questId);
  saveProgress(progress);
  
  return progress;
}

/**
 * Check if a quest is completed
 */
export function isQuestComplete(questId) {
  const progress = getProgress();
  return progress.completedQuests.includes(questId);
}

/**
 * Mark an expedition as completed
 */
export function markExpeditionComplete(expeditionId) {
  const progress = getProgress();
  
  if (!progress.completedExpeditions.includes(expeditionId)) {
    progress.completedExpeditions.push(expeditionId);
    saveProgress(progress);
  }
  
  return progress;
}

/**
 * Mark an expedition as incomplete
 */
export function markExpeditionIncomplete(expeditionId) {
  const progress = getProgress();
  
  progress.completedExpeditions = progress.completedExpeditions.filter(id => id !== expeditionId);
  saveProgress(progress);
  
  return progress;
}

/**
 * Check if an expedition is completed
 */
export function isExpeditionComplete(expeditionId) {
  const progress = getProgress();
  return progress.completedExpeditions.includes(expeditionId);
}

/**
 * Add to search history
 */
export function addToSearchHistory(searchTerm) {
  const progress = getProgress();
  
  // Remove if already exists (move to top)
  progress.searchHistory = progress.searchHistory.filter(term => term !== searchTerm);
  
  // Add to beginning
  progress.searchHistory.unshift(searchTerm);
  
  // Keep only last 10
  progress.searchHistory = progress.searchHistory.slice(0, 10);
  
  saveProgress(progress);
  return progress;
}

/**
 * Add to last visited items/tasks
 */
export function addToLastVisited(type, id, name) {
  const progress = getProgress();
  
  const visitedItem = {
    type, // 'item' or 'task'
    id,
    name,
    timestamp: new Date().toISOString(),
  };
  
  // Remove if already exists
  progress.lastVisited = progress.lastVisited.filter(
    item => !(item.type === type && item.id === id)
  );
  
  // Add to beginning
  progress.lastVisited.unshift(visitedItem);
  
  // Keep only last 20
  progress.lastVisited = progress.lastVisited.slice(0, 20);
  
  saveProgress(progress);
  return progress;
}

/**
 * Clear all progress
 */
export function clearProgress() {
  setCookie(COOKIE_NAME, '', -1); // Delete cookie
  return getProgress(); // Return fresh default progress
}

/**
 * Export progress as JSON file
 */
export function exportProgress() {
  const progress = getProgress();
  const dataStr = JSON.stringify(progress, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `arcraiders-progress-${new Date().toISOString().split('T')[0]}.json`;
  link.click();
  
  URL.revokeObjectURL(url);
}

/**
 * Import progress from JSON file
 */
export function importProgress(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const importedData = JSON.parse(e.target.result);
        saveProgress(importedData);
        resolve(importedData);
      } catch (error) {
        reject(new Error('Invalid progress file'));
      }
    };
    
    reader.onerror = () => reject(new Error('Error reading file'));
    reader.readAsText(file);
  });
}

export default {
  getProgress,
  saveProgress,
  markQuestComplete,
  markQuestIncomplete,
  isQuestComplete,
  markExpeditionComplete,
  markExpeditionIncomplete,
  isExpeditionComplete,
  addToSearchHistory,
  addToLastVisited,
  clearProgress,
  exportProgress,
  importProgress,
};
