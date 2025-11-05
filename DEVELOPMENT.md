# Development Guide

## Quick Start

### Backend Setup

1. Navigate to backend directory:
   ```powershell
   cd backend
   ```

2. Create and activate virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```powershell
   copy .env.example .env
   # Edit .env with your settings
   ```

5. Run the backend:
   ```powershell
   python -m app.main
   ```

   Backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Run the frontend:
   ```powershell
   npm run dev
   ```

   Frontend will be available at http://localhost:3000

## Development Workflow

1. **Start both servers** (in separate terminals):
   - Backend: `cd backend && python -m app.main`
   - Frontend: `cd frontend && npm run dev`

2. **Make changes** to your code

3. **Test changes**:
   - Frontend auto-reloads on save
   - Backend auto-reloads with `--reload` flag

## Project Structure

```
Arc-Raiders-Interactive-Wiki/
├── backend/               # Python FastAPI backend
│   ├── app/              # Application code
│   ├── scraper/          # Wiki scraping tools
│   └── migrations/       # Database migrations
├── frontend/             # React frontend
│   ├── src/             # React components and logic
│   └── public/          # Static assets
├── database/            # Database schema and scripts
├── scripts/             # Utility scripts
└── docs/                # Documentation
```

## Next Development Steps

Based on the Project Overview, here's the recommended development order:

### Phase 1: Foundation

1. **Initial Wiki Analysis** (PRIORITY)
   - Run scraper to analyze https://arcraiders.wiki/ structure
   - Document available data fields
   - Design database schema based on findings

2. **Database Setup**
   - Set up PostgreSQL locally
   - Create schema based on analysis
   - Set up Alembic migrations

3. **Backend API Development**
   - Implement API endpoints for items, quests, expeditions
   - Add search functionality
   - Create manual review workflow

4. **Frontend Core Components**
   - Build search bar with autocomplete
   - Create item detail page layout
   - Implement cookie-based state management
   - Build quest and expedition lists

5. **Integration**
   - Connect frontend to backend API
   - Test full data flow
   - Implement responsive design

## Testing

- Backend: `pytest` (to be set up)
- Frontend: `npm run test` (to be set up)
- Manual testing on multiple devices for mobile responsiveness

## Common Commands

### Backend
```powershell
# Activate virtual environment
.\backend\venv\Scripts\activate

# Install new dependency
pip install package-name
pip freeze > requirements.txt

# Run scraper
python -m scraper.wiki_scraper

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend
```powershell
# Install new dependency
npm install package-name

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check `.env` file exists and is configured
- Verify PostgreSQL is running (if database is set up)

### Frontend won't start
- Run `npm install` to ensure dependencies are installed
- Check for port conflicts (default: 3000)
- Clear node_modules and reinstall if needed

### CORS errors
- Verify backend CORS settings in `.env`
- Check frontend is using correct API URL in vite.config.js

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
