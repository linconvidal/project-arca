"""
Arca - A lightweight content management system using Markdown and YAML files.

This package provides tools for managing content stored in Markdown files with YAML front matter.
"""

__version__ = "0.1.0"
__author__ = "Arca Team"

from arca.core.manager import ContentManager
from arca.core.parser import BaseDocumentMeta, register_content_type 