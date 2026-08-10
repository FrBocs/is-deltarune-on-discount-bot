# Is Deltarune On Discount

A tiny Telegram bot that checks Steam prices once a day and messages you
whenever a tracked game (Deltarune by default) goes on sale.

It runs entirely for free on **GitHub Actions**. No server, no hosting.

## How it works

- A GitHub Actions workflow runs the Python script on a daily schedle.
- The script checks the current price of the game(s) you configured via the
  public Steam Store API.
- If a discount is found, it sends you a Telegram message with the price and
  a link to the store page.
- If you message the bot `/start`, it replies with a short explanation of
  how it works (the reply is sent the next time the scheduled workflow runs,
  not instantly).

## Setup

### 1. Create a Telegram bot

1. Open Telegram, search for **@BotFather**, and send `/newbot`.
2. Choose a name and a username ending in `bot`.
3. BotFather gives you a **bot token** (looks like `123456789:AAExxxxxxxxxxx`) and save it.
4. Send any message to your new bot (ex. "hi") so Telegram has something to return in the next step.

### 2. Find your chat ID

Open this URL in your browser, replacing `<YOUR_TOKEN>` with your bot token:

```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

Look for `"chat":{"id": NUMBER` in the response, that number is your **chat ID**.

### 3. Fork or create this repository on GitHub

Fork this repo, or create a new one and copy in:
- `is_deltarune_on_discount.py` (repository root)
- `.github/workflows/is_deltarune_on_discount.yml`

### 4. Add your secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name          | Value                          |
|-----------------------|---------------------------------|
| `TELEGRAM_BOT_TOKEN`  | The token from BotFather        |
| `TELEGRAM_CHAT_ID`    | The chat ID you found in step 2 |

### 5. Test it

Go to the **Actions** tab, select the workflow, and click **Run workflow** to
trigger it manually. Check the run log for errors, and check Telegram for a
message if the tracked game happens to be on sale.

That's it, from now on it runs automatically on the schedule you set.

## Customizing

### Track different games

Open `is_deltarune_on_discount.py` and edit the `APPIDS` dictionary near the top:

```python
APPIDS = {
    1671210: "Deltarune",
    620: "Portal 2",   # add as many as you want
}
```

You can find a game's appid in its Steam store URL, e.g.
`store.steampowered.com/app/1671210` → appid is `1671210`.

### Change the discount threshold

By default, `SOGLIA_SCONTO_MIN = 0` notifies you for any discount, even 1%.
Raise it if you only care about bigger sales:

```python
SOGLIA_SCONTO_MIN = 25  # only notify for 25%+ discounts
```

### Change the region/currency

```python
CC = "it"  # e.g. "us" for USD, "de" for Germany/EUR, etc.
```

### Change the schedule

Open `.github/workflows/is_deltarune_on_discount.yml` and edit the cron line.
GitHub Actions schedules always run in **UTC**, so convert your local time first:

```yaml
- cron: "0 16 * * *"   # 16:00 UTC every day
```

Cron format: `minute hour day month weekday`. You can use
[crontab.guru](https://crontab.guru) to build/verify a schedule.

## Notes

- GitHub Actions free tier includes 2000 minutes/month for private repos —
  a daily run of this script uses only a couple of minutes a month, so you
  won't come close to the limit.
- This project only supports a single Telegram chat per deployment. If you
  want it to work for multiple users, you'd need to add persistent storage
  (ex. a small database or a service like JSONBin) to track users.
