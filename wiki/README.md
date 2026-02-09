# Duck Framework Wiki

This directory contains the source files for the Duck Framework GitHub Wiki.

## 📚 Wiki Pages

The wiki includes the following pages:

1. **[Home](Home.md)** - Welcome page with overview and quick links
2. **[Getting Started](Getting-Started.md)** - Installation and first project guide
3. **[Features](Features.md)** - Comprehensive list of Duck's features
4. **[Configuration](Configuration.md)** - How to configure your Duck application
5. **[Components](Components.md)** - Guide to Lively Components system
6. **[Django Integration](Django-Integration.md)** - Integrate Duck with Django projects
7. **[Deployment](Deployment.md)** - Deploy Duck to production
8. **[Contributing](Contributing.md)** - How to contribute to Duck
9. **[FAQ](FAQ.md)** - Frequently asked questions

## 🚀 Publishing to GitHub Wiki

To publish these pages to the GitHub Wiki:

### Option 1: Manual Upload

1. Go to https://github.com/duckframework/duck/wiki
2. Click "New Page" or edit existing pages
3. Copy content from the respective `.md` files
4. Save each page

### Option 2: Using git-wiki

You can clone the wiki repository and push changes:

```bash
# Clone the wiki repository
git clone https://github.com/duckframework/duck.wiki.git

# Copy wiki files
cp wiki/*.md duck.wiki/

# Commit and push
cd duck.wiki
git add .
git commit -m "Update wiki pages"
git push origin master
```

### Option 3: Using gh CLI

```bash
# Install gh if not already installed
# Then use the API to create/update pages
```

## 📝 Writing Guidelines

When creating or editing wiki pages:

- Use clear, concise language
- Include code examples
- Add emojis for visual appeal (but don't overdo it)
- Use proper markdown formatting
- Link to related pages
- Keep content up-to-date
- Include practical examples

## 🎨 Formatting

- Use H1 (`#`) for page title
- Use H2 (`##`) for main sections
- Use H3 (`###`) for subsections
- Include horizontal rules (`---`) between major sections
- Use code blocks with language specification
- Use tables for comparisons
- Use blockquotes for important notes

## 🔗 Internal Links

Link to other wiki pages using:
```markdown
[Link Text](Page-Name)
```

For example:
```markdown
See the [Getting Started](Getting-Started) guide
```

## 🖼️ Images

To include images:
```markdown
![Alt text](https://raw.githubusercontent.com/duckframework/duck/main/images/image-name.png)
```

## ✅ Quality Checklist

Before publishing, ensure:

- [ ] All code examples are tested and working
- [ ] Links are valid and point to correct locations
- [ ] Spelling and grammar are correct
- [ ] Content is accurate and up-to-date
- [ ] Examples follow best practices
- [ ] Page is well-structured and easy to navigate
- [ ] Images (if any) are displaying correctly

## 🔄 Keeping Wiki Updated

The wiki should be updated when:

- New features are added to Duck
- APIs change
- Best practices evolve
- User feedback suggests improvements
- Bugs in documentation are found

## 📧 Questions?

If you have questions about the wiki content or structure:

- Open an issue on GitHub
- Ask in GitHub Discussions
- Contact the maintainers

---

**Note:** These wiki pages are designed to be attractive, simple, and comprehensive. They serve as the main documentation entry point for new users while providing detailed information for advanced users.
