import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

#Cấu hình
START_URL = "https://dalieu.vn/chuyen-mon"
OUTPUT_TXT = "tat_ca_benh_da_lieu.txt"
MAX_LOAD_MORE = 50
WAIT_SECONDS = 10 #Để tránh bị chặn


#Khởi tạo Chrome driver
def make_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


#Tải toàn bộ danh sách bài viết
def click_load_more_until_end(driver: webdriver.Chrome):
    wait = WebDriverWait(driver, WAIT_SECONDS)
    for i in range(MAX_LOAD_MORE):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

        # Nếu xuất hiện thông báo "Bạn đã xem hết bài viết" thì dừng
        try:
            end_text = driver.find_element(By.XPATH, "//p[contains(text(), 'Bạn đã xem hết bài viết')]")
            if end_text.is_displayed():
                print("Đã load hết bài viết.")
                break
        except:
            pass

        # Bấm nút "Tải thêm" nếu có
        try:
            btn = wait.until(EC.element_to_be_clickable((By.ID, "btn_loadmore")))
            print(f"Đang tải thêm lần {i + 1} ...")
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2.5)
        except:
            print("Không còn nút 'Tải thêm' → dừng.")
            break


#Lấy danh sách link bài viết
def parse_listing(driver: webdriver.Chrome):
    wait = WebDriverWait(driver, WAIT_SECONDS)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cate-left-item")))
    items = driver.find_elements(By.CSS_SELECTOR, "div.cate-left-item")

    links = []
    for it in items:
        try:
            a = it.find_element(By.CSS_SELECTOR, "h3 a")
            title = a.text.strip()
            href = a.get_attribute("href")
            links.append((title, href))
        except:
            continue
    return links


#Lấy nội dung chi tiết bài viết
def extract_content(driver: webdriver.Chrome, url: str):
    try:
        driver.get(url)
        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.detail-content"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        content_div = soup.select_one("div.detail-content")

        if not content_div:
            return ""

        # Xóa phần “TÀI LIỆU THAM KHẢO” trở đi
        for tag in content_div.find_all(string=lambda t: t and "TÀI LIỆU THAM KHẢO" in t.upper()):
            parent = tag.find_parent()
            if parent:
                for sib in list(parent.next_siblings):
                    sib.extract()
                parent.extract()
                break

        text = content_div.get_text("\n", strip=True)
        return text
    except Exception as e:
        print(f"Lỗi khi đọc {url}: {e}")
        return ""


#Ghi tất cả nội dung vào file TXT
def save_all_to_txt(articles, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for i, (title, content) in enumerate(articles, 1):
            f.write(f"=============================\n")
            f.write(f"{i}. {title}\n")
            f.write(f"=============================\n\n")
            f.write(content.strip() if content else "Không có nội dung")
            f.write("\n\n\n")
    print(f"Đã lưu toàn bộ {len(articles)} bài viết vào file: {output_path}")


def main():
    driver = make_driver(headless=False)
    try:
        driver.get(START_URL)
        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cate-left"))
        )

        print("Đang tải danh sách bài viết...")
        click_load_more_until_end(driver)
        links = parse_listing(driver)
        print(f"Thu được {len(links)} bài viết.")

        results = []
        for i, (title, href) in enumerate(links, 1):
            print(f"[{i}/{len(links)}] Đang đọc: {title}")
            content = extract_content(driver, href)
            results.append((title, content))
            time.sleep(1.0)

        save_all_to_txt(results, OUTPUT_TXT)
        print("Crawl xong")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
