---
id: system_config
title: "System Configuration"
updated_at: "2023-03-04"
---

# Arca System Configuration

## General Settings

```yaml
site_name: "Arca Documentation"
site_url: "https://docs.arcacms.org"
admin_email: "admin@arcacms.org"
default_locale: "en-US"
available_locales:
  - "en-US"
  - "fr-FR"
  - "es-ES"
  - "de-DE"
timezone: "UTC"
date_format: "YYYY-MM-DD"
time_format: "HH:mm:ss"
```

## Content Settings

```yaml
default_content_license: "CC BY-SA 4.0"
max_upload_size: 5242880 # 5MB
allowed_file_types:
  - image/jpeg
  - image/png
  - image/gif
  - image/svg+xml
  - application/pdf
  - text/plain
  - text/markdown
  - text/csv
media_storage_path: "public/media"
```

## User Authentication

```yaml
auth_providers:
  local: true
  github: true
  google: false
  facebook: false
session_expiry: 86400 # 24 hours
password_requirements:
  min_length: 10
  require_uppercase: true
  require_lowercase: true
  require_number: true
  require_special: true
```

## Email Settings

```yaml
smtp_host: "smtp.example.com"
smtp_port: 587
smtp_secure: true
smtp_user: "notifications@arcacms.org"
notification_templates:
  welcome: "templates/email/welcome.html"
  password_reset: "templates/email/password_reset.html"
  content_approved: "templates/email/content_approved.html"
```

## Performance

```yaml
cache_enabled: true
cache_expiry: 300 # 5 minutes
image_optimization: true
minify_html: true
gzip_compression: true
```

## Backups

```yaml
auto_backup: true
backup_interval: 86400 # 24 hours
backup_retention: 30 # days
backup_location: "/backups"
```
