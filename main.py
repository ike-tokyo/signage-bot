import os
import ftplib
from playwright.sync_api import sync_playwright

FTP_HOST = os.environ["FTP_HOST"]
FTP_USER = os.environ["FTP_USER"]
FTP_PASS = os.environ["FTP_PASS"]
FTP_DIR  = "/shintoshi-signage.com/public_html/ajax-contents/img/"

# ターゲット設定
targets = [
    {
        "url": "https://shintoshi-signage.com/ajax-contents/stock/",
        "file": "stock-yoko.jpg",
        "w": 1920,
        "h": 1080
    },    {
        "url": "https://shintoshi-signage.com/ajax-contents/stock/",
        "file": "stock-tate.jpg",
        "w": 1920,
        "h": 1080
    },
    {
        "url": "https://shintoshi-signage.com/ajax-contents/fullhd/weather/",
        "file": "weather.jpg",
        "w": 1080,
        "h": 1920
    }
]

# 普通のブラウザに見せかける設定
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def run():
    with sync_playwright() as p:
        # ブラウザ起動オプション（自動化検知の回避）
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        for t in targets:
            # コンテキスト作成時にヘッダー情報を追加
            context = browser.new_context(
                viewport={"width": t['w'], "height": t['h']},
                user_agent=USER_AGENT,
                locale='ja-JP',
                timezone_id='Asia/Tokyo',
                extra_http_headers={
                    # 「このサイトの中からリクエストしてますよ」という証明書
                    "Referer": "https://shintoshi-signage.com/",
                    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
                }
            )
            
            page = context.new_page()

            # Webdriverフラグの削除
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"Loading: {t['url']}")
            page.goto(t['url'])
            
            # データ読み込み完了を待つ（念の為10秒）
            # ネットワーク通信がなくなるまで待機
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                print("Network idle timeout, but taking screenshot anyway.")
            
            # 追加で少し待つ（描画アニメーション用）
            page.wait_for_timeout(3000)
            
            page.screenshot(path=t['file'], type='jpeg', quality=90)
            print(f"Captured: {t['file']}")
            
            context.close()
            
        browser.close()

    # FTPアップロード
    print("Uploading to FTP...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_DIR)
        
        for t in targets:
            if os.path.exists(t['file']):
                with open(t['file'], 'rb') as f:
                    ftp.storbinary(f"STOR {t['file']}", f)
                print(f"Uploaded: {t['file']}")
        
        ftp.quit()
    except Exception as e:
        print(f"FTP Error: {e}")

if __name__ == "__main__":
    run()
