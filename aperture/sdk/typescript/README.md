# Aperture TypeScript SDK

Official TypeScript/JavaScript client for the Aperture API - User Intelligence for AI Applications.

[![npm version](https://badge.fury.io/js/%40aperture%2Fsdk.svg)](https://badge.fury.io/js/%40aperture%2Fsdk)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-blue.svg)](https://www.typescriptlang.org/)

## Installation

```bash
npm install @aperture/sdk
# or
yarn add @aperture/sdk
# or
pnpm add @aperture/sdk
```

## Quick Start

```typescript
import { Aperture } from '@aperture/sdk';

// Initialize client
const client = new Aperture({ apiKey: 'your-aperture-key' });

// Send a message through Aperture
const response = await client.sendMessage({
  userId: 'user_123',
  message: "I'm trying to deploy my app on AWS but keep getting errors",
  llmProvider: 'openai',
  llmApiKey: 'sk-your-openai-key'
});

// Access the response
console.log(`AI: ${response.response}`);
console.log(`Why this response: ${response.apertureLink}`);
console.log(`Assessments extracted: ${response.assessmentCount}`);
```

## Features

- 🔌 **LLM Proxy** - Works with OpenAI and Anthropic
- 🧠 **Auto-Assessments** - Extracts user insights automatically
- 📊 **Pattern Discovery** - Find common patterns across users
- 🗣️ **Natural Language** - Create constructs from descriptions
- 📚 **Marketplace** - Pre-built construct templates
- 💪 **TypeScript First** - Full type safety and IntelliSense
- 🌐 **Isomorphic** - Works in Node.js and modern browsers

## Usage Examples

### Basic Conversation

```typescript
import { Aperture } from '@aperture/sdk';

const client = new Aperture({ apiKey: 'aperture_xxx' });

// Create conversation
const conversation = await client.createConversation('user_123', {
  source: 'web_app'
});

// Send messages
const response = await client.sendMessage({
  userId: 'user_123',
  message: 'How do I deploy to AWS?',
  conversationId: conversation.id,
  llmProvider: 'openai',
  llmApiKey: 'sk-...',
  systemPrompt: 'You are a helpful DevOps assistant'
});

console.log(response.response);
```

### Query User Assessments

```typescript
// Get all assessments for a user
const assessments = await client.getAssessments('user_123');

for (const assessment of assessments) {
  console.log(`${assessment.element}: ${assessment.value}`);
  console.log(`Confidence: ${assessment.confidence}`);
  console.log(`Reasoning: ${assessment.reasoning}`);
  console.log();
}

// Filter by element
const technical = await client.getAssessments('user_123', {
  element: 'technical_confidence',
  minConfidence: 0.7
});

// Get assessment with evidence
const detail = await client.getAssessment('user_123', assessment.id);
for (const evidence of detail.evidence) {
  console.log(`User said: ${evidence.userMessage}`);
}
```

### Pattern Discovery

```typescript
// Discover patterns across all users
const result = await client.discoverPatterns({
  minUsers: 10,
  minOccurrenceRate: 0.2,
  lookbackDays: 7
});

console.log(`Found ${result.patternsFound} patterns`);

for (const pattern of result.patterns) {
  console.log(`Pattern: ${pattern.name}`);
  console.log(`Found in: ${pattern.detectedIn} users`);
  console.log(`Confidence: ${pattern.confidence}`);
  console.log();
}
```

### Natural Language Constructs

```typescript
// Create construct from description
const result = await client.createConstructFromDescription(
  'I want to track if users are ready to upgrade to paid tier'
);

if (result.matchType === 'template') {
  console.log('Found similar templates:');
  for (const template of result.suggestedTemplates!) {
    console.log(`- ${template.name} (similarity: ${template.similarity})`);
  }
} else {
  console.log('Generated custom construct:');
  console.log(result.customGenerated);
}
```

### Browse Marketplace

```typescript
// Get all templates
const templates = await client.getConstructTemplates();

for (const template of templates) {
  console.log(`${template.name}: ${template.description}`);
}

// Search templates
const supportTemplates = await client.getConstructTemplates({
  useCase: 'customer support'
});
```

### User Corrections

```typescript
// Submit a correction
await client.correctAssessment('user_123', 'assess_456', {
  correctionType: 'wrong_value',
  userExplanation: "I'm actually very confident with AWS"
});
```

## API Reference

### `new Aperture(config)`

Initialize the client.

**Parameters:**
- `apiKey` (string): Your Aperture API key
- `baseUrl` (string, optional): API base URL (default: `https://api.aperture.dev`)
- `timeout` (number, optional): Request timeout in milliseconds (default: 30000)

### `sendMessage(params)`

Send a message through Aperture.

**Parameters:**
- `userId` (string): Your internal user identifier
- `message` (string): User's message
- `llmProvider` ('openai' | 'anthropic'): LLM provider
- `llmApiKey` (string): Customer's LLM API key
- `conversationId` (string, optional): Existing conversation ID
- `llmModel` (string, optional): Model to use
- `systemPrompt` (string, optional): System prompt
- `temperature` (number, optional): LLM temperature (default: 0.7)
- `maxTokens` (number, optional): Max tokens (default: 1000)
- `metadata` (object, optional): Optional metadata

**Returns:** `Promise<MessageResponse>`

### `getAssessments(userId, params?)`

Get assessments for a user.

**Parameters:**
- `userId` (string): User to query
- `params.element` (string, optional): Filter by element
- `params.minConfidence` (number, optional): Minimum confidence
- `params.maxConfidence` (number, optional): Maximum confidence
- `params.limit` (number, optional): Max results (default: 50)

**Returns:** `Promise<Assessment[]>`

### `getAssessment(userId, assessmentId)`

Get specific assessment with evidence.

**Returns:** `Promise<AssessmentWithEvidence>`

### `discoverPatterns(params?)`

Discover patterns across users.

**Parameters:**
- `minUsers` (number, optional): Minimum users (default: 10)
- `minOccurrenceRate` (number, optional): Minimum rate (default: 0.2)
- `lookbackDays` (number, optional): Days to analyze (default: 7)

**Returns:** `Promise<{ patternsFound: number; patterns: DiscoveredPattern[] }>`

### `createConstructFromDescription(description)`

Create construct from natural language.

**Parameters:**
- `description` (string): What you want to track

**Returns:** `Promise<ConstructFromDescriptionResult>`

### `getConstructTemplates(params?)`

Browse marketplace templates.

**Parameters:**
- `search` (string, optional): Search query
- `useCase` (string, optional): Filter by use case

**Returns:** `Promise<ConstructTemplate[]>`

## Types

### `MessageResponse`

Response from sending a message.

```typescript
interface MessageResponse {
  conversationId: string;
  messageId: string;
  response: string;
  apertureLink: string;
  assessmentCount: number;
  provider: string;
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}
```

### `Assessment`

User assessment with confidence score.

```typescript
interface Assessment {
  id: string;
  userId: string;
  element: string;
  valueType: 'score' | 'tag' | 'range' | 'text';
  valueData: any;
  value: any;
  reasoning: string;
  confidence: number;
  createdAt: string;
  updatedAt: string;
  userCorrected?: boolean;
  observationCount?: number;
}
```

### `AssessmentWithEvidence`

Assessment with supporting evidence (extends `Assessment`).

```typescript
interface AssessmentWithEvidence extends Assessment {
  evidence: Array<{
    userMessage: string;
    timestamp: string;
    conversationId: string;
  }>;
}
```

## Error Handling

```typescript
import { Aperture, ApertureAPIError, ApertureError } from '@aperture/sdk';

const client = new Aperture({ apiKey: 'your-key' });

try {
  const response = await client.sendMessage({...});
} catch (error) {
  if (error instanceof ApertureAPIError) {
    console.error(`API error ${error.statusCode}: ${error.message}`);
  } else if (error instanceof ApertureError) {
    console.error(`SDK error: ${error.message}`);
  } else {
    throw error;
  }
}
```

## Configuration

### Environment Variables

You can set your API key via environment variable:

```bash
export APERTURE_API_KEY="your-key"
```

```typescript
import { Aperture } from '@aperture/sdk';

const client = new Aperture({
  apiKey: process.env.APERTURE_API_KEY!
});
```

### Custom Base URL

For self-hosted or development:

```typescript
const client = new Aperture({
  apiKey: 'your-key',
  baseUrl: 'http://localhost:8000'
});
```

## Best Practices

### 1. Reuse Client Instance

```typescript
// Good: Create once, reuse
const client = new Aperture({ apiKey: '...' });

for (const userMessage of messages) {
  const response = await client.sendMessage({...});
}

// Bad: Creating new client each time
for (const userMessage of messages) {
  const client = new Aperture({ apiKey: '...' }); // Don't do this
  const response = await client.sendMessage({...});
}
```

### 2. Handle Errors Gracefully

```typescript
try {
  const response = await client.sendMessage({...});
} catch (error) {
  if (error instanceof ApertureAPIError && error.statusCode === 429) {
    // Rate limited - wait and retry
    await new Promise(resolve => setTimeout(resolve, 60000));
    const response = await client.sendMessage({...});
  } else {
    // Log error and use fallback
    console.error('Aperture error:', error);
    const response = await fallbackLlmCall({...});
  }
}
```

### 3. Use Metadata for Context

```typescript
const response = await client.sendMessage({
  userId: 'user_123',
  message: '...',
  llmProvider: 'openai',
  llmApiKey: 'sk-...',
  metadata: {
    source: 'web_app',
    sessionId: 'sess_789',
    userAgent: 'Mozilla/5.0...',
    experiment: 'variant_a'
  }
});
```

### 4. TypeScript Strict Mode

Enable strict mode in your `tsconfig.json` for better type safety:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true
  }
}
```

## Framework Integrations

See the `/examples` directory for:
- Next.js App Router integration
- Next.js Pages Router integration
- Express.js integration
- NestJS integration
- React hooks

## Browser Usage

The SDK works in modern browsers with fetch support:

```typescript
import { Aperture } from '@aperture/sdk';

const client = new Aperture({ apiKey: 'your-key' });

// Use in browser event handlers
button.addEventListener('click', async () => {
  const response = await client.sendMessage({
    userId: currentUser.id,
    message: input.value,
    llmProvider: 'openai',
    llmApiKey: 'sk-...'
  });

  displayResponse(response.response);
});
```

**Security Note:** Never expose your Aperture API key or LLM API keys in client-side code. Use a backend proxy for production apps.

## Support

- **Documentation:** https://docs.aperture.dev
- **GitHub Issues:** https://github.com/yourusername/aperture/issues
- **Discord:** [Join our community](#)
- **Email:** hello@aperture.dev

## License

MIT License - see LICENSE file for details

---

**Built with ❤️ by Aperture**

*Turn conversations into intelligence*
