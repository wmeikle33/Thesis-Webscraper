import os
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def create_directory(folder_name: str) -> None:
    Path(folder_name).mkdir(parents=True, exist_ok=True)

def does_file_exist(path: str) -> bool:
    return Path(path).is_file()

def write_to_file(path: str, data: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def create_new_file(path: str) -> None:
    Path(path).write_text("", encoding="utf-8")

def get_details(driver, directory: str, url: str, timeout: int = 10) -> None:
    out_path = str(Path(directory) / "articles.txt")
    wait = WebDriverWait(driver, timeout)

    driver.get(url)

    try:
        title_el = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "post-title")))
        print("\nTitle\n")
        write_to_file(out_path, "\nTitle:\n")
        print(title_el.text)
        write_to_file(out_path, title_el.text)
    except TimeoutException:
        print("\nTitle\nEmpty (timeout)\n")
        write_to_file(out_path, "\nTitle:\nEmpty\n")

    print("\nParagraphs\n")
    write_to_file(out_path, "\nParagraphs:\n")
    try:
        para_el = driver.find_element(By.CLASS_NAME, "tz-paragraph")
        print(para_el.text if para_el.text else "Empty")
        write_to_file(out_path, para_el.text if para_el.text else "Empty")
    except NoSuchElementException:
        print("Empty")
        write_to_file(out_path, "Empty")

    print("\nComments\n")
    write_to_file(out_path, "\nComments:\n")
    comments = driver.find_elements(By.CLASS_NAME, "reply-detail")
    if not comments:
        print("Empty")
        write_to_file(out_path, "Empty")
    else:
        for c in comments:
            txt = c.text.strip()
            if txt:
                print(txt + "\n")
                write_to_file(out_path, txt)

    print("\nSubComments\n")
    write_to_file(out_path, "\nSubComments:\n")
    subcomments = driver.find_elements(By.CLASS_NAME, "reply-sub-front")
    if not subcomments:
        print("Empty")
        write_to_file(out_path, "Empty")
    else:
        # dedupe by text (set(subcomments) isn't stable/useful)
        seen_txt = set()
        for sc in subcomments:
            txt = sc.text.strip()
            if txt and txt not in seen_txt:
                seen_txt.add(txt)
                print(txt + "\n")
                write_to_file(out_path, txt)

def main_scraper(driver, url: str, directory: str, thread_ids=("6830271", "6830286"), timeout: int = 10) -> None:
    create_directory(directory)
    out_path = str(Path(directory) / "articles.txt")
    if not does_file_exist(out_path):
        create_new_file(out_path)

    wait = WebDriverWait(driver, timeout)
    driver.get(url)

    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href]")))

    elems = driver.find_elements(By.XPATH, "//a[@href]")
    seen_urls = set()

    for elem in elems:
        href = elem.get_attribute("href")
        if not href or href in seen_urls:
            continue

        if ("thread" in href) and any(tid in href for tid in thread_ids):
            seen_urls.add(href)
            print("url:", href)
            write_to_file(out_path, "url: " + href)
            get_details(driver, directory, href, timeout=timeout)



main_scraper('http://club.autohome.com.cn/bbs/forum-c-5769-1.html#pvareaid=3454448','ModelYAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6404-1.html#pvareaid=2108152','LYRIQAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6035-1.html#pvareaid=2108152','ID-6XAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6029-1.html#pvareaid=3454448','MustangMach-EAutoHomeBlog')
