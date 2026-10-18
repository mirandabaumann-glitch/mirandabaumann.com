# mirandabaumann.com

Source for [mirandabaumann.com](https://mirandabaumann.com/), the personal professional website of Miranda L. Baumann, PhD.

The site is a single page that explains her current role, research expertise, professional background, selected publications, and contact information. It is a personal website, not an official website of the Georgia Department of Behavioral Health and Developmental Disabilities.

## What is here

| File | Purpose |
| --- | --- |
| `index.html` | All page content, including the page title, description, and structured data |
| `styles.css` | Layout, typography, and the light and dark color themes |
| `theme.js` | The light/dark toggle (about 50 lines; no libraries) |
| `favicon.svg` | Browser tab icon |
| `robots.txt`, `sitemap.xml` | Instructions for search engines |
| `_headers` | Security headers applied by Cloudflare Pages |
| `404.html` | "Page not found" page |
| `tests/check_site.py` | Automated checks (content, links, layout, themes, keyboard, contrast) |
| `docs/` | Implementation decisions, sanitized build brief, AI assistance note |

There is no framework, package manager, or build step. The files in this folder are exactly the files that are published.

## Hosting

- **Source:** this GitHub repository.
- **Hosting:** Cloudflare Pages, project `mirandabaumann-com`, connected to the `mirandabaumann.com` domain.
- **Publishing method:** direct upload. Cloudflare does **not** publish automatically when this repository changes. Every change is previewed and approved before it is published.

## Making a change (plain-language version)

1. **Ask for the change.** For example, in a Perplexity Computer task: "Update the publications on mirandabaumann.com to add …". The assistant edits the files, runs the checks, and shows you a preview.
2. **Review the preview.** Preview deployments get a separate `*.mirandabaumann-com.pages.dev` address. These addresses are publicly reachable if someone has the link, though they are not linked from anywhere.
3. **Approve publishing.** Only after you approve, the change is published to the live domain and committed to this repository.

Also update the "Last updated" line in the footer and the `<lastmod>` date in `sitemap.xml` when content changes.

## Editing by hand (optional)

1. On GitHub, open `index.html`, select the pencil icon, edit the text between the tags, and commit.
2. To preview on your own computer, download the repository and open `index.html` in a browser.
3. To publish, upload the folder in the Cloudflare dashboard: **Workers & Pages → mirandabaumann-com → Create deployment**, or run:
   ```
   npx wrangler pages deploy . --project-name mirandabaumann-com --branch main
   ```
   (Use `--branch preview` instead to make a preview without changing the live site.)

## Rolling back

If a published change has a problem: Cloudflare dashboard → **Workers & Pages → mirandabaumann-com → Deployments** → select the last good deployment → **Rollback to this deployment**. The live site switches back within seconds. Then fix or revert the change in this repository so the source matches what is live.

## Running the checks

```
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/check_site.py --links
```

Some sites (LinkedIn, Google Scholar, some publishers) refuse automated requests; the checker accepts those responses, so check those links by hand after changes.

## License

No license has been chosen. All rights reserved unless a license is added later.
