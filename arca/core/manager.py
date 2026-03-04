"""
Content Manager for Arca

This module integrates the watcher, database, and parser components to provide
a unified interface for managing content in the Arca system.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Callable, Union

from arca.core.watcher import ContentWatcher
from arca.core.db import ArcaDatabase
from arca.core.parser import process_file, register_content_type, BaseDocumentMeta

logger = logging.getLogger(__name__)

class ContentManager:
    """
    Manages content in the Arca system, integrating file watching, parsing, and database storage.
    """
    
    def __init__(self, 
                 content_dir: Union[str, Path],
                 db_path: Union[str, Path] = ':memory:',
                 file_extensions: Set[str] = {'.md', '.yaml', '.yml'},
                 auto_start: bool = True):
        """
        Initialize the content manager.
        
        Args:
            content_dir: Path to the content directory
            db_path: Path to the SQLite database file, or ':memory:' for in-memory database
            file_extensions: Set of file extensions to monitor
            auto_start: Whether to automatically start watching for changes
        """
        self.content_dir = Path(content_dir)
        self.file_extensions = file_extensions
        
        # Initialize database
        logger.info(f"Initializing database at {db_path}")
        self.db = ArcaDatabase(db_path)
        
        # Initialize watcher
        logger.info(f"Initializing content watcher for {content_dir}")
        self.watcher = ContentWatcher(
            content_dir=self.content_dir,
            file_extensions=self.file_extensions
        )
        
        # Register callbacks for file events
        self.watcher.on_created(self._handle_file_created)
        self.watcher.on_modified(self._handle_file_modified)
        self.watcher.on_deleted(self._handle_file_deleted)
        
        # Start watching if auto_start is True
        if auto_start:
            self.start()
    
    def start(self):
        """Start watching for changes and load existing content."""
        logger.info("Starting content manager")
        
        # Start the watcher
        self.watcher.start()
        
        # Scan existing files
        self.scan_existing_files()
    
    def stop(self):
        """Stop watching for changes and close the database."""
        logger.info("Stopping content manager")
        
        # Stop the watcher
        self.watcher.stop()
        
        # Close the database
        self.db.close()
    
    def scan_existing_files(self):
        """Scan existing files in the content directory and load them into the database."""
        logger.info(f"Scanning existing files in {self.content_dir}")
        
        # Reset the database to start fresh
        self.db.reset()
        
        # Process each file extension
        for ext in self.file_extensions:
            pattern = f"*{ext}"
            for file_path in self.content_dir.glob(f"**/{pattern}"):
                if file_path.is_file():
                    self._process_and_store_file(file_path)
        
        logger.info(f"Completed initial scan, loaded {self.db.count_documents()} documents")
    
    def _process_and_store_file(self, file_path: Path) -> Optional[str]:
        """
        Process a file and store it in the database.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str or None: Document ID if successful, None otherwise
        """
        try:
            # Process the file
            document = process_file(file_path)
            
            if document:
                # Store in database
                self.db.upsert_document(
                    document_id=document['id'],
                    file_path=document['file_path'],
                    content_type=document['content_type'],
                    title=document['title'],
                    content_markdown=document['content_markdown'],
                    content_html=document['content_html'],
                    metadata=document['metadata'],
                    tags=document['tags']
                )
                logger.debug(f"Stored document {document['id']} from {file_path}")
                return document['id']
        except Exception as e:
            logger.error(f"Error processing and storing file {file_path}: {e}")
        
        return None
    
    def _handle_file_created(self, file_path: Path):
        """
        Handle file creation event.
        
        Args:
            file_path: Path to the created file
        """
        logger.info(f"File created: {file_path}")
        self._process_and_store_file(file_path)
    
    def _handle_file_modified(self, file_path: Path):
        """
        Handle file modification event.
        
        Args:
            file_path: Path to the modified file
        """
        logger.info(f"File modified: {file_path}")
        self._process_and_store_file(file_path)
    
    def _handle_file_deleted(self, file_path: Path):
        """
        Handle file deletion event.
        
        Args:
            file_path: Path to the deleted file
        """
        logger.info(f"File deleted: {file_path}")
        self.db.delete_document_by_path(str(file_path))
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            dict or None: Document data or None if not found
        """
        return self.db.get_document(document_id)
    
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
        return self.db.get_documents(content_type, tag, limit, offset)
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search documents using full-text search.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            list: List of matching document dictionaries
        """
        return self.db.search(query, limit)
    
    def get_content_types(self) -> List[str]:
        """
        Get a list of all content types in the database.
        
        Returns:
            list: List of content type strings
        """
        return self.db.get_content_types()
    
    def get_tags(self) -> List[str]:
        """
        Get a list of all tags in the database.
        
        Returns:
            list: List of tag strings
        """
        return self.db.get_tags()
    
    def register_content_type(self, content_type: str, model_class: type):
        """
        Register a new content type with its corresponding Pydantic model.
        
        Args:
            content_type: The content type name
            model_class: The Pydantic model class for validation
        """
        register_content_type(content_type, model_class)
    
    def create_document(self, 
                       content_type: str,
                       title: str,
                       content: str,
                       metadata: Dict[str, Any],
                       file_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new document file and add it to the database.
        
        Args:
            content_type: Type of content (e.g., 'project', 'note')
            title: Document title
            content: Markdown content
            metadata: Dictionary of metadata
            file_name: Optional file name (without extension)
            
        Returns:
            dict or None: Created document data or None if failed
        """
        try:
            # Ensure content directory exists
            content_type_dir = self.content_dir / content_type
            content_type_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate file name if not provided
            if not file_name:
                # Use title as file name (slugified)
                import re
                file_name = re.sub(r'[^a-zA-Z0-9_-]', '', title.lower().replace(' ', '-'))
            
            # Ensure metadata has title
            metadata['title'] = title
            
            # Create file path
            file_path = content_type_dir / f"{file_name}.md"
            
            # Check if file already exists
            if file_path.exists():
                logger.warning(f"File {file_path} already exists")
                return None
            
            # Create front matter
            import yaml
            front_matter = yaml.dump(metadata, default_flow_style=False)
            
            # Write file with front matter and content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"---\n{front_matter}---\n\n{content}")
            
            logger.info(f"Created new document at {file_path}")
            
            # The watcher should detect this file creation and process it
            # But we'll also process it directly to return the document data
            document = process_file(file_path)
            
            if document:
                return document
            
            return None
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None
    
    def update_document(self,
                       document_id: str,
                       title: Optional[str] = None,
                       content: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Update an existing document.
        
        Args:
            document_id: ID of the document to update
            title: New title (optional)
            content: New Markdown content (optional)
            metadata: New metadata (optional)
            
        Returns:
            dict or None: Updated document data or None if failed
        """
        try:
            # Get the existing document
            document = self.db.get_document(document_id)
            if not document:
                logger.warning(f"Document {document_id} not found")
                return None
            
            # Get the file path
            file_path = Path(document['file_path'])
            if not file_path.exists():
                logger.warning(f"Document file {file_path} not found")
                return None
            
            # Read the existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Extract front matter and content
            from arca.core.parser import extract_front_matter
            existing_metadata, existing_markdown = extract_front_matter(existing_content)
            
            # Update metadata if provided
            if metadata:
                updated_metadata = {**existing_metadata, **metadata}
            else:
                updated_metadata = existing_metadata
            
            # Update title if provided
            if title:
                updated_metadata['title'] = title
            
            # Use new content if provided, otherwise keep existing
            updated_content = content if content is not None else existing_markdown
            
            # Create front matter
            import yaml
            front_matter = yaml.dump(updated_metadata, default_flow_style=False)
            
            # Write updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"---\n{front_matter}---\n\n{updated_content}")
            
            logger.info(f"Updated document {document_id} at {file_path}")
            
            # The watcher should detect this file modification and process it
            # But we'll also process it directly to return the updated document data
            updated_document = process_file(file_path)
            
            if updated_document:
                return updated_document
            
            return None
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            # Get the document to find its file path
            document = self.db.get_document(document_id)
            if not document:
                logger.warning(f"Document {document_id} not found")
                return False
            
            # Get the file path
            file_path = Path(document['file_path'])
            
            # Delete the file if it exists
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted document file {file_path}")
                
                # The watcher should detect this file deletion and update the database
                # But we'll also delete from the database directly
                self.db.delete_document(document_id)
                
                return True
            else:
                logger.warning(f"Document file {file_path} not found")
                
                # Delete from database anyway
                self.db.delete_document(document_id)
                
                return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False 