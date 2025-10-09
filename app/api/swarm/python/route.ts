/**
 * Next.js API Route - Proxy to Python HECTIC SWARM backend
 * Connects TypeScript UI to Python agents
 */
import { NextRequest, NextResponse } from 'next/server';

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    
    // Validate request
    if (!body.userMessage || !body.conversationId) {
      return NextResponse.json(
        { error: 'Missing userMessage or conversationId' },
        { status: 400 }
      );
    }
    
    console.log(`🔄 Proxying to Python swarm: ${body.userMessage.substring(0, 50)}...`);
    
    // Forward to Python backend
    const response = await fetch(`${PYTHON_BACKEND_URL}/swarm/orchestrate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const error = await response.text();
      console.error('❌ Python backend error:', error);
      return NextResponse.json(
        { error: 'Swarm orchestration failed', details: error },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`✅ Swarm response: ${data.tasks?.length || 0} tasks completed`);
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Proxy error:', error);
    
    // Check if Python backend is running
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return NextResponse.json(
        { 
          error: 'Python backend not reachable',
          hint: 'Start backend with: cd backend && python main.py'
        },
        { status: 503 }
      );
    }
    
    return NextResponse.json(
      { error: 'Internal server error', details: String(error) },
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET() {
  try {
    const response = await fetch(`${PYTHON_BACKEND_URL}/`);
    const data = await response.json();
    
    return NextResponse.json({
      status: 'connected',
      backend: data,
      backendUrl: PYTHON_BACKEND_URL
    });
  } catch (error) {
    return NextResponse.json({
      status: 'disconnected',
      error: 'Python backend not reachable',
      backendUrl: PYTHON_BACKEND_URL,
      hint: 'cd backend && python main.py'
    }, { status: 503 });
  }
}
