# Blog Pipeline — Daily Drafts to Live Site

End-to-end workflow: AI generates a draft → Tyler proofreads → records video → uploads to Submagic → posts to YouTube → publishes to live site with embedded video.

---

## Daily workflow at a glance

```
7 AM CST     GitHub Action runs blog_agent.py
             → drops draft into _drafts/YYYY-MM-DD_<slug>/
             → pushes to main branch
             → Cloudflare ignores _drafts/ (only blog/ is published)

Morning      Tyler runs: bin/sync-drafts.sh
             → pulls latest from GitHub
             → copies new review.docx files to ~/Desktop/Blog_Pipeline/draft/
             → opens Finder so you can see them

Anytime      Tyler opens draft .docx, proofreads
             → runs through CMG AI specialist if needed
             → marks DELETE if it shouldn't publish, EDIT if changes needed

Anytime      Tyler records 60-second video reading the script
             → uploads raw mp4 to Submagic (https://submagic.co)
             → downloads polished mp4 with captions + b-roll
             → uploads to YouTube as Unlisted or Public
             → copies the YouTube URL

Anytime      Tyler runs:
                bin/publish.py <slug> --video <youtube-url>
             → embeds video at the top of the post
             → moves HTML from _drafts/ to blog/
             → updates posts.json + sitemap.xml
             → commits and pushes
             → Cloudflare auto-deploys in ~30 seconds
```

---

## One-time setup

### 1. Make scripts executable

```bash
chmod +x bin/sync-drafts.sh bin/publish.py
```

### 2. Install local Python deps for publishing

```bash
pip3 install python-docx
```
(That's all — `publish.py` doesn't need the Anthropic SDK; the GitHub Action handles AI generation.)

### 3. (Optional) Auto-pull drafts in the morning via LaunchAgent

If you want the Desktop folder to refresh automatically when you wake your Mac, create `~/Library/LaunchAgents/com.tylerloans.sync-drafts.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tylerloans.sync-drafts</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/tyler/tylerloans/bin/sync-drafts.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/sync-drafts.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/sync-drafts.err</string>
</dict>
</plist>
```

Then load it:

```bash
launchctl load ~/Library/LaunchAgents/com.tylerloans.sync-drafts.plist
```

This runs every day at 7:15 AM (right after the GitHub Action's 7 AM run).

---

## Reference

### File structure inside `_drafts/<YYYY-MM-DD>_<slug>/`

```
_drafts/2026-05-25_first-time-homebuyer-mistakes-to-avoid-in-houston-tx-i/
├── index.html       # Pre-rendered blog page (publisher promotes this to blog/)
├── body.html        # Just the article body (Claude output, no chrome)
├── meta.json        # Topic, slug, date, meta description
└── review.docx      # The doc you proofread (video script + post body)
```

### Inside review.docx

- H1: Post title
- "Publish date:", "Slug:", "Status:", "Paste YouTube URL here:"
- H2: 🎬 60-Second Video Script (147–167 words you read on camera)
- H2: 📝 Blog Post (the actual article body)
- H2: FAQ (3 Q&As)

### `bin/publish.py` usage

```bash
# Publish with embedded video
bin/publish.py 2026-05-25_first-time-homebuyer-mistakes-to-avoid-in-houston-tx-i \
  --video https://youtu.be/AbCdEfGhIjK

# Or use the slug only (script searches _drafts/)
bin/publish.py first-time-homebuyer-mistakes --video https://youtu.be/AbCdEfGhIjK

# Publish without a video (you can add it later by editing blog/<slug>/index.html)
bin/publish.py first-time-homebuyer-mistakes

# Commit but don't push (review locally first)
bin/publish.py first-time-homebuyer-mistakes --video https://youtu.be/AbCdEfGhIjK --no-push
```

The publisher accepts any of these video formats:
- `https://youtu.be/AbCdEfGhIjK`
- `https://www.youtube.com/watch?v=AbCdEfGhIjK`
- `https://www.youtube.com/shorts/AbCdEfGhIjK`
- Just the ID: `AbCdEfGhIjK`

---

## Pause / resume the daily generator

- **Pause:** comment out the `schedule:` block in `.github/workflows/daily-blog.yml`, commit, push.
- **Resume:** uncomment, commit, push.
- **Manual one-off run:** GitHub → Actions → "Daily Blog Draft" → "Run workflow".

---

## Troubleshooting

**"Multiple matches" when running publish.py** — be more specific: include the date prefix or part of the slug that's unique.

**Video isn't showing up** — verify the URL is valid (`bin/publish.py` extracts the ID; if it can't parse it, it skips the embed and tells you).

**`_drafts/` folder is empty after `sync-drafts.sh`** — run `git -C ~/tylerloans pull` manually and check `_drafts/`. If empty, the GitHub Action may have failed; check Actions tab.

**Want to discard a draft entirely** — just `rm -rf _drafts/<folder>/` and `git push`. No need to publish it.
