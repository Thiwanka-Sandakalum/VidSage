import asyncio
from playwright.async_api import async_playwright
import http.cookiejar
from pathlib import Path

# Netscape cookies.txt format writer
def save_cookies_as_netscape(cookies, file_path):
    # Ensure parent directory exists
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            domain = cookie['domain']
            flag = 'TRUE' if domain.startswith('.') else 'FALSE'
            path = cookie['path']
            secure = 'TRUE' if cookie['secure'] else 'FALSE'
            expiry = str(cookie.get('expires', 0))
            name = cookie['name']
            value = cookie['value']
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")

async def fetch_youtube_cookies(output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.youtube.com')
        await page.wait_for_timeout(5000)  # Wait for cookies to be set
        cookies = await context.cookies()
        save_cookies_as_netscape(cookies, output_path)
        await browser.close()

async def ensure_youtube_cookies():
    output = Path(__file__).parent / "../cookies/cookie.txt"
    await fetch_youtube_cookies(str(output))

# Do not auto-fetch at import; call explicitly from app startup
