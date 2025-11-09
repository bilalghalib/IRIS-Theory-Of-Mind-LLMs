# Next.js + Aperture Chat Example

A simple chat application that integrates Aperture to build user understanding over time.

## Features

- 💬 Real-time chat interface
- 🧠 Automatic user intelligence extraction
- 🔍 "Why this response?" links for transparency
- 🎨 Clean, modern UI with Tailwind CSS
- ⚡ Next.js App Router (React Server Components)

## Setup

1. **Install dependencies:**

```bash
npm install
```

2. **Set environment variables:**

Create `.env.local`:

```bash
APERTURE_API_KEY=your_aperture_key
OPENAI_API_KEY=your_openai_key
```

3. **Run the development server:**

```bash
npm run dev
```

4. **Open your browser:**

Navigate to [http://localhost:3000](http://localhost:3000)

## How It Works

1. User types a message in the chat interface
2. Frontend sends message to `/api/chat` route
3. API route proxies message through Aperture
4. Aperture extracts user insights in the background
5. LLM response is returned to the user
6. User can click "Why this response?" to see what Aperture learned

## Project Structure

```
nextjs-chat/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts      # API endpoint that uses Aperture
│   ├── page.tsx              # Main chat UI
│   └── layout.tsx            # Root layout
├── .env.local                # Environment variables
└── package.json
```

## Key Files

### `/app/api/chat/route.ts`

API route that handles chat messages:

```typescript
const response = await aperture.sendMessage({
  userId,
  message,
  llmProvider: 'openai',
  llmApiKey: process.env.OPENAI_API_KEY!,
  systemPrompt: 'You are a helpful assistant...',
  metadata: { source: 'web_app' }
});
```

### `/app/page.tsx`

React component with chat UI that calls the API route.

## Customization

### Change LLM Provider

In `app/api/chat/route.ts`, change:

```typescript
llmProvider: 'anthropic',
llmApiKey: process.env.ANTHROPIC_API_KEY!,
```

### Add User Authentication

Replace the localStorage user ID with your auth system:

```typescript
// In page.tsx
import { useUser } from '@clerk/nextjs'; // or your auth provider

const { user } = useUser();
const userId = user?.id || 'anonymous';
```

### Query User Assessments

Add a new API route to query what Aperture knows:

```typescript
// app/api/assessments/route.ts
import { aperture } from '@/lib/aperture';

export async function GET(request: NextRequest) {
  const userId = request.nextUrl.searchParams.get('userId');

  const assessments = await aperture.getAssessments(userId!, {
    minConfidence: 0.7
  });

  return NextResponse.json({ assessments });
}
```

## Production Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy!

### Other Platforms

Works on any platform that supports Next.js:
- Netlify
- Railway
- Fly.io
- AWS Amplify

## Learn More

- [Aperture Documentation](https://docs.aperture.dev)
- [Next.js Documentation](https://nextjs.org/docs)
- [Aperture TypeScript SDK](https://github.com/yourusername/aperture/tree/main/sdk/typescript)

## License

MIT
