# Cloudflare review

Observed on 29 August 2026:

- HTTP `www` redirects to HTTPS `www`.
- HTTPS apex redirects to HTTPS `www`.
- HTTP apex first redirects to HTTPS apex and then to `www`; a single-hop redirect would be preferable.
- HTTPS is active.
- Cloudflare and GitHub Pages caching are active.
- The checked HTML responses did not expose a complete set of recommended security headers.
- Cloudflare currently adds content-signal text to `robots.txt`.

No DNS, redirect, cache or security setting was changed by this branch.

## Recommended settings to review manually

1. Keep `https://www.pikeshmaharjan.com.np` as the only canonical host.
2. Use one redirect rule that sends both HTTP and apex-host requests directly to the canonical HTTPS `www` URL while preserving path and query string.
3. Use Full (strict) SSL/TLS when the GitHub Pages origin certificate path is valid.
4. Keep Brotli or equivalent compression enabled.
5. Cache immutable versioned assets aggressively, but do not create long edge caching for HTML while content is changing.
6. Add response headers after testing:
   - `X-Content-Type-Options: nosniff`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Permissions-Policy` limiting unused browser features
   - `Content-Security-Policy` tailored to GitHub Pages, Google Fonts, YouTube, Cloudflare and—only after activation—Google advertising domains
7. Avoid duplicate Cloudflare and repository sitemap or robots transformations. Confirm the final public `robots.txt` includes the sitemap directive.
8. Purge only affected URLs after a deployment; avoid destructive global cache changes unless necessary.

Test security headers and redirects before enforcing a strict Content Security Policy, because AdSense and embedded video domains require explicit allowances.
