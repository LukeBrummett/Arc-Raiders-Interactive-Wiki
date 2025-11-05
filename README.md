# Arc Raiders Interactive Wiki

Interactive wiki for Arc Raiders with crafting visualization, quest chains, and progress tracking. Built with React + Python + PostgreSQL.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+ (or Docker)

### 1. Clone & Install Dependencies

```powershell
# Backend setup
cd backend
python -m venv venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Database Setup

**See detailed instructions:** [`docs/Database Setup Guide.md`](docs/Database%20Setup%20Guide.md)

**Quick Docker Setup:**
```powershell
docker run --name arcraiders-postgres `
  -e POSTGRES_USER=arcraiders `
  -e POSTGRES_PASSWORD=arcraiders `
  -e POSTGRES_DB=arcraiders_wiki `
  -p 5432:5432 `
  -d postgres:15
```

**Run Migrations:**
```powershell
cd backend
.venv\Scripts\Activate.ps1
alembic upgrade head
```

**Test Connection:**
```powershell
python test_db.py
```

### 3. Start Development Servers

**Using VS Code Tasks (Recommended):**
- Press `Ctrl+Shift+P` → "Tasks: Run Task" → "Start Both Servers"

**Manual:**
```powershell
# Backend (in backend/)
uvicorn app.main:app --reload

# Frontend (in frontend/)
npm run dev
```

- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

## 📁 Project Structure

```
Arc-Raiders-Interactive-Wiki/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # SQLAlchemy setup
│   │   └── models/              # Database models
│   │       ├── item.py          # Item model (loot, weapons, equipment)
│   │       └── task.py          # Task model (quests, expeditions, workshops)
│   ├── migrations/              # Alembic migrations
│   ├── scraper/                 # Wiki scraping tools
│   │   ├── wiki_scraper.py      # Index page scraper
│   │   └── detail_page_scraper.py  # Detail page scraper
│   ├── scraped_data/            # Scraped wiki data (JSON)
│   └── test_db.py               # Database verification script
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # React app with routing
│   │   ├── components/          # React components
│   │   └── pages/               # Page components
│   └── public/
├── docs/
│   ├── Project Overview.md               # Complete project documentation
│   ├── Wiki Data Structure Analysis.md   # Database schema design
│   ├── Database Setup Guide.md           # PostgreSQL setup instructions
│   └── Database Implementation Summary.md # Current implementation status
└── .vscode/
    └── tasks.json               # VS Code task automation
```

## 🗄️ Database Schema

### Items Table
Stores all loot, weapons, and equipment with flexible JSONB fields:
- Standard: `name`, `description`, `image_url`, `category`, `rarity`, `type`
- JSONB: `stats`, `sources`, `crafting_recipes`, `recycled_into`, `salvaged_into`

### Tasks Table
Stores quests, expeditions, and workshop upgrades:
- Quest fields: `trader`, `location`, `dialog`, `objectives`, `rewards`
- Workshop/Expedition: `stages`, `levels`, `station_type`
- Quest chains: `previous_task_id`, `next_tasks`

**Full schema details:** [`docs/Wiki Data Structure Analysis.md`](docs/Wiki%20Data%20Structure%20Analysis.md)

## 📊 Implementation Progress

### ✅ Phase 1: Analysis & Design (COMPLETE)
- Scraped 6 main wiki index pages
- Discovered 398 individual page URLs (215 items, 183 tasks)
- Analyzed detail page structures
- Finalized database schema

### 🔄 Phase 2: Database Setup (IN PROGRESS)
- ✅ Created SQLAlchemy models
- ✅ Created Alembic migrations
- ✅ Configured database environment
- ⏳ **Next:** Install PostgreSQL and run migrations

### 📋 Phase 3: Data Scraping (TODO)
- Enhance detail page scraper
- Scrape all 398 pages
- Populate database

### 📋 Phase 4: API Development (TODO)
- Build CRUD endpoints
- Add search functionality
- Test with Swagger UI

### 📋 Phase 5: Frontend (TODO)
- Item/quest list pages
- Detail pages with all data
- Cookie-based progress tracking

**Detailed status:** [`docs/Database Implementation Summary.md`](docs/Database%20Implementation%20Summary.md)

## 🛠️ Development Workflow

### VS Code Tasks
- **Start Both Servers** - Run backend + frontend together
- **Start Backend** - Run FastAPI server only
- **Start Frontend** - Run Vite dev server only
- **Install Backend Dependencies** - pip install
- **Install Frontend Dependencies** - npm install
- **Run Wiki Scraper** - Scrape wiki data

Access via: `Ctrl+Shift+P` → "Tasks: Run Task"

### Database Operations

**Create Migration:**
```powershell
alembic revision -m "description"
```

**Run Migrations:**
```powershell
alembic upgrade head
```

**Rollback:**
```powershell
alembic downgrade -1
```

**Check Status:**
```powershell
alembic current
alembic history
```

### Scraping Wiki Data

**Index Pages (already done):**
```powershell
python -m scraper.wiki_scraper
```

**Detail Pages (next step):**
```powershell
python -m scraper.detail_page_scraper
```

## 📚 Documentation

- **[Project Overview](docs/Project%20Overview.md)** - Complete vision, features, tech stack
- **[Wiki Data Structure Analysis](docs/Wiki%20Data%20Structure%20Analysis.md)** - Schema design and JSONB examples
- **[Database Setup Guide](docs/Database%20Setup%20Guide.md)** - PostgreSQL installation and configuration
- **[Database Implementation Summary](docs/Database%20Implementation%20Summary.md)** - Current status and next steps

## 🧪 Testing

**Database Connection:**
```powershell
python test_db.py
```

**API Tests (once implemented):**
- Visit http://localhost:8000/docs
- Try interactive Swagger UI

**Frontend:**
- Visit http://localhost:3000
- Check browser console for errors

## 🎯 Next Steps

1. **Install PostgreSQL** (see [Database Setup Guide](docs/Database%20Setup%20Guide.md))
2. **Run migrations:** `alembic upgrade head`
3. **Verify setup:** `python test_db.py`
4. **Enhance detail page scraper** to extract all data fields
5. **Scrape all 398 pages** and populate database
6. **Build API endpoints** for items and tasks
7. **Connect frontend** to API

## 📝 Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, BeautifulSoup4
- **Frontend:** React 18, Vite, Tailwind CSS, React Router
- **Database:** PostgreSQL 15 with JSONB
- **Development:** VS Code, Docker (optional)

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

## 📄 License

MIT

---

**Current Status:** Database models and migrations created. Ready for PostgreSQL installation! 🎉

