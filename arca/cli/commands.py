"""
Command-line interface for the Arca content management system.
"""
import os
import sys
import argparse
from pathlib import Path

from arca.app import main as start_server, app
from arca.data.manager import DataManager

def init_command(args):
    """Initialize a new content directory with example files"""
    data_dir = Path(args.directory) if args.directory else Path("arca/content")
    
    if data_dir.exists() and not args.force:
        print(f"Directory {data_dir} already exists. Use --force to overwrite.")
        return
    
    # Create the directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create example content types
    for content_type in ["projects", "notes", "tasks"]:
        content_type_dir = data_dir / content_type
        content_type_dir.mkdir(exist_ok=True)
        
        # Create an example file
        example_file = content_type_dir / f"example-{content_type[:-1]}.md"
        with open(example_file, "w") as f:
            f.write(f"""---
title: Example {content_type[:-1].title()}
status: active
tags:
  - example
  - {content_type[:-1]}
---

# Example {content_type[:-1].title()}

This is an example {content_type[:-1]} created by the Arca init command.
""")
    
    print(f"Initialized content directory at {data_dir.absolute()}")
    print("Created example content types: projects, notes, tasks")

def serve_command(args):
    """Start the content manager server"""
    print(f"Starting Arca server on port {args.port}...")
    
    # Use a proper server implementation that will block and keep the server running
    try:
        import uvicorn
        # This will actually block and keep the server running
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    except ImportError:
        print("Uvicorn is not installed. Trying FastHTML's serve function...")
        from fasthtml.common import serve
        # Call serve with explicit app and parameters to ensure it blocks
        serve(app=app, host="0.0.0.0", port=args.port)
    except Exception as e:
        print(f"ERROR starting server: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

def list_command(args):
    """List all documents"""
    data_dir = Path(args.directory) if args.directory else Path("arca/content")
    data_manager = DataManager(data_dir)
    
    if args.type:
        # List documents of a specific type
        items = data_manager.get_items(args.type)
        print(f"Documents of type '{args.type}':")
        for item in items:
            print(f"  - {item['id']}: {item.get('title', 'Untitled')}")
    else:
        # List all content types and their documents
        content_types = data_manager.get_content_types()
        for content_type in content_types:
            items = data_manager.get_items(content_type)
            print(f"{content_type.title()} ({len(items)} items):")
            for item in items:
                print(f"  - {item['id']}: {item.get('title', 'Untitled')}")

def show_command(args):
    """Show a specific document"""
    data_dir = Path(args.directory) if args.directory else Path("arca/content")
    data_manager = DataManager(data_dir)
    
    # Try to find the document in all content types
    for content_type in data_manager.get_content_types():
        item = data_manager.get_item(content_type, args.id)
        if item:
            print(f"# {item.get('title', 'Untitled')}")
            print(f"Type: {content_type}")
            print(f"ID: {item['id']}")
            print()
            print("## Metadata")
            for key, value in item.items():
                if key not in ['id', 'content']:
                    print(f"{key}: {value}")
            print()
            print("## Content")
            print(item.get('content', 'No content'))
            return
    
    print(f"Document with ID '{args.id}' not found.")

def search_command(args):
    """Search for documents"""
    data_dir = Path(args.directory) if args.directory else Path("arca/content")
    data_manager = DataManager(data_dir)
    
    results = []
    for content_type in data_manager.get_content_types():
        items = data_manager.get_items(content_type)
        for item in items:
            # Simple search in title, content, and metadata
            search_text = args.query.lower()
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            
            if search_text in title or search_text in content:
                results.append((content_type, item))
    
    if results:
        print(f"Found {len(results)} results for '{args.query}':")
        for content_type, item in results:
            print(f"  - [{content_type}] {item['id']}: {item.get('title', 'Untitled')}")
    else:
        print(f"No results found for '{args.query}'.")

def create_command(args):
    """Create a new document"""
    data_dir = Path(args.directory) if args.directory else Path("arca/content")
    data_manager = DataManager(data_dir)
    
    # Ensure the content type directory exists
    content_type_dir = data_dir / args.type
    content_type_dir.mkdir(exist_ok=True)
    
    # Generate a file name from the title
    file_name = args.title.lower().replace(' ', '-')
    file_path = content_type_dir / f"{file_name}.md"
    
    # Check if the file already exists
    if file_path.exists() and not args.force:
        print(f"File {file_path} already exists. Use --force to overwrite.")
        return
    
    # Create the document
    with open(file_path, "w") as f:
        f.write(f"""---
title: {args.title}
status: draft
tags:
  - {args.type[:-1] if args.type.endswith('s') else args.type}
---

# {args.title}

""")
    
    print(f"Created document at {file_path}")

def delete_command(args):
    """Delete a document"""
    data_dir = Path(args.directory) if args.directory else Path("arca/content")
    data_manager = DataManager(data_dir)
    
    # Try to find the document in all content types
    for content_type in data_manager.get_content_types():
        item = data_manager.get_item(content_type, args.id)
        if item:
            file_path = data_dir / content_type / f"{args.id}.md"
            if file_path.exists():
                if args.force or input(f"Are you sure you want to delete {file_path}? (y/n) ").lower() == 'y':
                    file_path.unlink()
                    print(f"Deleted document {args.id}")
                else:
                    print("Deletion cancelled")
                return
    
    print(f"Document with ID '{args.id}' not found.")

def validate_command(args):
    """Validate all content files"""
    data_dir = Path(args.directory) if args.directory else Path("arca/content")
    data_manager = DataManager(data_dir)
    
    print("Validating content files...")
    valid_count = 0
    invalid_count = 0
    
    for content_type in data_manager.get_content_types():
        content_type_dir = data_dir / content_type
        for file_path in content_type_dir.glob("*.md"):
            try:
                item = data_manager.parse_file(file_path)
                valid_count += 1
            except Exception as e:
                invalid_count += 1
                print(f"Error in {file_path}: {e}")
    
    print(f"Validation complete: {valid_count} valid files, {invalid_count} invalid files")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Arca - A lightweight content management system")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new content directory")
    init_parser.add_argument("--directory", "-d", help="Directory to initialize")
    init_parser.add_argument("--force", "-f", action="store_true", help="Force overwrite existing files")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the content manager server")
    serve_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to listen on")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all documents")
    list_parser.add_argument("--directory", "-d", help="Content directory")
    list_parser.add_argument("--type", "-t", help="Content type to list")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show a specific document")
    show_parser.add_argument("id", help="Document ID")
    show_parser.add_argument("--directory", "-d", help="Content directory")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--directory", "-d", help="Content directory")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new document")
    create_parser.add_argument("--title", "-t", required=True, help="Document title")
    create_parser.add_argument("--type", "-y", required=True, help="Content type")
    create_parser.add_argument("--directory", "-d", help="Content directory")
    create_parser.add_argument("--force", "-f", action="store_true", help="Force overwrite existing files")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a document")
    delete_parser.add_argument("id", help="Document ID")
    delete_parser.add_argument("--directory", "-d", help="Content directory")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate all content files")
    validate_parser.add_argument("--directory", "-d", help="Content directory")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_command(args)
    elif args.command == "serve":
        serve_command(args)
    elif args.command == "list":
        list_command(args)
    elif args.command == "show":
        show_command(args)
    elif args.command == "search":
        search_command(args)
    elif args.command == "create":
        create_command(args)
    elif args.command == "delete":
        delete_command(args)
    elif args.command == "validate":
        validate_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 