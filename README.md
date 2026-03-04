# Arca

Arca is a lightweight content management system that uses Markdown and YAML files as its primary data source. It provides a simple way to manage and view your content without the need for a traditional database.

## Features

- **File-Based Content**: Store your content in Markdown files with YAML front matter
- **Real-Time Updates**: Changes to files are automatically detected and reflected in the system
- **SQLite Indexing**: Fast content retrieval through SQLite indexing (ephemeral database)
- **Command-Line Interface**: Manage your content through a powerful CLI
- **Content Validation**: Validate your content against defined schemas using Pydantic
- **Full-Text Search**: Search through your content with SQLite FTS5
- **Content Types**: Organize your content into different types (projects, notes, tasks, etc.)
- **Tagging**: Tag your content for better organization and discovery

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/arca.git
cd arca

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

```bash
# Initialize a new content directory with example files
arca init

# Start the content manager
arca serve

# List all documents
arca list

# Show a specific document
arca show example-project

# Search for documents
arca search "example"

# Create a new document
arca create --title "My Document" --type projects

# Delete a document
arca delete my-document
```

## Content Structure

Arca organizes content into a directory structure like this:

```
content/
├── projects/
│   ├── project1.md
│   └── project2.md
├── notes/
│   ├── note1.md
│   └── note2.md
└── tasks/
    ├── task1.md
    └── task2.md
```

Each Markdown file can include YAML front matter for metadata:

```markdown
---
title: My Project
status: active
priority: 1
tags:
  - example
  - project
---

# My Project

This is the content of my project.
```

## Command-Line Interface

Arca provides a comprehensive CLI for managing your content:

- `arca init`: Initialize a new content directory
- `arca serve`: Start the content manager
- `arca list`: List all documents
- `arca show <id>`: Show a specific document
- `arca search <query>`: Search for documents
- `arca validate`: Validate all content files
- `arca create`: Create a new document
- `arca delete <id>`: Delete a document

Run `arca --help` for more information.

## Architecture

Arca follows a modular architecture:

1. **Content Layer**: Markdown and YAML files in the file system
2. **Monitoring Layer**: File watchers that detect changes
3. **Data Layer**: SQLite database for indexing and caching
4. **Core Layer**: Content manager that integrates the components
5. **CLI Layer**: Command-line interface for user interaction

## Development

To contribute to Arca:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
