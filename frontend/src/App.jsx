import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import HomePage from './pages/HomePage'

// Placeholder components - will be built out next
function ItemPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Item Details</h1>
      <p>Item visualization interface coming soon...</p>
    </div>
  )
}

function ItemsListPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">All Items</h1>
      <p>Item list coming soon...</p>
    </div>
  )
}

function TasksPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Quests & Expeditions</h1>
      <p>Task list and tracking coming soon...</p>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/items" element={<ItemsListPage />} />
        <Route path="/items/:id" element={<ItemPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/tasks/:id" element={<ItemPage />} />
      </Routes>
    </Router>
  )
}

export default App
