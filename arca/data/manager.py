"""
Data manager for Arca - handles reading and writing Markdown files with YAML front matter
"""
import os
import uuid
from pathlib import Path
import frontmatter
import yaml

class DataManager:
    """
    Manages data storage and retrieval for Arca
    All data is stored in Markdown files with YAML front matter
    """
    
    def __init__(self, data_dir):
        """
        Initialize the data manager
        
        Args:
            data_dir (Path): Path to the data directory
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)
    
    def get_content_types(self):
        """
        Get a list of available content types (directories in the data directory)
        
        Returns:
            list: List of content type names
        """
        if not self.data_dir.exists():
            return []
        
        return [d.name for d in self.data_dir.iterdir() 
                if d.is_dir() and not d.name.startswith('.')]
    
    def parse_file(self, file_path):
        """
        Parse a Markdown file with YAML front matter
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            dict: The parsed item (dictionary with metadata and content)
            
        Raises:
            Exception: If the file cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            post = frontmatter.load(file_path)
            item = dict(post.metadata)
            item['content'] = post.content
            
            # Validate required fields
            if 'id' not in item:
                item['id'] = file_path.stem
            
            return item
        except Exception as e:
            raise Exception(f"Failed to parse file: {e}")
    
    def get_items(self, content_type):
        """
        Get all items of a specific content type
        
        Args:
            content_type (str): The content type to get items for
            
        Returns:
            list: List of items (dictionaries with metadata and content)
        """
        content_dir = self.data_dir / content_type
        if not content_dir.exists():
            content_dir.mkdir(parents=True)
            return []
        
        items = []
        for file_path in content_dir.glob('*.md'):
            try:
                post = frontmatter.load(file_path)
                item = dict(post.metadata)
                item['content'] = post.content
                items.append(item)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return items
    
    def get_item(self, content_type, item_id):
        """
        Get a specific item by ID
        
        Args:
            content_type (str): The content type
            item_id (str): The item ID
            
        Returns:
            dict: The item data or None if not found
        """
        content_dir = self.data_dir / content_type
        if not content_dir.exists():
            return None
        
        # First try direct filename match
        file_path = content_dir / f"{item_id}.md"
        if file_path.exists():
            try:
                post = frontmatter.load(file_path)
                item = dict(post.metadata)
                item['content'] = post.content
                return item
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                return None
        
        # If not found, search by ID in metadata
        for file_path in content_dir.glob('*.md'):
            try:
                post = frontmatter.load(file_path)
                if post.metadata.get('id') == item_id:
                    item = dict(post.metadata)
                    item['content'] = post.content
                    return item
            except Exception:
                continue
        
        return None
    
    def create_item(self, content_type, metadata, content=""):
        """
        Create a new item
        
        Args:
            content_type (str): The content type
            metadata (dict): The item metadata
            content (str): The item content
            
        Returns:
            dict: The created item
        """
        content_dir = self.data_dir / content_type
        if not content_dir.exists():
            content_dir.mkdir(parents=True)
        
        # Ensure the item has an ID
        if 'id' not in metadata or not metadata['id']:
            metadata['id'] = str(uuid.uuid4())
        
        # Create a safe filename
        safe_id = metadata['id'].replace(' ', '_').lower()
        file_path = content_dir / f"{safe_id}.md"
        
        # Create the frontmatter post
        post = frontmatter.Post(content, **metadata)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        # Return the full item
        return {**metadata, 'content': content}
    
    def update_item(self, content_type, item_id, metadata, content=None):
        """
        Update an existing item
        
        Args:
            content_type (str): The content type
            item_id (str): The item ID
            metadata (dict): The updated metadata
            content (str, optional): The updated content
            
        Returns:
            dict: The updated item or None if not found
        """
        # Get the existing item
        existing_item = self.get_item(content_type, item_id)
        if not existing_item:
            return None
        
        content_dir = self.data_dir / content_type
        
        # Ensure ID remains the same
        metadata['id'] = item_id
        
        # If content is None, keep the existing content
        if content is None:
            content = existing_item.get('content', '')
        
        # Create a safe filename
        safe_id = item_id.replace(' ', '_').lower()
        file_path = content_dir / f"{safe_id}.md"
        
        # Create the frontmatter post
        post = frontmatter.Post(content, **metadata)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        # Return the full item
        return {**metadata, 'content': content}
    
    def delete_item(self, content_type, item_id):
        """
        Delete an item
        
        Args:
            content_type (str): The content type
            item_id (str): The item ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        content_dir = self.data_dir / content_type
        if not content_dir.exists():
            return False
        
        # First try direct filename match
        file_path = content_dir / f"{item_id}.md"
        if file_path.exists():
            file_path.unlink()
            return True
        
        # If not found, search by ID in metadata
        for file_path in content_dir.glob('*.md'):
            try:
                post = frontmatter.load(file_path)
                if post.metadata.get('id') == item_id:
                    file_path.unlink()
                    return True
            except Exception:
                continue
        
        return False 