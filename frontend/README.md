# Arc Raiders Interactive Wiki - Frontend

React frontend for the Arc Raiders Interactive Wiki, built with Vite and Tailwind CSS.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at http://localhost:3000

3. **Build for production:**
   ```bash
   npm run build
   ```

## Project Structure

```
frontend/
├── src/
│   ├── main.jsx             # Application entry point
│   ├── App.jsx              # Main App component with routing
│   ├── App.css              # App-specific styles
│   ├── index.css            # Global styles with Tailwind
│   ├── components/          # Reusable React components
│   ├── pages/               # Page components
│   ├── utils/               # Utility functions (cookies, API calls)
│   └── hooks/               # Custom React hooks
├── public/                  # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── postcss.config.js       # PostCSS configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **ESLint** - Code linting

## Next Steps

- [ ] Create component directory structure
- [ ] Build cookie management utility
- [ ] Implement search bar component
- [ ] Create item detail visualization component
- [ ] Build quest and expedition list components
- [ ] Implement responsive layouts
