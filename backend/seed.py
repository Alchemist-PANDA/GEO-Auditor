import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.modules.workspaces.models import Organization, User, Workspace, Project, Brand, Competitor
from app.modules.prompts.models import AIModel, Prompt
from app.modules.analysis.models import TopicCluster, Topic, Industry

async def main():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("Re-creating all database tables...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as db:
        print("Seeding initial mock data...")
        
        # 1. Organization & User
        org = Organization(name="Aether Digital")
        db.add(org)
        await db.flush()
        
        user = User(
            id="user_mock_12345", 
            email="alex@aether.com", 
            full_name="Alex Mercer", 
            organization_id=org.id, 
            role="org_admin"
        )
        db.add(user)
        
        # 2. Workspace & Project
        ws = Workspace(organization_id=org.id, name="Corporate Brand Monitor", tier="premium", prompt_limit=100)
        db.add(ws)
        await db.flush()
        
        project = Project(workspace_id=ws.id, name="US Credit Launch")
        db.add(project)
        await db.flush()
        
        # 3. Brand & Competitor
        brand = Brand(project_id=project.id, name="Rho", domain="rho.co")
        db.add(brand)
        await db.flush()
        
        comp1 = Competitor(brand_id=brand.id, name="Chase", domain="chase.com")
        comp2 = Competitor(brand_id=brand.id, name="American Express", domain="americanexpress.com")
        comp3 = Competitor(brand_id=brand.id, name="Brex", domain="brex.com")
        db.add_all([comp1, comp2, comp3])
        
        # 4. AI Models
        models = [
            AIModel(id="gpt-4o", name="GPT-4o", provider="OpenAI"),
            AIModel(id="claude-3-5-sonnet", name="Claude 3.5 Sonnet", provider="Anthropic"),
            AIModel(id="gemini-1.5-pro", name="Gemini 1.5 Pro", provider="Google"),
            AIModel(id="perplexity-sonar", name="Perplexity Sonar", provider="Perplexity")
        ]
        db.add_all(models)
        
        # 5. Prompts
        prompts = [
            Prompt(project_id=project.id, text="What is the best business credit card for startups?", locale="Global", tags=["competitive", "pricing"]),
            Prompt(project_id=project.id, text="Stripe alternative with no foreign transaction fees?", locale="Global", tags=["billing", "features"]),
            Prompt(project_id=project.id, text="How does Rho expense management compare to Brex?", locale="Global", tags=["features", "safety"])
        ]
        db.add_all(prompts)
        
        # 6. Industries & Topics
        ind = Industry(name="Fintech Software", description="Corporate cards, expense tracking, and invoicing.")
        db.add(ind)
        
        cluster = TopicCluster(name="Safety & Compliance", description="Security and regulatory measures.")
        db.add(cluster)
        await db.flush()
        
        topic = Topic(cluster_id=cluster.id, name="Encryption & Limits")
        db.add(topic)
        
        await db.commit()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
