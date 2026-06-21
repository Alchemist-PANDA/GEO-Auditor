from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.workspaces.models import Organization, Workspace, Project, Brand, Competitor, User
from app.modules.workspaces.schemas import WorkspaceCreate, ProjectCreate, BrandCreate, CompetitorCreate

class WorkspaceService:
    @staticmethod
    async def create_organization(db: AsyncSession, name: str) -> Organization:
        org = Organization(name=name)
        db.add(org)
        await db.flush()
        return org

    @staticmethod
    async def sync_user(db: AsyncSession, user_id: str, email: str, full_name: str, org_name: str) -> User:
        # Check if user already exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return user
            
        org = await WorkspaceService.create_organization(db, org_name)
        user = User(id=user_id, email=email, full_name=full_name, organization_id=org.id, role="org_admin")
        db.add(user)
        
        # Create default workspace
        workspace = Workspace(organization_id=org.id, name="Default Workspace", tier="pitch")
        db.add(workspace)
        await db.flush()
        
        # Create default project
        project = Project(workspace_id=workspace.id, name="General Brand tracking")
        db.add(project)
        await db.flush()
        
        return user

    @staticmethod
    async def create_workspace(db: AsyncSession, org_id: str, ws_in: WorkspaceCreate) -> Workspace:
        ws = Workspace(
            organization_id=org_id,
            name=ws_in.name,
            tier=ws_in.tier,
            prompt_limit=25 if ws_in.tier == "pitch" else 100
        )
        db.add(ws)
        await db.flush()
        return ws

    @staticmethod
    async def create_project(db: AsyncSession, project_in: ProjectCreate) -> Project:
        project = Project(workspace_id=project_in.workspace_id, name=project_in.name)
        db.add(project)
        await db.flush()
        return project

    @staticmethod
    async def create_brand(db: AsyncSession, brand_in: BrandCreate) -> Brand:
        brand = Brand(project_id=brand_in.project_id, name=brand_in.name, domain=brand_in.domain)
        db.add(brand)
        await db.flush()
        return brand

    @staticmethod
    async def create_competitor(db: AsyncSession, comp_in: CompetitorCreate) -> Competitor:
        comp = Competitor(brand_id=comp_in.brand_id, name=comp_in.name, domain=comp_in.domain)
        db.add(comp)
        await db.flush()
        return comp
        
    @staticmethod
    async def get_projects_by_workspace(db: AsyncSession, ws_id: str):
        res = await db.execute(select(Project).where(Project.workspace_id == ws_id))
        return res.scalars().all()
        
    @staticmethod
    async def get_brands_by_project(db: AsyncSession, project_id: str):
        res = await db.execute(select(Brand).where(Brand.project_id == project_id))
        return res.scalars().all()
