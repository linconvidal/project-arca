"""
Edit form component for Arca - provides a form for editing content items
with classic Windows 98 styling
"""

class EditForm:
    """
    Component for editing content items
    Styled with the classic Windows 98 aesthetic
    """
    
    def __init__(self, content_type, item=None, is_new=False):
        """
        Initialize the edit form
        
        Args:
            content_type (str): The type of content being edited
            item (dict, optional): The item to edit. Defaults to None.
            is_new (bool, optional): Whether this is a new item. Defaults to False.
        """
        self.content_type = content_type
        self.item = item or {}
        self.is_new = is_new
        
        # Set form properties
        self.content_type_title = content_type.replace('_', ' ').title()
        self.form_title = f"New {self.content_type_title}" if is_new else f"Edit {self.content_type_title}"
    
    def render(self):
        """
        Render the edit form with Windows 98 styling
        
        Returns:
            str: The rendered HTML
        """
        if not self.item:
            return self._render_not_found()
        
        # Extract common fields
        id_value = self.item.get('id', '')
        title = self.item.get('title', '')
        content = self.item.get('content', '')
        status = self.item.get('status', 'draft')
        tags = self.item.get('tags', [])
        tags_str = ', '.join(tags) if isinstance(tags, list) else tags
        
        # Form CSS
        form_css = """
            .win98-form {
                background-color: var(--win98-gray);
                padding: 15px;
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
                font-size: 12px;
            }
            
            .form-grid {
                display: grid;
                grid-template-columns: 100px 1fr;
                gap: 10px;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .form-label {
                font-weight: bold;
                color: var(--win98-black);
            }
            
            .form-control {
                padding: 4px 6px;
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
                font-size: 12px;
                border: 2px inset var(--win98-gray);
                background-color: var(--win98-white);
                color: var(--win98-black);
                outline: none;
                width: 100%;
            }
            
            .form-control:focus {
                outline: 1px dotted black;
            }
            
            .form-textarea {
                min-height: 200px;
                resize: vertical;
            }
            
            .form-select {
                padding: 2px;
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
                font-size: 12px;
                border: 2px inset var(--win98-gray);
                background-color: var(--win98-white);
                color: var(--win98-black);
                outline: none;
                width: 100%;
                height: 24px;
            }
            
            .form-actions {
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                margin-top: 15px;
            }
            
            .checkbox-container {
                display: inline-flex;
                align-items: center;
                gap: 5px;
            }
            
            .win98-checkbox {
                appearance: none;
                width: 13px;
                height: 13px;
                border: 2px inset var(--win98-gray);
                background-color: var(--win98-white);
                position: relative;
                cursor: pointer;
            }
            
            .win98-checkbox:checked::after {
                content: '✓';
                position: absolute;
                top: -2px;
                left: 1px;
                font-size: 11px;
                color: var(--win98-black);
            }
        """
        
        # Get the form fields HTML
        form_fields = self._render_form_fields()
        
        # Is this a new item or an existing one?
        form_title = "New " + self.content_type_title if self.is_new else "Edit " + self.content_type_title
        form_action = f"/{self.content_type}" if self.is_new else f"/{self.content_type}/{id_value}"
        
        # Render the form
        form_script = """
            // Add keyboard shortcuts for the form
            document.addEventListener('keydown', function(e) {
                // Escape key to cancel
                if (e.key === 'Escape') {
                    history.back();
                }
                
                // Ctrl+S to save
                if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    document.getElementById('edit-form').submit();
                }
            });
            
            // Focus on title field when form loads
            document.getElementById('title').focus();
        """
        
        return f"""
        <div class="win98-window">
            <div class="win98-window-title">
                <span>{form_title}</span>
                <div class="window-controls">
                    <button class="win98-btn" onclick="history.back()" title="Close">×</button>
                </div>
            </div>
            <div class="win98-panel-inset" style="padding: 1px;">
                <style>{form_css}</style>
                <form id="edit-form" class="win98-form" method="POST" action="{form_action}">
                    <input type="hidden" name="id" value="{id_value}">
                    {form_fields}
                    <div class="form-actions">
                        <button type="button" class="win98-btn" onclick="history.back()">
                            <i class="las la-times"></i> Cancel
                        </button>
                        <button type="submit" class="win98-btn">
                            <i class="las la-save"></i> Save
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="keyboard-shortcuts">
            <p>Keyboard shortcuts: <kbd>Esc</kbd> = Cancel, <kbd>Ctrl</kbd>+<kbd>S</kbd> = Save</p>
        </div>
        
        <script>
            {form_script}
        </script>
        """
    
    def _render_form_fields(self):
        """
        Render the form fields based on the content type
        
        Returns:
            str: The rendered HTML of the form fields
        """
        # Common fields for all content types
        title = self.item.get('title', '')
        content = self.item.get('content', '')
        status = self.item.get('status', 'draft')
        tags = self.item.get('tags', [])
        tags_str = ', '.join(tags) if isinstance(tags, list) else tags
        
        # Form fields HTML
        return f"""
            <div class="form-grid">
                <label class="form-label" for="title">Title:</label>
                <input type="text" id="title" name="title" value="{title}" class="form-control" required>
                
                <label class="form-label" for="status">Status:</label>
                <select id="status" name="status" class="form-select">
                    <option value="draft" {"selected" if status == "draft" else ""}>Draft</option>
                    <option value="pending" {"selected" if status == "pending" else ""}>Pending</option>
                    <option value="in progress" {"selected" if status == "in progress" else ""}>In Progress</option>
                    <option value="completed" {"selected" if status == "completed" else ""}>Completed</option>
                    <option value="published" {"selected" if status == "published" else ""}>Published</option>
                </select>
                
                <label class="form-label" for="tags">Tags:</label>
                <input type="text" id="tags" name="tags" value="{tags_str}" class="form-control" placeholder="Comma-separated tags">
            </div>
            
            <label class="form-label" for="content">Content:</label>
            <div style="margin-top: 5px;">
                <textarea id="content" name="content" class="form-control form-textarea">{content}</textarea>
            </div>
        """
    
    def _render_field(self, name, label, value="", field_type="text", required=False, description="", small=False, rows=5, options=None):
        """
        Render a form field with Windows 98 styling
        
        Args:
            name (str): The field name
            label (str): The field label
            value (str, optional): The field value. Defaults to "".
            field_type (str, optional): The field type. Defaults to "text".
            required (bool, optional): Whether the field is required. Defaults to False.
            description (str, optional): Field description. Defaults to "".
            small (bool, optional): Whether to use a small field. Defaults to False.
            rows (int, optional): Number of rows for textarea. Defaults to 5.
            options (list, optional): Options for select field. Defaults to None.
            
        Returns:
            str: The rendered HTML for the field
        """
        # Set field width based on small parameter
        width = "250px" if small else "100%"
        
        # Add required marker if needed
        required_marker = '<span style="color: red;">*</span>' if required else ''
        required_attr = 'required' if required else ''
        
        # Description HTML if provided
        description_html = f'<div style="font-size: 10px; color: #666; margin-top: 2px;">{description}</div>' if description else ''
        
        # Render different field types
        field_html = ""
        
        if field_type == "textarea":
            field_html = f"""
            <textarea 
                name="{name}" 
                id="{name}" 
                class="win98-input" 
                style="width: {width}; height: {rows * 18}px; font-size: 11px;" 
                {required_attr}
            >{value}</textarea>
            """
        elif field_type == "select":
            options_html = ""
            for option in options:
                selected = 'selected="selected"' if str(option['value']) == str(value) else ''
                options_html += f'<option value="{option["value"]}" {selected}>{option["label"]}</option>'
                
            field_html = f"""
            <select 
                name="{name}" 
                id="{name}" 
                class="win98-input" 
                style="width: {width}; font-size: 11px;" 
                {required_attr}
            >
                {options_html}
            </select>
            """
        else:  # Default to text input
            field_html = f"""
            <input 
                type="{field_type}" 
                name="{name}" 
                id="{name}" 
                value="{value}" 
                class="win98-input" 
                style="width: {width}; font-size: 11px;" 
                {required_attr}
            >
            """
        
        return f"""
        <div style="margin-bottom: 15px;">
            <label for="{name}" style="display: block; margin-bottom: 3px; font-size: 11px; font-weight: bold;">
                {label} {required_marker}
            </label>
            {field_html}
            {description_html}
        </div>
        """ 