import random
import threading
import time
from dataclasses import dataclass

import requests

try:
    from dhooks import Webhook as DhooksWebhook
except Exception:
    DhooksWebhook = None


@dataclass
class Config:
    webhook_url: str
    thread_limit: int
    range_start: int
    range_end: int


class WebhookClient:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self._dhooks = DhooksWebhook(webhook_url) if DhooksWebhook else None

    def send(self, message: str) -> None:
        if self._dhooks:
            self._dhooks.send(message)
            return

        response = requests.post(
            self.webhook_url,
            json={"content": message},
            timeout=10,
        )
        response.raise_for_status()


def find_group(session: requests.Session, config: Config, webhook: WebhookClient) -> None:
    group_id = random.randint(config.range_start, config.range_end)

    try:
        response = session.get(
            f"https://groups.roblox.com/v1/groups/{group_id}",
            timeout=10,
        )

        if response.status_code != 200:
            print(f"[-] Group not found: {group_id}")
            return

        payload = response.json()

        if payload.get("isLocked"):
            print(f"[-] Group locked: {group_id}")
            return

        if not payload.get("publicEntryAllowed"):
            print(f"[-] No public entry: {group_id}")
            return

        if payload.get("owner") is not None:
            print(f"[-] Group owned: {group_id}")
            return

        url = f"https://www.roblox.com/groups/{group_id}"
        webhook.send(f"Hit: {url}")
        print(f"[+] Hit: {group_id}")

    except requests.RequestException as exc:
        print(f"[!] Network error for {group_id}: {exc}")
    except ValueError as exc:
        print(f"[!] Failed to parse response for {group_id}: {exc}")


def worker(config: Config, webhook: WebhookClient) -> None:
    with requests.Session() as session:
        while True:
            find_group(session, config, webhook)


def ask_config() -> Config:
    print(
        """
____ _    ____ _  _ ____    ____ ____ ____ _  _ ___
|__| |    |___ |_/  [__     | __ |__/ |  | |  | |__]
|  | |___ |___ | \_ ___]    |__] |  \ |__| |__| |

____ _ _  _ ___  ____ ____
|___ | |\ | |  \ |___ |__/
|    | | \| |__/ |___ |  \
"""
    )

    webhook_url = input("[-] Enter your webhook URL: ").strip()
    threads = int(input("[-] How many threads: ").strip() or "25")

    raw_range = input("[-] Group ID range (start-end, default 1000000-1150000): ").strip()
    if raw_range:
        start_str, end_str = raw_range.split("-", maxsplit=1)
        range_start, range_end = int(start_str), int(end_str)
    else:
        range_start, range_end = 1_000_000, 1_150_000

    if range_start >= range_end:
        raise ValueError("Range start must be less than range end")

    return Config(
        webhook_url=webhook_url,
        thread_limit=threads,
        range_start=range_start,
        range_end=range_end,
    )


def main() -> None:
    config = ask_config()
    webhook = WebhookClient(config.webhook_url)

    for _ in range(config.thread_limit):
        t = threading.Thread(target=worker, args=(config, webhook), daemon=True)
        t.start()

    print(f"[*] Started {config.thread_limit} worker threads.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopped.")


if __name__ == "__main__":
    main()
