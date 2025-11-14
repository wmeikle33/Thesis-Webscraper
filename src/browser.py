def make_driver(s: Settings) -> webdriver.Chrome:
    opts = Options()
    if s.headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1400,900")
    PATH = '/Users/williammeikle/Downloads/chromedriver 7'
    driver = webdriver.Chrome(PATH, options=opts)
    driver.set_page_load_timeout(s.page_timeout_s)
    return driver
