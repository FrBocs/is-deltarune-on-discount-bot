"""
Is Deltarune On Discount
--------------------------
Checks the price of one or more Steam games and sends a Telegram message
if any of them are on sale (or below a chosen discount threshold).

SETUP:
1. Edit the CONFIGURATION section below to add the games you want to track.
2. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as environment variables
   (GitHub Actions secrets if you're running this via a workflow) -
   do NOT hardcode them here.
"""

import os
import requests

# ============================================================
# CONFIGURATION - edit this section to customize the bot
# ============================================================

# Steam appids of the games to track.
# You can find a game's appid in its store page URL, ex.:
# https://store.steampowered.com/app/1671210/DELTARUNE/  -> appid = 1671210
APPIDS = {
    1671210: "Deltarune",
    # 620: "Portal 2",           # <- add more games here: appid: "display name"
}

# Minimum discount percentage required to trigger a notification.
# 0 = notify for ANY discount, even 1%.
SOGLIA_SCONTO_MIN = 0

# Country/currency code used for pricing (e.g. "it" = Italy/EUR, "us" = USA/USD).
CC = "it"

# ============================================================
# CORE LOGIC - you normally don't need to touch anything below
# ============================================================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

WELCOME_MESSAGE = (
    "👋 Hi! This bot checks Steam prices once a day and messages you here "
    "whenever one of the tracked games goes on sale. No further action needed, "
    "just wait for a notification when there's a discount."
)


def check_start_command():
    """Check for any pending /start messages and reply with a short explanation."""
    if not TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    updates = resp.json().get("result", [])

    last_update_id = None
    for update in updates:
        last_update_id = update["update_id"]
        message = update.get("message", {})
        if message.get("text") == "/start":
            chat_id = message.get("chat", {}).get("id")
            if chat_id:
                send_telegram_message(WELCOME_MESSAGE, chat_id=chat_id)

    if last_update_id is not None:
        # Acknowledge processed updates so they aren't picked up again next run
        requests.get(url, params={"offset": last_update_id + 1}, timeout=15)


def get_price_info(appid: int):
    """Fetch current price info for a given Steam appid."""
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "cc": CC, "filters": "price_overview"}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    entry = data.get(str(appid), {})
    if not entry.get("success"):
        return None

    price_overview = entry.get("data", {}).get("price_overview")
    if not price_overview:
        # Game is free, region-locked, or has no price data available
        return None

    return {
        "discount_percent": price_overview.get("discount_percent", 0),
        "final_price": price_overview.get("final") / 100,  # cents -> currency units
        "initial_price": price_overview.get("initial") / 100,
        "currency": price_overview.get("currency"),
    }


def send_telegram_message(text: str, chat_id: str = None):
    chat_id = chat_id or TELEGRAM_CHAT_ID
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing from environment variables."
        )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()


def main():
    check_start_command()

    for appid, name in APPIDS.items():
        try:
            info = get_price_info(appid)
        except Exception as e:
            print(f"Error checking {name} ({appid}): {e}")
            continue

        if info is None:
            print(f"{name}: no price data available (free game or not sold in {CC.upper()}).")
            continue

        discount = info["discount_percent"]
        print(f"{name}: {discount}% off, price {info['final_price']} {info['currency']}")

        if discount >= SOGLIA_SCONTO_MIN and discount > 0:
            msg = (
                f"\U0001F3AE <b>{name}</b> is on sale!\n"
                f"Discount: <b>-{discount}%</b>\n"
                f"Price: <b>{info['final_price']:.2f} {info['currency']}</b> "
                f"(was {info['initial_price']:.2f} {info['currency']})\n"
                f"https://store.steampowered.com/app/{appid}/"
            )
            send_telegram_message(msg)
            print(f"-> Notification sent for {name}")


if __name__ == "__main__":
    main()
