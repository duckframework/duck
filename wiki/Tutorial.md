# 📚 Tutorial: Build Your First Duck App

Learn Duck by building a complete web application from scratch. This tutorial will guide you through creating a simple blog application.

---

## 🎯 What We'll Build

A simple blog with:
- Homepage listing all posts
- Individual post pages
- Admin interface to create posts
- Responsive design
- Real-time comment system

---

## 📋 Prerequisites

- Python 3.10+ installed
- Basic Python knowledge
- 30 minutes of your time

---

## 🚀 Step 1: Installation and Setup

### Install Duck

```bash
pip install git+https://github.com/duckframework/duck.git
```

### Create Project

```bash
duck makeproject myblog
cd myblog
```

### Start Server

```bash
duck runserver
```

Visit `http://localhost:8000` - you should see the Duck welcome page!

---

## 📝 Step 2: Create the Blog Model

### Define the Model

Edit or create `web/models.py` in your project root directory:

```python
from django.db import models
from django.utils import timezone

class Post(models.Model):
    """Blog post model"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    """Comment model"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author} on {self.post.title}'
```

### Create Database Tables

```bash
duck makemigrations
duck migrate
```

---

## 🏠 Step 3: Create the Homepage

### Create View

Edit `web/ui/pages/views.py`:

```python
from duck.shortcuts import render
from web.models import Post

def home(request):
    """Homepage showing all published posts"""
    posts = Post.objects.filter(published=True)
    
    return render(request, 'home.html', {
        'posts': posts,
        'title': 'My Blog'
    })
```

### Create Template

Create `web/ui/templates/home.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin-bottom: 0.5rem;
        }
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .post-card {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .post-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        .post-title {
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 1.5rem;
        }
        .post-title a {
            color: inherit;
            text-decoration: none;
        }
        .post-title a:hover {
            text-decoration: underline;
        }
        .post-meta {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .post-excerpt {
            line-height: 1.6;
            color: #555;
        }
        .no-posts {
            text-align: center;
            padding: 3rem;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦆 {{ title }}</h1>
        <p>A Duck Framework Blog</p>
    </div>
    
    <div class="container">
        {% if posts %}
            {% for post in posts %}
            <div class="post-card">
                <h2 class="post-title">
                    <a href="/post/{{ post.slug }}">{{ post.title }}</a>
                </h2>
                <div class="post-meta">
                    By {{ post.author }} • {{ post.created_at|date:"F d, Y" }}
                </div>
                <div class="post-excerpt">
                    {{ post.content|truncatewords:50 }}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-posts">
                <h2>No posts yet!</h2>
                <p>Create your first post in the admin panel.</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
```

### Add URL Route

Edit `web/urls.py`:

```python
from duck.routes import Path
from web.ui.pages.views import home

urlpatterns = [
    Path('/', home, name='home'),
]
```

---

## 📄 Step 4: Create Post Detail Page

### Create View

Add to `web/ui/pages/views.py`:

```python
from django.shortcuts import get_object_or_404

def post_detail(request, slug):
    """Display individual post"""
    post = get_object_or_404(Post, slug=slug, published=True)
    comments = post.comments.all()
    
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
    })
```

### Create Template

Create `web/ui/templates/post_detail.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ post.title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .nav {
            text-align: center;
            padding: 1rem;
        }
        .nav a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
        }
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .post {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .post-title {
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        .post-meta {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }
        .post-content {
            line-height: 1.8;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .comments {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #eee;
        }
        .comments-title {
            margin-bottom: 1.5rem;
            color: #667eea;
        }
        .comment {
            background: #f9f9f9;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        .comment-author {
            font-weight: bold;
            color: #667eea;
        }
        .comment-date {
            font-size: 0.8rem;
            color: #999;
        }
        .comment-content {
            margin-top: 0.5rem;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦆 My Blog</h1>
        <div class="nav">
            <a href="/">← Back to Home</a>
        </div>
    </div>
    
    <div class="container">
        <article class="post">
            <h1 class="post-title">{{ post.title }}</h1>
            <div class="post-meta">
                By {{ post.author }} • {{ post.created_at|date:"F d, Y" }}
            </div>
            <div class="post-content">
                {{ post.content|linebreaks }}
            </div>
        </article>
        
        <section class="comments">
            <h2 class="comments-title">Comments ({{ comments|length }})</h2>
            {% if comments %}
                {% for comment in comments %}
                <div class="comment">
                    <div>
                        <span class="comment-author">{{ comment.author }}</span>
                        <span class="comment-date">• {{ comment.created_at|date:"F d, Y" }}</span>
                    </div>
                    <div class="comment-content">
                        {{ comment.content }}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #999;">No comments yet. Be the first to comment!</p>
            {% endif %}
        </section>
    </div>
</body>
</html>
```

### Add URL Route

Update `web/urls.py`:

```python
from duck.routes import Path
from web.ui.pages.views import home, post_detail

urlpatterns = [
    Path('/', home, name='home'),
    Path('/post/<slug:slug>', post_detail, name='post_detail'),
]
```

---

## 👤 Step 5: Set Up Admin

### Register Models

Create `web/admin.py`:

```python
from django.contrib import admin
from web.models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published', 'created_at']
    list_filter = ['published', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author', 'content']
```

### Create Superuser

```bash
duck createsuperuser
```

Follow the prompts to create an admin account.

### Access Admin

Visit `http://localhost:8000/admin/` and log in with your credentials.

---

## 📝 Step 6: Create Some Posts

1. Go to `http://localhost:8000/admin/`
2. Click "Posts" → "Add Post"
3. Fill in:
   - Title: "Welcome to My Blog"
   - Slug: "welcome-to-my-blog"
   - Content: Write some content
   - Author: Your name
   - Published: ✓ (check this)
4. Save

Create 2-3 more posts to populate your blog.

---

## 🎉 Step 7: Test Your Blog

### View Homepage

Visit `http://localhost:8000/` - you should see all your published posts!

### View Post

Click on any post title to see the full post.

### Add Comments

In the admin, add some comments to posts to see them displayed.

---

## 🚀 Step 8: Add Real-Time Comments (Optional)

Let's make comments update in real-time using Lively Components!

### Create Comment Component

Create `web/components.py`:

```python
from duck.components import Component
from web.models import Comment

class CommentSection(Component):
    def __init__(self, post):
        super().__init__()
        self.post = post
        self.new_comment_author = ""
        self.new_comment_content = ""
    
    def add_comment(self):
        """Add a new comment"""
        if self.new_comment_author and self.new_comment_content:
            Comment.objects.create(
                post=self.post,
                author=self.new_comment_author,
                content=self.new_comment_content
            )
            # Clear form
            self.new_comment_author = ""
            self.new_comment_content = ""
            self.update()
    
    def render(self):
        comments = self.post.comments.all()
        
        comments_html = ''.join([
            f'''
            <div class="comment">
                <div>
                    <span class="comment-author">{comment.author}</span>
                    <span class="comment-date">• {comment.created_at.strftime("%B %d, %Y")}</span>
                </div>
                <div class="comment-content">{comment.content}</div>
            </div>
            '''
            for comment in comments
        ])
        
        return f'''
            <section class="comments">
                <h2 class="comments-title">Comments ({len(comments)})</h2>
                
                <div class="comment-form">
                    <input type="text" 
                           placeholder="Your name" 
                           value="{self.new_comment_author}"
                           oninput="component.new_comment_author = this.value">
                    <textarea placeholder="Your comment"
                              oninput="component.new_comment_content = this.value">{self.new_comment_content}</textarea>
                    <button onclick="component.add_comment()">Post Comment</button>
                </div>
                
                <div class="comments-list">
                    {comments_html if comments else '<p style="color: #999;">No comments yet. Be the first!</p>'}
                </div>
            </section>
        '''
```

### Update View

Modify `post_detail` view in `web/ui/pages/views.py`:

```python
from duck.shortcuts import render_component
from web.components import CommentSection

def post_detail(request, slug):
    """Display individual post"""
    post = get_object_or_404(Post, slug=slug, published=True)
    comment_section = CommentSection(post)
    
    return render(request, 'post_detail_live.html', {
        'post': post,
        'comment_section': comment_section,
    })
```

Now comments will update in real-time without page refresh!

---

## 🎨 Next Steps

Congratulations! You've built a functional blog with Duck. Here are some ideas to extend it:

### Easy Enhancements
- Add post categories/tags
- Add search functionality
- Add pagination for posts
- Add post images

### Intermediate Features
- User authentication for comments
- Rich text editor for posts
- Post likes/reactions
- Email notifications

### Advanced Features
- Full-text search with Elasticsearch
- Real-time collaborative editing
- Social media integration
- Analytics dashboard

---

## 📚 Learn More

Now that you've built your first app, explore:

- [Components Guide](Components) - Deep dive into Lively Components
- [Deployment Guide](Deployment) - Deploy your blog to production
- [Configuration](Configuration) - Customize your application
- [Django Integration](Django-Integration) - Add Duck to existing Django projects

---

## 🆘 Troubleshooting

### Server Won't Start
```bash
# Check if another process is using port 8000
duck runserver --port 8080
```

### Database Errors
```bash
# Re-run migrations
duck migrate
```

### Import Errors
```bash
# Ensure you're in the project directory
cd myblog
duck runserver
```

---

**Congratulations! You're now a Duck developer! 🦆**

Keep building amazing things!
