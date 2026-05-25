import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots');
const URL = 'http://localhost:8081/index.html';

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });
  const page = await context.newPage();

  // Track console errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error' || msg.type() === 'warning') {
      consoleErrors.push(`[${msg.type()}] ${msg.text()}`);
    }
  });
  page.on('pageerror', err => {
    consoleErrors.push(`PAGE ERROR: ${err.message}`);
  });

  console.log('=== STEP 1: Loading page ===');
  await page.goto(URL, { waitUntil: 'networkidle' });
  await sleep(2000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_initial_state.png'), fullPage: false });
  
  let eventCards = await page.$$('.group\\/card');
  console.log(`Found ${eventCards.length} event cards initially`);

  console.log('\n=== STEP 2: Subscribe test@test.com ===');
  const restoreInput = page.locator('input[placeholder="your@email.com"]');
  const restoreBtn = page.locator('button:has-text("Restore")');
  
  if (await restoreInput.isVisible()) {
    await restoreInput.fill('test@test.com');
    await sleep(200);
    await restoreBtn.click();
    await sleep(1500);
    console.log('Restore clicked');
  }

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_after_restore.png'), fullPage: false });

  const restoredEl = page.locator('text=Restored');
  if (await restoredEl.isVisible({ timeout: 1000 }).catch(() => false)) {
    console.log('SUCCESS: Subscribed as test@test.com');
  } else {
    console.log('WARNING: Not subscribed');
  }

  const manageHiddenBtn = page.locator('button:has-text("Manage Hidden")');
  let hiddenText = await manageHiddenBtn.textContent();
  console.log(`Hidden count: ${hiddenText}`);

  // ============================
  // TEST 1: RAPID DOUBLE CLICK
  // ============================
  console.log('\n============= TEST 1: RAPID DOUBLE CLICK =============');
  
  const firstHideBtn = page.locator('.group\\/card [title="Hide event"]').first();
  if (await firstHideBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
    const box = await firstHideBtn.boundingBox();
    if (box) {
      // Rapid double click at same position
      await page.mouse.click(box.x + box.width/2, box.y + box.height/2);
      await sleep(80);
      await page.mouse.click(box.x + box.width/2, box.y + box.height/2);
      await sleep(1500);
      
      console.log('Double click performed');
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T1_after_double_click.png'), fullPage: false });
      
      hiddenText = await manageHiddenBtn.textContent();
      console.log(`Hidden count after T1: ${hiddenText}`);
      
      // Check what events are still visible
      eventCards = await page.$$('.group\\/card');
      console.log(`Cards remaining: ${eventCards.length}`);
    }
  }

  // ============================
  // TEST 2: OPEN DETAIL PANEL, CLOSE, THEN HIDE
  // ============================
  console.log('\n============= TEST 2: DETAIL PANEL + HIDE =============');
  
  eventCards = await page.$$('.group\\/card');
  if (eventCards.length > 0) {
    const cardBox = await eventCards[0].boundingBox();
    if (cardBox) {
      // Click card body to open detail panel
      await page.mouse.click(cardBox.x + cardBox.width * 0.3, cardBox.y + cardBox.height / 2);
      await sleep(1000);
      
      const detailTitle = page.locator('text=Event Details');
      if (await detailTitle.isVisible({ timeout: 500 }).catch(() => false)) {
        console.log('Detail panel opened');
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T2_detail_open.png'), fullPage: false });
        
        // Close by clicking backdrop
        const backdrop = page.locator('.fixed.inset-0.z-40.backdrop-overlay');
        if (await backdrop.isVisible({ timeout: 500 }).catch(() => false)) {
          await backdrop.click({ position: { x: 10, y: 10 } });
          await sleep(800);
          console.log('Clicked backdrop to close');
          await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T2_detail_closed.png'), fullPage: false });
        }
        
        // Now click × on same card
        const hideBtn = page.locator('.group\\/card [title="Hide event"]').first();
        if (await hideBtn.isVisible({ timeout: 500 }).catch(() => false)) {
          await hideBtn.click();
          await sleep(1000);
          console.log('Clicked hide on card');
          hiddenText = await manageHiddenBtn.textContent();
          console.log(`Hidden count after T2: ${hiddenText}`);
        }
      } else {
        console.log('Detail panel did NOT open');
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T2_not_opened.png'), fullPage: false });
      }
    }
  }

  // ============================
  // TEST 3: HIDE THEN HIDE ANOTHER
  // ============================
  console.log('\n============= TEST 3: HIDE THEN HIDE ANOTHER =============');
  
  eventCards = await page.$$('.group\\/card');
  console.log(`Have ${eventCards.length} cards`);
  
  if (eventCards.length >= 2) {
    // Hide first card
    const b1 = page.locator('.group\\/card [title="Hide event"]').first();
    if (await b1.isVisible({ timeout: 500 }).catch(() => false)) {
      await b1.click();
      await sleep(1500);
      console.log('Hid first card');
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T3_after_first.png'), fullPage: false });
      
      hiddenText = await manageHiddenBtn.textContent();
      console.log(`Hidden count after first: ${hiddenText}`);
      
      // Hide second card
      const b2 = page.locator('.group\\/card [title="Hide event"]').first();
      if (await b2.isVisible({ timeout: 500 }).catch(() => false)) {
        await b2.click();
        await sleep(1500);
        console.log('Hid second card');
        
        hiddenText = await manageHiddenBtn.textContent();
        console.log(`Hidden count after second: ${hiddenText}`);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T3_after_second.png'), fullPage: false });
      }
    }
  } else if (eventCards.length === 1) {
    console.log('Only 1 card available - hiding it');
    const b1 = page.locator('.group\\/card [title="Hide event"]').first();
    if (await b1.isVisible({ timeout: 500 }).catch(() => false)) {
      await b1.click();
      await sleep(1000);
      console.log('Hid only card');
    }
  }

  // Count how many hidden now
  hiddenText = await manageHiddenBtn.textContent();
  const countStr = hiddenText.match(/\((\d+)\)/)?.[1] || '0';
  const hiddenSoFar = parseInt(countStr);
  console.log(`Total hidden so far: ${hiddenSoFar}`);

  // ============================
  // TEST 4: DETAIL PANEL HIDE
  // ============================
  console.log('\n============= TEST 4: DETAIL PANEL HIDE BUTTON =============');
  
  eventCards = await page.$$('.group\\/card');
  console.log(`Have ${eventCards.length} cards`);
  
  if (eventCards.length >= 1) {
    const cardBox = await eventCards[0].boundingBox();
    if (cardBox) {
      await page.mouse.click(cardBox.x + cardBox.width * 0.3, cardBox.y + cardBox.height / 2);
      await sleep(1000);
      
      const detailTitle = page.locator('text=Event Details');
      if (await detailTitle.isVisible({ timeout: 500 }).catch(() => false)) {
        console.log('Detail panel opened');
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T4_detail_open.png'), fullPage: false });
        
        // Click "Hide Event" button inside detail panel
        const hideEventBtn = page.locator('button:has-text("Hide Event")');
        if (await hideEventBtn.isVisible({ timeout: 500 }).catch(() => false)) {
          await hideEventBtn.click();
          await sleep(1500);
          console.log('Clicked Hide Event in detail panel');
          
          if (!(await detailTitle.isVisible({ timeout: 500 }).catch(() => false))) {
            console.log('Detail panel closed after hide');
          }
          
          hiddenText = await manageHiddenBtn.textContent();
          console.log(`Hidden count after T4: ${hiddenText}`);
          await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T4_after_hide.png'), fullPage: false });
        } else {
          console.log('Hide Event button not found');
          await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T4_no_hide_btn.png'), fullPage: false });
        }
      } else {
        console.log('Detail panel did not open');
      }
    }
  }

  // ============================
  // TEST 5: UNSUBSCRIBED TEST
  // ============================
  console.log('\n============= TEST 5: UNSUBSCRIBED TEST =============');
  
  const clearBtn = page.locator('button:has-text("Clear")');
  if (await clearBtn.isVisible({ timeout: 500 }).catch(() => false)) {
    await clearBtn.click();
    await sleep(1000);
    console.log('Clicked Clear');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T5_after_clear.png'), fullPage: false });
    
    eventCards = await page.$$('.group\\/card');
    console.log(`Have ${eventCards.length} cards after logout`);
    
    if (eventCards.length > 0) {
      // Click × on first card
      const hideBtn = page.locator('.group\\/card [title="Hide event"]').first();
      if (await hideBtn.isVisible({ timeout: 500 }).catch(() => false)) {
        await hideBtn.click();
        await sleep(1000);
        console.log('Clicked hide while unsubscribed');
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T5_after_unsubscribed_click.png'), fullPage: false });
        
        const subscribeTitle = page.locator('text=Get Event Alerts');
        const subscribeHeading = page.locator('text=Subscribe to Updates');
        
        if (await subscribeTitle.isVisible({ timeout: 1000 }).catch(() => false)) {
          console.log('Subscribe modal appeared - CORRECT');
          
          // Dismiss by clicking backdrop
          const backdrop = page.locator('.fixed.inset-0.z-40.backdrop-overlay');
          if (await backdrop.isVisible({ timeout: 500 }).catch(() => false)) {
            await backdrop.click({ position: { x: 10, y: 10 } });
            await sleep(1000);
            console.log('Clicked backdrop');
            
            if (!(await subscribeTitle.isVisible({ timeout: 500 }).catch(() => false))) {
              console.log('Modal dismissed');
            }
            
            await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T5_modal_dismissed.png'), fullPage: false });
            
            // Click × on another card
            const hideBtn2 = page.locator('.group\\/card [title="Hide event"]').first();
            if (await hideBtn2.isVisible({ timeout: 500 }).catch(() => false)) {
              await hideBtn2.click();
              await sleep(1000);
              console.log('Clicked hide on another card');
              
              if (await subscribeTitle.isVisible({ timeout: 1000 }).catch(() => false)) {
                console.log('Subscribe modal appeared again - CORRECT');
              } else {
                console.log('Subscribe modal did NOT appear - BUG?');
              }
              await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T5_modal_again.png'), fullPage: false });
            }
          } else {
            console.log('Backdrop not visible');
            await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T5_no_backdrop.png'), fullPage: false });
          }
        } else {
          console.log('Subscribe modal did NOT appear - BUG!');
          await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'T5_no_modal.png'), fullPage: false });
        }
      }
    }
  } else {
    console.log('Clear button not found');
  }

  // ============================
  // SUMMARY
  // ============================
  console.log('\n========================================');
  console.log('============= FINAL SUMMARY =============');
  console.log('========================================');
  console.log(`Console errors/warnings: ${consoleErrors.length}`);
  consoleErrors.forEach((err, i) => console.log(`  ${i+1}. ${err}`));

  // Final state screenshot
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '99_final_state.png'), fullPage: false });

  // Keep browser open
  console.log('\nBrowser remains open for inspection. Ctrl+C to close.');
}

run().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});