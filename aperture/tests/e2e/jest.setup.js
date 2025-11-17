const { toMatchImageSnapshot } = require('jest-image-snapshot');

expect.extend({ toMatchImageSnapshot });

// Global test configuration
process.env.HEADLESS = process.env.HEADLESS !== 'false';
process.env.SLOWMO = process.env.SLOWMO || '0';

// Increase timeout for all tests
jest.setTimeout(30000);
