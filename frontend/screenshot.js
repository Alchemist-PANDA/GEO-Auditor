const puppeteer = require('puppeteer');
const path = require('path');

const targetDir = 'C:\\Users\\CGS_Computer\\.gemini\\antigravity\\brain\\69a2b622-0610-4aed-ad92-fb850260567f\\';

const pages = [
  { name: 'dashboard', url: 'http://localhost:3000/dashboard' },
  { name: 'explorer', url: 'http://localhost:3000/explorer' },
  { name: 'prompts', url: 'http://localhost:3000/prompts' },
  { name: 'citations', url: 'http://localhost:3000/citations' },
  { name: 'model', url: 'http://localhost:3000/model' },
  { name: 'industry', url: 'http://localhost:3000/industry' },
  { name: 'search', url: 'http://localhost:3000/search' },
  { name: 'inbox', url: 'http://localhost:3000/inbox' }
];

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  for (const p of pages) {
    console.log(`Navigating to ${p.url}...`);
    try {
      await page.goto(p.url, { waitUntil: 'networkidle0', timeout: 30000 });
      await new Promise(r => setTimeout(r, 2000)); // wait for animations
      
      const filePath = path.join(targetDir, `current_${p.name}.png`);
      await page.screenshot({ path: filePath, fullPage: true });
      console.log(`Saved screenshot to ${filePath}`);
    } catch (e) {
      console.error(`Failed to screenshot ${p.name}:`, e.message);
    }
  }

  await browser.close();
})();
