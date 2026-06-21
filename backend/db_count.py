import asyncio
import os
import sys

# Ensure backend directory is on Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///e:/Profound-cloning/backend/geo_db.sqlite"

from sqlalchemy.future import select
from sqlalchemy import func
from app.core.database import AsyncSessionLocal
from app.modules.workspaces.models import User, Organization, Workspace, Project

async def print_counts():
    async with AsyncSessionLocal() as db:
        user_count = (await db.execute(select(func.count(User.id)))).scalar()
        org_count = (await db.execute(select(func.count(Organization.id)))).scalar()
        ws_count = (await db.execute(select(func.count(Workspace.id)))).scalar()
        proj_count = (await db.execute(select(func.count(Project.id)))).scalar()
        
        print(f"DATABASE COUNTS:")
        print(f"  Users: {user_count}")
        print(f"  Organizations: {org_count}")
        print(f"  Workspaces: {ws_count}")
        print(f"  Projects: {proj_count}")

if __name__ == "__main__":
    asyncio.run(print_counts())
