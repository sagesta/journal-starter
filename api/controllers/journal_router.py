import logging
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from api.repositories.postgres_repository import PostgresDB
from api.services import EntryService
import logging
logger = logging.getLogger(__name__)



router = APIRouter()

# TODO: Add authentication middleware
# TODO: Add request validation middleware
# TODO: Add rate limiting middleware
# TODO: Add API versioning
# TODO: Add response caching

async def get_entry_service() -> AsyncGenerator[EntryService, None]:

    async with PostgresDB() as db:
        yield EntryService(db)

@router.post("/entries/")
async def create_entry(request: Request, entry: dict, entry_service: EntryService = Depends(get_entry_service)):

    entry_data = {
        k: v for k, v in entry.items()
        if k not in ['id', 'created_at', 'updated_at']
    }
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        try:
            enriched_entry = await entry_service.create_entry(entry_data)
            await entry_service.db.create_entry(enriched_entry)
  
        except HTTPException as e:
          
            if e.status_code == 409:
                raise HTTPException(
                    status_code=409, detail="You already have an entry for today."
                )
            raise e
    return JSONResponse(content={"detail": "Entry created successfully"}, status_code=201)

# TODO: Implement GET /entries endpoint to list all journal entries
# Example response: [{"id": "123", "work": "...", "struggle": "...", "intention": "..."}]
@router.get("/entries")
async def get_all_entries(request: Request, entry_service: EntryService = Depends(get_entry_service)):
    try:
        entries = await entry_service.get_all_entries()
        return {"entries": entries}
    except Exception as e:
        logger.error(f"Error fetching entries: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/entries/{entry_id}")
async def get_entry(request: Request, entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    try:
        entry = await entry_service.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry
    except Exception as e:
        logger.error(f"Error fetching entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/entries/{entry_id}")
async def update_entry(request: Request, entry_id: str, entry_update: dict):
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.update_entry(entry_id, entry_update)
    if not result:
    
        raise HTTPException(status_code=404, detail="Entry not found")
  
    return result

# TODO: Implement DELETE /entries/{entry_id} endpoint to remove a specific entry
# Return 404 if entry not found
@router.delete("/entries/{entry_id}")
async def delete_entry(request: Request, entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    try:
        entry = await entry_service.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        await entry_service.delete_entry(entry_id)
        return {"message": "Entry deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/entries")
async def delete_all_entries(request: Request):
   
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        await entry_service.delete_all_entries()

    return {"detail": "All entries deleted"}