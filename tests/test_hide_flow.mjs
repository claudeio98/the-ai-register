import { chromium } from 'playwright';
import fs from 'fs';

const BASE = 'http://localhost:8081';
const API = 'http://localhost:8082';
const SCREENSHOTS = '/tmp/hide_tests';

fs.mkdirSync(SCREENSHOTS, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage();

// Collect console messages
const consoleLogs = [];
page.on('console', msg => consoleLogs.push(`${msg.type()}: ${msg.text()}`));
page.on('pageerror', err => consoleLogs.push(`PAGE ERROR: ${err.message}`));

console.log('=== SETUP: Open page and verify events load ===');
await page.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);

// Count events on the page
let eventCount = await page.evaluate(() => document.querySelectorAll('[title="Hide event"]').length);
console.log(`Event cards with hide buttons found: ${eventCount}`);
await page.screenshot({ path: `${SCREENSHOTS}/01-initial-load.png`, fullPage: false });

// ======== TEST 1: Unsubscribed user ========
console.log('\n=== TEST 1: Unsubscribed user -- click x on event list card ===');
const firstHideBtn = page.locator('[title="Hide event"]').first();
const btnCountBefore = await page.locator('[title="Hide event"]').count();
console.log(`Hide buttons before click: ${btnCountBefore}`);

await firstHideBtn.click();
await page.waitForTimeout(500);
await page.screenshot({ path: `${SCREENSHOTS}/02-unsubscribed-subscribe-modal.png`, fullPage: false });

// Check what appeared
const pageText = await page.locator('body').textContent();
const subscribeModalShown = pageText.includes('Subscribe to Updates');
console.log(`Subscribe modal visible: ${subscribeModalShown}`);

// Check if event count stayed the same
const btnCountAfter = await page.locator('[title="Hide event"]').count();
console.log(`Hide buttons after click: ${btnCountAfter} (expected: ${btnCountBefore})`);

// Close subscribe modal -- find the close button in the modal
const closeModalBtn = page.locator('.z-50 button:has-text("✕")');
if (await closeModalBtn.count() > 0) {
  await closeModalBtn.click();
  console.log('Clicked close button on subscribe modal');
} else {
  // Try clicking the backdrop
  await page.locator('.backdrop-overlay').first().click({ force: true });
  console.log('Clicked backdrop to close');
}
await page.waitForTimeout(300);
await page.screenshot({ path: `${SCREENSHOTS}/03-unsubscribed-modal-closed.png`, fullPage: false });

// ======== TEST 2: Become subscribed ========
console.log('\n=== TEST 2: Subscribe and become a subscribed user ===');
const email = 'test-hide@test.com';

// Subscribe via API
try {
  const subRes = await fetch(`${API}/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  const subData = await subRes.json();
  console.log('Subscribe API result:', JSON.stringify(subData));
} catch(e) {
  console.error('Subscribe API error:', e.message);
}

// Use Restore flow
const restoreInput = page.locator('input[placeholder="your@email.com"]');
await restoreInput.fill(email);
await page.waitForTimeout(200);
await page.screenshot({ path: `${SCREENSHOTS}/04-restore-email-filled.png`, fullPage: false });

const restoreBtn = page.locator('button:has-text("Restore")');
await restoreBtn.click();
await page.waitForTimeout(2000);
await page.screenshot({ path: `${SCREENSHOTS}/05-restore-result.png`, fullPage: false });

const restoredText = await page.locator('body').textContent();
console.log(`Restored message visible: ${restoredText.includes('Restored')}`);
const manageHiddenVisible = await page.locator('button:has-text("Manage Hidden")').count();
console.log(`Manage Hidden button count: ${manageHiddenVisible}`);

const lsEmail = await page.evaluate(() => localStorage.getItem('subscriber_email'));
console.log(`localStorage subscriber_email: ${lsEmail}`);

// ======== TEST 3: Subscribed user -- click x ========
console.log('\n=== TEST 3: Subscribed user -- click x on event list card ===');
await page.waitForTimeout(500);

const hideBtns1 = await page.locator('[title="Hide event"]').count();
let manageHiddenText = (await page.locator('button:has-text("Manage Hidden")').textContent()).trim();
console.log(`Before: hide buttons=${hideBtns1}, Manage Hidden text="${manageHiddenText}"`);

const hideBtn3 = page.locator('[title="Hide event"]').first();
await hideBtn3.click();
await page.waitForTimeout(500);
await page.screenshot({ path: `${SCREENSHOTS}/06-subscribed-click-hide.png`, fullPage: false });

const textAfterClick = await page.locator('body').textContent();
if (textAfterClick.includes('Hide this event?')) {
  console.log('Result: confirmation modal appeared');
  
  // Don't show this again checkbox
  const dontShowCheckbox = page.locator('input[type="checkbox"]');
  if (await dontShowCheckbox.count() > 0) {
    const isChecked = await dontShowCheckbox.isChecked();
    console.log(`"Don't show this again" checkbox checked: ${isChecked}`);
  }
  
  // Click "Hide Event"
  const hideEventBtn = page.locator('button:has-text("Hide Event")');
  if (await hideEventBtn.count() > 0) {
    await hideEventBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${SCREENSHOTS}/07-after-hide-event.png`, fullPage: false });
    
    const afterText = await page.locator('body').textContent();
    console.log(`Modal still visible: ${afterText.includes('Hide this event?')}`);
    
    const hideBtnsAfter3 = await page.locator('[title="Hide event"]').count();
    const manageHiddenAfter3 = (await page.locator('button:has-text("Manage Hidden")').textContent()).trim();
    console.log(`After hiding: hide buttons=${hideBtnsAfter3}, Manage Hidden="${manageHiddenAfter3}"`);
  } else {
    console.log('ERROR: Could not find "Hide Event" button in confirmation modal');
  }
} else if (textAfterClick.includes('Subscribe to Updates')) {
  console.log('Result: subscribe modal appeared (BUG - should show confirmation for subscribed user)');
} else {
  console.log('Result: no modal appeared - event may have been hidden directly');
}

// ======== TEST 4: Click x on another card ========
console.log('\n=== TEST 4: Click x on another card ===');
await page.waitForTimeout(300);

const hideBtns4 = await page.locator('[title="Hide event"]').count();
console.log(`Hide buttons remaining before second click: ${hideBtns4}`);

if (hideBtns4 > 0) {
  const hideBtn4 = page.locator('[title="Hide event"]').first();
  await hideBtn4.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${SCREENSHOTS}/08-second-hide-click.png`, fullPage: false });
  
  const txt4 = await page.locator('body').textContent();
  if (txt4.includes('Hide this event?')) {
    console.log('Confirmation modal appeared for second card');
    const hideEventBtn4 = page.locator('button:has-text("Hide Event")');
    if (await hideEventBtn4.count() > 0) {
      await hideEventBtn4.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: `${SCREENSHOTS}/09-second-hide-result.png`, fullPage: false });
      
      const hideBtnsAfter4 = await page.locator('[title="Hide event"]').count();
      const manageHidden4 = (await page.locator('button:has-text("Manage Hidden")').textContent()).trim();
      console.log(`After second hide: buttons=${hideBtnsAfter4}, Manage Hidden="${manageHidden4}"`);
      console.log('Second hide worked correctly');
    }
  } else if (txt4.includes('Subscribe to Updates')) {
    console.log('ERROR: Subscribe modal appeared for subscribed user');
  } else {
    console.log('No modal appeared - event was hidden directly (user checked "Don\'t show again")');
    await page.waitForTimeout(1000);
    
    const hideBtnsAfter4b = await page.locator('[title="Hide event"]').count();
    const manageHidden4b = (await page.locator('button:has-text("Manage Hidden")').textContent()).trim();
    console.log(`After second click: buttons=${hideBtnsAfter4b}, Manage Hidden="${manageHidden4b}"`);
  }
}

// ======== TEST 5: Click x, Cancel, then x again ========
console.log('\n=== TEST 5: Click x, Cancel, then x again ===');
const hideBtns5 = await page.locator('[title="Hide event"]').count();
if (hideBtns5 > 0) {
  const hideBtn5 = page.locator('[title="Hide event"]').first();
  await hideBtn5.click();
  await page.waitForTimeout(300);
  
  const txt5 = await page.locator('body').textContent();
  if (txt5.includes('Hide this event?')) {
    console.log('Confirmation modal appeared');
    const cancelBtn = page.locator('button:has-text("Cancel")');
    if (await cancelBtn.count() > 0) {
      await cancelBtn.click();
      await page.waitForTimeout(300);
      console.log('Clicked Cancel');
      await page.screenshot({ path: `${SCREENSHOTS}/10-after-cancel.png`, fullPage: false });
      
      // Check event is still there
      const hideBtnsAfterCancel = await page.locator('[title="Hide event"]').count();
      console.log(`Hide buttons after cancel: ${hideBtnsAfterCancel}`);
      
      // Click x again on same card
      const hideBtn5Again = page.locator('[title="Hide event"]').first();
      await hideBtn5Again.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: `${SCREENSHOTS}/11-click-again-after-cancel.png`, fullPage: false });
      
      const txt5Again = await page.locator('body').textContent();
      if (txt5Again.includes('Hide this event?')) {
        console.log('Confirmation modal appeared on second click (good - consistent)');
        
        const hideEventBtn5 = page.locator('button:has-text("Hide Event")');
        if (await hideEventBtn5.count() > 0) {
          await hideEventBtn5.click();
          await page.waitForTimeout(1000);
          await page.screenshot({ path: `${SCREENSHOTS}/12-hide-after-cancel-again.png`, fullPage: false });
          console.log('Clicked Hide Event after cancel-again cycle');
          
          const finalBtns5 = await page.locator('[title="Hide event"]').count();
          console.log(`Hide buttons after cycle: ${finalBtns5}`);
        }
      } else {
        console.log('WARNING: No confirmation modal on second click');
      }
    }
  }
}

// ======== TEST 6: Click x on highlight card ========
console.log('\n=== TEST 6: Click x on a highlight card ===');
const hideBtns6 = await page.locator('[title="Hide event"]').count();
console.log(`Hide buttons remaining: ${hideBtns6}`);

if (hideBtns6 > 0) {
  // The first 3 cards in the grid are highlights
  const allBtns = page.locator('[title="Hide event"]');
  const firstBtn = allBtns.first();
  
  // Get context - check if it's in the highlight section
  const isHighlight = await page.evaluate(() => {
    const btn = document.querySelector('[title="Hide event"]');
    if (!btn) return 'no-button';
    const sections = document.querySelectorAll('[class*="bg-gradient"]');
    for (const section of sections) {
      if (section.contains(btn)) return 'in-gradient-section';
    }
    return 'not-in-gradient-section';
  });
  console.log(`First button context: ${isHighlight}`);
  
  await firstBtn.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${SCREENSHOTS}/13-highlight-card-hide.png`, fullPage: false });
  
  const txt6 = await page.locator('body').textContent();
  if (txt6.includes('Hide this event?')) {
    console.log('Confirmation modal appeared for highlight card');
    
    const hideEventBtn6 = page.locator('button:has-text("Hide Event")');
    if (await hideEventBtn6.count() > 0) {
      await hideEventBtn6.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: `${SCREENSHOTS}/14-highlight-card-hide-result.png`, fullPage: false });
      
      const finalBtns6 = await page.locator('[title="Hide event"]').count();
      const manageHidden6 = (await page.locator('button:has-text("Manage Hidden")').textContent()).trim();
      console.log(`After highlight card hide: buttons=${finalBtns6}, Manage Hidden="${manageHidden6}"`);
      console.log('Highlight card hide worked correctly');
    }
  } else {
    console.log('No confirmation modal for highlight card');
  }
}

// Final state
console.log('\n=== FINAL STATE ===');
const finalBtns = await page.locator('[title="Hide event"]').count();
const finalManageText = (await page.locator('button:has-text("Manage Hidden")').textContent()).trim();
const finalLsEmail = await page.evaluate(() => localStorage.getItem('subscriber_email'));
const finalDontAsk = await page.evaluate(() => localStorage.getItem('hide_dont_ask'));
console.log(JSON.stringify({
  remainingHideButtons: finalBtns,
  manageHiddenText: finalManageText,
  subscriberEmail: finalLsEmail,
  hideDontAsk: finalDontAsk
}));

// Print console logs
console.log('\n=== CONSOLE LOGS ===');
consoleLogs.forEach(log => console.log(log));

await page.screenshot({ path: `${SCREENSHOTS}/99-final.png`, fullPage: false });
await browser.close();
console.log('\n=== TESTS COMPLETE ===');
console.log(`Screenshots in: ${SCREENSHOTS}`);