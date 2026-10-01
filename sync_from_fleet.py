import json
from pathlib import Path

FLEET_FILE = Path("/home/naufal-ananta/bot/twitter-scraper/fleet_accounts.json")
TWITER_BOT_ACCOUNTS = Path("/home/naufal-ananta/bot/Twiter-Scraper-Bot/accounts.json")
TWITER_BOT_WALLETS = Path("/home/naufal-ananta/bot/Twiter-Scraper-Bot/wallets.json")
FLEET_WALLETS = Path("/home/naufal-ananta/bot/twitter-scraper/wallets.json")

def sync():
    if not FLEET_FILE.exists():
        print("Fleet file not found!")
        return

    with open(FLEET_FILE, "r", encoding="utf-8") as f:
        fleet = json.load(f)

    # Sync wallets
    default_wallet = {
        "evm_address": "0x70660e8D4887c0e435007778f3e13cACA1c27694",
        "solana_address": "8x2Wq8qL7v2qZ9kM1J5K4L2n9P3m5v7z",
        "unspecified_default": "EVM",
        "reply_mode": "pure_address",
        "auto_like": True,
        "auto_retweet": True,
        "auto_follow": True,
        "auto_reply_wallet": True
    }
    if not TWITER_BOT_WALLETS.exists():
        with open(TWITER_BOT_WALLETS, "w", encoding="utf-8") as f:
            json.dump(default_wallet, f, indent=2)

    accounts_payload = {
        "active_account": fleet[0]["handle"] if fleet else "",
        "accounts": {}
    }

    for acc in fleet:
        handle = acc["handle"]
        accounts_payload["accounts"][handle] = {
            "screen_name": handle,
            "name": acc.get("name", handle),
            "auth_token": acc["authToken"],
            "ct0": acc["ct0"],
            "added_at": acc.get("lastActive", "2026-10-01 00:00:00"),
            "evm_address": acc.get("evm_address", default_wallet["evm_address"]),
            "solana_address": acc.get("solana_address", default_wallet["solana_address"])
        }

    with open(TWITER_BOT_ACCOUNTS, "w", encoding="utf-8") as f:
        json.dump(accounts_payload, f, indent=2, ensure_ascii=False)

    print(f"Successfully synced {len(fleet)} fleet accounts to Twiter-Scraper-Bot/accounts.json!")

if __name__ == "__main__":
    sync()
