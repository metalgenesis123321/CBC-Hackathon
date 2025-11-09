# main.py - PRODUCTION VERSION with Dashboard Processor
import asyncio, time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .utils import utc_now_iso, short_id, extract_first_json_block
from .clients import fetch_market_detail, fetch_news_for_market, call_claude, fetch_markets, fetch_latest_news
from .mcp import get_manipulation_report, call_mcp_with_payload, startup_mcp_servers, shutdown_mcp_servers
from .dashboard_processor import process_chat_for_dashboard

# prompts module supplied by prompt-engineer
try:
    from . import prompts as prompts_module
except Exception:
    prompts_module = None

app = FastAPI(title="PolySage API - Production")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# Lifecycle events for MCP servers
@app.on_event("startup")
async def on_startup():
    """Start MCP servers when API starts"""
    print("="*70)
    print("PolySage API Starting...")
    print("="*70)
    try:
        await startup_mcp_servers()
        print("✓ MCP servers initialized")
    except Exception as e:
        print(f"✗ CRITICAL: MCP servers failed to start: {e}")
        raise  # Don't continue if MCP servers fail
    print("="*70)


@app.on_event("shutdown")
async def on_shutdown():
    """Shutdown MCP servers when API stops"""
    print("\nShutting down MCP servers...")
    await shutdown_mcp_servers()
    print("✓ Shutdown complete")


@app.post("/chat")
async def post_chat(payload: Dict[str,Any]):
    """
    Main chat endpoint with dashboard generation.
    
    Returns:
        {
            "chat": {...},
            "dashboard": {...}  // Exact dashboardData.js format
        }
    """
    request_id = short_id()
    start_ts = time.time()

    query = payload.get("query") or payload.get("text")
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query' field")
    
    context = payload.get("context", {}) or {}
    market_id = context.get("market_id")

    print(f"\n[{request_id}] New chat request: {query[:50]}...")

    # 1) Fetch market & trades
    market = {"id": market_id} if market_id else {"id": "unknown", "title": query}
    trades = []
    
    if market_id:
        print(f"[{request_id}] Fetching market data for: {market_id}")
        try:
            market_task = asyncio.create_task(fetch_market_detail(market_id))
            trades_task = asyncio.create_task(fetch_trades(market_id, limit=50))
            market = await market_task
            trades = await trades_task
        except Exception as e:
            print(f"[{request_id}] Warning: Failed to fetch market details: {e}")
            market = {"id": market_id, "title": query}

    # 2) Fetch news
    print(f"[{request_id}] Fetching news...")
    try:
        news = await fetch_news_for_market((market.get("title") or query)[:200], page_size=5)
    except Exception as e:
        print(f"[{request_id}] Warning: Failed to fetch news: {e}")
        news = []

    # 3) Build structured prompt
    structured_prompt = {
        "mcp_payload": {
            "market_id": market.get("id"),
            "market": {
                "id": market.get("id"),
                "title": market.get("title"),
                "currentPrice": market.get("currentPrice") or market.get("lastPrice"),
                "volume24hr": market.get("volume24hr")
            },
            "recent_trades": market.get("recentTrades", trades),
            "orderbook": market.get("orderbook", {}),
            "news": news,
            "meta": {"request_id": request_id}
        },
        "system_prompt": "You are an expert prediction-market analyst. Provide clear, actionable analysis.",
        "user_prompt": f"Analyze this market comprehensively.\n\nQuestion: {market.get('title', query)}\n\nUser Query: {query}\n\nProvide analysis in JSON format with keys: answer, reasoning (array), recommended_action, confidence (0-1)"
    }

    # 4) Call MCP + Claude concurrently
    print(f"[{request_id}] Calling MCP servers + Claude...")
    
    mcp_payload = structured_prompt["mcp_payload"]
    system_prompt = structured_prompt["system_prompt"]
    user_prompt = structured_prompt["user_prompt"]

    try:
        # Run both concurrently
        mcp_task = asyncio.create_task(call_mcp_with_payload(mcp_payload))
        claude_task = asyncio.create_task(call_claude(
            system_prompt, 
            user_prompt,
            temperature=0.2,
            max_tokens=1000
        ))

        mcp_result = await mcp_task
        claude_raw = await claude_task
        
        print(f"[{request_id}] ✓ MCP analysis complete - Risk: {mcp_result.get('riskScore')}/100")
        
    except Exception as e:
        print(f"[{request_id}] ✗ CRITICAL: Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # 5) Parse Claude response
    try:
        claude_json = extract_first_json_block(claude_raw)
        if not claude_json or not isinstance(claude_json, dict):
            claude_json = {
                "answer": claude_raw,
                "reasoning": ["Analysis provided"],
                "recommended_action": "Review the detailed analysis",
                "confidence": 0.7
            }
    except Exception as e:
        print(f"[{request_id}] Warning: Failed to parse Claude JSON: {e}")
        claude_json = {
            "answer": claude_raw,
            "reasoning": [],
            "recommended_action": None,
            "confidence": 0.5
        }

    # 6) Transform MCP data into dashboard format using Claude
    print(f"[{request_id}] Transforming to dashboard format...")
    
    try:
        dashboard_data = await process_chat_for_dashboard(
            mcp_result=mcp_result,
            market=market,
            call_claude_func=call_claude
        )
        print(f"[{request_id}] ✓ Dashboard data generated")
        print(f"[{request_id}]   Health: {dashboard_data['healthScore']}/100")
        print(f"[{request_id}]   Liquidity: {dashboard_data['liquidityScore']}/10")
        print(f"[{request_id}]   News: {len(dashboard_data['news'])} articles")
        
    except Exception as e:
        print(f"[{request_id}] ✗ CRITICAL: Dashboard transformation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

    # 7) Build chat response
    chat_response = {
        "answer": claude_json.get("answer", "Analysis complete. See dashboard for details."),
        "reasoning": claude_json.get("reasoning", []),
        "recommended_action": claude_json.get("recommended_action"),
        "confidence": claude_json.get("confidence", 0.0),
    }

    elapsed = time.time() - start_ts
    print(f"[{request_id}] ✓ Request completed in {elapsed:.2f}s\n")

    # 8) Return final response
    return {
        "chat": chat_response,
        "dashboard": dashboard_data
    }


@app.get("/dashboard")
async def get_dashboard(market_id: str = Query(...)):
    """
    Get dashboard data for a specific market.
    
    Returns dashboard in exact dashboardData.js format.
    """
    request_id = short_id()
    print(f"\n[{request_id}] Dashboard request for: {market_id}")
    
    try:
        # Fetch market data
        market = await fetch_market_detail(market_id)
        trades = await fetch_trades(market_id, limit=50)
        news = await fetch_news_for_market(market.get("title") or market_id, page_size=5)
        
        print(f"[{request_id}] Running MCP analysis...")
        
        # Get MCP analysis
        mcp_result = await get_manipulation_report(
            market_id, 
            trades, 
            market.get("orderbook", {}), 
            news, 
            meta={"market": market}
        )
        
        print(f"[{request_id}] Transforming to dashboard format...")
        
        # Transform to dashboard format
        dashboard_data = await process_chat_for_dashboard(
            mcp_result=mcp_result,
            market=market,
            call_claude_func=call_claude
        )
        
        print(f"[{request_id}] ✓ Dashboard generated\n")
        
        return {
            "request_id": request_id,
            "timestamp": utc_now_iso(),
            "dashboard": dashboard_data,
            "mcp_status": "ok"
        }
        
    except Exception as e:
        print(f"[{request_id}] ✗ Dashboard generation failed: {e}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    from .clients import POLY_API_URL, NEWS_API_URL, CLAUDE_API_URL
    from .mcp import _mcp_manager
    
    mcp_poly_running = False
    mcp_news_running = False
    
    if _mcp_manager.initialized:
        mcp_poly_running = _mcp_manager.polymarket_proc is not None and _mcp_manager.polymarket_proc.poll() is None
        mcp_news_running = _mcp_manager.news_proc is not None and _mcp_manager.news_proc.poll() is None
    
    all_ok = mcp_poly_running and mcp_news_running and bool(CLAUDE_API_URL)
    
    return {
        "ok": all_ok,
        "ts": utc_now_iso(),
        "services": {
            "polymarket": bool(POLY_API_URL),
            "news": bool(NEWS_API_URL),
            "claude": bool(CLAUDE_API_URL),
            "mcp_polymarket": mcp_poly_running,
            "mcp_news": mcp_news_running
        }
    }


@app.get("/")
async def root():
    """API info"""
    return {
        "service": "PolySage API",
        "version": "2.0.0-production",
        "features": [
            "Real-time market analysis",
            "MCP server integration",
            "Claude-powered dashboard generation",
            "Structured data transformation"
        ],
        "endpoints": {
            "POST /chat": "Main chat endpoint with dashboard data",
            "GET /dashboard?market_id=X": "Get structured dashboard data",
            "GET /health": "Health check and service status"
        }
    }