"""
Arca CMS Demo - Thin Flask wrapper over the real Arca components.
Runs in Pyodide (browser). Only replaces DataManager with in-memory store.
Components (Layout, ListView, DetailView, EditForm) are the real ones.
"""
import json
import uuid
from datetime import datetime

import re

from flask import Flask, request
from arca.components.list_view import ListView
from arca.components.detail_view import DetailView
from arca.components.edit_form import EditForm

app = Flask(__name__)


# ---------------------------------------------------------------------------
# sessionStorage persistence — survives full page navigations (Pyodide restart)
# ---------------------------------------------------------------------------
def _save_store():
    """Serialize CONTENT_STORE to sessionStorage so it survives page reloads."""
    try:
        from js import sessionStorage
        sessionStorage.setItem("arca_content_store", json.dumps(CONTENT_STORE))
    except Exception:
        pass  # Not in browser (e.g. testing locally)


def _load_store():
    """Load CONTENT_STORE from sessionStorage if available."""
    try:
        from js import sessionStorage
        data = sessionStorage.getItem("arca_content_store")
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


def strip_html_wrapper(html):
    """
    Components like DetailView render full HTML documents (<!DOCTYPE>, <html>,
    <head>, <body>). When injected as a fragment via HTMX, the browser strips
    <head>/<style> tags, breaking CSS. This extracts <style>/<script> from
    <head> and the <body> content, returning a valid fragment.
    """
    if '<!DOCTYPE' not in html and '<html' not in html:
        return html  # Already a fragment

    # Extract all <style> blocks (from head or body)
    styles = re.findall(r'<style[^>]*>.*?</style>', html, re.DOTALL)

    # Extract <body> content
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    body = body_match.group(1).strip() if body_match else html

    # Extract <script> blocks from body (they're already in body content)
    # Prepend styles so CSS applies
    return '\n'.join(styles) + '\n' + body

# ---------------------------------------------------------------------------
# In-memory DataManager (same API as arca.data.manager.DataManager)
# ---------------------------------------------------------------------------
CONTENT_STORE = {
    "projects": {
        "project_alpha": {
            "id": "project_alpha",
            "title": "Project Alpha",
            "status": "in progress",
            "author": "Arca Team",
            "tags": ["research", "prototype"],
            "created": "2023-03-01",
            "modified": "2023-03-05",
            "content": "# Project Alpha\n\nThis is the first research prototype for our new initiative. The project aims to explore new possibilities in content management using simple file-based approaches.\n\n## Objectives\n\n- Simplify content management\n- Eliminate database dependencies\n- Enable version control of all content\n- Provide a clean, fast interface\n\n## Timeline\n\nThe project is expected to be completed within 3 months, with regular milestones along the way.",
        },
        "project_beta": {
            "id": "project_beta",
            "title": "Project Beta",
            "status": "planning",
            "author": "Arca Team",
            "tags": ["development", "frontend"],
            "created": "2023-03-02",
            "modified": "2023-03-04",
            "content": "# Project Beta\n\nThis is the follow-up project to Alpha that focuses on enhancing the frontend capabilities of our content management system.\n\n## Goals\n\n- Create a beautiful, responsive UI\n- Implement real-time content updates\n- Develop a component library for reuse\n- Ensure cross-browser compatibility\n\n## Technology Stack\n\n- FastHTML for server-side rendering\n- HTMX for frontend interactivity\n- Custom Windows 98 CSS for styling",
        },
        "project_gamma": {
            "id": "project_gamma",
            "title": "Project Gamma",
            "status": "planning",
            "author": "Arca Team",
            "tags": ["development", "frontend"],
            "created": "2023-03-03",
            "modified": "2023-03-03",
            "content": "# Project Gamma\n\nThis is the follow-up project to Beta that focuses on enhancing the frontend capabilities of our content management system.",
        },
    },
    "tasks": {
        "implement_file_watcher": {
            "id": "implement_file_watcher",
            "title": "Implement File Watcher",
            "status": "in progress",
            "author": "developer1",
            "tags": ["backend", "core"],
            "created": "2023-03-01",
            "modified": "2023-03-05",
            "content": "# Implement File Watcher\n\nDevelop a file system watcher that monitors changes to content files and triggers appropriate updates to the SQLite index.\n\n## Requirements\n\n- Watch for file creation, modification, and deletion\n- Handle large directories efficiently\n- Prevent race conditions during updates\n- Provide clear logging of file system events\n\n## Implementation Notes\n\n- Use the Watchdog library for cross-platform file system monitoring\n- Implement throttling to prevent excessive updates\n- Add unit tests to verify watcher behavior",
        },
        "design_ui_components": {
            "id": "design_ui_components",
            "title": "Design UI Components",
            "status": "pending",
            "author": "designer1",
            "tags": ["frontend", "design"],
            "created": "2023-03-02",
            "modified": "2023-03-04",
            "content": "# Design UI Components\n\nCreate a comprehensive set of UI components for the Arca interface.\n\n## Component List\n\n- Navigation bar\n- Content list view\n- Detail view\n- Edit form\n- Tag selector\n- Search interface\n\n## Design Guidelines\n\n- Use a clean, minimalist aesthetic\n- Ensure accessibility compliance\n- Apply consistent spacing and typography",
        },
        "implement_search": {
            "id": "implement_search",
            "title": "Implement Full-Text Search",
            "status": "in progress",
            "author": "jane_smith",
            "tags": ["backend", "performance", "feature"],
            "created": "2023-03-03",
            "modified": "2023-03-05",
            "content": "# Implement Full-Text Search\n\nWe need to implement a robust full-text search capability for Arca.\n\n## Requirements\n\n1. Content indexing with incremental updates\n2. Search API with filtering by content type, tags, dates\n3. Support for phrase matching and boolean operators\n4. Search results should return in < 200ms",
        },
    },
    "articles": {
        "introduction": {
            "id": "introduction",
            "title": "Introduction to Arca",
            "status": "published",
            "author": "Arca Team",
            "tags": ["documentation", "getting-started"],
            "created": "2023-03-01",
            "modified": "2023-03-04",
            "content": "# Introduction to Arca\n\nWelcome to Arca, a lightweight content management system that stores all data in Markdown files with YAML front matter.\n\n## Why Arca?\n\nArca was created to provide a simple, file-based approach to content management. Instead of relying on complex databases and APIs, Arca stores everything in plain text files that can be versioned with Git.\n\n## Key Features\n\n1. **File-Based**: All content is stored in Markdown files with YAML metadata\n2. **No Database**: No relational database or complex backend - just files\n3. **Version Control**: All content can be tracked with Git\n4. **Simple Interface**: Clean, fast web interface built with FastHTML and HTMX\n5. **Flexible Structure**: Organize content in folders or use metadata references",
        },
        "getting_started": {
            "id": "getting_started",
            "title": "Getting Started with Arca",
            "status": "published",
            "author": "jane_smith",
            "tags": ["documentation", "tutorial", "beginners"],
            "created": "2023-03-01",
            "modified": "2023-03-03",
            "content": "# Getting Started with Arca\n\nWelcome to Arca! This guide will walk you through the basics of setting up and using our file-based content management system.\n\n## Creating Your First Content\n\n1. Visit the web interface in your browser\n2. Click **New** and select a content type\n3. Fill in the required fields and save\n\n## Next Steps\n\n- Explore the content model\n- Learn about templates\n- Set up user permissions",
        },
        "case_study_acme": {
            "id": "case_study_acme",
            "title": "Case Study: ACME Corp",
            "status": "published",
            "author": "john_doe",
            "tags": ["case-study", "success-story"],
            "created": "2023-03-02",
            "modified": "2023-03-02",
            "content": "# How ACME Corp Streamlined Their Documentation with Arca\n\n## Challenge\n\nACME Corporation faced significant challenges managing their technical documentation.\n\n## Solution\n\nAfter evaluating several alternatives, ACME chose Arca for its simplicity and file-based approach.\n\n## Results\n\n- **90% reduction** in time-to-publish\n- **73% increase** in documentation contributions\n- **35% decrease** in support tickets\n- **$175,000 annual savings** in licensing costs",
        },
    },
    "pages": {
        "about": {
            "id": "about",
            "title": "About Arca",
            "status": "published",
            "author": "Arca Team",
            "tags": ["info"],
            "created": "2023-03-01",
            "modified": "2023-03-01",
            "content": "# About Arca\n\nArca is a lightweight, file-based Content Management System designed for simplicity and power.\n\n## Philosophy\n\n- **Files first**: Content lives in Markdown files, not databases\n- **Version control friendly**: Every change is trackable via Git\n- **Developer experience**: Built by developers, for developers\n- **Retro aesthetics**: A nostalgic Windows 98 UI that's actually functional",
        },
        "contact": {
            "id": "contact",
            "title": "Contact",
            "status": "published",
            "author": "Arca Team",
            "tags": ["info"],
            "created": "2023-03-01",
            "modified": "2023-03-01",
            "content": "# Contact\n\nGet in touch with the Arca team:\n\n- **GitHub**: github.com/project-arca\n- **Email**: hello@arca.dev\n- **Documentation**: Available in the Help section",
        },
    },
    "users": {
        "john_doe": {
            "id": "john_doe",
            "title": "John Doe",
            "status": "active",
            "author": "admin",
            "tags": ["admin", "editor"],
            "created": "2023-03-01",
            "modified": "2023-03-01",
            "content": "# John Doe\n\n**Role**: Administrator & Editor\n\nSenior technical writer with expertise in documentation systems and content architecture.",
        },
        "jane_smith": {
            "id": "jane_smith",
            "title": "Jane Smith",
            "status": "active",
            "author": "admin",
            "tags": ["developer", "editor"],
            "created": "2023-03-01",
            "modified": "2023-03-01",
            "content": "# Jane Smith\n\n**Role**: Developer & Editor\n\nFull-stack developer focused on search functionality and backend architecture.",
        },
    },
}

# Restore from sessionStorage if available (survives Pyodide restarts)
_saved = _load_store()
if _saved:
    CONTENT_STORE.clear()
    CONTENT_STORE.update(_saved)


def get_content_types():
    return sorted(CONTENT_STORE.keys())


def get_items(content_type):
    return list(CONTENT_STORE.get(content_type, {}).values())


def get_item(content_type, item_id):
    return CONTENT_STORE.get(content_type, {}).get(item_id)


def create_item(content_type, metadata, content=""):
    if content_type not in CONTENT_STORE:
        CONTENT_STORE[content_type] = {}
    item_id = metadata.get("id") or str(uuid.uuid4())[:8]
    now = datetime.now().strftime("%Y-%m-%d")
    item = {
        "id": item_id,
        "title": metadata.get("title", "Untitled"),
        "status": metadata.get("status", "draft"),
        "author": metadata.get("author", "demo_user"),
        "tags": [t.strip() for t in metadata.get("tags", "").split(",") if t.strip()]
        if isinstance(metadata.get("tags"), str)
        else metadata.get("tags", []),
        "created": now,
        "modified": now,
        "content": content,
    }
    CONTENT_STORE[content_type][item_id] = item
    _save_store()
    return item


def update_item(content_type, item_id, metadata, content=None):
    existing = get_item(content_type, item_id)
    if not existing:
        return None
    now = datetime.now().strftime("%Y-%m-%d")
    existing["title"] = metadata.get("title", existing["title"])
    existing["status"] = metadata.get("status", existing["status"])
    tags_raw = metadata.get("tags", existing["tags"])
    if isinstance(tags_raw, str):
        existing["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]
    existing["modified"] = now
    if content is not None:
        existing["content"] = content
    _save_store()
    return existing


def delete_item(content_type, item_id):
    items = CONTENT_STORE.get(content_type, {})
    if item_id in items:
        del items[item_id]
        _save_store()
        return True
    return False


# ---------------------------------------------------------------------------
# Home page (desktop icons) - only thing not from a component
# ---------------------------------------------------------------------------

def render_desktop():
    """Home page content with desktop icons. This matches Layout._render_desktop()."""
    return """
    <div style="height:100%;display:flex;flex-direction:column;">
        <div class="desktop-icons" style="padding:20px;flex:1;">
            <div class="desktop-icon"
                 hx-get="/list/pages" hx-target="#content-area" hx-push-url="true">
                <i class="las la-file-alt win98-icon primary" style="font-size:32px;margin-bottom:5px;"></i>
                <div class="desktop-icon-label">Pages</div>
            </div>
            <div class="desktop-icon"
                 hx-get="/list/articles" hx-target="#content-area" hx-push-url="true">
                <i class="las la-newspaper win98-icon primary" style="font-size:32px;margin-bottom:5px;"></i>
                <div class="desktop-icon-label">Articles</div>
            </div>
            <div class="desktop-icon"
                 hx-get="/list/projects" hx-target="#content-area" hx-push-url="true">
                <i class="las la-project-diagram win98-icon primary" style="font-size:32px;margin-bottom:5px;"></i>
                <div class="desktop-icon-label">Projects</div>
            </div>
            <div class="desktop-icon"
                 hx-get="/list/tasks" hx-target="#content-area" hx-push-url="true">
                <i class="las la-tasks win98-icon primary" style="font-size:32px;margin-bottom:5px;"></i>
                <div class="desktop-icon-label">Tasks</div>
            </div>
            <div class="desktop-icon"
                 hx-get="/list/users" hx-target="#content-area" hx-push-url="true">
                <i class="las la-user win98-icon primary" style="font-size:32px;margin-bottom:5px;"></i>
                <div class="desktop-icon-label">Users</div>
            </div>
        </div>

        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);">
            <div class="win98-window" style="width:350px;box-shadow:3px 3px 10px rgba(0,0,0,0.3);">
                <div class="win98-window-title">
                    <div style="display:flex;align-items:center;">
                        <i class="las la-info-circle la-md win98-icon primary" style="margin-right:5px;"></i>
                        <span>Welcome to Arca CMS</span>
                    </div>
                    <div style="display:flex;gap:2px;">
                        <button class="control-button minimize"></button>
                        <button class="control-button maximize"></button>
                        <button class="control-button close"></button>
                    </div>
                </div>
                <div style="padding:15px;text-align:center;">
                    <i class="las la-desktop win98-icon primary" style="font-size:64px;margin-bottom:10px;"></i>
                    <h2 style="font-size:14px;margin-bottom:10px;">Welcome to Arca CMS</h2>
                    <p style="font-size:11px;margin-bottom:5px;">This demo runs <b>entirely in your browser</b> via Pyodide (Python + WebAssembly).</p>
                    <p style="font-size:11px;margin-bottom:15px;color:var(--win98-dark-gray);">No server needed. Changes persist during your session.</p>
                    <div style="display:flex;justify-content:center;gap:5px;">
                        <button class="win98-btn" style="font-size:11px;padding:3px 8px;"
                                hx-get="/list/articles" hx-target="#content-area" hx-push-url="true">
                            View Articles
                        </button>
                        <button class="win98-btn" style="font-size:11px;padding:3px 8px;"
                                hx-get="/list/projects" hx-target="#content-area" hx-push-url="true">
                            View Projects
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <style>
        .desktop-icons { display:grid; grid-template-columns:repeat(auto-fill,80px); grid-gap:20px; }
        .desktop-icon { display:flex; flex-direction:column; align-items:center; cursor:pointer; padding:5px; text-align:center; }
        .desktop-icon:hover { background-color:rgba(0,0,128,0.1); }
        .desktop-icon-label { color:#000; font-size:11px; width:70px; text-align:center; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    </style>"""


# ---------------------------------------------------------------------------
# Flask routes - using the REAL Arca components
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_desktop()


@app.route("/list/<content_type>")
def list_content_route(content_type):
    items = get_items(content_type)
    list_view = ListView(content_type=content_type, items=items)
    return list_view.render()


@app.route("/view/<content_type>/<item_id>")
def view_item_route(content_type, item_id):
    item = get_item(content_type, item_id)
    if not item:
        return f'<div class="win98-window"><div class="win98-window-title">Not Found</div><div style="padding:20px;text-align:center;">Item <b>{item_id}</b> not found in {content_type}.</div></div>'
    detail_view = DetailView(content_type=content_type, item=item)
    return strip_html_wrapper(detail_view.render())


@app.route("/edit/<content_type>/<item_id>")
def edit_item_route(content_type, item_id):
    item = get_item(content_type, item_id)
    if not item:
        return f'<div class="win98-window"><div class="win98-window-title">Not Found</div><div style="padding:20px;text-align:center;">Item <b>{item_id}</b> not found in {content_type}.</div></div>'
    edit_form = EditForm(content_type=content_type, item=item)
    return edit_form.render()


@app.route("/new/<content_type>")
def new_item_route(content_type):
    # Pass a non-empty default item so EditForm.render() doesn't hit the
    # not-found path (empty dict is falsy in Python).
    default_item = {"id": "", "title": "", "content": "", "status": "draft", "tags": []}
    edit_form = EditForm(content_type=content_type, item=default_item, is_new=True)
    return edit_form.render()


@app.route("/<content_type>", methods=["POST"])
@app.route("/save/<content_type>", methods=["POST"])
def save_new_route(content_type):
    form_data = request.form.to_dict()
    content = form_data.pop("content", "")
    item = create_item(content_type, form_data, content)
    detail_view = DetailView(content_type=content_type, item=item)
    return strip_html_wrapper(detail_view.render())


@app.route("/<content_type>/<item_id>", methods=["POST"])
@app.route("/save/<content_type>/<item_id>", methods=["POST"])
def save_existing_route(content_type, item_id):
    form_data = request.form.to_dict()
    content = form_data.pop("content", "")
    item = update_item(content_type, item_id, form_data, content)
    if not item:
        return f'<div class="win98-window"><div class="win98-window-title">Not Found</div><div style="padding:20px;">Item not found.</div></div>'
    detail_view = DetailView(content_type=content_type, item=item)
    return strip_html_wrapper(detail_view.render())


@app.route("/delete/<content_type>/<item_id>", methods=["GET", "POST"])
def delete_item_route(content_type, item_id):
    delete_item(content_type, item_id)
    items = get_items(content_type)
    list_view = ListView(content_type=content_type, items=items)
    return list_view.render()
