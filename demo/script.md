# 60-Second Demo: sol-agent-wallet

Show: Claude Desktop → "swap 0.1 SOL for USDC" → transaction lands → Solscan opens.

## Setup (do this once, before recording)

1. Create a fresh **devnet** burner wallet. Export its base58 key.
2. Fund it with devnet SOL via `solana airdrop 2 <pubkey> --url devnet`.
3. Make sure Claude Desktop is configured with:
   ```json
   {
     "mcpServers": {
       "sol-agent-wallet": {
         "command": "uvx",
         "args": ["sol-agent-wallet"],
         "env": {
           "SOLANA_PRIVATE_KEY": "your_burner_base58_key",
           "SOLANA_NETWORK": "devnet"
         }
       }
     }
   }
   ```
4. Restart Claude Desktop. Verify it sees the tools by asking "what Solana tools do you have?".
5. Close all unrelated windows. Set wallpaper to plain dark grey. Hide menu bar (System Settings → Control Center → Auto-hide).
6. Quit Slack, Messages, mail — kill any notification source.

## Shot list (60s total budget)

| Time | Shot | What's on screen |
|---|---|---|
| 0–3s | Title card | "sol-agent-wallet" + "Claude can finally swap on Solana" |
| 3–8s | Claude Desktop empty | Cursor in the input box. Show the model picker if you want (subtle branding). |
| 8–18s | Type the prompt | Type at human speed: `swap 0.1 SOL for USDC on devnet`. Hit enter. |
| 18–32s | Tool approval | Claude shows the `sol_swap` tool call panel. Pause 2s so viewers can read the args. Click Approve. |
| 32–46s | Result lands | Claude responds with the ✅ message. Pause 1s. Cursor moves to the Solscan link. |
| 46–55s | Solscan opens | New tab. Show the confirmed transaction page. Highlight the swap instruction. |
| 55–60s | Outro card | `uvx sol-agent-wallet` + github.com/yksanjo/sol-agent-wallet |

**Pacing rules:**
- Don't speed-edit. Pauses where the viewer needs to read are not dead air.
- No background music. The terminal/UI is the story.
- Cursor should always be a real cursor, not a synthetic one — viewers spot it instantly.

## Recording

**Tool:** macOS screen recording (Cmd-Shift-5) for 1440x900 @ 30fps. Or **Kap** if you want a tighter crop without re-encoding.

```bash
# After recording, the raw file will be in ~/Desktop/Screen Recording <date>.mov
# Rename it to demo-raw.mov and move to demo/:
mv ~/Desktop/Screen\ Recording*.mov demo/demo-raw.mov
```

## Encoding

Two outputs: an optimized GIF for README inlining (Markdown renderers honor GIFs but not MP4s), and an MP4 for the X / LinkedIn / Discord posts.

### Optimized GIF (~3–5 MB target)

Two-pass palette generation gives a much smaller and cleaner GIF than the default conversion.

```bash
# Pass 1: build a palette tuned for the actual colors in the video
ffmpeg -y -i demo/demo-raw.mov \
  -vf "fps=15,scale=900:-1:flags=lanczos,palettegen=stats_mode=diff" \
  demo/palette.png

# Pass 2: render the GIF using that palette
ffmpeg -y -i demo/demo-raw.mov -i demo/palette.png \
  -lavfi "fps=15,scale=900:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
  demo/demo.gif

# Final size check — GitHub renders GIFs up to 10 MB inline, but 5 MB is faster
ls -lh demo/demo.gif
```

If it's still over ~5 MB, drop fps to 12 or scale to 800. Don't drop quality below `bayer_scale=5` — flat areas start to band.

### MP4 (for socials)

```bash
# H.264, 30fps, 1080p max width, two-pass for size/quality
ffmpeg -y -i demo/demo-raw.mov \
  -vf "scale='min(1920,iw)':-2:flags=lanczos,fps=30" \
  -c:v libx264 -preset slow -crf 22 \
  -movflags +faststart \
  -an \
  demo/demo.mp4

ls -lh demo/demo.mp4
```

**Twitter/X caps:** 512 MB, 140s max. We're well under both.
**LinkedIn caps:** 5 GB, 10 min. Fine.
**Discord:** 25 MB free tier — if you blow past, host on the GitHub release assets and link.

## Sanity checks before publishing

- [ ] Did you blur out the burner wallet's private key if it ever flashed?
- [ ] Did Claude Desktop's settings panel reveal anything (other configured MCP servers, user info)?
- [ ] Does the GIF loop cleanly, or does it cut on the outro card?
- [ ] Does the MP4 play in Safari, Chrome, and a phone's native player?
- [ ] Is the Solscan link in the recording on devnet (`?cluster=devnet`)?  *(If using mainnet for the recording: triple-check you only sent dust.)*

## Hosting

Commit `demo.gif` and `demo.mp4` to the repo under `demo/`. The README references `demo/demo.gif`. Don't put either in `.gitignore`.

For the social posts, upload natively (X, LinkedIn, Discord all kill GitHub-hosted links in their preview cards).
