# main.py
import os
import ftplib
from playwright.sync_api import sync_playwright

# GitHubのSecretsから情報を取得
FTP_HOST = os.environ["FTP_HOST"]
FTP_USER = os.environ["FTP_USER"]
FTP_PASS = os.environ["FTP_PASS"]
FTP_DIR  = "/shintoshi-signage.com/public_html/ajax-contents/img/" # Xserverのパス

targets = [
    {"url": "https://shintoshi-signage.com/ajax-contents/stock/", "file": "stock-yoko.jpg", "w": 1920, "h": 1080},
    {"url": "https://shintoshi-signage.com/ajax-contents/stock/", "file": "stock-tate.jpg", "w": 1080, "h": 1920},
    {"url": "https://shintoshi-signage.com/ajax-contents/weekweather2/", "file": "weather-tate.jpg", "w": 1080, "h": 1920}
]

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 画像生成
        for t in targets:
            page = browser.new_page(viewport={"width": t['w'], "height": t['h']})
            page.goto(t['url'])
            page.wait_for_timeout(15000) # 読み込み待機
            page.screenshot(path=t['file'], type='jpeg', quality=90)
            print(f"Captured: {t['file']}")
        browser.close()

    # FTPアップロード
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(FTP_DIR)
    for t in targets:
        if os.path.exists(t['file']):
            with open(t['file'], 'rb') as f:
                ftp.storbinary(f"STOR {t['file']}", f)
            print(f"Uploaded: {t['file']}")
    ftp.quit()

if __name__ == "__main__":
    run()