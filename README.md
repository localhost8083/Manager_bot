# Mars Manager — Discord community bot

24/7 Discord gateway bot for the [MarsAI](https://marsai.click) community server.

- Replies when **@mentioned** in watched channels (with per-channel conversation memory)
- Deletes messages containing **blocked words** (staff exempt)
- Explains **upstream API errors** pasted by users (once per error per channel per 10 min)
- Staff-only **announcements**: type `announce: <text>` in the staff channel → reposted to the announce channel with `@everyone`
- **Catch-up**: answers the newest unanswered mention it missed while offline
- All configuration (token, brain model, channels, blocked words) is polled live from a remote admin endpoint — no secrets in this repo, nothing to edit here

## Configuration

The bot is fully remote-configured. It polls an OpenAI-compatible admin endpoint every 60 s and live-reloads:

| Env var | Required | Description |
|---|---|---|
| `MARSAI_CRON_TOKEN` | yes | Bearer token for the config endpoint |
| `MARSAI_BOT_CONFIG_URL` | no | Config endpoint (default: `https://marsai.click/cron/discord-bot-config`) |

The config response provides: Discord bot token, brain (`base_url` + `api_key` + `model`, any OpenAI-compatible endpoint), watched/staff/announce channel IDs, staff role ID, blocked words, enabled flag.

## Deploy (bot-hosting.net / any Python host)

1. Runtime: **Python** (3.12+ recommended; any modern version works — no voice/audio deps)
2. Source: this GitHub repo, branch `main`
3. Start file: `bot.py`
4. Add env var `MARSAI_CRON_TOKEN` with your config-endpoint token
5. Discord Developer Portal → your bot → **enable the MESSAGE CONTENT privileged intent** (the bot retries every 5 min and logs until enabled)

That's it — all bot behavior is managed from the MarsAI admin panel, not from this repo.
