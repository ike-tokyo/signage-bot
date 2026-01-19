import os
import ftplib
from playwright.sync_api import sync_playwright

FTP_HOST = os.environ["FTP_HOST"]
FTP_USER = os.environ["FTP_USER"]
FTP_PASS = os.environ["FTP_PASS"]
FTP_DIR  = "/shintoshi-signage.com/public_html/ajax-contents/img/" # Xserverのパス

# ターゲット設定
targets = [
    {
        "url": "https://shintoshi-signage.com/ajax-contents/stock/",
        "file": "stock.jpg",
        "w": 1920,
        "h": 1080
    },
    {
        "url": "https://shintoshi-signage.com/ajax-contents/weekweather2/",
        "file": "weather.jpg",
        "w": 1080, # 縦型サイネージ用
        "h": 1920
    }
]

# 普通のブラウザに見せかけるための「名刺」
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for t in targets:
            # ここでUser Agentを設定してページを開く
            page = browser.new_page(
                viewport={"width": t['w'], "height": t['h']},
                user_agent=USER_AGENT
            )
            
            print(f"Loading: {t['url']}")
            page.goto(t['url'])
            
            # 読み込み待ち（データ取得エラーを防ぐため20秒に延長）
            page.wait_for_timeout(20000)
            
            page.screenshot(path=t['file'], type='jpeg', quality=90)
            print(f"Captured: {t['file']}")
            
            page.close() # ページを閉じる
            
        browser.close()

    # FTPアップロード処理
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
