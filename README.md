# Pikesh Maharjan — portfolio and blog

Personal portfolio at the site root and a separate Jekyll-powered blog under `/blog/`.

## Content structure

- `index.html`: professional portfolio
- `_posts/`: published Markdown articles
- `_drafts/post-template.md`: article template
- `_layouts/` and `_includes/`: reusable site components
- legal and trust pages: About, Contact, Privacy, Cookies, Terms and Disclaimer
- `ADSENSE.md`: inactive advertising configuration and consent requirements
- `CLOUDFLARE.md`: observed delivery setup and recommended manual checks

See `BLOGGING.md` for the publishing workflow.

## Local build

Requirements: Ruby, Bundler and Node.js.

```bash
bundle install
npm run configure:adsense
bundle exec jekyll build
npm run check:links
bundle exec jekyll serve
```

AdSense remains disabled when `ADSENSE_CLIENT_ID` is not supplied.

## Deployment

The production site currently uses GitHub Pages from the repository and Cloudflare for the custom domain. Changes should be proposed through a branch and pull request. Do not commit credentials or modify DNS and Cloudflare production settings without review.
