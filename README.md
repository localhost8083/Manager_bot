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

## Features

- Replies when **@mentioned** in watched channels (with per-channel conversation memory) — in the language the user writes (Bangla/English/Hindi)
- Answers **DMs** (one message per user per 5 min — hard anti-abuse floor)
- Welcomes **new members** in the server's system channel
- Posts a **daily tip** (UTC date rotation) to the announce channel
- `/status` slash command — ephemeral brain-chain health report (which models are cooling, fallback count since boot)
- Deletes messages containing **blocked words** (staff exempt)
- Explains **upstream API errors** pasted by users (once per error per channel per 10 min)
- Staff-only **announcements**: type `announce: <text>` in the staff channel → reposted to the announce channel with `@everyone`
- **Catch-up**: answers the newest unanswered mention it missed while offline
- **Brain fallback chain**: configure several models (comma separated) in the admin panel; the bot tries them in order and fails over on network errors, HTTP ≥ 400, or HTTP-200-with-empty-content; failed models get a 5-minute cooldown
- All configuration (token, brain, channels, blocked words) is polled live from a remote admin endpoint — no secrets in this repo, nothing to edit here

## Configuration

The bot is fully remote-configured. It polls an OpenAI-compatible admin endpoint every 60 s and live-reloads:

| Env var | Required | Description |
|---|---|---|
| `MARSAI_CRON_TOKEN` | yes | Bearer token for the config endpoint |
| `MARSAI_BOT_CONFIG_URL` | no | Config endpoint (default: `https://marsai.click/cron/discord-bot-config`) |

The config response provides: Discord bot token, brain (`base_url` + `api_key` + `model` + `models` fallback list, any OpenAI-compatible endpoint), watched/staff/announce channel IDs, staff role ID, blocked words, enabled flag.

## Deploy (bot-hosting.net / any Python host)

1. Runtime: **Python** (3.12+ recommended; any modern version works — no voice/audio deps)
2. Source: this GitHub repo, branch `main`
3. Start file: `bot.py`
4. Add env var `MARSAI_CRON_TOKEN` with your config-endpoint token
5. Discord Developer Portal → your bot → enable **both privileged intents**: MESSAGE CONTENT and SERVER MEMBERS

That's it — all bot behavior is managed from the MarsAI admin panel, not from this repo.

## Self-check

`python tests_brain.py` — stubs discord + urllib, verifies the fallback chain (failover order, empty-content detection, cooldown skip/expiry, retry-all-when-cooling, legacy single-model configs, total-failure raise). Exits 0 on pass.
