const puppeteer = require('puppeteer');
const path = require('path');

const token = process.argv[2];
if (!token) {
  console.error("Please provide the JWT auth token as an argument.");
  process.exit(1);
}

const outputPath = path.resolve(__dirname, '../docs/final_audit/dashboard.png');

(async () => {
  console.log("Launching headless browser...");
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  console.log("Navigating to login page to set local domain context...");
  await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle0', timeout: 30000 });

  console.log("Injecting JWT authentication token into localStorage...");
  await page.evaluate((jwt) => {
    localStorage.setItem('auth_token', jwt);
  }, token);

  console.log("Navigating to dashboard...");
  await page.goto('http://localhost:3000/dashboard', { waitUntil: 'networkidle0', timeout: 30000 });
  
  console.log("Waiting for animations and graphs to load...");
  await new Promise(r => setTimeout(r, 4000));

  console.log(`Taking screenshot and saving to ${outputPath}...`);
  await page.screenshot({ path: outputPath, fullPage: false });

  console.log("Screenshot successfully saved!");
  await browser.close();
})().catch(err => {
  console.error("Screenshot generation failed:", err.message);
  process.exit(1);
});
