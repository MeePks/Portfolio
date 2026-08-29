# Publishing blog articles

The portfolio remains at the site root. Blog content lives separately under `/blog/`.

## Create a post

1. Copy `_drafts/post-template.md`.
2. Rename it using `YYYY-MM-DD-short-title.md`.
3. Move the copy into `_posts/`.
4. Replace the front matter and article text.
5. Add the cover image under `assets/img/blog/`.
6. Commit the Markdown file and image.

Example filename:

```text
_posts/2026-09-05-indra-jatra-visitor-guide.md
```

GitHub Pages rebuilds the site automatically. The article then appears on the blog index and its category archive.

## Front-matter fields

| Field | Required | Purpose |
| --- | --- | --- |
| `title` | Yes | Article headline |
| `description` | Yes | Listing and search description |
| `date` | Yes | Publication date |
| `categories` | Yes | One or more archive categories |
| `location` | No | Destination or event location |
| `cover_image` | Recommended | Root-relative cover path |
| `cover_alt` | Required with image | Accessible image description |
| `cover_caption` | No | Credit or context |
| `youtube_id` | No | ID used for the privacy-enhanced embed |
| `youtube_url` | No | Full link for the watch-on-YouTube button |
| `youtube_title` | Recommended with video | Accessible iframe title |
| `reading_time` | No | Manual reading-time estimate |

## YouTube IDs

For this URL:

```text
https://www.youtube.com/watch?v=abc123XYZ
```

use:

```yaml
youtube_id: "abc123XYZ"
youtube_url: "https://www.youtube.com/watch?v=abc123XYZ"
```

## Images

Use WebP or optimized JPEG images. A practical target is:

- 1600px maximum width
- less than 300 KB when possible
- descriptive lowercase filenames
- accurate `cover_alt` text

Only publish photographs you own or have permission to use. Credit other creators when required.

## Jatra and cultural articles

Separate personal observation from historical claims. Verify dates each year because many festival dates follow a lunar calendar. Cite official, academic, community, or other reliable sources, and document etiquette and photography restrictions where relevant.

## Preview locally

With Ruby and Bundler installed:

```bash
bundle install
bundle exec jekyll serve
```

Open `http://localhost:4000/blog/`.
