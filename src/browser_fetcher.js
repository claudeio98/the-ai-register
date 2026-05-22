const { chromium } = require('playwright');

async function fetchRenderedContent(url) {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    const page = await context.newPage();

    try {
        console.error(`Navigating to: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

        // 2.3 Implement "Load More" logic
        let loadMoreClicked = 0;
        const maxLoadMore = 5;
        while (loadMoreClicked < maxLoadMore) {
            const loadMoreButton = await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button, a'));
                return buttons.find(b => {
                    const text = b.innerText.toLowerCase();
                    return text.includes('load more') || 
                           text.includes('show more') || 
                           text.includes('view more') || 
                           text.includes('next page');
                });
            });

            if (loadMoreButton) {
                console.error(`Clicking Load More button (${loadMoreClicked + 1}/${maxLoadMore})...`);
                await page.click(loadMoreButton).catch(() => {});
                await page.waitForTimeout(2000); 
                loadMoreClicked++;
            } else {
                break;
            }
        }

        // 2.4 Clean extraction + link gathering
        const result = await page.evaluate(() => {
            // Remove noise elements
            const noiseSelectors = ['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript', 'iframe'];
            noiseSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => el.remove());
            });

            // Extract all absolute links
            const links = Array.from(document.querySelectorAll('a[href]'))
                .map(a => a.href)
                .filter(href => href.startsWith('http'));

            return {
                title: document.title,
                content: document.body.innerText.replace(/\n\s*\n/g, '\n\n').trim(),
                links: [...new Set(links)] // Unique links
            };
        });

        await browser.close();
        return result;
    } catch (error) {
        console.error(`Error fetching ${url}: ${error.message}`);
        await browser.close();
        return null;
    }
}

const url = process.argv[2];
if (!url) {
    console.error('URL is required');
    process.exit(1);
}

fetchRenderedContent(url).then(result => {
    if (result) {
        process.stdout.write(JSON.stringify(result));
        process.exit(0);
    } else {
        process.exit(1);
    }
}).catch(err => {
    console.error(err);
    process.exit(1);
});
