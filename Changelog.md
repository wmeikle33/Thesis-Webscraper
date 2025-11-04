## [2.0.0] — 2025-11-05
### Changed
- Migrated to Selenium 4.x (replaced `find_element_by_*` with `driver.find_element(By, ...)`).
- Switched to explicit waits via `WebDriverWait`/`expected_conditions`.
- New CLI flags: `--headless`, `--delay`, `--jitter`.

### Removed
- Selenium 3 driver management notes.

### Migration
See [MIGRATING.md#1x-to-20].
