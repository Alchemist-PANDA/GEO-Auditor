from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.agency.models import Agency, Client
from app.modules.agency.schemas import AgencyCreate, ClientCreate

class AgencyService:
    @staticmethod
    async def create_agency(db: AsyncSession, agency_in: AgencyCreate) -> Agency:
        agency = Agency(
            organization_id=agency_in.organization_id,
            white_label_domain=agency_in.white_label_domain,
            logo_url=agency_in.logo_url,
            custom_colors=agency_in.custom_colors
        )
        db.add(agency)
        await db.flush()
        return agency

    @staticmethod
    async def create_client(db: AsyncSession, client_in: ClientCreate) -> Client:
        client = Client(
            agency_id=client_in.agency_id,
            workspace_id=client_in.workspace_id,
            billing_status=client_in.billing_status
        )
        db.add(client)
        await db.flush()
        return client

    @staticmethod
    async def get_agency_by_org(db: AsyncSession, org_id: str) -> Agency:
        res = await db.execute(select(Agency).where(Agency.organization_id == org_id))
        agency = res.scalar_one_or_none()
        if not agency:
            # Create a mock agency for default visualization
            agency = Agency(
                organization_id=org_id,
                white_label_domain="custom-seo-domain.com",
                logo_url="https://cdn.screenshottocode.com/7hwEKkbGAVGqNQ13HsZP0.png"
            )
            db.add(agency)
            await db.flush()
        return agency

    @staticmethod
    async def get_clients_by_agency(db: AsyncSession, agency_id: str) -> list[Client]:
        res = await db.execute(select(Client).where(Client.agency_id == agency_id))
        return res.scalars().all()
