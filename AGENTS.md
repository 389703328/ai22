# AGENTS.md - Development Guidelines for AI22 Project

This document provides essential information for AI agents working on this FastAPI + Vue 3 full-stack application.

## 🏗️ Project Structure

```
ai22/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── config.py       # Configuration management
│   │   ├── models/         # Pydantic models
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Core utilities (database, security)
│   │   ├── services/       # Business logic
│   │   └── db/             # Database models
│   ├── requirements.txt    # Python dependencies
│   └── pyproject.toml      # Project metadata
├── frontend/               # Vue 3 Frontend
│   ├── src/
│   │   ├── views/          # Page components
│   │   ├── stores/         # Pinia state management
│   │   ├── services/       # API services
│   │   ├── styles/         # Global CSS (modern design system)
│   │   └── router/         # Vue Router config
│   ├── package.json       # NPM dependencies
│   └── vite.config.js      # Vite build config
├── nginx/                  # Nginx configuration
└── docker-compose.yml      # Multi-container setup
```

## 🚀 Development Commands

### Backend Commands
```bash
# Navigate to backend
cd backend

# Start development server (recommended)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
pip install -r requirements.txt
```

### Frontend Commands
```bash
# Navigate to frontend
cd frontend

# Start development server (default port 5180)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install dependencies
npm install
```

### Docker Commands
```bash
# Start all services
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service_name]
```

## 🧪 Testing

**Note**: No testing framework is currently configured. When adding tests:

- For backend: Add `pytest` to requirements.txt and create test files in `backend/tests/`
- For frontend: Add testing setup to package.json (Jest/Vitest recommended)

### Running Single Tests (when implemented)
```bash
# Backend (pytest)
pytest tests/test_specific.py::test_function_name -v

# Frontend (Jest/Vitest)
npm test -- --testNamePattern="specific test"
```

## 📝 Code Style Guidelines

### Backend (Python/FastAPI)

#### Import Organization
```python
# Standard library imports first
import os
from typing import List, Optional

# Third-party imports second
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Local imports last
from app.models.user import UserResponse
from app.core.database import get_db
```

#### Naming Conventions
- **Files**: `snake_case.py` (e.g., `user_service.py`)
- **Classes**: `PascalCase` (e.g., `UserService`, `UserResponse`)
- **Functions/Variables**: `snake_case` (e.g., `get_users()`, `user_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)

#### Type Hints
- **Required**: All function parameters and return values must have type hints
- **Use Pydantic models** for request/response validation
- **Examples**:
```python
async def get_user(user_id: int) -> UserResponse:
    return UserResponse(id=user_id, username="test", email="test@example.com")

def create_user(user: UserCreate) -> UserResponse:
    # Implementation
```

#### Error Handling
- Use FastAPI's `HTTPException` for API errors
- Always include status codes and descriptive messages
- Example:
```python
from fastapi import HTTPException

if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

#### Database
- Use SQLAlchemy with async support
- Models in `app/db/models.py`
- Use dependency injection for database sessions
- Pydantic models in `app/models/` for API contracts

### Frontend (Vue 3)

#### Vue Component Structure
```vue
<template>
  <!-- Template content -->
</template>

<script>
// Use Composition API with <script setup> when possible
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user.js'

export default {
  name: 'ComponentName',
  setup() {
    // Reactive state and methods
    return {
      // Expose to template
    }
  }
}
</script>

<style scoped>
/* Component-specific styles */
</style>
```

#### Import Organization
```javascript
// Vue imports first
import { ref, computed, onMounted } from 'vue'

// External libraries second
import axios from 'axios'

// Local imports last
import { useUserStore } from '../stores/user.js'
import api from '../services/api.js'
```

#### Naming Conventions
- **Components**: `PascalCase.vue` (e.g., `UserProfile.vue`)
- **Files**: `kebab-case.js` for utilities, `PascalCase.vue` for components
- **Variables/Functions**: `camelCase` (e.g., `userName`, `fetchUsers()`)
- **CSS Classes**: `kebab-case` (e.g., `user-card`, `loading-spinner`)

#### State Management
- Use Pinia for state management
- Stores in `src/stores/`
- Follow pattern: `use[Feature]Store()` (e.g., `useUserStore()`)
- Example:
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const users = ref([])
  const loading = ref(false)
  
  const fetchUsers = async () => {
    loading.value = true
    try {
      // API call
    } finally {
      loading.value = false
    }
  }
  
  return { users, loading, fetchUsers }
})
```

#### API Integration
- Use centralized API service in `src/services/api.js`
- Axios instance with proper timeout and headers
- Error handling in store methods, not components
- Example:
```javascript
// services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

export default api

// In store
import api from '../services/api.js'

const fetchUsers = async () => {
  const response = await api.get('/users')
  users.value = response.data
}
```

## 🎨 Styling Guidelines

### CSS Architecture
- **Global styles**: `src/styles/global.css` (modern design system)
- **Component styles**: Scoped CSS in each component
- **CSS Variables**: Use the established design system variables

### Design System Variables (from global.css)
```css
/* Colors */
--primary: #667eea
--secondary: #764ba2
--success: #10b981
--warning: #f59e0b
--danger: #ef4444
--info: #3b82f6

/* Spacing */
--spacing-xs: 4px
--spacing-sm: 8px
--spacing-md: 12px
--spacing-lg: 16px
--spacing-xl: 24px

/* Typography */
--font-size-sm: 14px
--font-size-base: 16px
--font-size-lg: 18px
--font-size-xl: 20px

/* Transitions */
--transition-base: 300ms
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
```

### Animation Guidelines
- Use CSS animations from global.css (fadeIn, slideUp, etc.)
- Keep animations subtle and purposeful
- Respect `prefers-reduced-motion` for accessibility

## 🔧 Environment Configuration

### Backend Environment Variables
Create `.env` in backend directory:
```env
DEBUG=true
APP_NAME="FastAPI Backend"
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/ai22"
```

### Frontend Configuration
- Vite dev server: `http://localhost:5180`
- API proxy: `/api` → `http://localhost:8000`
- Update `vite.config.js` for different proxy settings

### 2026-02-03 (Latest)
- **Major Feature Update**: 完整的用户管理和权限控制系统
  - **数据库重构**: 添加 `users`, `mcp_tools`, `model_configs`, `knowledge_graphs` 表
  - **权限系统**: 实现多对多权限关联表（用户-专家、用户-子智能体、用户-MCP、用户-技能、用户-知识）
  - **后端API**: 
    - `/api/v1/users` - 完整的用户CRUD和权限管理
    - `/api/v1/mcp` - MCP工具管理
    - `/api/v1/models` - 模型配置管理
    - `/api/v1/experts/{id}/knowledge-graphs` - 知识图谱管理
  - **前端页面**:
    - `UserManagement.vue` - 用户管理（表格视图、权限配置）
    - `MCPManagement.vue` - MCP工具管理
    - `ModelManagement.vue` - 模型配置管理
    - 专家详情页新增"知识图谱"标签页
    - 专家列表新增"创建人"列
  - **数据库驱动**: 从 `psycopg` 切换至 `asyncpg`，全异步查询优化

### 2026-02-03 (Earlier)
- **Frontend Refactor**: Standardized `AIExpertManagement.vue` and `AIExpertDetail.vue` to use **Element Plus** components (Tabs, Dialogs, Tables, Forms) instead of custom CSS components, ensuring consistency with the project's frontend stack requirements.
- **Style Cleanup**: Removed redundant custom CSS for modals, tabs, and form elements in favor of framework-provided styles.
- **Improved UX**: Added loading states (v-loading), improved form validation visual cues, and standardized status tags using Element Plus.

## 📊 Database

- **Primary**: PostgreSQL (configured in docker-compose.yml)
- **ORM**: SQLAlchemy 2.0 with async support
- **Migration**: Manual schema updates (consider Alembic for production)
- **Connection**: Async connection pool configured in `core/database.py`

## 🔐 Security

- **Backend**: CORS configured for localhost:5173, 3000
- **Authentication**: JWT tokens (implement when needed)
- **Validation**: Pydantic models for all API inputs
- **Password Hashing**: bcrypt via passlib

## 🌐 API Design

### RESTful Conventions
- **Endpoints**: `/api/v1/{resource}`
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: 200 (success), 201 (created), 400 (bad request), 404 (not found), 500 (server error)
- **Responses**: JSON with consistent structure

### Response Format
```python
# Success response
{"id": 1, "username": "test", "email": "test@example.com"}

# Error response (FastAPI default)
{"detail": "User not found"}
```

## 🚀 Performance Guidelines

### Frontend
- Use Vue 3 Composition API for better reactivity
- Implement lazy loading for routes if needed
- Use computed properties for derived state
- Debounce search inputs and API calls

### Backend
- Use async/await for all I/O operations
- Database queries should be async
- Implement proper connection pooling
- Use pydantic for fast serialization/deserialization

## 📱 Responsive Design

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px  
- Desktop: > 1024px

### Guidelines
- Mobile-first approach
- Use CSS Grid and Flexbox for layouts
- Test across all viewport sizes
- Touch-friendly tap targets (minimum 44px)

## 🔄 Development Workflow

1. **Backend First**: Create API endpoints and models
2. **Frontend Integration**: Build UI components and integrate with API
3. **State Management**: Implement Pinia stores for complex state
4. **Styling**: Apply design system and ensure responsiveness
5. **Testing**: Test both API endpoints and UI interactions
6. **Docker**: Verify docker-compose setup works correctly

## 🐛 Common Issues & Solutions

### CORS Issues
- Ensure backend CORS includes frontend URL
- Check proxy configuration in vite.config.js

### Database Connection
- Verify PostgreSQL is running in docker-compose
- Check connection string in environment variables

### Import Errors
- Use correct relative imports in Python modules
- Include `.js` extensions in JavaScript imports

### Port Conflicts
- Backend: 8000, Frontend: 5180, Nginx: 80, PostgreSQL: 5432
- Adjust if ports are in use

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Element Plus UI](https://element-plus.org/)