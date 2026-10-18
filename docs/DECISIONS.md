# Implementation decisions

Short record of consequential choices. Newest at the bottom.

1. **Plain HTML, CSS, and a small script.** No framework, dependencies, or build step. A one-page profile does not need them, and this keeps maintenance close to zero.
2. **Cloudflare Pages with direct upload, not Git-triggered deployment.** The domain is already on Cloudflare. Direct upload means a commit to this repository never publishes by itself, which keeps the rule that every change is previewed and approved first.
3. **One page with section links.** Current role first; current position visually separated from previous positions.
4. **Third-person biography.** Reads naturally to visitors, search engines, and AI tools.
5. **Text only.** No headshot, logos, seals, or images, to avoid any appearance of official agency branding.
6. **Light and dark themes.** Follows the device setting by default. A manual choice is saved in the browser (localStorage) when allowed. The saved choice is applied in `<head>` before the page paints to avoid a flash. Without JavaScript, the toggle is hidden and the page follows the device setting.
7. **Single purple accent.** `#5b2a86` on white and `#c9a7f0` on charcoal (both above 8:1 contrast). The only "sheen" is a thin static gradient rule under the name.
8. **System fonts.** No web-font downloads; faster and nothing to maintain.
9. **Structured data limited to visible facts.** Name, PhD, title, employer, university, site URL, and the LinkedIn, Google Scholar, and ORCID links shown on the page.
10. **No analytics scripts.** Cloudflare's built-in traffic statistics only.
11. **Strict security headers** (`_headers`): no inline scripts or styles, no framing, no forms.
12. **Publications link to DOIs.** No publisher PDFs are hosted.
13. **Email addresses exempt from Cloudflare Email Obfuscation.** Cloudflare's default obfuscation replaced the addresses with "[email protected]" for readers without JavaScript (including search engines and AI tools). The Contact list is wrapped in `<!--email_off-->` comments so the approved, visible addresses are served as written.
