"""
Parser module for Arca

This module provides functionality to parse Markdown files with YAML front matter,
validate the data using Pydantic models, and convert Markdown to HTML.
"""
import os
import re
import yaml
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Type, List, Union
from datetime import datetime

import markdown
from pydantic import BaseModel, ValidationError, Field

logger = logging.getLogger(__name__)

# Default Pydantic models for document metadata
class BaseDocumentMeta(BaseModel):
    """Base model for document metadata"""
    id: Optional[str] = None
    title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"  # Allow extra fields not defined in the model

class ProjectMeta(BaseDocumentMeta):
    """Metadata for project documents"""
    status: str = "active"  # active, completed, archived
    deadline: Optional[datetime] = None
    priority: Optional[int] = None

class NoteMeta(BaseDocumentMeta):
    """Metadata for note documents"""
    category: Optional[str] = None
    related_to: List[str] = Field(default_factory=list)

class TaskMeta(BaseDocumentMeta):
    """Metadata for task documents"""
    status: str = "todo"  # todo, in_progress, done
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = None  # low, medium, high

# Registry of content types to metadata models
CONTENT_TYPE_MODELS = {
    "project": ProjectMeta,
    "note": NoteMeta,
    "task": TaskMeta,
}

def register_content_type(content_type: str, model: Type[BaseDocumentMeta]):
    """
    Register a new content type with its corresponding Pydantic model.
    
    Args:
        content_type: The content type name
        model: The Pydantic model class for validation
    """
    CONTENT_TYPE_MODELS[content_type] = model
    logger.info(f"Registered content type '{content_type}' with model {model.__name__}")

def get_content_type_from_path(file_path: Path) -> str:
    """
    Determine the content type from the file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: The content type
    """
    # Try to determine from parent directory name
    parent_dir = file_path.parent.name.lower()
    
    # Check if parent directory matches a known content type
    if parent_dir in CONTENT_TYPE_MODELS:
        return parent_dir
    
    # If not found, use a default type
    return "document"

def generate_id_from_path(file_path: Path) -> str:
    """
    Generate a unique ID from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: A unique ID
    """
    # Use the stem (filename without extension) as the ID
    stem = file_path.stem
    
    # If the stem contains spaces or special characters, create a slug
    if not re.match(r'^[a-zA-Z0-9_-]+$', stem):
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        slug = re.sub(r'[^a-zA-Z0-9_-]', '', stem.lower().replace(' ', '-'))
        return slug
    
    return stem

def extract_front_matter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML front matter from Markdown content.
    
    Args:
        content: The Markdown content with potential front matter
        
    Returns:
        tuple: (metadata dict, remaining content)
    """
    # Check for front matter delimiter
    front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    
    if match:
        # Extract front matter and remaining content
        front_matter_yaml = match.group(1)
        remaining_content = content[match.end():]
        
        try:
            # Parse YAML front matter
            metadata = yaml.safe_load(front_matter_yaml)
            if not isinstance(metadata, dict):
                logger.warning("Front matter is not a dictionary, using empty dict")
                metadata = {}
            return metadata, remaining_content
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML front matter: {e}")
            return {}, content
    
    # No front matter found
    return {}, content

def markdown_to_html(content: str) -> str:
    """
    Convert Markdown content to HTML.
    
    Args:
        content: Markdown content
        
    Returns:
        str: HTML content
    """
    # Configure Markdown extensions
    extensions = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.smarty'
    ]
    
    # Convert Markdown to HTML
    html = markdown.markdown(content, extensions=extensions)
    return html

def parse_markdown_file(file_path: Path) -> Tuple[Dict[str, Any], str, str]:
    """
    Parse a Markdown file, extracting front matter and converting content to HTML.
    
    Args:
        file_path: Path to the Markdown file
        
    Returns:
        tuple: (metadata dict, markdown content, html content)
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract front matter and content
        metadata, markdown_content = extract_front_matter(content)
        
        # Convert Markdown to HTML
        html_content = markdown_to_html(markdown_content)
        
        return metadata, markdown_content, html_content
    except Exception as e:
        logger.error(f"Error parsing Markdown file {file_path}: {e}")
        raise

def parse_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Parse a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        dict: Parsed YAML data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            logger.warning(f"YAML file {file_path} does not contain a dictionary")
            return {}
        
        return data
    except Exception as e:
        logger.error(f"Error parsing YAML file {file_path}: {e}")
        raise

def validate_metadata(metadata: Dict[str, Any], content_type: str) -> Dict[str, Any]:
    """
    Validate metadata using the appropriate Pydantic model.
    
    Args:
        metadata: Metadata dictionary
        content_type: Content type for selecting the validation model
        
    Returns:
        dict: Validated metadata (as a dict)
    """
    # Get the appropriate model for the content type
    model_class = CONTENT_TYPE_MODELS.get(content_type, BaseDocumentMeta)
    
    try:
        # Validate with Pydantic
        model_instance = model_class(**metadata)
        
        # Convert back to dict (this will include default values)
        validated_data = model_instance.dict()
        return validated_data
    except ValidationError as e:
        logger.error(f"Validation error for {content_type} metadata: {e}")
        raise

def process_markdown_file(file_path: Path) -> Dict[str, Any]:
    """
    Process a Markdown file, extracting metadata and content.
    
    Args:
        file_path: Path to the Markdown file
        
    Returns:
        dict: Document data including metadata and content
    """
    # Determine content type from path
    content_type = get_content_type_from_path(file_path)
    
    # Parse the Markdown file
    metadata, markdown_content, html_content = parse_markdown_file(file_path)
    
    # Ensure metadata has an ID
    if 'id' not in metadata or not metadata['id']:
        metadata['id'] = generate_id_from_path(file_path)
    
    # Set created_at and updated_at if not present
    file_stat = file_path.stat()
    if 'created_at' not in metadata or not metadata['created_at']:
        metadata['created_at'] = datetime.fromtimestamp(file_stat.st_ctime)
    if 'updated_at' not in metadata or not metadata['updated_at']:
        metadata['updated_at'] = datetime.fromtimestamp(file_stat.st_mtime)
    
    # Validate metadata
    try:
        validated_metadata = validate_metadata(metadata, content_type)
    except ValidationError as e:
        logger.warning(f"Validation failed for {file_path}, using unvalidated metadata: {e}")
        validated_metadata = metadata
    
    # Construct the document data
    document = {
        'id': validated_metadata['id'],
        'file_path': str(file_path),
        'content_type': content_type,
        'title': validated_metadata.get('title', file_path.stem),
        'content_markdown': markdown_content,
        'content_html': html_content,
        'metadata': validated_metadata,
        'tags': validated_metadata.get('tags', [])
    }
    
    return document

def process_yaml_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Process a YAML file, potentially updating metadata for a corresponding Markdown file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        dict or None: Document data if this is a standalone YAML file,
                     None if this is a companion to a Markdown file
    """
    # Check if there's a corresponding Markdown file
    markdown_path = file_path.with_suffix('.md')
    
    if markdown_path.exists():
        # This is a companion YAML file, we'll process it when handling the Markdown file
        logger.debug(f"Skipping companion YAML file {file_path} (will be processed with {markdown_path})")
        return None
    
    # This is a standalone YAML file
    content_type = get_content_type_from_path(file_path)
    yaml_data = parse_yaml_file(file_path)
    
    # Ensure it has an ID
    if 'id' not in yaml_data or not yaml_data['id']:
        yaml_data['id'] = generate_id_from_path(file_path)
    
    # Set created_at and updated_at if not present
    file_stat = file_path.stat()
    if 'created_at' not in yaml_data or not yaml_data['created_at']:
        yaml_data['created_at'] = datetime.fromtimestamp(file_stat.st_ctime)
    if 'updated_at' not in yaml_data or not yaml_data['updated_at']:
        yaml_data['updated_at'] = datetime.fromtimestamp(file_stat.st_mtime)
    
    # Validate data
    try:
        validated_data = validate_metadata(yaml_data, content_type)
    except ValidationError as e:
        logger.warning(f"Validation failed for {file_path}, using unvalidated data: {e}")
        validated_data = yaml_data
    
    # Construct the document data
    document = {
        'id': validated_data['id'],
        'file_path': str(file_path),
        'content_type': content_type,
        'title': validated_data.get('title', file_path.stem),
        'content_markdown': '',  # No Markdown content for standalone YAML
        'content_html': '',      # No HTML content for standalone YAML
        'metadata': validated_data,
        'tags': validated_data.get('tags', [])
    }
    
    return document

def process_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Process a file (Markdown or YAML) and extract its content and metadata.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict or None: Document data if processing succeeded, None otherwise
    """
    try:
        # Check file extension
        suffix = file_path.suffix.lower()
        
        if suffix == '.md':
            return process_markdown_file(file_path)
        elif suffix in ('.yaml', '.yml'):
            return process_yaml_file(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return None 