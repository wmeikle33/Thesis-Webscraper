This project produces the following datasets:

1. `autohome_posts.csv` — main dataset of scraped Autohome blog posts.

## Dataset: `autohome_posts.csv`

**Location:** `data/raw/autohome_posts.csv`  
**Format:** CSV, UTF-8, comma-separated  
**Granularity:** One row per blog post scraped from Autohome.

### Columns

| Column name       | Type       | Description                                                                 | Example                                | Nullable |
|-------------------|------------|-----------------------------------------------------------------------------|----------------------------------------|----------|
| `post_id`         | string     | Internal unique ID for the post (e.g. extracted from URL or generated).    | `"2024-05-17_123456"`                  | No       |
| `url`             | string     | Full URL to the blog post.                                                 | `"https://club.autohome.com.cn/.../"`  | No       |
| `title`           | string     | Title of the blog post.                                                    | `"My experience with BYD Han EV"`      | No       |
| `author`          | string     | Display name / username of the author.                                     | `"EVfan2024"`                          | Yes      |
| `posted_at`       | datetime   | Published datetime (Beijing time).                                         | `"2024-05-17 13:42:00"`                | Yes      |
| `body_text`       | string     | Main text content of the post (HTML stripped).                             | `"I bought the Han EV last month..."`  | No       |
| `raw_html`        | string     | Raw HTML of the main content block (optional, for debugging).              | `<div class="post">...`                | Yes      |
| `model_tags`      | string[]   | List of car models mentioned, as comma-separated or JSON array.            | `"Han EV, Tang DM-i"`                  | Yes      |
| `num_comments`    | integer    | Number of comments shown at scrape time.                                   | `23`                                   | Yes      |
| `scraped_at`      | datetime   | When this page was scraped (UTC).                                          | `"2024-05-18 02:00:00"`                | No       |
