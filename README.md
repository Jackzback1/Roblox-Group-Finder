# Roblox Group Finder

Simple Python script that scans a Roblox group ID range and sends matching ownerless groups to a Discord webhook.

## What it checks
A group is reported only when all of these are true:
- Group exists
- Group is not locked
- Public entry is allowed
- Group has no owner

## Setup
1. Install dependencies:
   ```bash
   pip install requests dhooks
   ```
   `dhooks` is optional; if missing, webhook messages are sent with plain `requests`.

2. Run:
   ```bash
   python main.py
   ```

3. Provide:
   - Discord webhook URL
   - Number of worker threads
   - Group ID range (for example `20243-345354`)

## Notes
- Higher thread counts can cause rate limiting.
- Stop with `Ctrl+C`.
