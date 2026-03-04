"""
List view component for Arca - displays a list of content items
with classic Windows 98 styling
"""
import markdown

class ListView:
    """
    Component for displaying a list of content items
    Styled with the classic Windows 98 aesthetic
    """
    
    def __init__(self, content_type, items):
        """
        Initialize the list view
        
        Args:
            content_type (str): The type of content being displayed
            items (list): List of items to display
        """
        self.content_type = content_type
        self.items = items
        
        # Set the content type title
        self.content_type_title = content_type.replace('_', ' ').title()
    
    def render(self):
        """
        Render the list view with Windows 98 styling
        
        Returns:
            str: The rendered HTML
        """
        if not self.items:
            return self._render_empty_state()
        
        # Render the items table
        items_html = ""
        for index, item in enumerate(self.items):
            items_html += self._render_item(item, index)
        
        # Context menu JavaScript functionality
        context_menu_script = """
            // Context menu functionality
            (function() {
                const contextMenu = document.getElementById('context-menu');
                let activeRow = null;
                
                // Add event listener to each table row
                document.querySelectorAll('.win98-table-body tr').forEach(row => {
                    row.addEventListener('contextmenu', function(e) {
                        e.preventDefault();
                        
                        // Save the row that was right-clicked
                        activeRow = this;
                        
                        // Position the context menu
                        contextMenu.style.left = e.pageX + 'px';
                        contextMenu.style.top = e.pageY + 'px';
                        contextMenu.style.display = 'block';
                    });
                    
                    // Double-click to view
                    row.addEventListener('dblclick', function() {
                        const id = this.getAttribute('data-id');
                        if (id) {
                            window.location.href = `/view/${self.content_type}/${id}`;
                        }
                    });
                });
                
                // Handle context menu actions
                document.querySelectorAll('.context-menu-item').forEach(item => {
                    item.addEventListener('click', function() {
                        if (!activeRow) return;
                        
                        const id = activeRow.getAttribute('data-id');
                        if (!id) return;
                        
                        const action = this.getAttribute('data-action');
                        
                        if (action === 'view') {
                            window.location.href = `/view/${self.content_type}/${id}`;
                        } else if (action === 'edit') {
                            window.location.href = `/edit/${self.content_type}/${id}`;
                        } else if (action === 'delete') {
                            if (confirm('Are you sure you want to delete this item?')) {
                                window.location.href = `/delete/${self.content_type}/${id}`;
                            }
                        }
                        
                        // Hide menu
                        contextMenu.style.display = 'none';
                    });
                });
                
                // Hide menu when clicking elsewhere
                document.addEventListener('click', function() {
                    if (contextMenu) {
                        contextMenu.style.display = 'none';
                    }
                });
            })();
        """
        
        return f"""
        <div class="win98-window">
            <div class="win98-window-title">
                <div style="display: flex; align-items: center;">
                    <i class="las la-table la-md win98-icon" style="margin-right: 6px;"></i>
                    {self.content_type_title}
                </div>
            </div>
            
            <div class="win98-panel-inset" style="padding: 10px; background-color: var(--win98-gray);">
                <!-- Action bar -->
                <div style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <a href="/new/{self.content_type}">
                        <button class="win98-btn">
                            <i class="las la-plus la-sm win98-icon" style="margin-right: 4px;"></i>
                            New {self.content_type_title}
                        </button>
                    </a>
                    <div>
                        <span>{len(self.items)} items</span>
                    </div>
                </div>
                
                <!-- Items table -->
                <div class="win98-panel-inset" style="background-color: var(--win98-white); padding: 1px;">
                    <table class="win98-table">
                        <thead class="win98-table-header">
                            <tr>
                                <th class="text-left">Title</th>
                                <th class="text-center">Status</th>
                                <th class="text-center">Author</th>
                                <th class="text-center">Modified</th>
                                <th class="text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="win98-table-body">
                            {items_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Context menu -->
        <div id="context-menu" class="win98-panel" style="display: none; position: absolute; z-index: 1000; width: 150px;">
            <div style="padding: 2px;">
                <div class="context-menu-item" data-action="view" style="padding: 3px 5px; cursor: pointer;">
                    <i class="las la-eye la-sm win98-icon" style="margin-right: 5px;"></i> View
                </div>
                <div class="context-menu-item" data-action="edit" style="padding: 3px 5px; cursor: pointer;">
                    <i class="las la-edit la-sm win98-icon" style="margin-right: 5px;"></i> Edit
                </div>
                <div class="context-menu-item" data-action="delete" style="padding: 3px 5px; cursor: pointer;">
                    <i class="las la-trash la-sm win98-icon" style="margin-right: 5px;"></i> Delete
                </div>
            </div>
        </div>
        
        <script>
            {context_menu_script}
        </script>
        """
    
    def _render_empty_state(self):
        """
        Render an empty state with Windows 98 styling
        
        Returns:
            str: The rendered HTML for empty state
        """
        return f"""
        <div class="win98-window">
            <div class="win98-window-title">
                <div style="display: flex; align-items: center;">
                    <i class="las la-table la-md win98-icon" style="margin-right: 6px;"></i>
                    {self.content_type_title}
                </div>
            </div>
            
            <div class="win98-panel-inset" style="padding: 20px; text-align: center; background-color: var(--win98-gray);">
                <div style="margin: 20px auto; max-width: 300px;">
                    <i class="las la-info-circle win98-icon primary" style="font-size: 48px; margin: 0 auto 15px; display: block;"></i>
                    <h3 style="font-size: 14px; margin-bottom: 10px; font-weight: bold;">No {self.content_type_title} Found</h3>
                    <p style="font-size: 12px; margin-bottom: 20px;">Create your first {self.content_type_title.lower()} to get started.</p>
                    
                    <a href="/new/{self.content_type}">
                        <button class="win98-btn">
                            <i class="las la-plus la-sm win98-icon" style="margin-right: 4px;"></i>
                            Create {self.content_type_title}
                        </button>
                    </a>
                </div>
            </div>
        </div>
        """
    
    def _render_item(self, item, index):
        """
        Render a single item in the list
        
        Args:
            item (dict): The item to render
            index (int): The index of the item
            
        Returns:
            str: The rendered HTML for the item
        """
        # Extract item data
        id_value = item.get('id', '')
        title = item.get('title', 'Untitled')
        status = item.get('status', '')
        author = item.get('author', 'System')
        modified = item.get('modified', '')
        modified_display = self._format_date(modified)
        
        # Row classes - alternate rows for better readability
        row_class = "win98-table-row-alt" if index % 2 == 1 else "win98-table-row"
        
        # Windows 98 style row with pixelated borders and beveled effect
        return f"""
            <tr class="{row_class}" data-id="{id_value}">
                <td class="win98-table-cell text-left">
                    <a href="/view/{self.content_type}/{id_value}" style="color: var(--win98-dark-blue); text-decoration: none; font-weight: bold;">
                        {title}
                    </a>
                </td>
                <td class="win98-table-cell text-center">{status}</td>
                <td class="win98-table-cell text-center">{author}</td>
                <td class="win98-table-cell text-center">{modified_display}</td>
                <td class="win98-table-cell text-center">
                    <button class="win98-icon-btn" aria-label="View" onclick="window.location.href='/view/{self.content_type}/{id_value}';">
                        <i class="las la-eye"></i>
                    </button>
                    <button class="win98-icon-btn" aria-label="Edit" onclick="window.location.href='/edit/{self.content_type}/{id_value}';">
                        <i class="las la-edit"></i>
                    </button>
                    <button class="win98-icon-btn" aria-label="Delete" onclick="if(confirm('Are you sure you want to delete this item?')) window.location.href='/delete/{self.content_type}/{id_value}';">
                        <i class="las la-trash"></i>
                    </button>
                </td>
            </tr>
        """
    
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
    
    def render_content_types_menu(self, content_types):
        """
        Render a menu of content types
        
        Args:
            content_types (list): The content types to render
            
        Returns:
            str: The rendered HTML
        """
        menu_items = ""
        for content_type in content_types:
            title = content_type.replace('_', ' ').title()
            
            # Choose appropriate icon based on content type
            icon_class = "la-file"
            if "post" in content_type or "article" in content_type:
                icon_class = "la-file-alt"
            elif "image" in content_type or "photo" in content_type:
                icon_class = "la-image"
            elif "video" in content_type:
                icon_class = "la-video"
            elif "user" in content_type or "author" in content_type:
                icon_class = "la-user"
            elif "product" in content_type:
                icon_class = "la-box"
            elif "category" in content_type:
                icon_class = "la-folder"
            
            menu_items += f"""
            <div style="display: flex; align-items: center; margin-bottom: 6px; cursor: pointer;"
                 hx-get="/list/{content_type}" 
                 hx-target="#content-area" 
                 hx-push-url="true">
                <i class="las {icon_class} la-md win98-icon primary" style="margin-right: 5px;"></i>
                {title}
            </div>
            """
        
        return f"""
        <div class="win98-window" style="margin-bottom: 20px; width: 100%;">
            <div class="win98-window-title">
                <div style="display: flex; align-items: center;">
                    <i class="las la-list la-md win98-icon primary" style="margin-right: 6px;"></i>
                    Content Types
                </div>
            </div>
            
            <div style="padding: 15px;">
                <h3 style="font-size: 14px; margin-bottom: 10px;">Select a Content Type</h3>
                <div class="win98-separator"></div>
                <div style="margin-top: 10px;">
                    {menu_items}
                </div>
            </div>
        </div>
        """ 