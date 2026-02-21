# Tray Bien v3 - React + FastAPI

Modern web application for extracting board game component data from PDF rulebooks using AI.

## Architecture

- **Backend**: FastAPI (Python) on port 8000
- **Frontend**: Vite + React + TypeScript on port 5173
- **AI Providers**: Gemini, Claude, OpenAI, Ollama (local)
- **Styling**: Tailwind CSS

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or pnpm

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Configure API keys** (optional - can also be entered in UI):

```bash
cp .env.example .env
# Edit .env and add your API keys
```

**Start backend server**:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Frontend Setup

```bash
cd frontend
npm install
```

**Start frontend dev server**:

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

The Vite dev server automatically proxies `/api/*` requests to the backend at `http://localhost:8000`.

## Phase 1 Features

✅ **Implemented**:
- PDF upload from browser
- AI component extraction (Gemini, Claude, OpenAI, Ollama)
- Component display grouped by type (player, shared, setup, board_and_rules)
- Game metadata extraction (name, player count, factions/colors)
- Extraction notes and warnings
- Token usage tracking
- Error handling and user feedback
- Loading states with spinner

## Usage

1. **Start both servers** (backend on port 8000, frontend on port 5173)
2. **Open browser** to `http://localhost:5173`
3. **Upload a PDF** rulebook (from `game_Rules_EN/` directory or elsewhere)
4. **Select AI provider** (Gemini, Claude, OpenAI, or Ollama)
5. **Enter API key** (optional - leave blank to use backend settings)
6. **Click "Extract Components"**
7. **View results** - components grouped by category

## Project Structure

```
tray-bien/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # API routes and app initialization
│   │   ├── models.py        # Pydantic models
│   │   └── services/
│   │       ├── pdf_processor.py      # PDF text extraction
│   │       └── component_extractor.py # AI extraction logic
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── components/
│   │   │   ├── PDFUploader.tsx       # Upload form
│   │   │   └── ComponentDisplay.tsx  # Results display
│   │   ├── api/
│   │   │   └── client.ts    # API client functions
│   │   └── types/
│   │       └── index.ts     # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts       # Vite config with API proxy
├── src/                      # Original Streamlit app (unchanged)
└── app.py                    # Original Streamlit entry point
```

## API Endpoints

### `POST /api/extract`

Extract components from a PDF rulebook.

**Request** (multipart/form-data):
- `file`: PDF file
- `provider`: AI provider ('gemini', 'claude', 'openai', 'ollama')
- `api_key`: Optional API key

**Response**:
```json
{
  "success": true,
  "data": {
    "component_groups": [...],
    "game_name": "...",
    "player_count": {"min": 1, "max": 4},
    "factions_or_colors": [...],
    "extraction_notes": "...",
    "components": [...],
    "metadata": {
      "tokens_used": {...},
      "provider": "..."
    }
  }
}
```

### `GET /health`

Health check endpoint.

**Response**: `{"status": "ok"}`

## Known Limitations (Phase 1)

- No settings persistence (API key must be entered each time or configured in backend .env)
- No component editing after extraction
- No full wizard flow (box setup, layout preferences, etc.)
- No 3D preview
- No STL export
- Synchronous extraction (blocks during AI processing)
- No drag-and-drop file upload
- Basic error handling (no retry logic)

## Future Phases

- **Phase 2**: Settings API, persistent storage, component editing
- **Phase 3**: Full wizard flow (box setup, component inventory, layout preferences)
- **Phase 4**: 3D preview integration
- **Phase 5**: STL file generation and export
- **Phase 6**: Multi-user support, saved designs, design sharing

## Testing

**Manual testing checklist**:
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can upload PDF from browser
- [ ] Loading spinner shows during extraction
- [ ] Components display in grouped format
- [ ] Game metadata (name, player count) displays correctly
- [ ] Extraction notes display when present
- [ ] Token usage shows in footer
- [ ] Error messages display clearly
- [ ] Works with different AI providers
- [ ] No CORS errors in browser console

## Troubleshooting

### CORS errors

Check that FastAPI CORS middleware includes `http://localhost:5173` in allowed origins.

### API key errors

- For Gemini: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- For Claude: Get API key from [Anthropic Console](https://console.anthropic.com/)
- For OpenAI: Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- For Ollama: No API key needed, must be running locally on port 11434

### PDF parsing errors

- Ensure PDF is text-based (not scanned image)
- Check file size (limit is ~10MB by default)
- Try a different PDF to rule out corruption

### Import errors (backend)

Ensure all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

### TypeScript errors (frontend)

Ensure all dependencies are installed:
```bash
cd frontend
npm install
```

## License

Same as parent Tray Bien project.
