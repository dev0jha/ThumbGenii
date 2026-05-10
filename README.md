# ThumbGenii

## Backend (FastAPI)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env

# Run the server
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## Frontend (React + Vite)

```bash
cd Frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The frontend dev server runs at `http://localhost:5173` by default.
