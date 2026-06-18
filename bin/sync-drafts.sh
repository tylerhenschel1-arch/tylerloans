#!/usr/bin/env bash
# Pull the latest drafts from GitHub and mirror them to the Desktop folder.
# Run this each morning (or set up a LaunchAgent to run it on login).
#
#   bin/sync-drafts.sh
#
# - Runs `git pull` in the repo
# - Copies any new _drafts/<...>/review.docx into ~/Desktop/Blog_Pipeline/draft/
# - Leaves files alone if they already exist (no overwriting your edits)
#
# Folder layout on Desktop after running:
#   ~/Desktop/Blog_Pipeline/draft/      <- new daily drafts land here
#   ~/Desktop/Blog_Pipeline/approved/   <- move drafts here when ready to publish
#   ~/Desktop/Blog_Pipeline/published/  <- moved here by the publisher

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PIPELINE_DIR="$HOME/Desktop/Blog_Pipeline"
DRAFT_DIR="$PIPELINE_DIR/draft"
APPROVED_DIR="$PIPELINE_DIR/approved"
PUBLISHED_DIR="$PIPELINE_DIR/published"

mkdir -p "$DRAFT_DIR" "$APPROVED_DIR" "$PUBLISHED_DIR"

echo "Pulling latest drafts from GitHub..."
git -C "$REPO_DIR" pull --rebase --quiet || git -C "$REPO_DIR" pull --rebase

shopt -s nullglob
copied=0
for d in "$REPO_DIR"/_drafts/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    src="$d/review.docx"
    [ -f "$src" ] || continue
    dest="$DRAFT_DIR/${name}.docx"
    if [ ! -e "$dest" ]; then
        cp "$src" "$dest"
        echo "  + $name.docx"
        copied=$((copied+1))
    fi
done

if [ "$copied" -eq 0 ]; then
    echo "No new drafts. Desktop folder is up to date."
else
    echo "Copied $copied new draft(s) to $DRAFT_DIR"
fi

open "$DRAFT_DIR" 2>/dev/null || true
