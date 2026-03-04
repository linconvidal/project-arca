"""
Arca - A lightweight CMS using FastHTML and Markdown/YAML files
"""
import os
import sys
import argparse
from pathlib import Path

try:
    from fasthtml import FastHTML
    # Import serve correctly from fasthtml.common
    from fasthtml.common import serve
except ImportError:
    print("FastHTML is not installed. Please run 'poetry install' to install dependencies.")
    sys.exit(1)

from arca.components.layout import Layout
from arca.components.list_view import ListView
from arca.components.detail_view import DetailView
from arca.components.edit_form import EditForm
from arca.data.manager import DataManager

# Initialize the data manager
# Get content directory from environment variable or use default
# This will be overridden by command-line arguments if provided
content_dir = os.environ.get("ARCA_CONTENT_DIR", "arca/content")
data_dir = Path(content_dir)
data_manager = DataManager(data_dir)

# Create the FastHTML app
app = FastHTML()

def is_htmx_request(request):
    """Check if the request comes from HTMX"""
    return request.headers.get("HX-Request") == "true"

@app.route("/")
def home(request):
    """Home page showing available content types"""
    content_types = data_manager.get_content_types()
    
    # Create the content list or empty state message
    if content_types:
        # Use our new list view's content_types_menu method
        list_view = ListView("", [])  # Empty list view just to use the render_content_types_menu method
        content_list = list_view.render_content_types_menu(content_types)
    else:
        content_list = f'''
        <div class="p-8 bg-gray-50 dark:bg-gray-800/50 rounded-apple border border-gray-200 dark:border-gray-700/70 animate-fade-in shadow-swiss ring-1 ring-black/5 dark:ring-white/5">
            <p class="text-gray-600 dark:text-gray-300 mb-4">No content types found. This could be because:</p>
            <ul class="list-disc pl-6 text-gray-600 dark:text-gray-300 space-y-2">
                <li>The content directory is empty</li>
                <li>The content directory path is incorrect (currently using: <code class="bg-gray-100 dark:bg-gray-700/80 px-2 py-1 rounded-apple-sm">{data_dir.absolute()}</code>)</li>
                <li>Permissions issues preventing access to content files</li>
            </ul>
            <div class="mt-6 p-5 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 rounded-apple-sm border border-blue-200 dark:border-blue-800/30 shadow-sm">
                <p class="font-medium">Solutions:</p>
                <ol class="list-decimal pl-6 mt-3 space-y-2">
                    <li>Create subfolders in your content directory for each content type</li>
                    <li>Set the correct content directory using the <code class="bg-blue-100 dark:bg-blue-800/30 px-2 py-0.5 rounded-apple-sm">--content-dir</code> parameter</li>
                    <li>Set the <code class="bg-blue-100 dark:bg-blue-800/30 px-2 py-0.5 rounded-apple-sm">ARCA_CONTENT_DIR</code> environment variable</li>
                </ol>
            </div>
        </div>
        '''
    
    children = f"""
    <div class="max-w-4xl mx-auto px-4 py-12">
        <div class="text-center mb-12 animate-fade-in">
            <h1 class="text-6xl font-bold mb-4 text-white">Arca</h1>
            <p class="text-xl text-gray-400">A lightweight content management system</p>
        </div>
        
        {content_list}
    </div>
    """
    
    # If HTMX request, return only the content
    if is_htmx_request(request):
        return children
    
    # Otherwise, return the full layout
    layout = Layout()
    return layout.render(children)

@app.route("/list/{content_type}")
def list_content(request):
    """List all content of a specific type"""
    # Get content_type from the request path parameters
    content_type = request.path_params.get("content_type")
    print(f"List content for type: {content_type}")
    
    items = data_manager.get_items(content_type)
    list_view = ListView(content_type=content_type, items=items)
    content = list_view.render()
    
    # If HTMX request, return only the content
    if is_htmx_request(request):
        return content
    
    # Otherwise, return the full layout
    layout = Layout()
    return layout.render(content)

@app.route("/view/{content_type}/{item_id}")
def view_item(request):
    """View a specific content item"""
    # Get parameters from the request path
    content_type = request.path_params.get("content_type")
    item_id = request.path_params.get("item_id")
    print(f"View item: {item_id} of type: {content_type}")
    
    item = data_manager.get_item(content_type, item_id)
    
    if not item:
        not_found_content = f"""
        <div class="max-w-3xl mx-auto text-center">
            <div class="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
                <h1 class="text-2xl font-bold mb-3 text-red-600">Not Found</h1>
                <p class="text-gray-600 mb-6">Item <span class="font-mono bg-gray-100 px-2 py-1 rounded">{item_id}</span> not found in {content_type}</p>
                <a 
                    href="/list/{content_type}" 
                    class="px-4 py-2 bg-primary text-white rounded hover:bg-primary/80 transition-all"
                    hx-get="/list/{content_type}" 
                    hx-target="#content-area" 
                    hx-push-url="true"
                >
                    Back to list
                </a>
            </div>
        </div>
        """
        
        # If HTMX request, return only the content
        if is_htmx_request(request):
            return not_found_content
            
        # Otherwise, return the full layout
        layout = Layout()
        return layout.render(not_found_content)
    
    detail_view = DetailView(content_type=content_type, item=item)
    content = detail_view.render()
    
    # If HTMX request, return only the content
    if is_htmx_request(request):
        return content
        
    # Otherwise, return the full layout
    layout = Layout()
    return layout.render(content)

@app.route("/edit/{content_type}/{item_id}")
def edit_item(request):
    """Edit a specific content item"""
    # Get parameters from the request path
    content_type = request.path_params.get("content_type")
    item_id = request.path_params.get("item_id")
    print(f"Edit item: {item_id} of type: {content_type}")
    
    item = data_manager.get_item(content_type, item_id)
    
    if not item:
        not_found_content = f"""
        <div class="max-w-3xl mx-auto text-center">
            <div class="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
                <h1 class="text-2xl font-bold mb-3 text-red-600">Not Found</h1>
                <p class="text-gray-600 mb-6">Item <span class="font-mono bg-gray-100 px-2 py-1 rounded">{item_id}</span> not found in {content_type}</p>
                <a 
                    href="/list/{content_type}" 
                    class="px-4 py-2 bg-primary text-white rounded hover:bg-primary/80 transition-all"
                    hx-get="/list/{content_type}" 
                    hx-target="#content-area" 
                    hx-push-url="true"
                >
                    Back to list
                </a>
            </div>
        </div>
        """
        
        # If HTMX request, return only the content
        if is_htmx_request(request):
            return not_found_content
            
        # Otherwise, return the full layout
        layout = Layout()
        return layout.render(not_found_content)
    
    edit_form = EditForm(content_type=content_type, item=item)
    content = edit_form.render()
    
    # If HTMX request, return only the content
    if is_htmx_request(request):
        return content
        
    # Otherwise, return the full layout
    layout = Layout()
    return layout.render(content)

@app.route("/new/{content_type}")
def new_item(request):
    """Create a new content item"""
    # Get content_type from the request path
    content_type = request.path_params.get("content_type")
    print(f"New item of type: {content_type}")
    
    edit_form = EditForm(content_type=content_type, item=None, is_new=True)
    content = edit_form.render()
    
    # If HTMX request, return only the content
    if is_htmx_request(request):
        return content
        
    # Otherwise, return the full layout
    layout = Layout()
    return layout.render(content)

@app.route("/save/{content_type}", methods=["POST"])
def create_item(request):
    """Create a new content item"""
    # Get content_type from the request path
    content_type = request.path_params.get("content_type")
    print(f"Create new item of type: {content_type}")
    
    form_data = request.form
    
    # Convert form data to item format
    item_data = {}
    for key, value in form_data.items():
        if key != "content":
            item_data[key] = value
    
    content = form_data.get("content", "")
    
    # Create new item
    item = data_manager.create_item(content_type, item_data, content)
    
    # Redirect to view the item (either HTMX or regular redirect)
    if is_htmx_request(request):
        return app.redirect(f"/view/{content_type}/{item['id']}")
    else:
        return app.redirect(f"/view/{content_type}/{item['id']}")

@app.route("/save/{content_type}/{item_id}", methods=["POST"])
def update_item(request):
    """Update an existing content item"""
    # Get parameters from the request path
    content_type = request.path_params.get("content_type")
    item_id = request.path_params.get("item_id")
    print(f"Update item: {item_id} of type: {content_type}")
    
    form_data = request.form
    
    # Convert form data to item format
    item_data = {}
    for key, value in form_data.items():
        if key != "content":
            item_data[key] = value
    
    content = form_data.get("content", "")
    
    # Update existing item
    item = data_manager.update_item(content_type, item_id, item_data, content)
    
    # Redirect to view the item (either HTMX or regular redirect)
    if is_htmx_request(request):
        return app.redirect(f"/view/{content_type}/{item['id']}")
    else:
        return app.redirect(f"/view/{content_type}/{item['id']}")

@app.route("/delete/{content_type}/{item_id}", methods=["POST"])
def delete_item(request):
    """Delete a content item"""
    # Get parameters from the request path
    content_type = request.path_params.get("content_type")
    item_id = request.path_params.get("item_id")
    print(f"Delete item: {item_id} of type: {content_type}")
    
    data_manager.delete_item(content_type, item_id)
    
    # Redirect to list view (either HTMX or regular redirect)
    if is_htmx_request(request):
        return app.redirect(f"/list/{content_type}")
    else:
        return app.redirect(f"/list/{content_type}")

def main():
    """Main entry point for the application"""
    global data_dir, data_manager
    
    print("Entering main() function in arca/app.py")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start the Arca content management system")
    parser.add_argument("--content-dir", dest="content_dir", default=None,
                        help="Path to the content directory (default: 'content' or value of ARCA_CONTENT_DIR env var)")
    parser.add_argument("--port", type=int, default=8000, 
                        help="Port to run the server on")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host to bind the server to")
    
    args = parser.parse_args()
    
    # Update data directory if provided via command line
    if args.content_dir:
        data_dir = Path(args.content_dir)
        # Re-initialize the data manager with the new path
        data_manager = DataManager(data_dir)
        print(f"Content directory set to {data_dir.absolute()} from command line")
    else:
        print(f"Using content directory: {data_dir.absolute()}")
    
    # Ensure data directory exists
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        print(f"Created content directory at {data_dir.absolute()}")
    else:
        print(f"Content directory exists at {data_dir.absolute()}")
    
    # Start the server
    print("About to start Arca server...")
    print(f"App routes: {app.routes}")
    
    try:
        print("Starting server with FastHTML...")
        print(f"Server URL: http://{args.host}:{args.port}")
        # Call serve with the app instance and explicit host/port to ensure it blocks
        serve(app=app, host=args.host, port=args.port)
    except Exception as e:
        print(f"ERROR starting server: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("Exiting main() function")

if __name__ == "__main__":
    main() 