import puppeteer, { Browser, Page } from 'puppeteer';

export class BrowserHelper {
  private browser: Browser | null = null;
  private page: Page | null = null;

  async launch(): Promise<void> {
    this.browser = await puppeteer.launch({
      headless: process.env.HEADLESS !== 'false',
      slowMo: parseInt(process.env.SLOWMO || '0', 10),
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });
    this.page = await this.browser.newPage();
    await this.page.setViewport({ width: 1920, height: 1080 });
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.page = null;
    }
  }

  getPage(): Page {
    if (!this.page) {
      throw new Error('Browser not launched. Call launch() first.');
    }
    return this.page;
  }

  getBrowser(): Browser {
    if (!this.browser) {
      throw new Error('Browser not launched. Call launch() first.');
    }
    return this.browser;
  }

  async goto(url: string, options?: any): Promise<void> {
    const page = this.getPage();
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000,
      ...options
    });
  }

  async screenshot(name: string): Promise<Buffer> {
    const page = this.getPage();
    return await page.screenshot({
      fullPage: true,
      path: `./screenshots/${name}.png`
    });
  }

  async waitForSelector(selector: string, timeout = 5000): Promise<void> {
    const page = this.getPage();
    await page.waitForSelector(selector, { timeout });
  }

  async click(selector: string): Promise<void> {
    const page = this.getPage();
    await page.click(selector);
  }

  async type(selector: string, text: string): Promise<void> {
    const page = this.getPage();
    await page.type(selector, text);
  }

  async getText(selector: string): Promise<string> {
    const page = this.getPage();
    const element = await page.$(selector);
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    return await page.evaluate(el => el.textContent || '', element);
  }

  async getInputValue(selector: string): Promise<string> {
    const page = this.getPage();
    return await page.$eval(selector, (el: any) => el.value);
  }

  async waitForNavigation(options?: any): Promise<void> {
    const page = this.getPage();
    await page.waitForNavigation({
      waitUntil: 'networkidle2',
      timeout: 30000,
      ...options
    });
  }

  async evaluate<T>(fn: any, ...args: any[]): Promise<T> {
    const page = this.getPage();
    return await page.evaluate(fn, ...args);
  }
}

export const createBrowser = (): BrowserHelper => new BrowserHelper();
