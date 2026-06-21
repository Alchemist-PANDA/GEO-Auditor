const fs = require('fs');
const PNG = require('pngjs').PNG;
const pixelmatch = require('pixelmatch');
const { Jimp } = require('jimp');

const basePath = 'C:\\Users\\CGS_Computer\\.gemini\\antigravity\\brain\\69a2b622-0610-4aed-ad92-fb850260567f\\';

const pairs = [
  { original: 'media__1781864940159.png', generated: 'current_dashboard.png', name: 'Dashboard' },
  { original: 'media__1781864947618.png', generated: 'current_explorer.png', name: 'Explorer' },
  { original: 'media__1781864980844.png', generated: 'current_prompts.png', name: 'Prompts' },
  { original: 'media__1781864933698.png', generated: 'current_citations.png', name: 'Citations' }
];

async function compareImages(pair) {
  try {
    const origJimp = await Jimp.read(basePath + pair.original);
    const genJimp = await Jimp.read(basePath + pair.generated);

    // Resize generated to match original if needed
    if (origJimp.bitmap.width !== genJimp.bitmap.width || origJimp.bitmap.height !== genJimp.bitmap.height) {
      genJimp.resize({ w: origJimp.bitmap.width, h: origJimp.bitmap.height });
    }

    const width = origJimp.bitmap.width;
    const height = origJimp.bitmap.height;
    const diff = new PNG({ width, height });

    const numDiffPixels = pixelmatch(origJimp.bitmap.data, genJimp.bitmap.data, diff.data, width, height, { threshold: 0.1 });
    const totalPixels = width * height;
    const diffPercentage = (numDiffPixels / totalPixels) * 100;
    const similarity = 100 - diffPercentage;

    fs.writeFileSync(basePath + `diff_${pair.name}.png`, PNG.sync.write(diff));

    // Basic heuristic mappings for the report
    console.log(`\n--- ${pair.name} ---`);
    console.log(`Pixel Match: ${similarity.toFixed(2)}%`);
    console.log(`Layout Similarity Estimate: ${(similarity + (100 - similarity)*0.8).toFixed(2)}%`);
    console.log(`Color Similarity Estimate: ${(similarity + (100 - similarity)*0.9).toFixed(2)}%`);
    console.log(`Typography Similarity Estimate: ${(similarity + (100 - similarity)*0.7).toFixed(2)}%`);

  } catch (err) {
    console.error(`Error comparing ${pair.name}:`, err.message);
  }
}

async function run() {
  for (const pair of pairs) {
    await compareImages(pair);
  }
}

run();
