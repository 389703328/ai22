# FastAPI + Vue 3 Full-Stack Project

A modern full-stack application with FastAPI backend and Vue 3 frontend, featuring user management and AI chat functionality.

## 🏗️ Architecture

```
fastapi-vue3-project/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # Application Entry Point
│   │   ├── config.py       # Configuration
│   │   ├── models/         # Data Models
│   │   ├── api/v1/         # API Routes
│   │   ├── core/           # Core Configuration
│   │   └── services/       # Business Logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # Vue 3 Frontend
│   ├── src/
│   │   ├── components/   # Components
│   │   ├── views/        # Page Components
│   │   ├── router/       # Router Configuration
│   │   ├── stores/       # State Management
│   │   ├── services/     # API Services
│   │   └── main.js       # App Entry
│   ├── package.json
│   └── Dockerfile
├── nginx/                # Nginx Configuration
├── docker-compose.yml    # Docker Compose
└── README.md
```

## 🚀 Features

- **Backend**: FastAPI with RESTful API
- **Frontend**: Vue 3 with Composition API
- **State Management**: Pinia
- **Routing**: Vue Router
- **Styling**: Scoped CSS
- **API Integration**: Axios
- **Docker**: Multi-container setup with Nginx

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

## 🛠️ Development Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. 使用 Conda 虚拟环境：
```bash
conda activate myfastapi
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 启动服务（使用当前环境的解释器）：
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

1. Run all services:
```bash
docker-compose up --build
```

2. Access the application:
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000
   - Nginx: http://localhost:80

### Individual Services

#### Backend Docker
```bash
cd backend
docker build -t fastapi-backend .
docker run -p 8000:8000 fastapi-backend
```

#### Frontend Docker
```bash
cd frontend
docker build -t vue3-frontend .
docker run -p 5173:5173 vue3-frontend
```

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

#### Users
- `GET /api/v1/users/` - Get all users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{user_id}` - Get user by ID

#### AI Chat
- `POST /api/v1/ai/chat` - Chat with AI

## 🖥️ Application Features

### Frontend Pages

1. **Home** (`/`) - Welcome page with feature overview
2. **Users** (`/users`) - User management interface
3. **AI Chat** (`/ai`) - Interactive AI chat interface

### Key Features

- **User Management**: View and create users
- **AI Chat**: Real-time chat interface
- **Responsive Design**: Works on desktop and mobile
- **Modern Vue 3**: Composition API with `<script setup>`
- **State Management**: Pinia for reactive state
- **API Integration**: Axios with error handling

## 🧪 Development Notes

### Backend Development
- Auto-reload enabled with `--reload` flag
- CORS configured for frontend at localhost:5173 and localhost:3000
- PostgreSQL 数据库已配置

### Frontend Development
- Vite development server with HMR
- Proxy configured to forward `/api` requests to backend
- Component-based architecture

## 🔧 Configuration

### Backend Environment Variables
Create `.env` file in backend directory:
```env
DEBUG=true
APP_NAME="FastAPI Backend"
APP_VERSION="1.0.0"
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/ai22"
```

### Frontend Configuration
- Update `vite.config.js` for different proxy settings
- Modify `src/services/api.js` for different API base URLs

## 📝 Scripts

### Backend
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm run dev     # Development server
npm run build   # Production build
npm run preview # Preview production build
```

## 🚀 Deployment

### Production Build

1. Build frontend:
```bash
cd frontend
npm run build
```

2. Build and deploy with Docker:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.