"""
数据库迁移脚本 - 添加文件路径和API Key字段
运行此脚本以更新现有数据库结构
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量获取数据库连接URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai22")

# 将 psycopg 格式转换为 asyncpg 格式
if DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


async def migrate():
    """执行数据库迁移"""
    
    # 连接数据库
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("开始数据库迁移...")
        
        # 1. 为 expert_knowledge_items 表添加文件字段
        print("\n1. 更新 expert_knowledge_items 表...")
        await conn.execute("""
            ALTER TABLE expert_knowledge_items 
            ADD COLUMN IF NOT EXISTS file_path VARCHAR(500),
            ADD COLUMN IF NOT EXISTS file_name VARCHAR(200);
        """)
        print("✓ expert_knowledge_items 表更新成功")
        
        # 2. 为 expert_skill_items 表添加文件字段
        print("\n2. 更新 expert_skill_items 表...")
        await conn.execute("""
            ALTER TABLE expert_skill_items 
            ADD COLUMN IF NOT EXISTS file_path VARCHAR(500),
            ADD COLUMN IF NOT EXISTS file_name VARCHAR(200);
        """)
        print("✓ expert_skill_items 表更新成功")
        
        # 3. 为 expert_sub_agents 表添加 api_key 字段
        print("\n3. 更新 expert_sub_agents 表...")
        await conn.execute("""
            ALTER TABLE expert_sub_agents 
            ADD COLUMN IF NOT EXISTS api_key VARCHAR(500);
        """)
        print("✓ expert_sub_agents 表更新成功")
        
        # 4. 为 knowledge_graphs 表添加文件字段
        print("\n4. 更新 knowledge_graphs 表...")
        await conn.execute("""
            ALTER TABLE knowledge_graphs 
            ADD COLUMN IF NOT EXISTS file_path VARCHAR(500),
            ADD COLUMN IF NOT EXISTS file_name VARCHAR(200);
        """)
        print("✓ knowledge_graphs 表更新成功")
        
        print("\n" + "="*50)
        print("✅ 数据库迁移完成！")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    print("数据库迁移脚本")
    print("="*50)
    print(f"数据库: {DATABASE_URL}")
    print("="*50)
    
    asyncio.run(migrate())
