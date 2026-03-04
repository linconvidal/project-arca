"""
Database module for Arca

This module provides a SQLite-based ephemeral database for indexing and caching
content from Markdown and YAML files. The database is not the source of truth;
it can be recreated at any time from the content files.
"""
import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ArcaDatabase:
    """
    SQLite database for Arca content indexing and caching.
    """
    
    def __init__(self, db_path: Union[str, Path] = ':memory:'):
        """
        Initialize the database.
        
        Args:
            db_path: Path to the SQLite database file, or ':memory:' for in-memory database
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Enable JSON support
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self._create_tables()
        
        logger.info(f"Initialized database at {self.db_path}")
    
    def _create_tables(self):
        """Create the necessary tables for content storage."""
        with self._transaction() as cursor:
            # Main documents table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                file_path TEXT UNIQUE NOT NULL,
                content_type TEXT NOT NULL,
                title TEXT,
                content_markdown TEXT,
                content_html TEXT,
                metadata TEXT,  -- JSON string of all metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Tags table for many-to-many relationship
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            ''')
            
            # Document-tag relationship table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id TEXT,
                tag_id INTEGER,
                PRIMARY KEY (document_id, tag_id),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)')
            
            # Create virtual table for full-text search
            cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                id, title, content_markdown,
                content='documents',
                content_rowid='rowid'
            )
            ''')
            
            # Create triggers to keep FTS index updated
            cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(id, title, content_markdown)
                VALUES (new.id, new.title, new.content_markdown);
            END
            ''')
            
            cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, id, title, content_markdown)
                VALUES('delete', old.id, old.title, old.content_markdown);
            END
            ''')
            
            cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, id, title, content_markdown)
                VALUES('delete', old.id, old.title, old.content_markdown);
                INSERT INTO documents_fts(id, title, content_markdown)
                VALUES (new.id, new.title, new.content_markdown);
            END
            ''')
    
    @contextmanager
    def _transaction(self):
        """Context manager for database transactions."""
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Database transaction error: {e}")
            raise
        finally:
            cursor.close()
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Closed database connection")
    
    def reset(self):
        """Reset the database by dropping and recreating all tables."""
        with self._transaction() as cursor:
            cursor.execute("DROP TABLE IF EXISTS document_tags")
            cursor.execute("DROP TABLE IF EXISTS tags")
            cursor.execute("DROP TABLE IF EXISTS documents_fts")
            cursor.execute("DROP TABLE IF EXISTS documents")
            
        self._create_tables()
        logger.info("Reset database to initial state")
    
    def upsert_document(self, 
                       document_id: str,
                       file_path: str,
                       content_type: str,
                       title: Optional[str],
                       content_markdown: str,
                       content_html: Optional[str],
                       metadata: Dict[str, Any],
                       tags: Optional[List[str]] = None) -> str:
        """
        Insert or update a document in the database.
        
        Args:
            document_id: Unique identifier for the document
            file_path: Path to the source file
            content_type: Type of content (e.g., 'project', 'note')
            title: Document title
            content_markdown: Markdown content
            content_html: HTML rendered from Markdown (optional)
            metadata: Dictionary of metadata
            tags: List of tags for the document
            
        Returns:
            str: The document ID
        """
        with self._transaction() as cursor:
            # Convert metadata to JSON
            metadata_json = json.dumps(metadata)
            
            # Check if document exists
            cursor.execute("SELECT id FROM documents WHERE id = ?", (document_id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing document
                cursor.execute('''
                UPDATE documents
                SET file_path = ?, content_type = ?, title = ?, 
                    content_markdown = ?, content_html = ?, metadata = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (file_path, content_type, title, content_markdown, 
                      content_html, metadata_json, document_id))
                logger.debug(f"Updated document: {document_id}")
            else:
                # Insert new document
                cursor.execute('''
                INSERT INTO documents (id, file_path, content_type, title, 
                                      content_markdown, content_html, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (document_id, file_path, content_type, title, 
                      content_markdown, content_html, metadata_json))
                logger.debug(f"Inserted new document: {document_id}")
            
            # Handle tags if provided
            if tags:
                # First, remove existing tags for this document
                cursor.execute("DELETE FROM document_tags WHERE document_id = ?", (document_id,))
                
                # Insert or get tags
                for tag_name in tags:
                    # Try to insert the tag (will fail if it already exists)
                    try:
                        cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                        tag_id = cursor.lastrowid
                    except sqlite3.IntegrityError:
                        # Tag already exists, get its ID
                        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                        tag_id = cursor.fetchone()[0]
                    
                    # Link tag to document
                    cursor.execute('''
                    INSERT INTO document_tags (document_id, tag_id)
                    VALUES (?, ?)
                    ''', (document_id, tag_id))
            
            return document_id
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the database.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            bool: True if a document was deleted, False otherwise
        """
        with self._transaction() as cursor:
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            deleted = cursor.rowcount > 0
            
            if deleted:
                logger.debug(f"Deleted document: {document_id}")
            else:
                logger.warning(f"Attempted to delete non-existent document: {document_id}")
            
            return deleted
    
    def delete_document_by_path(self, file_path: str) -> bool:
        """
        Delete a document from the database by its file path.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            bool: True if a document was deleted, False otherwise
        """
        with self._transaction() as cursor:
            cursor.execute("DELETE FROM documents WHERE file_path = ?", (str(file_path),))
            deleted = cursor.rowcount > 0
            
            if deleted:
                logger.debug(f"Deleted document with path: {file_path}")
            else:
                logger.warning(f"Attempted to delete non-existent document with path: {file_path}")
            
            return deleted
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            dict: Document data or None if not found
        """
        with self._transaction() as cursor:
            cursor.execute('''
            SELECT d.*, GROUP_CONCAT(t.name) as tag_list
            FROM documents d
            LEFT JOIN document_tags dt ON d.id = dt.document_id
            LEFT JOIN tags t ON dt.tag_id = t.id
            WHERE d.id = ?
            GROUP BY d.id
            ''', (document_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convert row to dict
            doc = dict(row)
            
            # Parse metadata JSON
            doc['metadata'] = json.loads(doc['metadata']) if doc['metadata'] else {}
            
            # Parse tags
            doc['tags'] = doc['tag_list'].split(',') if doc['tag_list'] else []
            del doc['tag_list']
            
            return doc
    
    def get_document_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its file path.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            dict: Document data or None if not found
        """
        with self._transaction() as cursor:
            cursor.execute('''
            SELECT d.*, GROUP_CONCAT(t.name) as tag_list
            FROM documents d
            LEFT JOIN document_tags dt ON d.id = dt.document_id
            LEFT JOIN tags t ON dt.tag_id = t.id
            WHERE d.file_path = ?
            GROUP BY d.id
            ''', (str(file_path),))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convert row to dict
            doc = dict(row)
            
            # Parse metadata JSON
            doc['metadata'] = json.loads(doc['metadata']) if doc['metadata'] else {}
            
            # Parse tags
            doc['tags'] = doc['tag_list'].split(',') if doc['tag_list'] else []
            del doc['tag_list']
            
            return doc
    
    def get_documents(self, 
                     content_type: Optional[str] = None,
                     tag: Optional[str] = None,
                     limit: int = 100,
                     offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get a list of documents, optionally filtered by content type or tag.
        
        Args:
            content_type: Filter by content type
            tag: Filter by tag
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            
        Returns:
            list: List of document dictionaries
        """
        query = '''
        SELECT d.*, GROUP_CONCAT(t.name) as tag_list
        FROM documents d
        LEFT JOIN document_tags dt ON d.id = dt.document_id
        LEFT JOIN tags t ON dt.tag_id = t.id
        '''
        
        params = []
        where_clauses = []
        
        if content_type:
            where_clauses.append("d.content_type = ?")
            params.append(content_type)
        
        if tag:
            where_clauses.append("t.name = ?")
            params.append(tag)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += '''
        GROUP BY d.id
        ORDER BY d.updated_at DESC
        LIMIT ? OFFSET ?
        '''
        
        params.extend([limit, offset])
        
        with self._transaction() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                doc = dict(row)
                
                # Parse metadata JSON
                doc['metadata'] = json.loads(doc['metadata']) if doc['metadata'] else {}
                
                # Parse tags
                doc['tags'] = doc['tag_list'].split(',') if doc['tag_list'] else []
                del doc['tag_list']
                
                documents.append(doc)
            
            return documents
    
    def get_content_types(self) -> List[str]:
        """
        Get a list of all content types in the database.
        
        Returns:
            list: List of content type strings
        """
        with self._transaction() as cursor:
            cursor.execute("SELECT DISTINCT content_type FROM documents")
            return [row[0] for row in cursor.fetchall()]
    
    def get_tags(self) -> List[str]:
        """
        Get a list of all tags in the database.
        
        Returns:
            list: List of tag strings
        """
        with self._transaction() as cursor:
            cursor.execute("SELECT name FROM tags ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search documents using full-text search.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            list: List of matching document dictionaries
        """
        with self._transaction() as cursor:
            # Use FTS5 to search
            cursor.execute('''
            SELECT d.*, GROUP_CONCAT(t.name) as tag_list, rank
            FROM documents_fts fts
            JOIN documents d ON fts.id = d.id
            LEFT JOIN document_tags dt ON d.id = dt.document_id
            LEFT JOIN tags t ON dt.tag_id = t.id
            WHERE documents_fts MATCH ?
            GROUP BY d.id
            ORDER BY rank
            LIMIT ?
            ''', (query, limit))
            
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                doc = dict(row)
                
                # Parse metadata JSON
                doc['metadata'] = json.loads(doc['metadata']) if doc['metadata'] else {}
                
                # Parse tags
                doc['tags'] = doc['tag_list'].split(',') if doc['tag_list'] else []
                del doc['tag_list']
                
                documents.append(doc)
            
            return documents
    
    def count_documents(self, content_type: Optional[str] = None) -> int:
        """
        Count the number of documents, optionally filtered by content type.
        
        Args:
            content_type: Filter by content type
            
        Returns:
            int: Number of documents
        """
        with self._transaction() as cursor:
            if content_type:
                cursor.execute("SELECT COUNT(*) FROM documents WHERE content_type = ?", (content_type,))
            else:
                cursor.execute("SELECT COUNT(*) FROM documents")
            
            return cursor.fetchone()[0] 