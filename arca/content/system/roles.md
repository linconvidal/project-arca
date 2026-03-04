---
id: system_roles
title: "User Roles and Permissions"
updated_at: "2023-03-04"
---

# User Roles and Permissions

This configuration defines the user roles and their associated permissions in the Arca system.

## Available Roles

```yaml
roles:
  - id: admin
    name: "Administrator"
    description: "Full system access with all permissions"

  - id: editor
    name: "Editor"
    description: "Can create, edit, and publish content"

  - id: author
    name: "Author"
    description: "Can create and edit their own content, but cannot publish"

  - id: contributor
    name: "Contributor"
    description: "Can create content drafts only"

  - id: viewer
    name: "Viewer"
    description: "Read-only access to published content"
```

## Permission Assignments

```yaml
permissions:
  admin:
    - manage_users
    - manage_roles
    - manage_system
    - create_content
    - edit_any_content
    - publish_content
    - delete_content
    - manage_comments
    - view_analytics
    - manage_media
    - manage_menus
    - manage_taxonomies

  editor:
    - create_content
    - edit_any_content
    - publish_content
    - delete_own_content
    - manage_comments
    - view_analytics
    - manage_media
    - manage_menus
    - manage_taxonomies

  author:
    - create_content
    - edit_own_content
    - delete_own_content
    - manage_own_media
    - view_own_analytics

  contributor:
    - create_content
    - edit_own_draft_content
    - manage_own_media

  viewer:
    - view_published_content
```

## Permission Definitions

```yaml
permission_details:
  manage_users:
    description: "Create, edit, and delete user accounts"

  manage_roles:
    description: "Assign and modify user roles"

  manage_system:
    description: "Change system configurations"

  create_content:
    description: "Create new content items"

  edit_own_content:
    description: "Edit content created by the user"

  edit_any_content:
    description: "Edit all content regardless of author"

  edit_own_draft_content:
    description: "Edit only draft content created by the user"

  publish_content:
    description: "Change content status to published"

  delete_own_content:
    description: "Delete content created by the user"

  delete_content:
    description: "Delete any content regardless of author"

  manage_comments:
    description: "Moderate and delete comments"

  view_analytics:
    description: "Access all site analytics"

  view_own_analytics:
    description: "Access analytics for own content only"

  manage_media:
    description: "Upload and manage all media files"

  manage_own_media:
    description: "Upload and manage own media files only"

  manage_menus:
    description: "Create and edit navigation menus"

  manage_taxonomies:
    description: "Create and edit categories and tags"

  view_published_content:
    description: "View content with published status"
```
