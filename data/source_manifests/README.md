# RoleLens source manifests

Checked on 2026-09-26 (individual entries retain their check date). These are source links and short author-written descriptions, not scraped source text.

## Files

- `pm_v2_source_candidates.json`: 18 checked PM-specific job posting URLs, five AI PM and 13 commercial/ads/monetization PM. Ten unique links inform the original fictional v2 evaluation cards; the file contains no source JD body.
- `jd_sources.json`: earlier broad PM source scan with 30 posting URLs: 10 OpenAI, 16 Anthropic, four Perplexity. These are background links, not 30 collected JD texts or the v2 evaluation set.
- `ai_docs.json`: 20 official AI documentation URLs: 10 OpenAI, five Anthropic, five Google AI.
- `commercial_knowledge_sources.json`: ten official Google Ads, Amazon Ads, TikTok Ads, Stripe and Spotify Ads documentation or guide URLs with author-written PM-use summaries.

## Verification

The 18 targeted PM postings and all 30 knowledge documents were checked at their official pages. In the earlier broad scan, OpenAI and Anthropic posting detail pages were opened directly and showed the listed title and an Apply control. Perplexity's four URLs and titles came from its public Ashby posting API; its JavaScript-rendered detail pages could not be read independently in the text-only browser. The separate status and verification_method fields preserve that distinction. Listings and documentation may change after the checked date; recheck before use.

The documentation summaries are original short paraphrases for finding relevant reading. These source manifests contain no official job description or documentation article text, personal resumes, or candidate data. Do not present an API-listed Perplexity posting as a directly verified detail page.
