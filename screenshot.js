const { chromium } = require('playwright');

(async () => {
  const url = process.argv[2]

  const browser = await chromium.launch({
    headless: false
  });
  const context = await browser.newContext();
  const page = await context.newPage();
  // await page.setViewportSize({
  //   width: 1200,
  //   height: 1200,
  // })
  await page.goto(url, { waitUntil: 'load'});
  await page.screenshot({ path: 'screenshot.png', fullPage: true });
  await browser.close();

  console.log('Screenshot taken successfully!');
})();
