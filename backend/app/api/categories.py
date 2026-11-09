from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.core.errors import AICMSException
from backend.app.models.category import Category
from backend.app.models.metadata import DocumentMetadata
from backend.app.models.user import User
from backend.app.schemas.category import CategoryCreate, CategoryResponse
from backend.app.services.audit_service import record_audit_event

router = APIRouter(prefix="/categories", tags=["Taxonomy Management"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CategoryResponse]:
    """
    List all categories in the approved taxonomy along with associated document counts (AICMS-F-019).
    """
    stmt = (
        select(
            Category,
            func.count(DocumentMetadata.id).label("doc_count"),
        )
        .outerjoin(DocumentMetadata, DocumentMetadata.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for cat, doc_count in rows:
        items.append(
            CategoryResponse(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                created_at=cat.created_at,
                document_count=doc_count,
            )
        )
    return items


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    cat_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_roles("admin")),
) -> CategoryResponse:
    """
    Create a new approved taxonomy category (Admin-only, AICMS-F-019, TC-ADM-01).
    """
    stmt = select(Category).where(func.lower(Category.name) == cat_in.name.lower().strip())
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise AICMSException(
            code="CATEGORY_ALREADY_EXISTS",
            message=f"Category '{cat_in.name.strip()}' already exists in taxonomy.",
            status_code=409,
        )

    cat = Category(
        name=cat_in.name.strip(),
        description=cat_in.description.strip() if cat_in.description else None,
    )
    db.add(cat)
    await db.flush()

    await record_audit_event(
        db,
        event_type="TAXONOMY_CREATED",
        status="SUCCESS",
        username=admin_user.username,
        user_id=admin_user.id,
        details=f"Created taxonomy category '{cat.name}' (id={cat.id})",
    )
    await db.commit()
    await db.refresh(cat)

    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        created_at=cat.created_at,
        document_count=0,
    )


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_roles("admin")),
):
    """
    Delete a taxonomy category with referential integrity protection (Admin-only, AICMS-F-019, TC-ADM-01).
    Rejects deletion if category is currently assigned to any active documents.
    """
    cat = await db.get(Category, category_id)
    if not cat:
        raise AICMSException(
            code="NOT_FOUND",
            message=f"Category with id {category_id} not found.",
            status_code=404,
        )

    # Referential integrity check (TC-ADM-01)
    count_stmt = select(func.count(DocumentMetadata.id)).where(DocumentMetadata.category_id == category_id)
    doc_count = (await db.execute(count_stmt)).scalar() or 0
    if doc_count > 0:
        raise AICMSException(
            code="CATEGORY_IN_USE",
            message=f"Cannot delete category '{cat.name}' because {doc_count} document(s) are currently assigned to it.",
            status_code=409,
        )

    cat_name = cat.name
    await db.delete(cat)

    await record_audit_event(
        db,
        event_type="TAXONOMY_DELETED",
        status="SUCCESS",
        username=admin_user.username,
        user_id=admin_user.id,
        details=f"Deleted taxonomy category '{cat_name}' (id={category_id})",
    )
    await db.commit()

    return {"message": f"Taxonomy category '{cat_name}' successfully deleted."}
