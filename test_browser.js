// Real browser regressions; use `npx playwright install chromium` after npm install.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require('playwright');

const output = path.join(__dirname, 'output/playwright');
fs.mkdirSync(output, { recursive: true });
const downloads = path.join(output, 'downloads');
fs.mkdirSync(downloads, { recursive: true });
const mime = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  const name = path.resolve(__dirname, '.' + (new URL(req.url, 'http://localhost').pathname === '/' ? '/index.html' : new URL(req.url, 'http://localhost').pathname));
  if (!name.startsWith(__dirname + path.sep)) { res.writeHead(403).end(); return; }
  res.setHeader('Content-Type', mime[path.extname(name)] || 'application/octet-stream');
  fs.createReadStream(name).on('error', () => res.writeHead(404).end()).pipe(res);
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined, downloadsPath: downloads });
    if (!process.argv.includes('--offline-only')) {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'block' });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.addInitScript(() => {
        window.testNow = Number(localStorage.getItem('testNow')) || 1800000000000;
        Date.now = () => window.testNow;
      });
      await page.goto(base);
      await page.locator('#tabBtn_live').click();
      await page.locator('#clockToggleBtn').click();
      await page.evaluate(() => {
        clearInterval(AppState.clock.intervalId); // Simulate suspended callbacks.
        testNow += 61250;
      });
      await page.locator('#clockToggleBtn').click();
      assert.equal(await page.locator('#matchClockDisplay').innerText(), '01:01');
      assert.equal(await page.evaluate(() => AppState.playerTimers[AppState.match.starters[0]]), 61.25);
      await page.locator('#clockToggleBtn').click();
      await page.evaluate(() => localStorage.setItem('testNow', testNow + 120000));
      await page.reload();
      assert.equal(await page.locator('#clockToggleBtn').innerText(), 'PAUSE ⏸');
      assert.equal(await page.evaluate(() => AppState.clock.seconds), 181.25);
      assert.equal(await page.evaluate(() => AppState.playerTimers[AppState.match.starters[0]]), 181.25);
      assert((await page.locator('#clockToggleBtn').getAttribute('class')).includes('bg-amber-500'));
      await page.evaluate(() => { App.toggleTimer(); App.setPeriod('2nd Half'); });
      await page.reload();
      assert.equal(await page.evaluate(() => AppState.clock.running), false);
      assert((await page.locator('#periodBtn_2').getAttribute('class')).includes('bg-cyber-cyan'));
      console.log('✓ Browser start/pause controls, suspended callbacks and running/paused reload');

      // Keep the actual PDF renderer and save call; capture its blob for raster QA.
      await page.evaluate(() => {
        const create = URL.createObjectURL;
        URL.createObjectURL = blob => {
          if (blob.type === 'application/pdf') blob.arrayBuffer().then(bytes => { window.pdfBytes = Array.from(new Uint8Array(bytes)); });
          return create(blob);
        };
        HTMLAnchorElement.prototype.click = function () {}; // Downloads are tested separately below.
        window.canvasSizes = [];
        const dataUrl = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function (...args) {
          window.canvasSizes.push({width:this.width,height:this.height});
          return dataUrl.apply(this,args);
        };
        const exportPdf = App.exportPdf;
        App.exportPdf = function (report, filename) {
          window.reportText = report.textContent;
          window.reportHtml = report.innerHTML;
          return exportPdf.call(this, report, filename);
        };
        const fixture = {...structuredClone(AppState.match), id:'a', title:'Fixture A', teamName:'Regression FC', opponent:'Wolves', date:'2026-10-10', durationSeconds:3600,
          ourGoals:4, opponentGoals:2, playerTimers:{[AppState.squad[0].id]:3600}, events:[{type:'Goal',playerId:AppState.squad[0].id,playerNumber:1,playerName:'Mateo Rossi',matchTimeSeconds:60}]};
        AppState.matchHistory = [fixture, {...structuredClone(fixture),id:'b',title:'Fixture B',opponent:'Eagles',ourGoals:2,opponentGoals:3,date:'2026-10-14'}];
        AppState.match.ourGoals = 2;
        AppState.match.opponentGoals = 1;
        AppState.selectedGameIds = ['a','b','live'];
        App.saveStorage();
      });
      async function exportReport(name, expression) {
        await page.evaluate(() => { window.pdfBytes = null; });
        assert.equal(await page.evaluate(expression), true, `${name}: generation failed`);
        await page.waitForFunction(() => window.pdfBytes, null, { timeout: 180000 });
        const bytes = Buffer.from(await page.evaluate(() => window.pdfBytes));
        assert(bytes.length > 15000, `${name}: empty PDF`);
        assert.equal(bytes.subarray(0, 4).toString(), '%PDF');
        fs.writeFileSync(path.join(output, `${name}.pdf`), bytes);
        assert.equal(await page.evaluate(() => App.pdfExportBusy), false);
        assert.equal(await page.locator('.html2pdf__overlay').count(), 0, 'Renderer must clean up');
        assert.equal(await page.locator('#pdfMatchDate').count(), 1, 'Template must remain intact');
        console.log(`✓ ${name} (${bytes.length} bytes)`);
      }
      await page.evaluate(() => window.scrollTo(0,0));
      await exportReport('single', () => App.generateSingleMatchPdf('a'));
      await page.evaluate(() => window.scrollTo(0,600));
      const scroll = await page.evaluate(() => scrollY);
      assert(scroll > 0);
      await exportReport('single-scrolled', () => App.generateSingleMatchPdf('a'));
      assert.equal(await page.evaluate(() => scrollY), scroll, 'Export must preserve scroll position');
      await exportReport('legacy-history', () => App.openExportModal('a'));
      await exportReport('range', () => App.generateDateRangePdf('2026-10-01','2026-10-31','all'));
      assert((await page.evaluate(() => reportText)).includes('GF: 6 | GA: 5'));
      await exportReport('selected', () => App.openExportModal('selected'));
      assert((await page.evaluate(() => reportText)).includes('Score: 8 - 6 (Duration: 123:01)'));
      assert((await page.evaluate(() => reportText)).includes('123:01'), 'Selected player minutes must aggregate');
      await exportReport('legacy-live', () => App.openExportModal());
      await exportReport('single-again', () => App.generateSingleMatchPdf('b'));

      // A stress case that exceeded 50,000 raster pixels vertically in the old path.
      await page.evaluate(() => {
        AppState.matchHistory[0].events = Array.from({length:1000}, (_,i) => ({type:'Goal',playerNumber:1,playerName:`EVENT ${i+1}`,matchTimeSeconds:i}));
      });
      await exportReport('long-timeline', () => App.generateSingleMatchPdf('a'));
      await page.evaluate(() => {
        const fixture = AppState.matchHistory[0];
        AppState.matchHistory = Array.from({length:160},(_,i)=>({...fixture,id:`range_${i}`,opponent:`FIXTURE ${i+1}`,events:[]}));
      });
      await exportReport('long-range', () => App.generateDateRangePdf('2026-10-01','2026-10-31','all'));
      const sizes = await page.evaluate(() => canvasSizes);
      assert(sizes.length > 25);
      assert(sizes.every(size => size.width <= 1500 && size.height <= 2200), 'Raster pages must stay bounded');
      // Missing library and a rejected render must clean up and permit a later retry.
      await page.evaluate(async () => {
        const library = window.html2pdf;
        window.html2pdf = undefined;
        if (await App.generateSingleMatchPdf('range_0') !== false) throw new Error('Missing library was not handled');
        window.html2pdf = library;
        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function () { throw new Error('Injected render failure'); };
        try {
          if (await App.generateSingleMatchPdf('range_0') !== false) throw new Error('Render failure was not handled');
        } finally { HTMLCanvasElement.prototype.getContext = getContext; }
        if (App.pdfExportBusy) throw new Error('Export lock leaked');
        if (document.querySelector('.html2pdf__overlay')) throw new Error('Renderer overlay leaked after failure');
      });
      await exportReport('retry', () => App.generateSingleMatchPdf('range_0'));
      assert.deepEqual(errors, []);
      await page.screenshot({path:path.join(output,'mobile-app.png'),fullPage:true});
      await context.close();

    }

    // Real download and cached reload use a separate context with service workers enabled.
    const offline = await browser.newContext();
    const cached = await offline.newPage();
    await cached.goto(base);
    await cached.evaluate(async () => { await navigator.serviceWorker.ready; });
    await cached.reload();
    await cached.waitForFunction(() => navigator.serviceWorker.controller);
    const assets = await cached.evaluate(async () => {
      const cache = await caches.open('gameon-v8');
      return {icon:!!(await cache.match('./icon.jpg')),app:!!(await cache.match('./index.html'))};
    });
    assert.deepEqual(assets,{icon:true,app:true});
    await offline.setOffline(true);
    await cached.reload();
    await cached.locator('#tabBtn_live').click();
    await cached.evaluate(() => {
      window.darkTablePixels = 0;
      const toDataURL = HTMLCanvasElement.prototype.toDataURL;
      HTMLCanvasElement.prototype.toDataURL = function (...args) {
        const rgba = this.getContext('2d').getImageData(0,0,this.width,this.height).data;
        for (let i=0;i<rgba.length;i+=4) {
          if (rgba[i] === 30 && rgba[i+1] === 41 && rgba[i+2] === 59) window.darkTablePixels++;
        }
        return toDataURL.apply(this,args);
      };
    });
    const download = cached.waitForEvent('download');
    await cached.evaluate(() => App.openExportModal());
    const file = await download;
    assert.match(file.suggestedFilename(), /^GameOn_.*\.pdf$/);
    assert.equal(await file.failure(), null);
    const downloadPath = await file.path();
    let downloadedPdf;
    // Windows may briefly hold an exclusive handle after Chromium reports
    // completion. Retry the file read, rather than changing the app's save path.
    for (let attempt = 0; attempt < 30; attempt++) {
      try {
        downloadedPdf = fs.readFileSync(downloadPath);
        if (downloadedPdf.subarray(-20).toString().includes('%%EOF')) break;
      } catch (error) {
        if (!['EPERM','EBUSY'].includes(error.code) || attempt === 29) throw error;
      }
      await new Promise(resolve => setTimeout(resolve,100));
    }
    assert(downloadedPdf, 'Downloaded PDF could not be read');
    assert.equal(downloadedPdf.subarray(0,4).toString(), '%PDF');
    assert(downloadedPdf.subarray(-20).toString().includes('%%EOF'));
    fs.writeFileSync(path.join(output,'offline-download.pdf'), downloadedPdf);
    assert((await cached.evaluate(() => darkTablePixels)) > 3000, 'Offline PDF must retain its styled table header');
    await offline.close();
    console.log('✓ Offline cache/reload, PDF library, image and real download');

    // The generated standalone artifact must carry the same fixes and work from disk.
    const standalone = await browser.newPage({serviceWorkers:'block'});
    await standalone.goto(require('node:url').pathToFileURL(path.join(__dirname,'gameon.html')).href);
    assert.equal(await standalone.evaluate(() => typeof App.syncClock), 'function');
    assert.equal(await standalone.evaluate(() => typeof html2pdf), 'function');
    await standalone.close();
    console.log(`${process.argv.includes('--offline-only') ? 'Offline browser regressions' : 'All browser regressions'} passed. PDFs saved under output/playwright for raster review.`);
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
