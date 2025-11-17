/**
 * Next.js App Router Example - Chat API Route
 *
 * This example shows how to integrate Aperture into a Next.js chat application.
 * It proxies user messages through Aperture to build user understanding over time.
 */

import { Aperture } from '@aperture/sdk';
import { NextRequest, NextResponse } from 'next/server';

// Initialize Aperture client (reuse across requests)
const aperture = new Aperture({
  apiKey: process.env.APERTURE_API_KEY!,
});

export async function POST(request: NextRequest) {
  try {
    const { message, userId, conversationId } = await request.json();

    // Validate required fields
    if (!message || !userId) {
      return NextResponse.json(
        { error: 'Missing required fields: message, userId' },
        { status: 400 }
      );
    }

    // Send message through Aperture
    const response = await aperture.sendMessage({
      userId,
      message,
      conversationId,
      llmProvider: 'openai',
      llmApiKey: process.env.OPENAI_API_KEY!,
      systemPrompt: 'You are a helpful assistant that provides clear, concise answers.',
      temperature: 0.7,
      metadata: {
        source: 'web_app',
        userAgent: request.headers.get('user-agent'),
        timestamp: new Date().toISOString()
      }
    });

    return NextResponse.json({
      message: response.response,
      conversationId: response.conversationId,
      messageId: response.messageId,
      apertureLink: response.apertureLink,
      assessmentCount: response.assessmentCount
    });

  } catch (error: any) {
    console.error('Chat error:', error);

    return NextResponse.json(
      {
        error: 'Failed to process message',
        detail: error.message
      },
      { status: 500 }
    );
  }
}
