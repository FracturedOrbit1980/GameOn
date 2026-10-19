# Timer and PDF bug-fix verification

## Scope and sources

`index.html` is the source. Rebuild `gameon.html` with `npm run bundle`; `npm test` rejects stale bundled application logic. The legacy `build_html.py` scaffold is disabled to prevent overwriting fixes. CSS did not change, so a Tailwind rebuild is unnecessary.

Existing `gameon_*` storage keys and saved match records are retained. Clock version 2 adds running state and a timestamp checkpoint. Old clocks migrate paused because their running state was never recorded. Current running sessions catch up on reload, background return and before substitutions, events, reports or archival. Invalid/future checkpoints pause safely. Fractional seconds are retained internally and displayed as whole elapsed seconds. Reset still resets only the stopwatch; End match archives player totals and clears the live session.

All existing PDF entry points use one renderer with separate report nodes. Selected-game scores sum recorded scores, including manual score adjustments. Each A4 page is rasterized separately, avoiding one enormous report canvas. Normal rows/events stay together; an individual item taller than a page must split. Actual page numbers replace the hard-coded “Page 1 of 1”. Files still download through the existing PDF library; missing-library/render failures give an error and allow retry.

The renderer's cloned document also receives a snapshot of loaded CSS rules. Visual inspection reproduced an unstyled legacy report offline even though the original app had loaded its cached CSS; the renderer's iframe could not reload that stylesheet. The browser regression checks pixels from the actual offline raster to retain the styled table header.

The service worker version is bumped to v8 so existing installations can receive the changed app on reload; `icon.jpg` is also precached. There is no new cache strategy or phone sharing flow.

## Automated checks

```sh
npm install
npm run bundle
npm test
npx playwright install chromium
npm run test:browser
```

An installed Chromium binary can be selected with the `PLAYWRIGHT_CHROMIUM_EXECUTABLE` environment variable. This is useful in environments with managed browser installations.

- Logic regressions simulate delayed callbacks, fractional boundaries, start/pause/resume, substitutions, period changes, running reload, final archive values, new-match/reset behavior, old storage and invalid timestamps.
- Browser tests exercise the actual start/pause buttons, suspended-callback recovery and real reloads. PDF coverage includes single, range, legacy live/history, selected matches, repeats, scrolled exports, 1,000 timeline events, 160 fixtures, missing-library/render failures, retry, offline reload and a real download. Raster dimensions are bounded per page. The generated standalone app is loaded from disk.
- PDFs under `output/playwright/` are test artifacts and ignored by Git. Render them with Poppler, for example `pdftoppm -scale-to 1000 -png output/playwright/long-timeline.pdf output/playwright/long-timeline`, then inspect pages. Rasterized PDFs cannot be validated by text extraction alone.

## Reproduction evidence

Before the export fix, a 390 × 844 Chromium viewport exported a complete short report at scroll position zero. At scroll position 600, the same report started partway down the PDF and cut off player rows. After the fix the report remains complete at both scroll positions without moving the user's page.

Exporting a newer report and then using the legacy export threw `Cannot set properties of null (setting 'innerText')`: the named ledger elements had been removed. Isolated report nodes preserve the original template across repeated exports.

The old 1,000-event path requested a 1,468 × 50,644 canvas. It rendered on this desktop Chromium; a canvas-limit blank export was **not** reproduced there. The new path uses page-sized canvases and produced 25 pages. First, middle and last pages were visually inspected, including the final event. Desktop automation does not establish iPhone canvas behavior or phone download support.

## Android and iPhone manual checklist

Run on Android Chrome/installed PWA and iPhone Safari/Add to Home Screen. These device checks remain manual; no physical phone testing has been performed.

1. Back up real data first. Load existing history and confirm scores, squads and past player minutes survive the update. Reload once online to receive v8, then verify offline startup and an offline PDF.
2. Start the clock, lock the phone or switch apps for at least two minutes, return, and compare match/player times with elapsed wall time. Repeat with a force-close/reopen while running and while paused. Paused time must not count.
3. Substitute a player after returning, pause/resume and change half. End the match; compare archived duration and each player's minutes with the live totals. Check the next match starts at zero. Confirm stopwatch Reset retains player totals, as its label promises.
4. Export from the header, history, single/date-range dialog and Export Selected in succession. Include manually adjusted scores and conceded goals. Repeat from the bottom of a scrolled page and with a long report. Open the downloaded PDFs and inspect the first, middle and last pages, totals, final row/event and page numbers. Confirm the OS download/open flow and retry after a failed export.

Forward system-clock changes are indistinguishable from real elapsed time while the app is suspended. Backward changes pause the clock rather than subtracting time. Very large reports still take time and produce larger downloads even though raster memory is bounded per page.
