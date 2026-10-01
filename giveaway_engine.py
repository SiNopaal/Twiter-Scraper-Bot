import asyncio
import json
import os
import sys
import time
import random
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNTS_FILE = BASE_DIR / "accounts.json"
COOKIES_FILE = BASE_DIR / "cookies.json"
WALLETS_FILE = BASE_DIR / "wallets.json"
GIVEAWAYS_FILE = RESULTS_DIR / "giveaways_found.json"
HISTORY_FILE = RESULTS_DIR / "airdrop_history.json"

from airdrop_parser import analyze_airdrop_tweet, is_genuine_giveaway_drop
from wallet_config import load_wallet_config

def load_accounts_list():
    if ACCOUNTS_FILE.exists():
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                accs = []
                for k, v in data.get("accounts", {}).items():
                    accs.append(v)
                if accs:
                    return accs
        except Exception:
            pass

    if COOKIES_FILE.exists():
        try:
            with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                c = json.load(f)
                if c.get("auth_token") and c.get("ct0"):
                    return [{
                        "screen_name": "default",
                        "auth_token": c["auth_token"],
                        "ct0": c["ct0"]
                    }]
        except Exception:
            pass

    return []

def load_entered_history():
    if not HISTORY_FILE.exists():
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_entered_history(hist):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2, ensure_ascii=False)

def is_already_entered(tweet_id, account=""):
    hist = load_entered_history()
    tid = str(tweet_id)
    if not account:
        return tid in hist
    key = f"{account.lower()}_{tid}"
    return key in hist or (tid in hist and hist[tid].get("account", "").lower() == account.lower())

def record_giveaway_entry(tweet_id, tweet_info, actions_done, account=""):
    hist = load_entered_history()
    tid = str(tweet_id)
    key = f"{account.lower()}_{tid}" if account else tid
    hist[key] = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "account": account,
        "author": tweet_info.get("author", ""),
        "url": tweet_info.get("url", f"https://x.com/i/status/{tid}"),
        "reward": tweet_info.get("reward", ""),
        "wallet_type": tweet_info.get("wallet_type", ""),
        "actions": actions_done
    }
    save_entered_history(hist)

def save_giveaways_found(tweets):
    with open(GIVEAWAYS_FILE, "w", encoding="utf-8") as f:
        json.dump(tweets, f, indent=2, ensure_ascii=False)

def load_giveaways_found():
    if not GIVEAWAYS_FILE.exists():
        return []
    try:
        with open(GIVEAWAYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

QUERY_STREAMS = {
    "EVM": [
        ('("drop your 0x" OR "drop 0x" OR "drop your evm" OR "drop your eth" OR "drop metamask") (RT OR Like) -filter:replies', "EVM Live Drop"),
        ('("eth giveaway" OR "base giveaway" OR "evm giveaway") ("0x" OR "evm" OR "eth") -filter:replies', "EVM Giveaway Stream")
    ],
    "SOLANA": [
        ('("drop your sol" OR "drop sol address" OR "drop solana address" OR "drop sol addy") (RT OR Like) -filter:replies', "Solana Live Drop"),
        ('("sol giveaway" OR "solana giveaway" OR "$SOL giveaway") ("drop" OR "address" OR "wallet") -filter:replies', "Solana Giveaway Stream")
    ],
    "ALL": [
        ('("drop your 0x" OR "drop 0x" OR "drop your sol" OR "drop sol" OR "drop your base" OR "drop your address") (RT OR Like) -filter:replies', "Multi-Chain Drop Live"),
        ('("giveaway" OR "airdrop") ("drop sol" OR "drop 0x" OR "drop wallet" OR "drop address") -filter:replies', "Global Giveaway Stream")
    ]
}

async def scrape_giveaways(
    account=None,
    category="ALL",
    max_count=10,
    max_age_hours=48.0,
    headless=True,
    auto_enter=False
):
    accounts = load_accounts_list()
    selected_acc = None
    if account:
        for a in accounts:
            if a.get("screen_name", "").lower() == account.lower():
                selected_acc = a
                break
    if not selected_acc and accounts:
        selected_acc = accounts[0]

    if not selected_acc:
        raise Exception("Tidak ada akun di accounts.json atau cookies.json. Salin accounts.json.example ke accounts.json terlebih dahulu.")

    auth_token = selected_acc.get("auth_token", "")
    ct0 = selected_acc.get("ct0", "")
    wallet_cfg = load_wallet_config()
    acc_handle = selected_acc.get("screen_name", "user")

    cat = category.upper() if category.upper() in ["EVM", "SOLANA", "ALL"] else "ALL"
    streams = QUERY_STREAMS[cat]

    results = []
    seen_ids = set()

    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(
                channel="chrome",
                headless=headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
        except Exception:
            browser = await p.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 850},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

        await context.add_cookies([
            {"name": "auth_token", "value": auth_token, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": ct0, "domain": ".x.com", "path": "/"}
        ])

        page = await context.new_page()

        for query_str, stream_label in streams:
            if len(results) >= max_count:
                break

            search_url = f"https://x.com/search?q={urllib.parse.quote(query_str)}&f=live"
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_selector('article[data-testid="tweet"]', timeout=20000)
                await asyncio.sleep(1.5)
            except Exception:
                pass

            articles = await page.locator('article[data-testid="tweet"]').all()
            for art in articles:
                if len(results) >= max_count:
                    break

                status_link = art.locator('a[href*="/status/"]').first
                if await status_link.count() == 0:
                    continue
                href = await status_link.get_attribute("href")
                if not href or "/status/" not in href:
                    continue

                parts = href.strip("/").split("/")
                if len(parts) < 3:
                    continue
                author = parts[0]
                tweet_id = parts[2].split("?")[0]

                if tweet_id in seen_ids:
                    continue
                seen_ids.add(tweet_id)

                text_el = art.locator('[data-testid="tweetText"]').first
                if await text_el.count() == 0:
                    continue
                tweet_text = await text_el.inner_text()

                is_valid, reason = is_genuine_giveaway_drop(tweet_text)
                if not is_valid:
                    continue

                req = analyze_airdrop_tweet(tweet_text, author)

                user_el = art.locator('[data-testid="User-Name"]').first
                author_name = (await user_el.inner_text()).split("\n")[0] if await user_el.count() > 0 else author

                time_el = art.locator("time").first
                created_at_str = ""
                age_hours = 0.0
                if await time_el.count() > 0:
                    dt_str = await time_el.get_attribute("datetime")
                    if dt_str:
                        try:
                            created_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                            now_dt = datetime.now(timezone.utc)
                            age_hours = (now_dt - created_dt).total_seconds() / 3600.0
                            created_at_str = f"{age_hours:.1f}h ago"
                            if max_age_hours and age_hours > max_age_hours:
                                continue
                        except Exception:
                            pass

                item = {
                    "id": tweet_id,
                    "url": f"https://x.com/{author}/status/{tweet_id}",
                    "author": author,
                    "author_name": author_name,
                    "text": tweet_text,
                    "reward": req.reward,
                    "wallet_type": req.wallet_type or "UNSPECIFIED",
                    "summary_label": req.summary_label,
                    "requires_like": req.requires_like,
                    "requires_rt": req.requires_rt,
                    "requires_follow": req.requires_follow,
                    "requires_tag": req.requires_tag,
                    "tag_count": req.tag_count,
                    "accounts_to_follow": req.accounts_to_follow,
                    "address_only": req.address_only_required,
                    "age_hours": round(age_hours, 1),
                    "created_at": created_at_str,
                    "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "entered": is_already_entered(tweet_id, acc_handle)
                }

                if auto_enter and not item["entered"]:
                    actions = await execute_single_entry(context, item, acc_handle, wallet_cfg)
                    item["entered"] = True
                    item["actions_done"] = actions

                results.append(item)

        await browser.close()

    existing = load_giveaways_found()
    existing_dict = {t["id"]: t for t in existing}
    for r in results:
        existing_dict[r["id"]] = r
    combined = list(existing_dict.values())
    combined.sort(key=lambda x: x.get("discovered_at", ""), reverse=True)
    save_giveaways_found(combined[:100])

    return results

async def execute_single_entry(context, tweet_item, acc_handle, wallet_cfg):
    actions = []
    page = await context.new_page()
    try:
        await page.goto(tweet_item["url"], wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)

        # 1. Like
        if tweet_item.get("requires_like", True):
            like_btn = await page.query_selector('article[data-testid="tweet"] [data-testid="like"]')
            if like_btn:
                await like_btn.click()
                actions.append("LIKE")
                await asyncio.sleep(1)

        # 2. Retweet
        if tweet_item.get("requires_rt", True):
            rt_btn = await page.query_selector('article[data-testid="tweet"] [data-testid="retweet"]')
            if rt_btn:
                await rt_btn.click()
                await asyncio.sleep(0.5)
                confirm = await page.wait_for_selector('[data-testid="retweetConfirm"]', timeout=4000)
                if confirm:
                    await confirm.click()
                    actions.append("RETWEET")
                await asyncio.sleep(1)

        # 3. Follow
        if tweet_item.get("requires_follow"):
            follow_btn = await page.query_selector('button[data-testid*="-follow"]')
            if follow_btn:
                await follow_btn.click()
                actions.append(f"FOLLOW(@{tweet_item['author']})")
                await asyncio.sleep(1)

        # 4. Drop Address
        w_type = tweet_item.get("wallet_type", "EVM")
        target_addr = wallet_cfg.get("solana_address") if w_type == "SOLANA" else wallet_cfg.get("evm_address")
        if not target_addr:
            target_addr = wallet_cfg.get("evm_address") or wallet_cfg.get("solana_address")

        if target_addr and tweet_item.get("summary_label", "").find("Drop") != -1:
            reply_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=8000)
            if reply_box:
                await reply_box.click()
                await page.keyboard.type(target_addr, delay=random.randint(10, 20))
                await asyncio.sleep(1)
                submit = await page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=5000)
                if submit:
                    await submit.click()
                    actions.append(f"DROP({w_type}: {target_addr[:6]}...{target_addr[-4:]})")
                    await asyncio.sleep(2)

        record_giveaway_entry(tweet_item["id"], tweet_item, actions, acc_handle)
    except Exception as e:
        actions.append(f"ERROR: {str(e)[:50]}")
    finally:
        await page.close()
    return actions

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Twitter Giveaway Scraper Engine")
    parser.add_argument("-c", "--category", choices=["ALL", "SOLANA", "EVM"], default="ALL")
    parser.add_argument("-m", "--max", type=int, default=10)
    parser.add_argument("-a", "--account", type=str, default=None)
    parser.add_argument("--auto-enter", action="store_true")
    args = parser.parse_args()

    print(f"[*] Menjalankan Scraper Giveaway (Kategori: {args.category}, Max: {args.max})...")
    res = asyncio.run(scrape_giveaways(
        account=args.account,
        category=args.category,
        max_count=args.max,
        auto_enter=args.auto_enter
    ))
    print(f"\n[✓] Berhasil menemukan {len(res)} giveaway valid:")
    for r in res:
        print(f"• [{r['wallet_type']}] {r['reward']} | @{r['author']}: {r['summary_label']}")
        print(f"  URL: {r['url']}")
        print(f"  Snippet: {r['text'][:80].replace(chr(10), ' ')}...")
        print()
