# Arc Raiders Interactive Wiki - Project Overview

**Project Name:** Arc Raiders Interactive Wiki  
**Created:** 2025-11-04  
**Maintainer:** LukeBrummett  
**Status:** ON HOLD - Discovered Existing Comprehensive Database

---

## 🛑 Project Status Update (2025-11-04)

**DISCOVERED:** [ardb.app](https://ardb.app/) provides a comprehensive database with most planned features already implemented:

- ✅ Quest Tracker - [https://ardb.app/trackers/quests](https://ardb.app/trackers/quests)
- ✅ Item Tracker - [https://ardb.app/trackers/required-items](https://ardb.app/trackers/required-items)
- ✅ Recipe Tracker - [https://ardb.app/trackers/recipes](https://ardb.app/trackers/recipes)
- ✅ Hideout Tracker - [https://ardb.app/trackers/hideout](https://ardb.app/trackers/hideout)
- ✅ Comprehensive item database - [https://ardb.app/db/items](https://ardb.app/db/items)
- ✅ Quest database with locations - [https://ardb.app/db/quests](https://ardb.app/db/quests)
- ✅ ARC enemy database - [https://ardb.app/db/arc](https://ardb.app/db/arc)

**DECISION:** Project paused to evaluate:
1. Whether to pivot to features ardb.app doesn't offer (AI recommendations, item comparison, build optimization)
2. Whether to contribute to ardb.app instead
3. Whether to continue as a complementary tool with different UX/features

**CURRENT STATE:**
- Backend API fully functional (214 items, 26 tasks from arcraiders.wiki)
- Frontend homepage with working search implemented
- Database schema flexible enough to integrate multiple data sources
- All code committed to GitHub repository

---

## Table of Contents
1. [Project Vision](#project-vision)
2. [Technical Architecture](#technical-architecture)
3. [Business Guidelines](#business-guidelines)
4. [Core Features](#core-features)
5. [Data Management](#data-management)
6. [User Experience](#user-experience)
7. [Future Scope](#future-scope)
8. [Development Roadmap](#development-roadmap)

---

## Project Vision

The Arc Raiders Interactive Wiki aims to be the definitive, community-focused resource for Arc Raiders players. This project will aggregate and organize game data from https://arcraiders.wiki/ while maintaining a custom, manually-curated database. The focus is on delivering a unique, interactive user experience that goes beyond traditional wiki functionality.

**Key Differentiators:**
- Interactive item relationship visualization (crafting trees, quest chains)
- Cookie-based progress tracking without requiring user accounts
- Robust, fully-featured search across all game content
- Mobile-first responsive design
- Maintainer-controlled data quality through manual review processes

---

## Technical Architecture

### Frontend
- **Framework:** React
- **Purpose:** Dynamic SPA for modern UI and robust state management
- **Key Libraries:**
  - State management (React Context/Redux)
  - Routing (React Router)
  - Cookie management
  - Search/autocomplete components
  - Mobile-responsive CSS framework (Tailwind CSS recommended)

### Backend
- **Language:** Python
- **Framework:** Flask or FastAPI (recommended for RESTful API)
- **Purpose:** API server for data retrieval and management
- **Key Components:**
  - RESTful API endpoints
  - Data validation layer
  - Manual review workflow system
  - Scraper orchestration

### Database
- **System:** PostgreSQL
- **Purpose:** Relational data storage for items, quests, expeditions, and relationships
- **Key Schema Areas:**
  - Items table
  - Quests table (with questline relationships)
  - Expeditions table
  - Crafting relationships (many-to-many)
  - Icon spawn locations
  - Image/asset references

### Hosting
- **Production:** AWS (EC2 for application, RDS for PostgreSQL)
- **Development:** Localhost
- **CI/CD:** TBD based on deployment needs

### Data Scraping

**⚠️ UPDATE:** Original plan was to scrape https://arcraiders.wiki/, but discovered [ardb.app](https://ardb.app/) has significantly more comprehensive data including:
- Item sell prices and detailed stats
- Complete quest objectives and locations
- Crafting recipes with exact requirements
- Built-in progress tracking

**Original Plan (May Be Superseded):**
- **Source:** https://arcraiders.wiki/
- **Technology:** Python (BeautifulSoup/Scrapy)
- **Execution:** Manual trigger scripts
- **Timing:** During game update windows
- **Workflow:** Scrape → Manual Review → Database Update

**Future Considerations:**
- Investigate if ardb.app has an API
- Consider scraping both sources and merging data
- Evaluate whether custom scraping is still necessary

---

## Business Guidelines

### Data Ownership & Control
- **Own Database:** Maintain custom PostgreSQL database derived from wiki scrapes
- **Manual Curation Priority:** All data changes require manual review before database updates
- **Maintainer-Only Access:** No public-facing data modification capabilities
- **Quality Over Speed:** Accuracy and reliability trump automation

### User Privacy & Access
- **No User Accounts:** Zero user registration or authentication required
- **Cookie-Based Progress:** All tracking stored locally in browser cookies
- **No Cloud Sync:** User progress is device-specific
- **Privacy-First:** No user data collection or analytics (beyond optional future scope)

### Content Management
- **Live Service Model:** Wiki reflects current game version only
- **No Version Control:** Historical data not maintained
- **Update Windows:** Planned data updates during game patches
- **Image Rights:** Use scraped wiki images; supplemented with official assets when available

### Mobile Optimization
- **Requirement:** All features must be fully responsive and mobile-ready
- **Design Philosophy:** Mobile-first approach
- **Testing:** Cross-device compatibility testing required

---

## Core Features

### 1. Interactive Website Interface

#### Main Search Bar
- **Location:** Primary screen/homepage
- **Functionality:**
  - Autocomplete suggestions
  - Fuzzy matching for typos
  - Category filtering (items, quests, expeditions)
  - Search history (cookie-based)
  - Recommended/commonly searched items display
  - Real-time results as user types

#### Item Visualization Screen
**Layout:**
```
┌─────────────────────────────────────────┐
│         Additional Details              │
│                                         │
├──────────┬──────────────┬──────────────┤
│          │              │              │
│  Left:   │   Center:    │   Right:     │
│Components│Selected Item │  Use Cases   │
│  (What   │   (Main      │  (What it's  │
│  crafts  │   Card)      │   used for)  │
│   this)  │              │              │
│          │              │              │
│ Prior    │   Current    │   Next       │
│ Quest    │    Quest     │   Quest      │
│          │              │              │
└──────────┴──────────────┴──────────────┘
│         Additional Details              │
└─────────────────────────────────────────┘
```

**Item Details Include:**
- Item name and icon
- Description
- Rarity/tier
- Crafting components (left panel)
- What it's used to craft (right panel)
- Related quests/expeditions (with notification badges)
- Icon spawn locations
- Scraped image from wiki

**Quest Details Include:**
- Quest name and icon
- Description
- Prior quest in chain (left panel)
- Next quest in chain (right panel)
- Rewards
- Requirements
- Progression tracking

### 2. Quest Management System

#### Quest List Features
- **Checkable Items:** Click to mark complete
- **Progress Tracking:** Percentage completion display
- **Questline Visualization:** See full chain of connected quests
- **Filtering Options:**
  - By completion status
  - By questline
  - By reward type
  - By difficulty (future scope)
  - By region (future scope)

#### Quest Progression
- **Linear Chains:** Prior → Current → Next quest navigation
- **Branching Support:** Handle multiple quest paths
- **Completion Notifications:** Visual indicators for incomplete quest-related items
- **Cookie Persistence:** Progress saved locally

### 3. Expedition Management System

#### Expedition List Features
- **Checkable Items:** Click to mark complete
- **Progress Tracking:** Percentage completion display
- **Filtering Options:**
  - By completion status
  - By difficulty (future scope)
  - By region (future scope)
  - By reward type (future scope)

#### Expedition Details
- Similar interactive UI as quests
- Expedition-specific item requirements
- Completion rewards
- Related items highlighted

### 4. Crafting & Item Relationships

#### Relationship Types
- **Components:** What items are needed to craft this item
- **Recipes:** What can be crafted using this item
- **Recycling:** What this item breaks down into
- **Quest Integration:** Which quests require/reward this item
- **Expedition Integration:** Which expeditions require/reward this item

#### Visual Indicators
- **Notification Badges:** Show unchecked quests/expeditions using this item
- **Removed When Checked:** Notifications disappear once quest/expedition marked complete
- **Interactive Navigation:** Click component/recipe items to navigate to their pages

### 5. Icon Spawn Locations
- **Data Tracked:** Which icons/locations items spawn in
- **Display:** List or visual map (future scope for map integration)
- **Filtering:** Find all items that spawn in specific locations

---

## Data Management

### Scraping Process

#### 1. Manual Trigger
- Maintainer initiates scrape script during game update windows
- Script runs against https://arcraiders.wiki/
- Target pages:
  - Individual item pages
  - Quest pages
  - Expedition pages
  - Icon/location pages

#### 2. Data Extraction
**Scraped Data Points:**
- Item names, descriptions, icons, images
- Crafting recipes and components
- Recycling outputs
- Quest chains and requirements
- Expedition requirements
- Icon spawn locations
- Item relationships

#### 3. Manual Review Workflow
- Scraped data staged in separate tables/JSON files
- Maintainer reviews changes:
  - New items/quests added
  - Modified descriptions
  - Changed relationships
  - Removed content
- Conflict resolution for data inconsistencies
- Approval required before database update

#### 4. Database Update
- Approved changes merged into production database
- Relationships updated (crafting, quests, expeditions)
- Image assets downloaded and stored
- Indexing updated for search functionality

### Database Schema (Conceptual)

**NOTE:** The schema below is a **preliminary conceptual outline only**. Actual table structures will be determined after analyzing the scraped wiki data structure. Additional columns, tables, and relationships will be added as needed to accommodate all data fields available from https://arcraiders.wiki/.

**Schema Design Approach:**
- Initial scrape will reveal actual data structure
- Schema will be iteratively refined based on wiki content
- Flexible design to accommodate new fields as game updates
- Migration system for schema changes

#### Items Table (Preliminary)
```sql
-- This is a CONCEPTUAL example - actual schema TBD after wiki scrape
- id (primary key)
- name
- description
- rarity
- icon_url
- image_url
- created_at
- updated_at
-- Additional columns will be added based on wiki data structure
```

#### Quests Table (Preliminary)
```sql
-- This is a CONCEPTUAL example - actual schema TBD after wiki scrape
- id (primary key)
- name
- description
- questline_id (foreign key)
- prior_quest_id (foreign key, self-referential)
- next_quest_id (foreign key, self-referential)
- icon_url
- rewards_text
- requirements_text
- created_at
- updated_at
-- Additional columns will be added based on wiki data structure
```

#### Expeditions Table (Preliminary)
```sql
-- This is a CONCEPTUAL example - actual schema TBD after wiki scrape
- id (primary key)
- name
- description
- icon_url
- rewards_text
- requirements_text
- created_at
- updated_at
-- Additional columns will be added based on wiki data structure
```

#### Crafting Relationships Table (Many-to-Many) (Preliminary)
```sql
-- This is a CONCEPTUAL example - actual schema TBD after wiki scrape
- id (primary key)
- recipe_item_id (foreign key to items)
- component_item_id (foreign key to items)
- quantity
-- Additional columns will be added based on wiki data structure
```

#### Quest Item Relationships Table (Preliminary)
```sql
-- This is a CONCEPTUAL example - actual schema TBD after wiki scrape
- id (primary key)
- quest_id (foreign key)
- item_id (foreign key)
- relationship_type (required/reward)
-- Additional columns will be added based on wiki data structure
```

#### Icon Locations Table (Preliminary)
```sql
-- This is a CONCEPTUAL example - actual schema TBD after wiki scrape
- id (primary key)
- item_id (foreign key)
- location_name
- spawn_details
-- Additional columns will be added based on wiki data structure
```

---

## User Experience

### Cookie-Based State Management

#### Tracked Progress
- Checked quests (stored as array of quest IDs)
- Checked expeditions (stored as array of expedition IDs)
- Search history (recent searches)
- Preferred filters/settings
- Last visited items

#### Cookie Structure (Example)
```json
{
  "completedQuests": [1, 5, 12, 45],
  "completedExpeditions": [2, 8],
  "searchHistory": ["Arc Weapon", "Iron Ore", "Main Quest 1"],
  "lastVisited": [
    {"type": "item", "id": 123, "timestamp": "2025-11-04T06:05:51Z"}
  ]
}
```

#### Privacy Considerations
- No server-side storage of user progress
- No IP tracking or analytics (unless future scope approved)
- Clear cookies option in settings
- Data export option (download cookie data as JSON)

### Responsive Design Requirements

#### Mobile (< 768px)
- Stacked layout for item relationships (components above, uses below)
- Hamburger menu for navigation
- Touch-optimized checkboxes
- Simplified search interface
- Collapsible detail sections

#### Tablet (768px - 1024px)
- Two-column layout where appropriate
- Optimized spacing for touch targets
- Side-by-side quest progression

#### Desktop (> 1024px)
- Three-column layout for item visualization
- Expanded search with filters
- Hover states and tooltips
- Keyboard navigation support

---

## Future Scope

### Phase 2 Features (Post-Launch)
1. **Patch Update Notifications**
   - Track game version updates
   - Highlight new/changed items
   - Changelog display

2. **Analytics & Trending**
   - Most searched items
   - Popular quests
   - Commonly crafted items
   - Regional popularity (if user base grows)

3. **"Commonly Found At" Enhancements**
   - Interactive map integration
   - Coordinates display
   - Screenshots of locations
   - Community-submitted spawn data

4. **Advanced Filtering**
   - Filter quests by difficulty, region, NPC
   - Filter items by rarity, type, source
   - Filter expeditions by difficulty, time to complete

5. **Enhanced Visualization**
   - Interactive crafting tree diagrams
   - Quest dependency graphs
   - Item progression paths

6. **Community Features** (Requires careful consideration)
   - User-submitted tips/notes (moderated)
   - Build sharing (item loadouts)
   - Quest guides

7. **Export/Import Progress**
   - Export cookie data to file
   - Import progress from file (device migration)

8. **Dark Mode**
   - Theme toggle
   - Persistent preference

---

## Development Roadmap

### Phase 0: Planning & Setup (Current)
- [x] Requirements gathering
- [x] Project overview documentation
- [x] Finalize tech stack decisions
- [x] Set up development environment
- [x] Create GitHub repository structure

### Phase 1: Foundation (MVP)
#### Backend Development
- [x] Set up Python project structure (FastAPI)
- [x] **Perform initial wiki scrape to analyze data structure**
- [ ] Scrape sample detail pages for complete field discovery
- [ ] **Design PostgreSQL schema based on actual wiki data**
- [ ] Create database migration system
- [ ] Build RESTful API endpoints:
  - GET /items
  - GET /items/:id
  - GET /quests
  - GET /quests/:id
  - GET /expeditions
  - GET /expeditions/:id
  - GET /search?q=

#### Frontend Development
- [ ] Set up React project structure
- [ ] Implement routing
- [ ] Create cookie management utility
- [ ] Build core components:
  - Search bar
  - Item detail page
  - Quest list
  - Expedition list
  - Item relationship visualization
- [ ] Implement responsive CSS/styling

#### Data Scraping
- [ ] **Build initial scraper to analyze wiki structure**
- [ ] **Document scraped data fields and structure**
- [ ] Build production scraper scripts for https://arcraiders.wiki/
- [ ] Create manual review interface/workflow
- [ ] Initial data population

### Phase 2: Testing & Refinement
- [ ] Cross-browser testing
- [ ] Mobile device testing
- [ ] Performance optimization
- [ ] Search functionality tuning
- [ ] Bug fixes and UX improvements

### Phase 3: Deployment
- [ ] AWS setup (EC2, RDS)
- [ ] Domain and SSL configuration
- [ ] CI/CD pipeline
- [ ] Production deployment
- [ ] Monitoring and logging setup

### Phase 4: Post-Launch
- [ ] User feedback collection
- [ ] Iterative improvements
- [ ] Future scope feature prioritization
- [ ] Regular data updates with game patches

---

## Appendix

### Key Design Principles
1. **Simplicity First:** No unnecessary complexity
2. **Data Quality:** Manual review ensures accuracy
3. **User Privacy:** No tracking, no accounts, no data collection
4. **Mobile-First:** Optimize for smallest screens, enhance for larger
5. **Performance:** Fast load times, efficient queries
6. **Maintainability:** Clean code, clear documentation
7. **Schema Flexibility:** Design database to accommodate evolving wiki data structure

### Technology Decision Rationale

#### Why React?
- Component-based architecture fits interactive UI needs
- Large ecosystem for search, routing, state management
- Strong mobile development support
- Developer familiarity

#### Why Python + PostgreSQL?
- Python excellent for web scraping (BeautifulSoup, Scrapy)
- Flask/FastAPI provide clean RESTful API frameworks
- PostgreSQL handles complex relationships (crafting, quests)
- Strong data integrity with relational model
- Flexible schema evolution with migrations

#### Why AWS?
- Scalability as user base grows
- RDS for managed PostgreSQL
- EC2 flexibility for application hosting
- Cost-effective for small-to-medium projects

#### Why No User Accounts?
- Reduces complexity (no auth, password reset, etc.)
- Privacy-focused approach
- Faster development
- Cookies sufficient for progress tracking
- Aligns with single-player game context

---

## Contact & Contribution

**Maintainer:** LukeBrummett  
**Repository:** TBD  
**Documentation:** This file (`Project_Overview.md`)

For questions, suggestions, or contributions, please contact the maintainer or open an issue in the project repository.

---

## Potential Pivot Directions (Post-ardb.app Discovery)

Since ardb.app already provides comprehensive tracking and database features, potential unique value propositions:

### 1. AI-Powered Assistant
- Natural language queries: "I need more fabric" → suggests best sources/quests
- Item comparison and ranking: "Which assault rifle is best for X?"
- Build optimization based on playstyle
- Quest path recommendations

### 2. Complementary Features
- Different UX/design approach (may appeal to different users)
- Offline-first PWA capability
- Import/export from ardb.app
- Mobile-optimized experience
- Community tips and strategies layer

### 3. Developer/API Focus
- Public API for Arc Raiders data (if ardb.app doesn't have one)
- Developer tools for the Arc Raiders community
- Data aggregation from multiple sources
- Historical data tracking (patch changes, meta shifts)

### 4. Collaboration
- Reach out to ardb.app developers
- Contribute features/improvements to their platform
- Partner on complementary tools

---

**Last Updated:** 2025-11-04 (Evening - Post-ardb.app Discovery)  
**Version:** 1.2  
**Status:** Living Document (Project On Hold Pending Direction Decision)