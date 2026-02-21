# Migration Guide

This document describes breaking changes and how to upgrade between major versions.

---

## 1.x to 2.0

### TL;DR
- Upgrade to Selenium 4
- Replace deprecated `find_element_by_*` calls with `find_element(By.*, ...)`
- Prefer explicit waits (`WebDriverWait`) over implicit waits / `sleep`
- Update CLI usage: new flags `--headless`, `--delay`, `--jitter`

### Why this change?
Selenium 4 removed/fully deprecated older APIs and encourages explicit waits for stability.

### Requirements / prerequisites
- Python: (state your supported versions, e.g. 3.10+)
- Selenium: 4.x
- Browser + driver: Chrome/Edge/Firefox supported (whatever your project supports)

### Breaking changes

#### 1) Selenium API changes
**Before (1.x):**
```python
el = driver.find_element_by_css_selector("div.post")

from selenium.webdriver.common.by import By
el = driver.find_element(By.CSS_SELECTOR, "div.post")

