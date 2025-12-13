# OpenAg-DB Frontend

This directory contains the frontend application for OpenAg-DB, built with Vite + React + TypeScript.

## ✨ Features

- **Mock Data**: Currently displays hardcoded equipment data for demonstration
- **Equipment Browser**: View tractors, combines, and implements
- **Search & Filter**: Search by name/description and filter by category
- **Statistics Dashboard**: Shows count of equipment by type
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Deployment

The frontend is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

**Live Site**: https://adam133.github.io/equipment-testing/

The deployment workflow (`.github/workflows/deploy-frontend.yml`) automatically:
1. Builds the React application
2. Uploads the build artifacts
3. Deploys to GitHub Pages

## 🛠️ Development

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd src/frontend
npm install
```

### Development Server

```bash
npm run dev
```

This will start the development server at http://localhost:5173

### Build

```bash
npm run build
```

This creates a production build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 📁 Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   └── EquipmentCard.tsx
│   ├── lib/              # Utilities and mock data
│   │   └── mockApi.ts    # Mock backend responses
│   ├── App.tsx           # Main app component
│   ├── App.css           # Styles
│   ├── main.tsx          # Entry point
│   └── vite-env.d.ts     # TypeScript declarations
├── dist/                 # Build output (not committed)
├── index.html            # HTML template
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
└── vite.config.ts        # Vite configuration
```

## 🎨 Mock Data

The frontend currently uses mock data defined in `src/lib/mockApi.ts`. This includes:

- **5 Tractors**: John Deere, Case IH, New Holland, Kubota models
- **3 Combines**: John Deere, Case IH, New Holland models
- **3 Implements**: Planter, ripper, and disk implements

Mock API functions simulate network delays (300ms) to mimic real API behavior.

## 🔧 Configuration

### Base Path

The application is configured to run at `/equipment-testing/` path for GitHub Pages deployment. This is set in `vite.config.ts`:

```typescript
export default defineConfig({
  base: '/equipment-testing/',
})
```

For local development or different deployment targets, update this value.

## 🚧 Future Enhancements

- [ ] Connect to real FastAPI backend
- [ ] Add detailed equipment view pages
- [ ] Implement contribution form
- [ ] Add equipment comparison feature
- [ ] Integrate authentication for contributions
- [ ] Add data visualization charts
- [ ] Implement advanced filtering options

## 📝 Notes

- The application uses TypeScript for type safety
- Mock data simulates the expected API response structure
- All equipment follows the Pydantic models defined in `src/core/models.py`
