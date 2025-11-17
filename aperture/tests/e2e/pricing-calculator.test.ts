import { BrowserHelper, createBrowser } from './helpers/browser';

describe('Pricing Calculator E2E Tests', () => {
  let browser: BrowserHelper;
  const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

  beforeAll(async () => {
    browser = createBrowser();
    await browser.launch();
  });

  afterAll(async () => {
    await browser.close();
  });

  beforeEach(async () => {
    await browser.goto(`${BASE_URL}/pricing-calculator.html`);
  });

  describe('Initial Load', () => {
    test('should display header with title', async () => {
      await browser.waitForSelector('.calculator-header h1');
      const title = await browser.getText('.calculator-header h1');
      expect(title).toContain('Find Your Perfect Plan');
    });

    test('should show default values', async () => {
      const conversationsValue = await browser.getText('#conversations-value');
      const assessmentsValue = await browser.getText('#assessments-value');
      const totalAssessments = await browser.getText('#total-assessments');

      expect(conversationsValue).toContain('1');
      expect(assessmentsValue).toBe('3');
      expect(totalAssessments).toContain('3');
    });

    test('should display recommended plan', async () => {
      await browser.waitForSelector('#plan-name');
      const planName = await browser.getText('#plan-name');
      expect(planName).toBeTruthy();
      expect(['Free', 'Starter', 'Pro', 'Business', 'Enterprise']).toContain(planName);
    });
  });

  describe('Slider Interactions', () => {
    test('should update conversations value when slider moves', async () => {
      const page = browser.getPage();

      // Get initial value
      const initialValue = await browser.getText('#conversations-value');

      // Move slider
      await page.evaluate(() => {
        const slider = document.getElementById('conversations') as HTMLInputElement;
        slider.value = '5000';
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      });

      // Wait a bit for update
      await page.waitForTimeout(100);

      const newValue = await browser.getText('#conversations-value');
      expect(newValue).not.toBe(initialValue);
      expect(newValue).toContain('5');
    });

    test('should update assessments per conversation', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const slider = document.getElementById('assessments-per-conv') as HTMLInputElement;
        slider.value = '7';
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const newValue = await browser.getText('#assessments-value');
      expect(newValue).toBe('7');
    });

    test('should update total assessments calculation', async () => {
      const page = browser.getPage();

      // Set conversations to 2000
      await page.evaluate(() => {
        const slider = document.getElementById('conversations') as HTMLInputElement;
        slider.value = '2000';
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      });

      // Set assessments per conv to 5
      await page.evaluate(() => {
        const slider = document.getElementById('assessments-per-conv') as HTMLInputElement;
        slider.value = '5';
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const total = await browser.getText('#total-assessments');
      // 2000 * 5 = 10,000
      expect(total).toContain('10');
    });
  });

  describe('Plan Recommendations', () => {
    test('should recommend Free plan for low usage', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '200';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '2';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const planName = await browser.getText('#plan-name');
      expect(planName).toBe('Free');

      const price = await browser.getText('#plan-price');
      expect(price).toBe('$0');
    });

    test('should recommend Starter plan for moderate usage', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '1000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '3';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const planName = await browser.getText('#plan-name');
      expect(planName).toBe('Starter');

      const price = await browser.getText('#plan-price');
      expect(price).toBe('$29');
    });

    test('should recommend Pro plan for higher usage', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '5000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '4';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const planName = await browser.getText('#plan-name');
      expect(planName).toBe('Pro');

      const price = await browser.getText('#plan-price');
      expect(price).toBe('$99');
    });

    test('should recommend Business plan for high usage', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '20000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '4';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const planName = await browser.getText('#plan-name');
      expect(planName).toBe('Business');

      const price = await browser.getText('#plan-price');
      expect(price).toBe('$299');
    });

    test('should recommend Enterprise for very high usage', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '50000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '8';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const planName = await browser.getText('#plan-name');
      expect(planName).toBe('Enterprise');

      const price = await browser.getText('#plan-price');
      expect(price).toBe('Custom');
    });
  });

  describe('Plan Features Display', () => {
    test('should show features for recommended plan', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '5000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const features = await page.$$eval('#plan-features li', items =>
        items.map(item => item.textContent?.trim())
      );

      expect(features.length).toBeGreaterThan(0);
      expect(features.some(f => f?.includes('assessments/month'))).toBe(true);
    });

    test('should show headroom calculation', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '1000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '3';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const headroom = await page.$('#headroom');
      expect(headroom).toBeTruthy();

      const headroomValue = await browser.getText('#headroom-value');
      expect(headroomValue).toContain('assessments');
    });
  });

  describe('Annual Cost Calculation', () => {
    test('should calculate annual cost for paid plans', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '1000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const annualCost = await browser.getText('#annual-cost');
      expect(annualCost).toMatch(/\$\d+/);
    });

    test('should show savings with annual billing', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '5000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const savings = await browser.getText('#annual-savings');
      expect(savings).toContain('Save');
      expect(savings).toMatch(/\$\d+/);
    });

    test('should show $0 annual cost for free plan', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '200';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const annualCost = await browser.getText('#annual-cost');
      expect(annualCost).toBe('$0');
    });
  });

  describe('CTA Button', () => {
    test('should update CTA for free plan', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '200';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const ctaText = await browser.getText('#cta-button');
      expect(ctaText).toContain('Get Started');
    });

    test('should update CTA for paid plans', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '5000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const ctaText = await browser.getText('#cta-button');
      expect(ctaText).toContain('Free Trial');
    });

    test('should update CTA for enterprise plan', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '80000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const ctaText = await browser.getText('#cta-button');
      expect(ctaText).toContain('Contact Sales');
    });

    test('should have valid href', async () => {
      const page = browser.getPage();
      const href = await page.$eval('#cta-button', (el: any) => el.href);
      expect(href).toBeTruthy();
      expect(href.startsWith('http') || href.startsWith('mailto:')).toBe(true);
    });
  });

  describe('Number Formatting', () => {
    test('should format large numbers with K suffix', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '50000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const conversationsValue = await browser.getText('#conversations-value');
      expect(conversationsValue).toContain('K');
    });

    test('should format total assessments correctly', async () => {
      const page = browser.getPage();

      await page.evaluate(() => {
        const conv = document.getElementById('conversations') as HTMLInputElement;
        conv.value = '10000';
        conv.dispatchEvent(new Event('input', { bubbles: true }));

        const assess = document.getElementById('assessments-per-conv') as HTMLInputElement;
        assess.value = '5';
        assess.dispatchEvent(new Event('input', { bubbles: true }));
      });

      await page.waitForTimeout(100);

      const total = await browser.getText('#total-assessments');
      expect(total).toContain('K');
    });
  });

  describe('Overage Protection Note', () => {
    test('should display overage protection information', async () => {
      const page = browser.getPage();
      const hasOverageInfo = await page.evaluate(() => {
        return document.body.textContent?.includes('Overage protection');
      });
      expect(hasOverageInfo).toBe(true);
    });

    test('should show overage pricing', async () => {
      const page = browser.getPage();
      const hasOveragePrice = await page.evaluate(() => {
        return document.body.textContent?.includes('$0.01 per assessment');
      });
      expect(hasOveragePrice).toBe(true);
    });
  });

  describe('Responsive Design', () => {
    test('should work on mobile viewport', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 375, height: 667 });
      await browser.goto(`${BASE_URL}/pricing-calculator.html`);

      await browser.waitForSelector('.calculator-header');
      const title = await browser.getText('.calculator-header h1');
      expect(title).toBeTruthy();
    });

    test('should work on tablet viewport', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 768, height: 1024 });
      await browser.goto(`${BASE_URL}/pricing-calculator.html`);

      await browser.waitForSelector('#conversations');
      const slider = await page.$('#conversations');
      expect(slider).toBeTruthy();
    });
  });
});
