"""Documentation manager for docless monorepo."""

import json
from dataclasses import dataclass
from datetime import datetime

from .db_manager import ContextDB


@dataclass
class Documentation:
    entity_type: str
    entity_id: str
    doc_type: str
    title: str
    content: str
    metadata: dict[str, str] | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocManager:
    """Manage documentation in database."""

    def __init__(self, db: ContextDB):
        self.db = db

    def add_doc(self, doc: Documentation) -> int:
        """Add documentation to database."""
        query = """
        INSERT INTO documentation (entity_type, entity_id, doc_type, title, content, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING id
        """
        metadata_json = json.dumps(doc.metadata) if doc.metadata else None

        result = self.db.conn.execute(
            query,
            [
                doc.entity_type,
                doc.entity_id,
                doc.doc_type,
                doc.title,
                doc.content,
                metadata_json,
            ],
        ).fetchone()

        return int(result[0]) if result else 0

    def get_docs(
        self,
        entity_type: str | None = None,
        entity_id: str | None = None,
        doc_type: str | None = None,
    ) -> list[Documentation]:
        """Get documentation by filters."""
        conditions = []
        params = []

        if entity_type:
            conditions.append("entity_type = ?")
            params.append(entity_type)
        if entity_id:
            conditions.append("entity_id = ?")
            params.append(entity_id)
        if doc_type:
            conditions.append("doc_type = ?")
            params.append(doc_type)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM documentation WHERE {where_clause} ORDER BY updated_at DESC"

        results = self.db.conn.execute(query, params).fetchall()

        docs = []
        for row in results:
            docs.append(
                Documentation(
                    id=row[0],
                    entity_type=row[1],
                    entity_id=row[2],
                    doc_type=row[3],
                    title=row[4],
                    content=row[5],
                    metadata=json.loads(row[6]) if row[6] else None,
                    created_at=row[7],
                    updated_at=row[8],
                )
            )

        return docs

    def update_doc(self, doc_id: int, content: str, title: str | None = None) -> bool:
        """Update documentation content."""
        if title:
            query = """
            UPDATE documentation
            SET content = ?, title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            params = [content, title, doc_id]
        else:
            query = """
            UPDATE documentation
            SET content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            params = [content, doc_id]

        result = self.db.conn.execute(query, params)
        return bool(result.rowcount > 0)

    def search_docs(self, query: str) -> list[Documentation]:
        """Search documentation content."""
        search_query = """
        SELECT * FROM documentation
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY updated_at DESC
        """
        pattern = f"%{query}%"
        results = self.db.conn.execute(search_query, [pattern, pattern]).fetchall()

        docs = []
        for row in results:
            docs.append(
                Documentation(
                    id=row[0],
                    entity_type=row[1],
                    entity_id=row[2],
                    doc_type=row[3],
                    title=row[4],
                    content=row[5],
                    metadata=json.loads(row[6]) if row[6] else None,
                    created_at=row[7],
                    updated_at=row[8],
                )
            )

        return docs

    def delete_doc(self, doc_id: int) -> bool:
        """Delete documentation."""
        query = "DELETE FROM documentation WHERE id = ?"
        result = self.db.conn.execute(query, [doc_id])
        return bool(result.rowcount > 0)
