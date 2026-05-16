from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class FileService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_files(self, project_id: UUID):
        pass

    async def single_file(self, project_id: UUID, path: str):
        pass
