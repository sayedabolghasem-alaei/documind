import uuid
from datetime import datetime, timezone

from app.database.connection import get_connection


class ConversationRepository:

    @staticmethod
    def _get_current_time():
        return datetime.now(timezone.utc).isoformat()

    def create_conversation(self, title="New Chat"):

        conversation_id = str(uuid.uuid4())
        current_time = self._get_current_time()

        connection = get_connection()

        try:
            connection.execute(
                """
                INSERT INTO conversations (
                    id, title, created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, title, current_time, current_time)
            )

            connection.commit()

            return conversation_id

        finally:
            connection.close()

    def get_conversations(self):

        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    def get_conversation(self, conversation_id):

        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                WHERE id = ?
                """,
                (conversation_id,)
            ).fetchone()

            return dict(row) if row else None

        finally:
            connection.close()

    def save_message(self, conversation_id, role, content):

        current_time = self._get_current_time()

        connection = get_connection()

        try:
            connection.execute(
                """
                INSERT INTO messages (
                    conversation_id, role, content, created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, role, content, current_time)
            )

            connection.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                """,
                (current_time, conversation_id)
            )

            connection.commit()

        finally:
            connection.close()

    def get_messages(self, conversation_id):

        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT id, conversation_id, role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,)
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    def rename_conversation(self, conversation_id, new_title):

        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                UPDATE conversations
                SET title = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    new_title,
                    self._get_current_time(),
                    conversation_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        finally:
            connection.close()

    def delete_conversation(self, conversation_id):

        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                DELETE FROM conversations
                WHERE id = ?
                """,
                (conversation_id,)
            )

            connection.commit()

            return cursor.rowcount > 0

        finally:
            connection.close()

    def add_document(
        self,
        conversation_id: str,
        document_id: str,
        filename: str,
        stored_filename: str
    ) -> None:

        connection = get_connection()

        try:
            connection.execute(
                """
                INSERT INTO conversation_documents (
                    conversation_id,
                    document_id,
                    filename,
                    stored_filename,
                    uploaded_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    document_id,
                    filename,
                    stored_filename,
                    self._get_current_time()
                )
            )

            connection.commit()

        finally:
            connection.close()