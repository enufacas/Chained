# =============================================================================
# Chained Blog Infrastructure - Cloud Storage + Cloud Run
# =============================================================================
# This configuration sets up infrastructure for serving AI-generated blog posts:
# - Cloud Storage bucket for blog content
# - Cloud Run service to serve the blog
#
# The blog-writer ADK agent writes posts to Cloud Storage, and they're served
# via Cloud Run with a clean URL structure.
# =============================================================================

# =============================================================================
# Cloud Storage Bucket for Blog Posts
# =============================================================================

resource "google_storage_bucket" "blog" {
  name          = "${var.project_id}-chained-blog"
  location      = var.region
  force_destroy = false

  # Enable website hosting
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }

  # CORS configuration for browser access
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type", "Cache-Control"]
    max_age_seconds = 3600
  }

  # Uniform bucket-level access for simpler IAM
  uniform_bucket_level_access = true

  # Versioning for content history
  versioning {
    enabled = true
  }

  # Lifecycle rule to clean up old versions after keeping 5 most recent
  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Make the bucket publicly readable
resource "google_storage_bucket_iam_member" "blog_public" {
  bucket = google_storage_bucket.blog.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Grant the ADK agents service account write access
resource "google_storage_bucket_iam_member" "blog_writer_access" {
  bucket = google_storage_bucket.blog.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.adk_agents.email}"
}

# =============================================================================
# Default Blog Content
# =============================================================================

# Create index.html for the blog
resource "google_storage_bucket_object" "blog_index" {
  name         = "index.html"
  bucket       = google_storage_bucket.blog.name
  content_type = "text/html"
  content      = <<-EOT
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chained AI Blog</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
                color: #fff;
                min-height: 100vh;
                padding: 2rem;
            }
            .container { max-width: 900px; margin: 0 auto; }
            header { text-align: center; margin-bottom: 3rem; }
            h1 { font-size: 2.5rem; margin-bottom: 1rem; }
            .subtitle { color: #888; font-size: 1.1rem; }
            .blog-list { display: grid; gap: 1.5rem; }
            .blog-card {
                background: rgba(255,255,255,0.05);
                border-radius: 12px;
                padding: 1.5rem;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .blog-card:hover { border-color: #00d4ff; }
            .blog-card h2 { font-size: 1.3rem; margin-bottom: 0.5rem; }
            .blog-card h2 a { color: #fff; text-decoration: none; }
            .blog-card h2 a:hover { color: #00d4ff; }
            .meta { color: #888; font-size: 0.9rem; }
            .empty { text-align: center; padding: 3rem; color: #888; }
            footer { text-align: center; margin-top: 3rem; color: #666; }
            footer a { color: #00d4ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🤖 Chained AI Blog</h1>
                <p class="subtitle">AI-generated insights on technology, research, and innovation</p>
            </header>
            <main id="blog-list" class="blog-list">
                <div class="empty">
                    <h2>🚀 Coming Soon</h2>
                    <p>Blog posts are generated automatically by our ADK A2A agents.</p>
                    <p>Check back soon for AI-generated content!</p>
                </div>
            </main>
            <footer>
                <p>Powered by <a href="https://github.com/enufacas/Chained">Chained</a> autonomous AI ecosystem</p>
            </footer>
        </div>
        <script>
            async function loadPosts() {
                try {
                    const resp = await fetch('./posts.json');
                    if (resp.ok) {
                        const posts = await resp.json();
                        if (posts.length > 0) renderPosts(posts);
                    }
                } catch(e) {}
            }
            function renderPosts(posts) {
                document.getElementById('blog-list').innerHTML = posts.map(p => `
                    <article class="blog-card">
                        <h2><a href="posts/$${p.slug}.html">$${p.title}</a></h2>
                        <p class="meta">📅 $${new Date(p.date).toLocaleDateString()} · ⏱️ $${p.readTime} min read</p>
                    </article>
                `).join('');
            }
            loadPosts();
        </script>
    </body>
    </html>
  EOT

  depends_on = [google_storage_bucket.blog]
}

# Create posts.json index
resource "google_storage_bucket_object" "blog_posts_json" {
  name         = "posts.json"
  bucket       = google_storage_bucket.blog.name
  content_type = "application/json"
  content      = "[]"

  # Don't overwrite if it already exists with actual posts
  lifecycle {
    ignore_changes = [content]
  }

  depends_on = [google_storage_bucket.blog]
}

# Create 404.html
resource "google_storage_bucket_object" "blog_404" {
  name         = "404.html"
  bucket       = google_storage_bucket.blog.name
  content_type = "text/html"
  content      = <<-EOT
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Page Not Found | Chained AI Blog</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                background: #0a0a1a; color: #fff;
                min-height: 100vh; display: flex;
                align-items: center; justify-content: center;
                text-align: center;
            }
            h1 { font-size: 4rem; margin-bottom: 1rem; }
            a { color: #00d4ff; }
        </style>
    </head>
    <body>
        <div>
            <h1>404</h1>
            <p>Page not found. <a href="/">Return to blog</a></p>
        </div>
    </body>
    </html>
  EOT

  depends_on = [google_storage_bucket.blog]
}

# Create posts directory marker
resource "google_storage_bucket_object" "blog_posts_dir" {
  name         = "posts/"
  bucket       = google_storage_bucket.blog.name
  content_type = "application/x-directory"
  content      = ""

  depends_on = [google_storage_bucket.blog]
}

# =============================================================================
# Outputs
# =============================================================================

output "blog_bucket_name" {
  description = "Name of the blog storage bucket"
  value       = google_storage_bucket.blog.name
}

output "blog_bucket_url" {
  description = "Public URL of the blog (direct Cloud Storage)"
  value       = "https://storage.googleapis.com/${google_storage_bucket.blog.name}"
}

output "blog_website_url" {
  description = "Website-style URL for the blog"
  value       = "https://storage.googleapis.com/${google_storage_bucket.blog.name}/index.html"
}
