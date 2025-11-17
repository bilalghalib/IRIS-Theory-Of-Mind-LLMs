import { BrowserHelper, createBrowser } from './helpers/browser';

describe('Visual Regression Tests', () => {
  let browser: BrowserHelper;
  const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  const UPDATE_SCREENSHOTS = process.env.UPDATE_SCREENSHOTS === 'true';

  beforeAll(async () => {
    browser = createBrowser();
    await browser.launch();
  });

  afterAll(async () => {
    await browser.close();
  });

  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1920, height: 1080 }
  ];

  describe('Landing Page Screenshots', () => {
    for (const viewport of viewports) {
      test(`should match snapshot on ${viewport.name}`, async () => {
        const page = browser.getPage();
        await page.setViewport({ width: viewport.width, height: viewport.height });
        await browser.goto(`${BASE_URL}/`);

        // Wait for all images and fonts to load
        await page.evaluate(() => {
          return Promise.all([
            document.fonts.ready,
            ...Array.from(document.images).map(img => {
              if (img.complete) return Promise.resolve();
              return new Promise(resolve => {
                img.onload = img.onerror = resolve;
              });
            })
          ]);
        });

        const screenshot = await page.screenshot({ fullPage: true });

        expect(screenshot).toMatchImageSnapshot({
          customSnapshotIdentifier: `landing-page-${viewport.name}`,
          failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.01,
          failureThresholdType: 'percent'
        });
      });
    }
  });

  describe('Pricing Calculator Screenshots', () => {
    for (const viewport of viewports) {
      test(`should match snapshot on ${viewport.name}`, async () => {
        const page = browser.getPage();
        await page.setViewport({ width: viewport.width, height: viewport.height });
        await browser.goto(`${BASE_URL}/pricing-calculator.html`);

        await page.evaluate(() => {
          return document.fonts.ready;
        });

        const screenshot = await page.screenshot({ fullPage: true });

        expect(screenshot).toMatchImageSnapshot({
          customSnapshotIdentifier: `pricing-calculator-${viewport.name}`,
          failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.01,
          failureThresholdType: 'percent'
        });
      });
    }
  });

  describe('Interactive State Screenshots', () => {
    test('should capture hero section on hover', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 });
      await browser.goto(`${BASE_URL}/`);

      // Hover over primary CTA
      await page.hover('.btn-primary');
      await page.waitForTimeout(300); // Wait for hover animation

      const screenshot = await page.screenshot({
        clip: { x: 0, y: 0, width: 1920, height: 800 }
      });

      expect(screenshot).toMatchImageSnapshot({
        customSnapshotIdentifier: 'hero-cta-hover',
        failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.05,
        failureThresholdType: 'percent'
      });
    });

    test('should capture pricing card on hover', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 });
      await browser.goto(`${BASE_URL}/`);

      // Scroll to pricing section
      await page.evaluate(() => {
        const pricing = document.querySelector('.pricing');
        pricing?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });

      await page.waitForTimeout(500);

      // Hover over featured pricing card
      await page.hover('.pricing-card.featured');
      await page.waitForTimeout(300);

      const pricingSection = await page.$('.pricing');
      const screenshot = await pricingSection!.screenshot();

      expect(screenshot).toMatchImageSnapshot({
        customSnapshotIdentifier: 'pricing-card-hover',
        failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.05,
        failureThresholdType: 'percent'
      });
    });

    test('should capture calculator with different values', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 });
      await browser.goto(`${BASE_URL}/pricing-calculator.html`);

      // Set specific values
      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '10000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '5';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(300);

      const screenshot = await page.screenshot({ fullPage: true });

      expect(screenshot).toMatchImageSnapshot({
        customSnapshotIdentifier: 'calculator-pro-plan',
        failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.01,
        failureThresholdType: 'percent'
      });
    });
  });

  describe('Component Screenshots', () => {
    test('should capture hero section', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 });
      await browser.goto(`${BASE_URL}/`);

      const heroSection = await page.$('.hero');
      const screenshot = await heroSection!.screenshot();

      expect(screenshot).toMatchImageSnapshot({
        customSnapshotIdentifier: 'hero-section',
        failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.01,
        failureThresholdType: 'percent'
      });
    });

    test('should capture features grid', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 });
      await browser.goto(`${BASE_URL}/`);

      const featuresSection = await page.$('.features');
      const screenshot = await featuresSection!.screenshot();

      expect(screenshot).toMatchImageSnapshot({
        customSnapshotIdentifier: 'features-grid',
        failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.01,
        failureThresholdType: 'percent'
      });
    });

    test('should capture testimonials section', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 });
      await browser.goto(`${BASE_URL}/`);

      await page.evaluate(() => {
        const testimonials = Array.from(document.querySelectorAll('.container'))
          .find(el => el.textContent?.includes('Loved by Developers'));
        testimonials?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });

      await page.waitForTimeout(500);

      const testimonialsSection = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('.container'))
          .find(el => el.textContent?.includes('Loved by Developers'));
      });

      if (testimonialsSection) {
        const screenshot = await page.screenshot({
          clip: await page.evaluate((el) => {
            const rect = el!.getBoundingClientRect();
            return {
              x: rect.left,
              y: rect.top,
              width: rect.width,
              height: rect.height
            };
          }, testimonialsSection)
        });

        expect(screenshot).toMatchImageSnapshot({
          customSnapshotIdentifier: 'testimonials-section',
          failureThreshold: UPDATE_SCREENSHOTS ? 1 : 0.05,
          failureThresholdType: 'percent'
        });
      }
    });
  });

  describe('Dark Mode (Future)', () => {
    // Placeholder for future dark mode testing
    test.skip('should match dark mode snapshot', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 });

      // Emulate dark mode preference
      await page.emulateMediaFeatures([
        { name: 'prefers-color-scheme', value: 'dark' }
      ]);

      await browser.goto(`${BASE_URL}/`);

      const screenshot = await page.screenshot({ fullPage: true });

      expect(screenshot).toMatchImageSnapshot({
        customSnapshotIdentifier: 'landing-page-dark-mode',
        failureThreshold: 0.01,
        failureThresholdType: 'percent'
      });
    });
  });
});
