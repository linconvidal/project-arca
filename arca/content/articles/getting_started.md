---
id: getting_started
title: "Getting Started with Arca"
status: "published"
author: "jane_smith"
date: "2023-03-01"
tags:
  - documentation
  - tutorial
  - beginners
---

# Getting Started with Arca

Welcome to Arca! This guide will walk you through the basics of setting up and using our file-based content management system.

## Installation

Arca can be installed in several ways, depending on your preferences:

### 1. Docker Installation (Recommended)

```bash
docker pull arcacms/arca:latest
docker run -p 3000:3000 -v /path/to/content:/app/content arcacms/arca:latest
```

### 2. NPM Installation

```bash
npm install -g @arcacms/cli
arca init my-site
cd my-site
arca dev
```

### 3. Manual Installation

```bash
git clone https://github.com/arcacms/arca.git
cd arca
npm install
npm run build
npm start
```

## Creating Your First Content

Once Arca is running, you can start creating content:

1. Visit `http://localhost:3000/admin` in your browser
2. Log in with the default credentials (admin/admin)
3. Click "New Content" and select a content type
4. Fill in the required fields and save

Alternatively, you can create content directly by adding Markdown files to the appropriate directories:

```markdown
---
id: my_first_post
title: "My First Post"
status: "draft"
author: "your_username"
date: "2023-03-01"
---

# Hello World

This is my first post using Arca!
```

## Customizing Your Site

Arca uses a simple theme system based on templates and CSS. To customize your site:

1. Create a `themes` directory in your project root
2. Create a new theme folder inside, e.g., `themes/my-theme`
3. Add template files to override the defaults

A basic theme structure looks like:

```
themes/my-theme/
├── templates/
│   ├── page.html
│   ├── article.html
│   └── home.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── theme.yaml
```

## Next Steps

- [Explore the content model](/docs/content-model)
- [Learn about templates](/docs/templates)
- [Set up user permissions](/docs/permissions)
- [Configure webhooks](/docs/webhooks)

Happy content creating!
