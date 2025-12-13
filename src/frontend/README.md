# OpenAg-DB Frontend

This directory contains the frontend application for OpenAg-DB, built with Vite + React + Shadcn UI.

## Setup

The frontend is a standalone React application that will be deployed to GitHub Pages.

### Prerequisites

- Node.js 18+ and npm
- The OpenAg-DB API running (or configured endpoint)

### Installation

```bash
cd src/frontend
npm install
```

### Development

```bash
npm run dev
```

This will start the development server at http://localhost:5173

### Build

```bash
npm run build
```

This creates a production build in the `dist/` directory.

### Deployment

The frontend is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch.

## Structure

```
frontend/
├── public/          # Static assets
├── src/
│   ├── components/  # React components
│   ├── lib/         # Utilities and API client
│   ├── pages/       # Page components
│   ├── App.tsx      # Main app component
│   └── main.tsx     # Entry point
├── index.html       # HTML template
├── package.json     # Node dependencies
├── tsconfig.json    # TypeScript config
└── vite.config.ts   # Vite configuration
```

## Features

- Search and filter agricultural equipment
- View detailed equipment specifications
- Submit corrections and contributions
- Browse by category (Tractors, Combines, Implements)
- Responsive design with Tailwind CSS

## TODO

- [ ] Initialize Vite project
- [ ] Install React and dependencies
- [ ] Add Shadcn UI components
- [ ] Create search interface
- [ ] Implement API integration
- [ ] Add contribution form
- [ ] Configure GitHub Pages deployment
