# 文件上传和API Key功能使用指南

本次更新为AI22项目添加了以下功能：

## 🆕 新增功能

### 1. 知识库文件上传
- 支持在创建/编辑知识条目时上传文件
- 支持的文件格式：txt, md, pdf等
- 文件会保存在 `backend/uploads/knowledge/expert_{id}/` 目录

### 2. 技能库文件上传
- 支持在创建/编辑技能时上传文件
- 支持的文件格式：py, js, md等
- 文件会保存在 `backend/uploads/skills/expert_{id}/` 目录

### 3. 知识图谱文件上传
- 支持在创建/编辑知识图谱时上传文件
- 支持的文件格式：json, graphml等
- 文件会保存在 `backend/uploads/knowledge_graphs/expert_{id}/` 目录

### 4. 子智能体API Key配置
- 可为每个子智能体单独配置API Key（可选）
- 支持密码输入框，保护API Key安全

## 📦 安装步骤

### 1. 运行数据库迁移

首先需要更新数据库结构以支持新字段：

```bash
cd backend
python migrate_file_fields.py
```

迁移脚本会添加以下字段：
- `expert_knowledge_items`: `file_path`, `file_name`
- `expert_skill_items`: `file_path`, `file_name`
- `expert_sub_agents`: `api_key`
- `knowledge_graphs`: `file_path`, `file_name`

### 2. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端服务

```bash
cd frontend
npm run dev
```

## 🔧 使用方法

### 知识库文件上传

1. 进入专家详情页
2. 切换到"知识库"标签
3. 点击"新建条目"或"编辑"
4. 在表单中找到"文件上传"区域
5. 点击"选择文件"按钮上传文件
6. 填写其他必填字段后保存

### 技能库文件上传

1. 进入专家详情页
2. 切换到"Skills库"标签
3. 点击"新建技能"或"编辑"
4. 在表单中找到"文件上传"区域
5. 点击"选择文件"按钮上传文件
6. 填写其他必填字段后保存

### 知识图谱文件上传

1. 进入专家详情页
2. 切换到"知识图谱"标签
3. 点击"新建图谱"或"编辑"
4. 在表单中找到"文件上传"区域
5. 点击"选择文件"按钮上传文件
6. 填写其他必填字段后保存

### 子智能体API Key配置

1. 进入专家详情页
2. 切换到"子智能体"标签
3. 点击"新建智能体"或"编辑"
4. 在表单中找到"API Key（可选）"字段
5. 输入API Key（支持密码显示/隐藏）
6. 填写其他必填字段后保存

## 📁 文件存储结构

```
backend/
└── uploads/
    ├── knowledge/
    │   └── expert_{id}/
    │       └── {timestamp}_{filename}
    ├── skills/
    │   └── expert_{id}/
    │       └── {timestamp}_{filename}
    └── knowledge_graphs/
        └── expert_{id}/
            └── {timestamp}_{filename}
```

## 🔒 安全注意事项

1. **API Key安全**
   - API Key在数据库中以明文存储，建议后续实现加密
   - 前端使用密码输入框防止屏幕泄露
   - 不要在日志中记录API Key

2. **文件上传安全**
   - 当前版本限制每次上传1个文件
   - 建议添加文件大小限制（如10MB）
   - 建议添加文件类型白名单验证
   - 生产环境应配置专门的文件存储服务（如OSS）

## 🔄 API端点说明

### 文件上传API

#### 上传知识库文件
```
POST /api/v1/upload/knowledge
Content-Type: multipart/form-data

参数:
- file: 上传的文件
- expert_id: 专家ID

响应:
{
  "success": true,
  "data": {
    "file_path": "knowledge/expert_1/20260203_120000_example.txt",
    "file_name": "example.txt",
    "size": 1024
  }
}
```

#### 上传技能文件
```
POST /api/v1/upload/skill
Content-Type: multipart/form-data

参数:
- file: 上传的文件
- expert_id: 专家ID
```

#### 上传知识图谱文件
```
POST /api/v1/upload/knowledge-graph
Content-Type: multipart/form-data

参数:
- file: 上传的文件
- expert_id: 专家ID
```

### 数据模型变更

所有创建和更新API现在支持以下新字段：

#### 知识条目
```json
{
  "title": "标题",
  "content": "内容",
  "file_path": "knowledge/expert_1/file.txt",
  "file_name": "file.txt",
  "metadata": {},
  "enabled": true
}
```

#### 技能条目
```json
{
  "name": "技能名称",
  "description": "描述",
  "content": "内容",
  "file_path": "skills/expert_1/file.py",
  "file_name": "file.py",
  "category": "分类",
  "tags": [],
  "enabled": true
}
```

#### 知识图谱
```json
{
  "name": "图谱名称",
  "description": "描述",
  "graph_type": "general",
  "storage": "neo4j",
  "file_path": "knowledge_graphs/expert_1/graph.json",
  "file_name": "graph.json",
  "config": {}
}
```

#### 子智能体
```json
{
  "name": "智能体名称",
  "description": "描述",
  "prompt": "提示词",
  "api_key": "sk-xxx",
  "status": "active"
}
```

## 🚀 后续优化建议

1. **文件管理**
   - 添加文件删除功能
   - 添加文件预览功能
   - 实现文件版本管理
   - 添加文件大小和类型限制

2. **API Key管理**
   - 实现API Key加密存储
   - 添加API Key有效性验证
   - 支持多个API Key配置

3. **云存储集成**
   - 集成阿里云OSS/AWS S3
   - 实现CDN加速
   - 添加文件备份机制

4. **文件处理**
   - 自动提取文件内容
   - 支持文件内容索引
   - 实现文件内容搜索

## ❓ 常见问题

### Q: 文件上传失败怎么办？
A: 检查以下几点：
- 确保 `backend/uploads` 目录有写入权限
- 检查文件大小是否超限
- 查看后端日志了解详细错误信息

### Q: API Key会被泄露吗？
A: 当前实现中：
- 前端使用密码框显示
- 数据库明文存储（建议后续加密）
- 不会在日志中打印
- 建议定期更换API Key

### Q: 已上传的文件如何访问？
A: 目前上传的文件存储在服务器本地，可以通过 `file_path` 字段获取相对路径。后续可以实现文件下载API。

### Q: 能否批量上传文件？
A: 当前版本每次只能上传1个文件。如需批量上传，可以多次调用上传接口。

## 📞 技术支持

如有问题，请参考：
- 项目文档: [AGENTS.md](../AGENTS.md)
- 后端API文档: http://localhost:8000/docs
- GitHub Issues: [项目Issues页面]
