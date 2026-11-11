import asyncio
import json
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.core.security import get_password_hash
from backend.app.models.category import Category
from backend.app.models.document import Document
from backend.app.models.metadata import DocumentMetadata, DocumentVector
from backend.app.models.permission import DocumentPermission
from backend.app.models.user import User
from backend.app.services.ai_service import generate_embedding
from backend.app.services.auth_service import seed_initial_users

DEMO_DOCUMENTS = [
    {
        "title": "FastAPI and PostgreSQL Architecture Spec",
        "filename": "fastapi_pgvector_spec.pdf",
        "file_type": "pdf",
        "category": "Engineering",
        "confidence": 0.94,
        "content": (
            "Architecture design specification for the AI-Powered Content Management System (AICMS). "
            "The system uses FastAPI for high-throughput asynchronous REST API endpoints. "
            "Vector representations are stored directly in PostgreSQL using the pgvector extension. "
            "All similarity lookups compute cosine distance directly on 384-dimensional dense vectors."
        ),
        "keywords": ["fastapi", "postgresql", "pgvector", "architecture", "endpoints", "cosine distance"],
        "topics": ["Architecture", "Database", "Vector Search"],
        "owner_username": "regular_user",
        "is_private": False,
    },
    {
        "title": "Q3 Financial Performance and Revenue Report",
        "filename": "q3_financial_report.docx",
        "file_type": "docx",
        "category": "Finance",
        "confidence": 0.96,
        "content": (
            "Quarterly fiscal review and financial performance analysis. Total revenue exceeded initial budget "
            "estimates by twelve percent, driven by enterprise software licensing and cloud infrastructure optimizations. "
            "Operating expenses remained balanced across all accounting quarters, ensuring a solid fiscal surplus."
        ),
        "keywords": ["quarterly", "revenue", "budget", "financial", "accounting", "fiscal"],
        "topics": ["Finance", "Budget", "Revenue"],
        "owner_username": "regular_user",
        "is_private": False,
    },
    {
        "title": "Master Services Contract and Compliance Terms",
        "filename": "master_contract_legal.pdf",
        "file_type": "pdf",
        "category": "Legal",
        "confidence": 0.92,
        "content": (
            "Standard terms and conditions for commercial software licensing and services agreement. "
            "Includes comprehensive contractual liability clauses, intellectual property protection, regulatory data "
            "privacy compliance under GDPR, and formal dispute arbitration mechanisms."
        ),
        "keywords": ["contract", "agreement", "liability", "compliance", "intellectual property", "regulatory"],
        "topics": ["Legal", "Contracts", "Compliance"],
        "owner_username": "regular_user",
        "is_private": False,
    },
    {
        "title": "Employee Benefits and Workplace Leave Policy",
        "filename": "hr_benefits_policy.txt",
        "file_type": "txt",
        "category": "Human Resources",
        "confidence": 0.91,
        "content": (
            "Human resources operational guidelines outlining employee healthcare insurance coverage, parental leave policies, "
            "retirement 401k matching benefits, and annual performance review cycles for full-time staff personnel."
        ),
        "keywords": ["employee", "benefits", "leave policy", "personnel", "recruitment", "human resources"],
        "topics": ["HR", "Policy", "Benefits"],
        "owner_username": "regular_user",
        "is_private": False,
    },
    {
        "title": "Executive Strategic Acquisitions Memo (RESTRICTED)",
        "filename": "confidential_mna_memo.pdf",
        "file_type": "pdf",
        "category": "Finance",
        "confidence": 0.98,
        "content": (
            "CONFIDENTIAL: Board of Directors strategic M&A memo. Detailed evaluation of acquisition targets, "
            "enterprise valuation multiples, and proprietary deal structures strictly restricted to executive leadership."
        ),
        "keywords": ["confidential", "acquisitions", "valuation", "merger", "proprietary", "restricted"],
        "topics": ["Confidential", "Executive", "Finance"],
        "owner_username": "admin_user",
        "is_private": True,  # Accessible only to admin, invisible to regular_user in search
    },
]


async def seed_demo():
    print("Initializing demo database and seeding initial personas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_initial_users(session)

        # Retrieve user objects
        res = await session.execute(select(User))
        users = {u.username: u for u in res.scalars().all()}

        # Seed categories
        categories = ["Engineering", "Finance", "Legal", "Human Resources", "Operations", "General"]
        cat_map = {}
        for c in categories:
            c_res = await session.execute(select(Category).where(Category.name == c))
            cat_obj = c_res.scalar_one_or_none()
            if not cat_obj:
                cat_obj = Category(name=c, description=f"{c} documentation")
                session.add(cat_obj)
                await session.flush()
            cat_map[c] = cat_obj

        # Ingest demo documents
        for doc_def in DEMO_DOCUMENTS:
            owner = users[doc_def["owner_username"]]
            existing = await session.execute(select(Document).where(Document.title == doc_def["title"]))
            if existing.scalar_one_or_none():
                continue

            content_bytes = doc_def["content"].encode("utf-8")
            import hashlib
            file_hash = hashlib.sha256(content_bytes).hexdigest()
            storage_path = os.path.join("backend/storage/uploads", f"{file_hash}.{doc_def['file_type']}")
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            with open(storage_path, "wb") as f:
                f.write(content_bytes)

            doc = Document(
                title=doc_def["title"],
                original_filename=doc_def["filename"],
                file_type=doc_def["file_type"],
                file_size=len(content_bytes),
                file_hash=file_hash,
                storage_path=storage_path,
                status="COMPLETED",
                owner_id=owner.id,
            )
            session.add(doc)
            await session.flush()

            # Assign owner permissions
            perm = DocumentPermission(
                document_id=doc.id,
                user_id=owner.id,
                can_read=True,
                can_edit=True,
                can_delete=True,
            )
            session.add(perm)

            # Metadata
            meta = DocumentMetadata(
                document_id=doc.id,
                extracted_title=doc_def["title"],
                extracted_author=owner.username,
                extracted_text=doc_def["content"],
                word_count=len(doc_def["content"].split()),
                character_count=len(doc_def["content"]),
                category_id=cat_map[doc_def["category"]].id,
                category_name=doc_def["category"],
                category_confidence=doc_def["confidence"],
                keywords=json.dumps(doc_def["keywords"]),
                topics=json.dumps(doc_def["topics"]),
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                model_version="v2",
            )
            session.add(meta)

            # Vector embedding
            vec = generate_embedding(doc_def["content"])
            doc_vec = DocumentVector(
                document_id=doc.id,
                chunk_index=0,
                chunk_text=doc_def["content"],
                embedding=vec,
            )
            session.add(doc_vec)
            print(f"Seeded document: '{doc.title}' ({doc_def['category']}) - Owner: {owner.username}")

        await session.commit()
    print("Demo seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_demo())
