# Frontend to Backend Integration

This document describes how the frontend connects to the Unity Catalog backend.

## Architecture

The frontend is a React + TypeScript application built with Vite. It connects to the FastAPI backend which queries Unity Catalog Delta tables via DuckDB.

```
Frontend (React/TS) → FastAPI Backend → DuckDB → Unity Catalog Delta Tables
     Port 5173            Port 8000
```

## Configuration

### Backend API URL

The frontend uses an environment variable to configure the backend API URL:

- **Development**: `http://localhost:8000` (default)
- **Production**: Set via `VITE_API_URL` environment variable

Create a `.env` file in `src/frontend/` based on `.env.example`:

```bash
VITE_API_URL=http://localhost:8000
```

### CORS

The backend API is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:5173`

In development mode (when `ENVIRONMENT=development`), all origins are allowed.

## API Client

The frontend uses a dedicated API client (`src/frontend/src/lib/api.ts`) that provides typed functions for all backend endpoints:

- `getAllEquipment()` - Get all equipment
- `getEquipmentByCategory(category)` - Filter by category
- `getTractors()` - Get tractors
- `getCombines()` - Get combines
- `getImplements()` - Get implements
- `searchEquipment(query)` - Search equipment (client-side for now)
- `getStats()` - Get database statistics

All functions return Promises and throw errors on failure.

## Backend Endpoints

The backend provides the following REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Health check |
| `/equipment` | GET | List all equipment with filters |
| `/equipment/tractors` | GET | List tractors |
| `/equipment/combines` | GET | List combines |
| `/equipment/implements` | GET | List implements |
| `/equipment/{id}` | GET | Get equipment by ID |
| `/stats` | GET | Get database statistics |
| `/contributions` | POST | Submit corrections |
| `/docs` | GET | OpenAPI documentation |

## Running Locally

### 1. Start the Backend

```bash
# Install dependencies
pip install -e .

# Start the API server
python -m api.main
```

The API will start on `http://localhost:8000`.

### 2. Start the Frontend

```bash
cd src/frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will start on `http://localhost:5173`.

### 3. Test the Integration

Open your browser to `http://localhost:5173` to see the frontend connected to the backend.

## Unity Catalog Configuration

The backend requires Unity Catalog credentials to query data:

```bash
export DATABRICKS_TOKEN="your-token"
export DATABRICKS_HOST="your-workspace.databricks.com"
```

If these are not configured, the backend will return empty results but continue to work (graceful degradation).

## Data Flow

1. User opens the frontend in their browser
2. Frontend loads and calls `api.getAllEquipment()` and `api.getStats()`
3. API client makes HTTP requests to the backend (`http://localhost:8000`)
4. Backend receives requests and queries Unity Catalog via DuckDB
5. Backend returns JSON data to the frontend
6. Frontend displays the equipment data to the user

## Migration from Mock Data

The previous implementation used hardcoded mock data in `src/frontend/src/lib/mockApi.ts`. This has been replaced with the real API client that connects to the backend.

**Changes:**
- ✅ Created `src/frontend/src/lib/api.ts` with real API client
- ✅ Updated `src/frontend/src/App.tsx` to use `api` instead of `mockApi`
- ✅ Backend endpoints now query Unity Catalog (with graceful fallback)
- ✅ Added environment variable support for API URL configuration
- ✅ Updated footer message to reflect real backend connection

**Preserved:**
- ✅ Mock API kept for testing purposes (`mockApi.ts` and `mockApi.test.ts`)
- ✅ All existing tests continue to pass
- ✅ Same TypeScript interfaces for equipment data

## Testing

### Backend Tests

```bash
python -m pytest tests/test_api.py -v
```

### Frontend Tests

```bash
cd src/frontend
npm test
```

### Manual Testing

1. Start both backend and frontend
2. Open browser to `http://localhost:5173`
3. Open browser console (F12)
4. Check that API calls are being made to `localhost:8000`
5. Verify that equipment data is displayed (or "No equipment found" if database is empty)

## Troubleshooting

### Frontend can't connect to backend

- Check that the backend is running on port 8000
- Verify CORS settings in `src/api/main.py`
- Check browser console for CORS errors

### Backend returns empty data

- This is expected if Unity Catalog is not configured
- Set `DATABRICKS_TOKEN` and `DATABRICKS_HOST` environment variables
- Verify Unity Catalog tables exist and contain data

### Port conflicts

- Backend uses port 8000 (configurable via uvicorn)
- Frontend uses port 5173 (configurable in `vite.config.ts`)

## Known Limitations and Future Improvements

### Performance Optimizations (Future Work)

The current implementation fetches data from Unity Catalog and performs some filtering in Python memory. This works well for small to medium datasets but could be optimized for larger datasets by:

1. **Push-down filtering to SQL**: Year, horsepower, tank capacity, and width filters should be added to the SQL queries rather than filtering in Python
2. **Server-side search**: The search functionality currently filters all equipment client-side; should be implemented as a backend endpoint with database-level text search
3. **Statistics caching**: Stats endpoint queries all tables on every request; could be cached or computed incrementally
4. **Manufacturer counting**: Currently returns 0; needs implementation to count unique manufacturers across all tables
5. **Last updated tracking**: Currently returns null; needs implementation to track and return the last update timestamp

These optimizations are documented for future enhancement but do not affect the core functionality of the frontend-backend integration.

## Production Deployment

For production deployment:

1. Build the frontend:
   ```bash
   cd src/frontend
   npm run build
   ```

2. Set the API URL environment variable:
   ```bash
   export VITE_API_URL=https://api.your-domain.com
   ```

3. Deploy the backend as a containerized service

4. Deploy the frontend static files to a CDN or static hosting service

5. Configure Unity Catalog credentials in the backend environment
