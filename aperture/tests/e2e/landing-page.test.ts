import { BrowserHelper, createBrowser } from './helpers/browser';

describe('Landing Page E2E Tests', () => {
  let browser: BrowserHelper;
  const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

  beforeAll(async () => {
    browser = createBrowser();
    await browser.launch();
  });

  afterAll(async () => {
    await browser.close();
  });

  describe('Hero Section', () => {
    beforeEach(async () => {
      await browser.goto(`${BASE_URL}/`);
    });

    test('should display main headline', async () => {
      await browser.waitForSelector('.hero h1');
      const headline = await browser.getText('.hero h1');
      expect(headline).toContain('Stop Guessing');
      expect(headline).toContain('Start Knowing Your Users');
    });

    test('should display subheadline with value proposition', async () => {
      const subheadline = await browser.getText('.hero p');
      expect(subheadline).toContain('structured intelligence');
      expect(subheadline).toContain('personalize experiences');
    });

    test('should have CTA buttons', async () => {
      await browser.waitForSelector('.btn-primary');
      await browser.waitForSelector('.btn-secondary');

      const primaryBtn = await browser.getText('.btn-primary');
      expect(primaryBtn).toContain('Start Free');
    });

    test('should show trust indicators', async () => {
      const indicators = await browser.getText('.hero');
      expect(indicators).toContain('5-minute setup');
      expect(indicators).toContain('BYOK');
      expect(indicators).toContain('OpenAI');
    });
  });

  describe('Social Proof Section', () => {
    beforeEach(async () => {
      await browser.goto(`${BASE_URL}/`);
    });

    test('should display metrics', async () => {
      const page = browser.getPage();

      // Check for conversation count
      const conversationsMetric = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('div'));
        return elements.find(el => el.textContent?.includes('50K+'))?.textContent;
      });
      expect(conversationsMetric).toBeTruthy();

      // Check for accuracy metric
      const accuracyMetric = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('div'));
        return elements.find(el => el.textContent?.includes('95%'))?.textContent;
      });
      expect(accuracyMetric).toBeTruthy();
    });

    test('should show company logos placeholder', async () => {
      const page = browser.getPage();
      const hasLogos = await page.evaluate(() => {
        return document.body.textContent?.includes('Trusted by forward-thinking');
      });
      expect(hasLogos).toBe(true);
    });
  });

  describe('Features Section', () => {
    beforeEach(async () => {
      await browser.goto(`${BASE_URL}/`);
    });

    test('should display all key features', async () => {
      const page = browser.getPage();

      const features = [
        'Works With Any LLM',
        'Auto-Extract Insights',
        'Confidence Scores',
        'Evidence Trails',
        'User Corrections',
        'Pattern Discovery'
      ];

      for (const feature of features) {
        const hasFeature = await page.evaluate((featureName) => {
          return document.body.textContent?.includes(featureName);
        }, feature);
        expect(hasFeature).toBe(true);
      }
    });

    test('should have feature icons', async () => {
      const page = browser.getPage();
      const iconCount = await page.$$eval('.feature-icon', icons => icons.length);
      expect(iconCount).toBeGreaterThanOrEqual(6);
    });
  });

  describe('Testimonials Section', () => {
    beforeEach(async () => {
      await browser.goto(`${BASE_URL}/`);
    });

    test('should display testimonials', async () => {
      const page = browser.getPage();

      const testimonials = [
        'Sarah Chen',
        'Marcus Rodriguez',
        'Emma Thompson'
      ];

      for (const name of testimonials) {
        const hasTestimonial = await page.evaluate((authorName) => {
          return document.body.textContent?.includes(authorName);
        }, name);
        expect(hasTestimonial).toBe(true);
      }
    });

    test('should show quantifiable results', async () => {
      const page = browser.getPage();

      const hasMetrics = await page.evaluate(() => {
        const text = document.body.textContent || '';
        return text.includes('35%') || text.includes('3 user segments');
      });
      expect(hasMetrics).toBe(true);
    });
  });

  describe('Pricing Section', () => {
    beforeEach(async () => {
      await browser.goto(`${BASE_URL}/`);
    });

    test('should display all pricing tiers', async () => {
      const page = browser.getPage();

      const tiers = ['Starter', 'Pro', 'Business'];

      for (const tier of tiers) {
        const hasTier = await page.evaluate((tierName) => {
          return document.body.textContent?.includes(tierName);
        }, tier);
        expect(hasTier).toBe(true);
      }
    });

    test('should show pricing amounts', async () => {
      const page = browser.getPage();

      const prices = ['$29', '$99', '$299'];

      for (const price of prices) {
        const hasPrice = await page.evaluate((priceText) => {
          return document.body.textContent?.includes(priceText);
        }, price);
        expect(hasPrice).toBe(true);
      }
    });

    test('should highlight most popular plan', async () => {
      const page = browser.getPage();
      const hasMostPopular = await page.evaluate(() => {
        return document.body.textContent?.includes('MOST POPULAR');
      });
      expect(hasMostPopular).toBe(true);
    });

    test('should show special offers', async () => {
      const page = browser.getPage();
      const hasOffers = await page.evaluate(() => {
        const text = document.body.textContent || '';
        return text.includes('50% off') && text.includes('early-stage startups');
      });
      expect(hasOffers).toBe(true);
    });
  });

  describe('CTA Section', () => {
    beforeEach(async () => {
      await browser.goto(`${BASE_URL}/`);
    });

    test('should have final CTA', async () => {
      const page = browser.getPage();
      const hasCtaHeadline = await page.evaluate(() => {
        return document.body.textContent?.includes('Stop Treating Your Users Like Strangers');
      });
      expect(hasCtaHeadline).toBe(true);
    });

    test('should have action buttons', async () => {
      const page = browser.getPage();
      const buttons = await page.$$eval('a.btn', btns =>
        btns.map(btn => btn.textContent?.trim())
      );

      const hasStartButton = buttons.some(text => text?.includes('Start Building'));
      expect(hasStartButton).toBe(true);
    });
  });

  describe('Responsive Design', () => {
    test('should work on mobile viewport', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 375, height: 667 }); // iPhone SE
      await browser.goto(`${BASE_URL}/`);

      await browser.waitForSelector('.hero h1');
      const headline = await browser.getText('.hero h1');
      expect(headline).toContain('Stop Guessing');
    });

    test('should work on tablet viewport', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 768, height: 1024 }); // iPad
      await browser.goto(`${BASE_URL}/`);

      await browser.waitForSelector('.pricing-cards');
      const page2 = browser.getPage();
      const pricingVisible = await page2.$('.pricing-cards');
      expect(pricingVisible).toBeTruthy();
    });

    test('should work on desktop viewport', async () => {
      const page = browser.getPage();
      await page.setViewport({ width: 1920, height: 1080 }); // Desktop
      await browser.goto(`${BASE_URL}/`);

      await browser.waitForSelector('.features');
      const page2 = browser.getPage();
      const featuresVisible = await page2.$('.features');
      expect(featuresVisible).toBeTruthy();
    });
  });

  describe('Links and Navigation', () => {
    beforeEach(async () => {
      await browser.goto(`${BASE_URL}/`);
    });

    test('should have working footer links', async () => {
      const page = browser.getPage();
      const links = await page.$$eval('footer a', anchors =>
        anchors.map(a => ({
          href: a.getAttribute('href'),
          text: a.textContent?.trim()
        }))
      );

      expect(links.length).toBeGreaterThan(0);
      expect(links.some(link => link.text?.includes('Documentation'))).toBe(true);
      expect(links.some(link => link.text?.includes('GitHub'))).toBe(true);
    });

    test('should have mailto link for contact', async () => {
      const page = browser.getPage();
      const hasMailto = await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a'));
        return links.some(a => a.getAttribute('href')?.startsWith('mailto:'));
      });
      expect(hasMailto).toBe(true);
    });
  });
});
