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

### Testing

```bash
# Run tests once
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

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
│   │   ├── EquipmentCard.tsx
│   │   └── EquipmentCard.test.tsx
│   ├── lib/              # Utilities and mock data
│   │   ├── mockApi.ts    # Mock backend responses
│   │   └── mockApi.test.ts
│   ├── test/             # Test setup
│   │   └── setup.ts
│   ├── App.tsx           # Main app component
│   ├── App.css           # Styles
│   ├── main.tsx          # Entry point
│   └── vite-env.d.ts     # TypeScript declarations
├── dist/                 # Build output (not committed)
├── index.html            # HTML template
├── package.json          # Dependencies
├── package-lock.json     # Locked dependencies
├── tsconfig.json         # TypeScript config
└── vite.config.ts        # Vite configuration
```

## 🧪 Testing

The frontend uses Vitest for unit testing with React Testing Library for component tests.

**Test Coverage:**
- Mock API functions (filtering, searching, statistics)
- EquipmentCard component rendering for all equipment types
- Type-specific fields (tractor, combine, implement)

**Running Tests:**
```bash
npm test              # Run all tests
npm run test:watch    # Watch mode for development
npm run test:coverage # Generate coverage report
```

**CI/CD:**
Frontend tests run automatically in GitHub Actions on every push and pull request.

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

### Development Server

The Vite dev server is configured to listen only on `localhost` to prevent browser security prompts:

```typescript
export default defineConfig({
  server: {
    host: 'localhost',
  },
})
```

This prevents modern browsers (Chrome 138+, Edge 144+) from showing a "local network access" permission popup. If you need to access the dev server from other devices on your network, you can temporarily change this to `host: '0.0.0.0'` or use the `--host` flag.

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
