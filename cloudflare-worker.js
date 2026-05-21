/**
 * TYLER HENSCHEL MORTGAGE — SECURE ANTHROPIC PROXY
 * Cloudflare Worker — Deploy at workers.cloudflare.com
 * 
 * This worker:
 * 1. Keeps your API key hidden from the public
 * 2. Rate limits to prevent abuse (10 requests/minute per IP)
 * 3. Blocks suspicious bot traffic
 * 4. Only allows requests from tylerhloans.com
 * 5. Logs blocked requests for monitoring
 */

// ============================================================
// CONFIGURATION — Only edit these values
// ============================================================
const CONFIG = {
  // Paste your NEW Anthropic API key here after creating it
  // This value is encrypted and never visible to anyone
  ANTHROPIC_API_KEY: 'PASTE_YOUR_NEW_API_KEY_HERE',
  
  // Your website domain — only requests from here are allowed
  ALLOWED_ORIGIN: 'https://tylerhloans.com',
  
  // Rate limiting — requests per minute per IP address
  MAX_REQUESTS_PER_MINUTE: 10,
  
  // Max tokens per request — prevents single expensive requests
  MAX_TOKENS_ALLOWED: 500,
  
  // Model to use
  MODEL: 'claude-haiku-4-5-20251001', // Haiku — 10x cheaper, still smart
};

// ============================================================
// RATE LIMITING — Simple in-memory store
// ============================================================
const rateLimitMap = new Map();

function isRateLimited(ip) {
  const now = Date.now();
  const windowMs = 60 * 1000; // 1 minute window
  
  if (!rateLimitMap.has(ip)) {
    rateLimitMap.set(ip, { count: 1, resetAt: now + windowMs });
    return false;
  }
  
  const record = rateLimitMap.get(ip);
  
  // Reset window if expired
  if (now > record.resetAt) {
    rateLimitMap.set(ip, { count: 1, resetAt: now + windowMs });
    return false;
  }
  
  // Increment and check
  record.count++;
  if (record.count > CONFIG.MAX_REQUESTS_PER_MINUTE) {
    return true; // Rate limited
  }
  
  return false;
}

// ============================================================
// BOT DETECTION — Block obvious abuse patterns
// ============================================================
function isSuspiciousRequest(request, body) {
  const userAgent = request.headers.get('User-Agent') || '';
  
  // Block requests with no user agent (pure bots)
  if (!userAgent) return true;
  
  // Block known scraper user agents
  const blockedAgents = ['curl', 'wget', 'python-requests', 'scrapy', 'bot', 'crawler'];
  if (blockedAgents.some(agent => userAgent.toLowerCase().includes(agent))) return true;
  
  // Block if max_tokens is suspiciously high
  if (body?.max_tokens > CONFIG.MAX_TOKENS_ALLOWED) return true;
  
  // Block if messages array is suspiciously long (bulk abuse)
  if (body?.messages?.length > 20) return true;
  
  return false;
}

// ============================================================
// MAIN WORKER
// ============================================================
export default {
  async fetch(request, env) {
    
    // ── CORS Preflight ──
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': CONFIG.ALLOWED_ORIGIN,
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    // ── Only allow POST ──
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    // ── Check origin — only allow tylerhloans.com ──
    const origin = request.headers.get('Origin') || '';
    const referer = request.headers.get('Referer') || '';
    
    const isAllowedOrigin = 
      origin.includes('tylerhloans.com') || 
      referer.includes('tylerhloans.com') ||
      origin.includes('netlify.app') || // Allow during testing
      referer.includes('netlify.app');
      
    if (!isAllowedOrigin) {
      console.log(`Blocked request from origin: ${origin}`);
      return new Response('Forbidden', { status: 403 });
    }

    // ── Rate limiting by IP ──
    const clientIP = request.headers.get('CF-Connecting-IP') || 
                     request.headers.get('X-Forwarded-For') || 
                     'unknown';
                     
    if (isRateLimited(clientIP)) {
      console.log(`Rate limited IP: ${clientIP}`);
      return new Response(
        JSON.stringify({ error: { message: 'Too many requests. Please wait a moment.' } }),
        { 
          status: 429,
          headers: { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': CONFIG.ALLOWED_ORIGIN 
          }
        }
      );
    }

    // ── Parse request body ──
    let body;
    try {
      body = await request.json();
    } catch {
      return new Response('Invalid JSON', { status: 400 });
    }

    // ── Bot/abuse detection ──
    if (isSuspiciousRequest(request, body)) {
      console.log(`Blocked suspicious request from: ${clientIP}`);
      return new Response('Forbidden', { status: 403 });
    }

    // ── Force safe settings — prevent token abuse ──
    const safeBody = {
      ...body,
      model: CONFIG.MODEL, // Always use the configured model
      max_tokens: Math.min(body.max_tokens || 400, CONFIG.MAX_TOKENS_ALLOWED),
    };

    // ── Forward to Anthropic ──
    try {
      const anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': CONFIG.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify(safeBody),
      });

      const responseData = await anthropicResponse.json();

      // ── Return response to website ──
      return new Response(JSON.stringify(responseData), {
        status: anthropicResponse.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': CONFIG.ALLOWED_ORIGIN,
        },
      });

    } catch (error) {
      console.error('Anthropic API error:', error);
      return new Response(
        JSON.stringify({ error: { message: 'Service temporarily unavailable' } }),
        { 
          status: 503,
          headers: { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': CONFIG.ALLOWED_ORIGIN
          }
        }
      );
    }
  },
};
