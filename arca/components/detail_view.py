"""
Detail view component for Arca - displays a single content item
with classic Windows 98 styling
"""
import markdown

class DetailView:
    """
    Component for displaying a single content item in detail
    Styled with the classic Windows 98 aesthetic
    """
    
    def __init__(self, content_type, item):
        """
        Initialize the detail view
        
        Args:
            content_type (str): The type of content being displayed
            item (dict): The item to display
        """
        self.content_type = content_type
        self.item = item
        
        # Set the content type title
        self.content_type_title = content_type.replace('_', ' ').title()
        self.item_title = item.get('title', 'Untitled') if item else 'Not Found'
    
    def render(self):
        """
        Render the detail view with Windows 98 styling
        
        Returns:
            str: The rendered HTML
        """
        if not self.item:
            return '<div class="win98-window"><div class="win98-window-title">Not Found</div><div class="win98-window-content">Item not found.</div></div>'
        
        # Extract fields
        title = self.item.get('title', 'Untitled')
        content = self.item.get('content', '')
        status = self.item.get('status', 'draft')
        author = self.item.get('author', 'Unknown')
        
        # Render content as HTML (from markdown)
        try:
            import markdown
            content_html = markdown.markdown(content) if content else '<p><em>No content available.</em></p>'
        except ImportError:
            content_html = content if content else '<p><em>No content available.</em></p>'
        
        # Render metadata
        metadata_html = self._render_metadata(self.item)
        
        # Detail view CSS
        detail_css = """
            /* Basic reset */
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            .detail-container {
                display: flex;
                flex-direction: column;
                height: 100%;
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
                font-size: 12px;
            }
            
            .win98-window {
                border: 2px solid;
                border-color: var(--win98-white) var(--win98-black) var(--win98-black) var(--win98-white);
                box-shadow: 2px 2px 0 var(--win98-white) inset, -2px -2px 0 var(--win98-dark-gray) inset;
                background-color: var(--win98-gray);
            }
            
            .win98-window-content {
                padding: 8px;
            }
            
            .win98-action-bar {
                display: flex;
                gap: 6px;
                margin-bottom: 12px;
                padding: 6px;
                background-color: var(--win98-light-gray);
                border: 1px solid;
                border-color: var(--win98-dark-gray) var(--win98-white) var(--win98-white) var(--win98-dark-gray);
            }
            
            /* Tab styling */
            .tabs {
                display: flex;
                border-bottom: 1px solid var(--win98-dark-gray);
                background-color: var(--win98-gray);
                margin-bottom: 0;
                padding: 4px 8px 0 8px;
                position: relative;
                z-index: 1;
            }
            
            .tab {
                padding: 6px 12px;
                cursor: pointer;
                background-color: var(--win98-light-gray);
                border: 1px solid var(--win98-dark-gray);
                border-bottom: none;
                margin-right: 4px;
                position: relative;
                font-size: 12px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                box-shadow: inset 1px 1px 0 var(--win98-white);
                position: relative;
                top: 1px;
            }
            
            .tab.active {
                background-color: var(--win98-light-gray);
                z-index: 2;
                border-bottom: 1px solid var(--win98-light-gray);
                font-weight: bold;
            }
            
            .tab-content {
                display: none;
                padding: 16px;
                background-color: var(--win98-light-gray);
                border: 1px solid var(--win98-dark-gray);
                border-top: none;
                flex-grow: 1;
                overflow: auto;
                position: relative;
                z-index: 0;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .metadata-grid {
                display: grid;
                grid-template-columns: 120px 1fr;
                gap: 8px;
                margin-bottom: 15px;
            }
            
            .metadata-label {
                font-weight: bold;
                color: var(--win98-dark-blue);
            }
            
            .metadata-value {
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
            }
            
            .status-badge {
                display: inline-block;
                padding: 3px 8px;
                border: 1px solid var(--win98-dark-gray);
                background-color: var(--win98-light-gray);
                font-size: 11px;
            }
            
            .tags-container {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
            }
            
            .win98-tag {
                display: inline-block;
                padding: 3px 8px;
                font-size: 11px;
                background-color: var(--win98-gray);
                border: 1px solid;
                border-color: var(--win98-white) var(--win98-dark-gray) var(--win98-dark-gray) var(--win98-white);
                white-space: nowrap;
            }
            
            .content-area {
                padding: 16px;
                background-color: var(--win98-white);
                border: 1px solid var(--win98-dark-gray);
                min-height: 200px;
                overflow: auto;
                line-height: 1.4;
            }
            
            .content-area h1, .content-area h2, .content-area h3 {
                margin-top: 1.2em;
                margin-bottom: 0.8em;
            }
            
            .content-area p {
                margin-bottom: 1em;
            }
            
            .content-area ul, .content-area ol {
                margin-left: 2em;
                margin-bottom: 1em;
            }
            
            .keyboard-shortcuts {
                margin-top: 16px;
                font-size: 11px;
                color: var(--win98-dark-gray);
                padding: 8px;
                border-top: 1px solid var(--win98-dark-gray);
            }
            
            kbd {
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
                background-color: var(--win98-light-gray);
                border: 1px solid var(--win98-dark-gray);
                padding: 1px 4px;
                font-size: 10px;
                border-radius: 2px;
            }
            
            /* Windows 98 Icon Styling */
            .win98-icon {
                color: var(--win98-black);
                -webkit-font-smoothing: none;
                -moz-osx-font-smoothing: grayscale;
                image-rendering: pixelated;
                text-shadow: 0.5px 0 0 var(--win98-dark-gray), 0 0.5px 0 var(--win98-dark-gray);
                margin-right: 4px;
            }
            
            .win98-icon.primary {
                color: var(--win98-dark-blue);
            }
            
            .win98-icon.destructive {
                color: var(--win98-red);
            }
            
            .win98-icon.success {
                color: var(--win98-green);
            }
            
            /* Line Awesome specific sizes */
            .la-sm {
                font-size: 12px;
            }
            
            .la-md {
                font-size: 16px;
            }
            
            .la-lg {
                font-size: 24px;
            }
            
            .win98-button {
                padding: 5px 10px;
                margin: 0 2px;
                display: inline-flex;
                align-items: center;
            }
            
            /* Window title styling */
            .win98-window-title {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 4px 6px;
                background: var(--title-bar-gradient, linear-gradient(90deg, #000080, #1084d0));
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
        """
        
        # Windows 98 style detail view
        
        # Get the item ID for use in JavaScript
        item_id = self.item["id"]
        
        # JavaScript code in a separate variable to avoid f-string issues
        detail_script = f"""
            function switchTab(event, tabId) {{
                // Hide all tab contents
                var tabContents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < tabContents.length; i++) {{
                    tabContents[i].classList.remove('active');
                }}
                
                // Remove active class from all tabs
                var tabs = document.getElementsByClassName('tab');
                for (var i = 0; i < tabs.length; i++) {{
                    tabs[i].classList.remove('active');
                }}
                
                // Show the clicked tab content and mark the tab as active
                document.getElementById(tabId).classList.add('active');
                event.currentTarget.classList.add('active');
            }}
            
            // Delete confirmation
            document.getElementById('delete-btn').addEventListener('click', function() {{
                if (confirm('Are you sure you want to delete this item?')) {{
                    window.location.href = '/delete/{self.content_type}/{item_id}';
                }}
            }});
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {{
                if (e.altKey) {{
                    switch(e.key.toLowerCase()) {{
                        case 'b':
                            window.location.href = '/list/{self.content_type}';
                            break;
                        case 'e': 
                            window.location.href = '/edit/{self.content_type}/{item_id}';
                            break;
                        case 'p':
                            window.print();
                            break;
                        case 'd':
                            document.getElementById('delete-btn').click();
                            break;
                    }}
                }}
            }});
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>{detail_css}</style>
            <link rel="stylesheet" href="https://maxst.icons8.com/vue-static/landings/line-awesome/line-awesome/1.3.0/css/line-awesome.min.css">
        </head>
        <body>
            <div class="detail-container">
                <div class="win98-window">
                    <div class="win98-window-title">
                        <div>
                            <i class="las la-file-alt la-md win98-icon"></i>
                            {title}
                        </div>
                        <div class="win98-window-controls">
                            <button class="win98-btn-minimize">_</button>
                            <button class="win98-btn-maximize">□</button>
                            <button class="win98-btn-close">×</button>
                        </div>
                    </div>
                    <div class="win98-window-content">
                        <div class="win98-action-bar">
                            <button class="win98-button" onclick="window.location.href='/list/{self.content_type}'">
                                <i class="las la-arrow-left la-md win98-icon"></i> Back to List
                            </button>
                            <button class="win98-button" onclick="window.location.href='/edit/{self.content_type}/{self.item["id"]}'">
                                <i class="las la-edit la-md win98-icon"></i> Edit
                            </button>
                            <button class="win98-button" onclick="window.print()">
                                <i class="las la-print la-md win98-icon"></i> Print
                            </button>
                            <button class="win98-button" id="delete-btn">
                                <i class="las la-trash la-md win98-icon"></i> Delete
                            </button>
                        </div>
                        
                        <div class="tabs">
                            <div class="tab active" onclick="switchTab(event, 'content-tab')">Content</div>
                            <div class="tab" onclick="switchTab(event, 'properties-tab')">Properties</div>
                            <div class="tab" onclick="switchTab(event, 'history-tab')">History</div>
                        </div>
                        
                        <div id="content-tab" class="tab-content active">
                            <div class="content-area">
                                {content_html}
                            </div>
                        </div>
                        
                        <div id="properties-tab" class="tab-content">
                            {metadata_html}
                        </div>
                        
                        <div id="history-tab" class="tab-content">
                            <h3>Version History</h3>
                            <div class="win98-table">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>User</th>
                                            <th>Changes</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>{self._format_date(self.item.get('created', None))}</td>
                                            <td>{author}</td>
                                            <td>Created document</td>
                                        </tr>
                                        <tr>
                                            <td>{self._format_date(self.item.get('modified', None))}</td>
                                            <td>{author}</td>
                                            <td>Updated document</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div class="keyboard-shortcuts">
                            Keyboard shortcuts: <kbd>Alt+B</kbd> Back to List | <kbd>Alt+E</kbd> Edit | <kbd>Alt+P</kbd> Print | <kbd>Alt+D</kbd> Delete
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                {detail_script}
            </script>
        </body>
        </html>
        """
        
        return html
    
    def _render_metadata(self, item):
        """
        Render the item metadata as HTML.
        
        Args:
            item: The item to render metadata for
            
        Returns:
            str: HTML string of the rendered metadata
        """
        # Extract metadata fields
        author = item.get('author', 'Unknown')
        created = item.get('created', None)
        modified = item.get('modified', None)
        status = item.get('status', 'draft')
        tags = item.get('tags', [])
        
        # Format dates
        created_str = self._format_date(created) if created else 'Unknown'
        modified_str = self._format_date(modified) if modified else 'Unknown'
        
        # Format tags with Win98 styling
        if tags:
            tags_html = '<div class="tags-container">'
            for tag in tags:
                tags_html += f'<div class="win98-tag">{tag}</div>'
            tags_html += '</div>'
        else:
            tags_html = '<span class="metadata-value">None</span>'
        
        # Status badge with color
        status_color = 'lightgreen' if status == 'published' else 'lightgray'
        if status == 'draft':
            status_color = 'lightyellow'
        elif status == 'archived':
            status_color = 'lightgray'
        
        status_badge = f'<span class="status-badge" style="background-color: {status_color}">{status}</span>'
        
        # Render metadata grid
        metadata_html = f"""
        <div class="metadata-grid">
            <div class="metadata-label">Author:</div>
            <div class="metadata-value">{author}</div>
            
            <div class="metadata-label">Created:</div>
            <div class="metadata-value">{created_str}</div>
            
            <div class="metadata-label">Modified:</div>
            <div class="metadata-value">{modified_str}</div>
            
            <div class="metadata-label">Status:</div>
            <div class="metadata-value">{status_badge}</div>
            
            <div class="metadata-label">Tags:</div>
            <div class="metadata-value">{tags_html}</div>
        </div>
        """
        
        return metadata_html
    
    def _format_date(self, date_str):
        """
        Format a date string to a more readable format
        
        Args:
            date_str (str): The date string to format
            
        Returns:
            str: The formatted date
        """
        if not date_str:
            return "—"
        
        # Simple formatting for now - in a real app would use datetime
        return date_str
    
    def _render_not_found(self):
        """
        Render a not found message with Windows 98 styling
        
        Returns:
            str: The rendered HTML
        """
        return f"""
        <div class="win98-window" style="margin-bottom: 20px; width: 100%;">
            <div class="win98-window-title">
                <div style="display: flex; align-items: center;">
                    <img src="data:image/gif;base64,R0lGODlhEAAQAIAAAP///8zMzCH5BAEAAAEALAAAAAAQABAAAAIdjI+py+0Po5wHVICz1YnvTXlWaIZmJ6Zq+rZuGxQAOw==" class="win98-icon" alt="">
                    Not Found
                </div>
            </div>
            
            <div style="padding: 20px; text-align: center;">
                <div class="win98-panel-inset" style="padding: 20px; max-width: 400px; margin: 0 auto;">
                    <img src="data:image/gif;base64,R0lGODlhIAAgAIAAAP///+/vACH5BAEAAAEALAAAAAAgACAAAAI0jI+py+0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf+DwwKh8Si8YhMKpcCADs=" style="width: 32px; height: 32px; margin: 0 auto 10px;">
                    <h3 style="font-size: 14px; margin-bottom: 10px; color: #000080;">Item Not Found</h3>
                    <p style="font-size: 11px; margin-bottom: 20px;">The {self.content_type_title.lower()} you're looking for could not be found.</p>
                    <button class="win98-btn" 
                            hx-get="/{self.content_type}" 
                            hx-target="#content-area" 
                            hx-push-url="true">
                        Back to List
                    </button>
                </div>
            </div>
        </div>
        """
    
    def _get_status_color(self, status):
        """
        Get the appropriate color for a status
        
        Args:
            status (str): The status string
            
        Returns:
            str: The color as a CSS color value
        """
        status = status.lower()
        if status == 'published':
            return 'green'
        elif status == 'draft':
            return '#808080'
        elif status == 'archived':
            return '#a0a0a0'
        elif status == 'deleted':
            return 'red'
        else:
            return '#000080'  # Default Win98 blue 