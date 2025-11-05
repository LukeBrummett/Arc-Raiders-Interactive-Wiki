import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'

// Placeholder components - will be built out later
function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-4">Arc Raiders Interactive Wiki</h1>
      <p className="text-lg">Search bar and main interface coming soon...</p>
    </div>
  )
}

function ItemPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Item Details</h1>
      <p>Item visualization interface coming soon...</p>
    </div>
  )
}

function QuestsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Quests</h1>
      <p>Quest list and tracking coming soon...</p>
    </div>
  )
}

function ExpeditionsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Expeditions</h1>
      <p>Expedition list and tracking coming soon...</p>
    </div>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/items/:id" element={<ItemPage />} />
          <Route path="/quests" element={<QuestsPage />} />
          <Route path="/expeditions" element={<ExpeditionsPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
