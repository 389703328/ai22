from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import shutil
from typing import Optional
import os
from datetime import datetime

router = APIRouter()

# 文件上传的根目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def get_upload_path(upload_type: str) -> Path:
    """获取特定类型的上传目录"""
    path = UPLOAD_DIR / upload_type
    path.mkdir(exist_ok=True)
    return path


def save_uploaded_file(file: UploadFile, upload_type: str) -> tuple[str, str]:
    """
    保存上传的文件
    返回: (文件路径, 原始文件名)
    """
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    unique_filename = f"{timestamp}_{file.filename}"
    
    upload_path = get_upload_path(upload_type)
    file_path = upload_path / unique_filename
    
    # 保存文件
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 返回相对路径和原始文件名
    relative_path = str(file_path.relative_to(UPLOAD_DIR))
    return relative_path, file.filename


@router.post("/upload/knowledge")
async def upload_knowledge_file(
    file: UploadFile = File(...),
    expert_id: int = Form(...)
):
    """上传知识库文件"""
    try:
        file_path, original_filename = save_uploaded_file(file, f"knowledge/expert_{expert_id}")
        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "file_name": original_filename,
                "size": file.size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/upload/skill")
async def upload_skill_file(
    file: UploadFile = File(...),
    expert_id: int = Form(...)
):
    """上传技能文件"""
    try:
        file_path, original_filename = save_uploaded_file(file, f"skills/expert_{expert_id}")
        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "file_name": original_filename,
                "size": file.size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/upload/knowledge-graph")
async def upload_knowledge_graph_file(
    file: UploadFile = File(...),
    expert_id: int = Form(...)
):
    """上传知识图谱文件"""
    try:
        file_path, original_filename = save_uploaded_file(file, f"knowledge_graphs/expert_{expert_id}")
        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "file_name": original_filename,
                "size": file.size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("/uploads/{file_path:path}")
async def download_file(file_path: str):
    """下载文件"""
    full_path = UPLOAD_DIR / file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return {"file_path": str(full_path)}
