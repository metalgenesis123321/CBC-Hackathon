# # # main.py - PRODUCTION VERSION with Dashboard Processor
# # import asyncio, time
# # from typing import Dict, Any, Optional
# # from fastapi import FastAPI, Query, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware

# # from utils import utc_now_iso, short_id, extract_first_json_block
# # from clients import fetch_market_detail, fetch_news_for_market, call_claude, fetch_markets, fetch_latest_news
# # from mcp import get_manipulation_report, call_mcp_with_payload, startup_mcp_servers, shutdown_mcp_servers
# # from dashboard_processor import process_chat_for_dashboard

# # # prompts module supplied by prompt-engineer
# # try:
# #     from . import prompts as prompts_module
# # except Exception:
# #     prompts_module = None

# # app = FastAPI(title="PolySage API - Production")
# # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# # # Lifecycle events for MCP servers
# # @app.on_event("startup")
# # async def on_startup():
# #     """Start MCP servers when API starts"""
# #     print("="*70)
# #     print("PolySage API Starting...")
# #     print("="*70)
# #     try:
# #         await startup_mcp_servers()
# #         print("✓ MCP servers initialized")
# #     except Exception as e:
# #         print(f"✗ CRITICAL: MCP servers failed to start: {e}")
# #         raise  # Don't continue if MCP servers fail
# #     print("="*70)


# # @app.on_event("shutdown")
# # async def on_shutdown():
# #     """Shutdown MCP servers when API stops"""
# #     print("\nShutting down MCP servers...")
# #     await shutdown_mcp_servers()
# #     print("✓ Shutdown complete")


# # @app.post("/chat")
# # async def post_chat(payload: Dict[str,Any]):
# #     """
# #     Main chat endpoint with dashboard generation.
    
# #     Returns:
# #         {
# #             "chat": {...},
# #             "dashboard": {...}  // Exact dashboardData.js format
# #         }
# #     """
# #     request_id = short_id()
# #     start_ts = time.time()

# #     query = payload.get("query") or payload.get("text")
# #     if not query:
# #         raise HTTPException(status_code=400, detail="Missing 'query' field")
    
# #     context = payload.get("context", {}) or {}
# #     market_id = context.get("market_id")

# #     print(f"\n[{request_id}] New chat request: {query[:50]}...")

# #     # 1) Fetch market & trades
# #     market = {"id": market_id} if market_id else {"id": "unknown", "title": query}
# #     trades = []
    
# #     if market_id:
# #         print(f"[{request_id}] Fetching market data for: {market_id}")
# #         try:
# #             market_task = asyncio.create_task(fetch_market_detail(market_id))
            
# #             market = await market_task
            
# #         except Exception as e:
# #             print(f"[{request_id}] Warning: Failed to fetch market details: {e}")
# #             market = {"id": market_id, "title": query}

# #     # 2) Fetch news
# #     print(f"[{request_id}] Fetching news...")
# #     try:
# #         news = await fetch_news_for_market((market.get("title") or query)[:200], page_size=5)
# #     except Exception as e:
# #         print(f"[{request_id}] Warning: Failed to fetch news: {e}")
# #         news = []

# #     # 3) Build structured prompt
# #     structured_prompt = {
# #         "mcp_payload": {
# #             "market_id": market.get("id"),
# #             "market": {
# #                 "id": market.get("id"),
# #                 "title": market.get("title"),
# #                 "currentPrice": market.get("currentPrice") or market.get("lastPrice"),
# #                 "volume24hr": market.get("volume24hr")
# #             },
# #             "recent_trades": market.get("recentTrades", trades),
# #             "orderbook": market.get("orderbook", {}),
# #             "news": news,
# #             "meta": {"request_id": request_id}
# #         },
# #         "system_prompt": "You are an expert prediction-market analyst. Provide clear, actionable analysis.",
# #         "user_prompt": f"Analyze this market comprehensively.\n\nQuestion: {market.get('title', query)}\n\nUser Query: {query}\n\nProvide analysis in JSON format with keys: answer, reasoning (array), recommended_action, confidence (0-1)"
# #     }

# #     # 4) Call MCP + Claude concurrently
# #     print(f"[{request_id}] Calling MCP servers + Claude...")
    
# #     mcp_payload = structured_prompt["mcp_payload"]
# #     system_prompt = structured_prompt["system_prompt"]
# #     user_prompt = structured_prompt["user_prompt"]

# #     try:
# #         # Run both concurrently
# #         mcp_task = asyncio.create_task(call_mcp_with_payload(mcp_payload))
# #         claude_task = asyncio.create_task(call_claude(
# #             system_prompt, 
# #             user_prompt,
# #             temperature=0.2,
# #             max_tokens=1000
# #         ))

# #         mcp_result = await mcp_task
# #         claude_raw = await claude_task
        
# #         print(f"[{request_id}] ✓ MCP analysis complete - Risk: {mcp_result.get('riskScore')}/100")
        
# #     except Exception as e:
# #         print(f"[{request_id}] ✗ CRITICAL: Analysis failed: {e}")
# #         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# #     # 5) Parse Claude response
# #     try:
# #         claude_json = extract_first_json_block(claude_raw)
# #         if not claude_json or not isinstance(claude_json, dict):
# #             claude_json = {
# #                 "answer": claude_raw,
# #                 "reasoning": ["Analysis provided"],
# #                 "recommended_action": "Review the detailed analysis",
# #                 "confidence": 0.7
# #             }
# #     except Exception as e:
# #         print(f"[{request_id}] Warning: Failed to parse Claude JSON: {e}")
# #         claude_json = {
# #             "answer": claude_raw,
# #             "reasoning": [],
# #             "recommended_action": None,
# #             "confidence": 0.5
# #         }

# #     # 6) Transform MCP data into dashboard format using Claude
# #     print(f"[{request_id}] Transforming to dashboard format...")
    
# #     try:
# #         dashboard_data = await process_chat_for_dashboard(
# #             mcp_result=mcp_result,
# #             market=market,
# #             call_claude_func=call_claude
# #         )
# #         print(f"[{request_id}] ✓ Dashboard data generated")
# #         print(f"[{request_id}]   Health: {dashboard_data['healthScore']}/100")
# #         print(f"[{request_id}]   Liquidity: {dashboard_data['liquidityScore']}/10")
# #         print(f"[{request_id}]   News: {len(dashboard_data['news'])} articles")
        
# #     except Exception as e:
# #         print(f"[{request_id}] ✗ CRITICAL: Dashboard transformation failed: {e}")
# #         raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

# #     # 7) Build chat response
# #     chat_response = {
# #         "answer": claude_json.get("answer", "Analysis complete. See dashboard for details."),
# #         "reasoning": claude_json.get("reasoning", []),
# #         "recommended_action": claude_json.get("recommended_action"),
# #         "confidence": claude_json.get("confidence", 0.0),
# #     }

# #     elapsed = time.time() - start_ts
# #     print(f"[{request_id}] ✓ Request completed in {elapsed:.2f}s\n")

# #     # 8) Return final response
# #     return {
# #         "chat": chat_response,
# #         "dashboard": dashboard_data
# #     }


# # @app.get("/dashboard")
# # async def get_dashboard(market_id: str = Query(...)):
# #     """
# #     Get dashboard data for a specific market.
    
# #     Returns dashboard in exact dashboardData.js format.
# #     """
# #     request_id = short_id()
# #     print(f"\n[{request_id}] Dashboard request for: {market_id}")
    
# #     try:
# #         # Fetch market data
# #         market = await fetch_market_detail(market_id)
# #         news = await fetch_news_for_market(market.get("title") or market_id, page_size=5)
        
# #         print(f"[{request_id}] Running MCP analysis...")
        
# #         # Get MCP analysis
# #         mcp_result = await get_manipulation_report(
# #             market_id, 
# #             market.get("orderbook", {}), 
# #             news, 
# #             meta={"market": market}
# #         )
        
# #         print(f"[{request_id}] Transforming to dashboard format...")
        
# #         # Transform to dashboard format
# #         dashboard_data = await process_chat_for_dashboard(
# #             mcp_result=mcp_result,
# #             market=market,
# #             call_claude_func=call_claude
# #         )
        
# #         print(f"[{request_id}] ✓ Dashboard generated\n")
        
# #         return {
# #             "request_id": request_id,
# #             "timestamp": utc_now_iso(),
# #             "dashboard": dashboard_data,
# #             "mcp_status": "ok"
# #         }
        
# #     except Exception as e:
# #         print(f"[{request_id}] ✗ Dashboard generation failed: {e}\n")
# #         raise HTTPException(status_code=500, detail=str(e))


# # @app.get("/health")
# # async def health():
# #     """Health check endpoint"""
# #     from clients import POLY_API_URL, NEWS_API_URL, CLAUDE_API_URL
# #     from mcp import _mcp_manager
    
# #     mcp_poly_running = False
# #     mcp_news_running = False
    
# #     if _mcp_manager.initialized:
# #         mcp_poly_running = _mcp_manager.polymarket_proc is not None and _mcp_manager.polymarket_proc.poll() is None
# #         mcp_news_running = _mcp_manager.news_proc is not None and _mcp_manager.news_proc.poll() is None
    
# #     all_ok = mcp_poly_running and mcp_news_running and bool(CLAUDE_API_URL)
    
# #     return {
# #         "ok": all_ok,
# #         "ts": utc_now_iso(),
# #         "services": {
# #             "polymarket": bool(POLY_API_URL),
# #             "news": bool(NEWS_API_URL),
# #             "claude": bool(CLAUDE_API_URL),
# #             "mcp_polymarket": mcp_poly_running,
# #             "mcp_news": mcp_news_running
# #         }
# #     }


# # @app.get("/")
# # async def root():
# #     """API info"""
# #     return {
# #         "service": "PolySage API",
# #         "version": "2.0.0-production",
# #         "features": [
# #             "Real-time market analysis",
# #             "MCP server integration",
# #             "Claude-powered dashboard generation",
# #             "Structured data transformation"
# #         ],
# #         "endpoints": {
# #             "POST /chat": "Main chat endpoint with dashboard data",
# #             "GET /dashboard?market_id=X": "Get structured dashboard data",
# #             "GET /health": "Health check and service status"
# #         }
# #     }
# # main.py - PRODUCTION VERSION with Two-Type Chat System
# import asyncio, time
# from typing import Dict, Any, Optional
# from fastapi import FastAPI, Query, HTTPException
# from fastapi.middleware.cors import CORSMiddleware

# from utils import utc_now_iso, short_id, extract_first_json_block
# from clients import fetch_market_detail, fetch_news_for_market, call_claude, fetch_markets, fetch_latest_news
# from mcp import get_manipulation_report, call_mcp_with_payload, startup_mcp_servers, shutdown_mcp_servers

# # prompts module supplied by prompt-engineer
# try:
#     from . import prompts as prompts_module
# except Exception:
#     prompts_module = None

# app = FastAPI(title="PolySage API - Production")
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# # Lifecycle events for MCP servers
# @app.on_event("startup")
# async def on_startup():
#     """Start MCP servers when API starts"""
#     print("="*70)
#     print("PolySage API Starting...")
#     print("="*70)
#     try:
#         await startup_mcp_servers()
#         print("✓ MCP servers initialized")
#     except Exception as e:
#         print(f"✗ CRITICAL: MCP servers failed to start: {e}")
#         raise  # Don't continue if MCP servers fail
#     print("="*70)


# @app.on_event("shutdown")
# async def on_shutdown():
#     """Shutdown MCP servers when API stops"""
#     print("\nShutting down MCP servers...")
#     await shutdown_mcp_servers()
#     print("✓ Shutdown complete")


# async def classify_chat_intent(query: str, market_id: Optional[str]) -> Dict[str, Any]:
#     """
#     Classify user intent: general_qa, dashboard_generation, or out_of_scope
#     """
#     classification_system = """You are a query classifier for a Polymarket analysis system.
# Classify the user's query into one of these categories:

# 1. "general_qa" - Questions about Polymarket (how it works, general info, explanations)
# 2. "dashboard_generation" - Requests for analysis/dashboard/insights about a specific market/bet
# 3. "out_of_scope" - Anything not related to Polymarket or prediction markets

# Respond with ONLY a JSON object: {"intent": "general_qa|dashboard_generation|out_of_scope", "reason": "brief explanation"}"""

#     classification_prompt = f"""Query: {query}
# Market ID provided: {"Yes" if market_id else "No"}

# Classify this query."""

#     try:
#         response = await call_claude(
#             classification_system,
#             classification_prompt,
#             temperature=0.1,
#             max_tokens=200
#         )
#         result = extract_first_json_block(response)
#         if result and "intent" in result:
#             return result
#     except Exception as e:
#         print(f"Classification failed: {e}")
    
#     # Fallback: if market_id exists, assume dashboard request
#     if market_id:
#         return {"intent": "dashboard_generation", "reason": "market_id provided"}
#     return {"intent": "general_qa", "reason": "fallback classification"}


# async def handle_general_qa(query: str, request_id: str) -> str:
#     """
#     Handle general questions about Polymarket - returns 3 sentence response
#     """
#     system_prompt = """You are a knowledgeable assistant for Polymarket, a prediction market platform.
# Answer questions concisely and accurately about:
# - How Polymarket works
# - Prediction markets in general
# - Trading mechanics
# - Market types and features

# Provide your answer in EXACTLY 3 sentences. Be clear, informative, and concise."""

#     user_prompt = f"Question: {query}\n\nProvide a clear 3-sentence answer."
    
#     print(f"[{request_id}] Handling general Q&A...")
    
#     try:
#         # Check if we need MCP data for this question
#         needs_data = any(keyword in query.lower() for keyword in 
#                         ['current', 'latest', 'recent', 'trending', 'popular', 'volume'])
        
#         if needs_data:
#             print(f"[{request_id}] Fetching current market data via MCP...")
#             try:
#                 markets = await fetch_markets(limit=5)
#                 context = f"\n\nCurrent trending markets: {[m.get('title', '') for m in markets[:3]]}"
#                 user_prompt += context
#             except Exception as e:
#                 print(f"[{request_id}] Warning: Could not fetch market data: {e}")
        
#         response = await call_claude(
#             system_prompt,
#             user_prompt,
#             temperature=0.3,
#             max_tokens=300
#         )
        
#         return response.strip()
        
#     except Exception as e:
#         print(f"[{request_id}] Error in general Q&A: {e}")
#         return "I apologize, but I'm having trouble processing your question right now. Polymarket is a prediction market platform where users can trade on the outcomes of future events. Please try rephrasing your question or visit polymarket.com for more information."


# async def handle_dashboard_generation(query: str, market_id: str, request_id: str) -> Dict[str, Any]:
#     """
#     Generate dashboard data for a specific market/bet
#     """
#     print(f"[{request_id}] Generating dashboard for market: {market_id}")
    
#     # 1) Fetch market data
#     try:
#         market = await fetch_market_detail(market_id)
#         print(f"[{request_id}] ✓ Market data retrieved: {market.get('title', '')[:50]}...")
#     except Exception as e:
#         print(f"[{request_id}] ✗ Failed to fetch market: {e}")
#         raise HTTPException(status_code=404, detail=f"Market not found: {market_id}")
    
#     # 2) Fetch related news
#     try:
#         news = await fetch_news_for_market(market.get("title", ""), page_size=10)
#         print(f"[{request_id}] ✓ Found {len(news)} news articles")
#     except Exception as e:
#         print(f"[{request_id}] Warning: News fetch failed: {e}")
#         news = []
    
#     # 3) Build MCP payload for analysis
#     mcp_payload = {
#         "market_id": market.get("id"),
#         "market": {
#             "id": market.get("id"),
#             "title": market.get("title"),
#             "currentPrice": market.get("currentPrice") or market.get("lastPrice"),
#             "volume24hr": market.get("volume24hr")
#         },
#         "recent_trades": market.get("recentTrades", []),
#         "orderbook": market.get("orderbook", {}),
#         "news": news,
#         "meta": {"request_id": request_id, "user_query": query}
#     }
    
#     # 4) Get MCP analysis
#     print(f"[{request_id}] Running MCP analysis...")
#     try:
#         mcp_result = await call_mcp_with_payload(mcp_payload)
#         print(f"[{request_id}] ✓ MCP analysis complete - Risk: {mcp_result.get('riskScore', 'N/A')}/100")
#     except Exception as e:
#         print(f"[{request_id}] ✗ MCP analysis failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
#     # 5) Transform to dashboard format using structured prompt
#     system_prompt = """You are a data transformation specialist for prediction market analysis.

# Your task: Convert MCP analysis results into a structured dashboard JSON format.

# CRITICAL RULES:
# 1. Output ONLY valid JSON - no explanations, no markdown, no additional text
# 2. All numeric fields must be numbers (not strings)
# 3. All array fields must be arrays (not null)
# 4. Follow the exact schema provided
# 5. Base your analysis on the MCP data provided

# You will receive:
# - MCP analysis results (risk scores, manipulation signals, trends)
# - Market data (prices, volume, trades)
# - News articles

# Generate a comprehensive dashboard dict."""

#     user_prompt = f"""Based on this MCP analysis and market data, generate the dashboard JSON:

# MARKET: {market.get('title', '')}
# CURRENT PRICE: {market.get('currentPrice', 0)}
# VOLUME 24H: {market.get('volume24hr', 0)}

# MCP ANALYSIS:
# {mcp_result}

# NEWS COUNT: {len(news)}

# Generate a JSON object with these fields:
# {{
#   "healthScore": <0-100 integer based on manipulation risk, liquidity, volume>,
#   "liquidityScore": <0-10 float based on volume and orderbook depth>,
#   "volatilityIndex": <0-100 integer based on price movements>,
#   "sentimentScore": <-1 to 1 float based on news sentiment>,
#   "riskFactors": [<array of string risk factors identified>],
#   "opportunities": [<array of string opportunities>],
#   "keyMetrics": {{
#     "volume24h": <number>,
#     "priceChange24h": <number percentage>,
#     "uniqueTraders": <number>,
#     "avgTradeSize": <number>
#   }},
#   "news": [<array of news objects with title, summary, sentiment, relevance>],
#   "priceHistory": [<array of price points for last 7 days>],
#   "recommendation": "<BUY|SELL|HOLD>",
#   "confidence": <0-1 float>
# }}

# Output ONLY the JSON object, nothing else."""

#     print(f"[{request_id}] Transforming to dashboard format...")
#     try:
#         dashboard_response = await call_claude(
#             system_prompt,
#             user_prompt,
#             temperature=0.2,
#             max_tokens=2500
#         )
        
#         # Extract JSON from response
#         dashboard_data = extract_first_json_block(dashboard_response)
        
#         if not dashboard_data or not isinstance(dashboard_data, dict):
#             raise ValueError("Failed to generate valid dashboard JSON")
        
#         print(f"[{request_id}] ✓ Dashboard generated successfully")
#         print(f"[{request_id}]   Health: {dashboard_data.get('healthScore', 'N/A')}/100")
#         print(f"[{request_id}]   Recommendation: {dashboard_data.get('recommendation', 'N/A')}")
        
#         return dashboard_data
        
#     except Exception as e:
#         print(f"[{request_id}] ✗ Dashboard transformation failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")


# @app.post("/chat")
# async def post_chat(payload: Dict[str, Any]):
#     """
#     Main chat endpoint - handles two types of requests:
#     1. General Q&A about Polymarket (returns 3-sentence chat response)
#     2. Dashboard generation for specific market (returns dashboard JSON)
    
#     Request body:
#         {
#             "query": "user question",
#             "market_id": "optional market ID for dashboard generation"
#         }
    
#     Response formats:
#         General Q&A: {"type": "chat", "response": "3 sentence answer"}
#         Dashboard: {"type": "dashboard", "data": {...dashboard object...}}
#         Out of scope: {"type": "error", "message": "..."}
#     """
#     request_id = short_id()
#     start_ts = time.time()
    
#     # Validate input
#     query = payload.get("query") or payload.get("text")
#     if not query:
#         raise HTTPException(status_code=400, detail="Missing 'query' field")
    
#     market_id = payload.get("market_id")
    
#     print(f"\n[{request_id}] New chat request: {query[:60]}...")
#     if market_id:
#         print(f"[{request_id}] Market ID: {market_id}")
    
#     # Step 1: Classify intent
#     classification = await classify_chat_intent(query, market_id)
#     intent = classification.get("intent", "general_qa")
    
#     print(f"[{request_id}] Intent classified as: {intent}")
#     print(f"[{request_id}] Reason: {classification.get('reason', 'N/A')}")
    
#     # Step 2: Route to appropriate handler
#     try:
#         if intent == "out_of_scope":
#             elapsed = time.time() - start_ts
#             print(f"[{request_id}] ✓ Out of scope query handled in {elapsed:.2f}s\n")
            
#             return {
#                 "type": "error",
#                 "message": "I'm designed to help with Polymarket-related questions and market analysis. Your query appears to be outside my scope. Please ask about prediction markets, how Polymarket works, or request analysis for a specific market."
#             }
        
#         elif intent == "general_qa":
#             response = await handle_general_qa(query, request_id)
            
#             elapsed = time.time() - start_ts
#             print(f"[{request_id}] ✓ General Q&A completed in {elapsed:.2f}s\n")
            
#             return {
#                 "type": "chat",
#                 "response": response
#             }
        
#         elif intent == "dashboard_generation":
#             if not market_id:
#                 return {
#                     "type": "error",
#                     "message": "To generate a dashboard, please provide a market_id. You can find market IDs on polymarket.com or ask me to search for specific markets."
#                 }
            
#             dashboard_data = await handle_dashboard_generation(query, market_id, request_id)
            
#             elapsed = time.time() - start_ts
#             print(f"[{request_id}] ✓ Dashboard generation completed in {elapsed:.2f}s\n")
            
#             return {
#                 "type": "dashboard",
#                 "data": dashboard_data
#             }
        
#         else:
#             raise HTTPException(status_code=500, detail="Unknown intent classification")
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"[{request_id}] ✗ Request failed: {e}\n")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/dashboard")
# async def get_dashboard(market_id: str = Query(...)):
#     """
#     Get dashboard data for a specific market.
    
#     Returns dashboard in structured JSON format.
#     """
#     request_id = short_id()
#     print(f"\n[{request_id}] Dashboard request for: {market_id}")
    
#     try:
#         dashboard_data = await handle_dashboard_generation(
#             query=f"Generate dashboard for market {market_id}",
#             market_id=market_id,
#             request_id=request_id
#         )
        
#         return {
#             "request_id": request_id,
#             "timestamp": utc_now_iso(),
#             "dashboard": dashboard_data,
#             "status": "ok"
#         }
        
#     except Exception as e:
#         print(f"[{request_id}] ✗ Dashboard generation failed: {e}\n")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/health")
# async def health():
#     """Health check endpoint"""
#     from clients import POLY_API_URL, NEWS_API_URL, CLAUDE_API_URL
#     from mcp import _mcp_manager
    
#     mcp_poly_running = False
#     mcp_news_running = False
    
#     if _mcp_manager.initialized:
#         mcp_poly_running = _mcp_manager.polymarket_proc is not None and _mcp_manager.polymarket_proc.poll() is None
#         mcp_news_running = _mcp_manager.news_proc is not None and _mcp_manager.news_proc.poll() is None
    
#     all_ok = mcp_poly_running and mcp_news_running and bool(CLAUDE_API_URL)
    
#     return {
#         "ok": all_ok,
#         "ts": utc_now_iso(),
#         "services": {
#             "polymarket": bool(POLY_API_URL),
#             "news": bool(NEWS_API_URL),
#             "claude": bool(CLAUDE_API_URL),
#             "mcp_polymarket": mcp_poly_running,
#             "mcp_news": mcp_news_running
#         }
#     }


# @app.get("/")
# async def root():
#     """API info"""
#     return {
#         "service": "PolySage API",
#         "version": "3.0.0-production",
#         "features": [
#             "Two-type chat system (General Q&A / Dashboard Generation)",
#             "Intent classification",
#             "MCP server integration",
#             "Claude-powered structured analysis",
#             "3-sentence concise responses for general queries"
#         ],
#         "chat_types": {
#             "general_qa": "Ask questions about Polymarket - get 3-sentence answers",
#             "dashboard_generation": "Request market analysis - get full dashboard JSON",
#             "out_of_scope": "Non-Polymarket queries are politely declined"
#         },
#         "endpoints": {
#             "POST /chat": "Main chat endpoint (supports both types)",
#             "GET /dashboard?market_id=X": "Direct dashboard data retrieval",
#             "GET /health": "Health check and service status"
#         },
#         "request_format": {
#             "query": "Your question or request (required)",
#             "market_id": "Market ID for dashboard generation (optional)"
#         }
#     }
# main.py - PRODUCTION with Exact Dashboard Format
import asyncio, time, json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from utils import utc_now_iso, short_id, extract_first_json_block
from clients import fetch_market_detail, fetch_news_for_market, call_claude, fetch_markets
from mcp import call_mcp_with_payload, startup_mcp_servers, shutdown_mcp_servers

app = FastAPI(title="PolySage API - Production")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def on_startup():
    """Start MCP servers when API starts"""
    print("="*70)
    print("PolySage API Starting...")
    print("="*70)
    
    import os
    claude_key = os.getenv("CLAUDE_API_KEY")
    if not claude_key:
        print("✗ CRITICAL: CLAUDE_API_KEY environment variable not set!")
        raise RuntimeError("Missing required API key: CLAUDE_API_KEY")
    
    print(f"✓ Claude API key configured: {claude_key[:20]}...")
    
    try:
        await startup_mcp_servers()
        print("✓ MCP servers initialized")
    except Exception as e:
        print(f"✗ WARNING: MCP servers failed to start: {e}")
    print("="*70)


@app.on_event("shutdown")
async def on_shutdown():
    """Shutdown MCP servers when API stops"""
    print("\nShutting down MCP servers...")
    await shutdown_mcp_servers()
    print("✓ Shutdown complete")


async def classify_chat_intent(query: str, market_id: Optional[str]) -> Dict[str, Any]:
    """Classify user intent with fallback heuristics"""
    
    # Try Claude classification first
    classification_system = """You are a query classifier for a Polymarket analysis system.
Classify into: general_qa, dashboard_generation, or out_of_scope
Respond with JSON: {"intent": "...", "reason": "..."}"""

    classification_prompt = f"""Query: {query}
Market ID provided: {"Yes" if market_id else "No"}
Classify this query."""

    try:
        response = await call_claude(
            classification_system,
            classification_prompt,
            temperature=0.1,
            max_tokens=200
        )
        result = extract_first_json_block(response)
        if result and "intent" in result:
            return result
    except Exception as e:
        print(f"⚠️  Classification failed: {e}, using fallback...")
    
    # Fallback heuristics
    query_lower = query.lower()
    
    out_of_scope_keywords = ['weather', 'recipe', 'cook', 'movie', 'music']
    if any(k in query_lower for k in out_of_scope_keywords):
        if 'polymarket' not in query_lower:
            return {"intent": "out_of_scope", "reason": "unrelated topic"}
    
    dashboard_keywords = ['analyze', 'dashboard', 'should i', 'risk', 'insight']
    if market_id or any(k in query_lower for k in dashboard_keywords):
        return {"intent": "dashboard_generation", "reason": "analysis request"}
    
    return {"intent": "general_qa", "reason": "general question"}


async def handle_general_qa(query: str, request_id: str) -> str:
    """Handle general Q&A - returns 3 sentences"""
    
    system_prompt = """You are a Polymarket expert assistant.
Answer in EXACTLY 3 sentences. Be clear and informative."""

    user_prompt = f"Question: {query}\n\nProvide a clear 3-sentence answer."
    
    print(f"[{request_id}] Handling general Q&A...")
    
    try:
        needs_data = any(k in query.lower() for k in ['current', 'latest', 'trending'])
        
        if needs_data:
            try:
                markets = await fetch_markets(limit=3)
                titles = [m.get('title', '')[:40] for m in markets[:3]]
                user_prompt += f"\n\nTrending: {titles}"
            except:
                pass
        
        response = await call_claude(system_prompt, user_prompt, temperature=0.3, max_tokens=300)
        return response.strip()
        
    except Exception as e:
        print(f"[{request_id}] ✗ Error: {e}")
        return "I apologize, but I'm having trouble processing your question. Polymarket is a prediction market platform where users trade on event outcomes. Please try rephrasing your question."


async def handle_dashboard_generation(query: str, market_id: str, request_id: str) -> Dict[str, Any]:
    """Generate dashboard in EXACT required format"""
    
    print(f"[{request_id}] Generating dashboard for: {market_id}")
    
    # Fetch market data
    try:
        market = await fetch_market_detail(market_id)
        print(f"[{request_id}] ✓ Market: {market.get('title', '')[:50]}...")
    except Exception as e:
        print(f"[{request_id}] ✗ Market fetch failed: {e}")
        raise HTTPException(status_code=404, detail=f"Market not found: {market_id}")
    
    # Fetch news
    try:
        news = await fetch_news_for_market(market.get("title", ""), page_size=10)
        print(f"[{request_id}] ✓ Found {len(news)} news articles")
    except:
        news = []
    
    # MCP analysis
    mcp_payload = {
        "market_id": market.get("id"),
        "market": {
            "id": market.get("id"),
            "title": market.get("title"),
            "currentPrice": market.get("currentPrice", 0.5),
            "volume24hr": market.get("volume24hr", 0)
        },
        "recent_trades": market.get("recentTrades", []),
        "orderbook": market.get("orderbook", {}),
        "news": news,
        "meta": {"request_id": request_id}
    }
    
    print(f"[{request_id}] Running MCP analysis...")
    try:
        mcp_result = await call_mcp_with_payload(mcp_payload)
        print(f"[{request_id}] ✓ MCP complete")
    except:
        mcp_result = {"riskScore": 50}
    
    # Generate dashboard with Claude
    system_prompt = """You are a prediction market dashboard generator.

Generate a COMPLETE dashboard JSON object with realistic, coherent data.

CRITICAL:
1. Output ONLY valid JSON
2. Follow the EXACT schema
3. Generate realistic time-series data
4. Make data internally consistent
5. No explanations, just JSON"""

    # Format news for Claude
    news_info = []
    for article in news[:5]:
        news_info.append({
            "title": article.get("title", ""),
            "source": article.get("source", {}).get("name", "Unknown"),
            "publishedAt": article.get("publishedAt", "")
        })

    user_prompt = f"""Generate dashboard JSON for:

MARKET: {market.get('title', '')}
PRICE: {market.get('currentPrice', 0.5)}
VOLUME_24H: ${market.get('volume24hr', 0):,.0f}
RISK: {mcp_result.get('riskScore', 50)}/100

NEWS: {json.dumps(news_info, indent=2)}

Generate JSON with this EXACT structure:
{{
  "question": "{market.get('title', '')}",
  "healthScore": <0-100 int, inverse of risk>,
  "liquidityScore": <0-10 float based on volume>,
  
  "volumeData": {{
    "24h": [
      {{"time": "00:00", "volume": <num>}}, {{"time": "04:00", "volume": <num>}},
      {{"time": "08:00", "volume": <num>}}, {{"time": "12:00", "volume": <num>}},
      {{"time": "16:00", "volume": <num>}}, {{"time": "20:00", "volume": <num>}}
    ],
    "7d": [
      {{"time": "Mon", "volume": <num>}}, {{"time": "Tue", "volume": <num>}},
      {{"time": "Wed", "volume": <num>}}, {{"time": "Thu", "volume": <num>}},
      {{"time": "Fri", "volume": <num>}}, {{"time": "Sat", "volume": <num>}},
      {{"time": "Sun", "volume": <num>}}
    ],
    "1m": [
      {{"time": "Week 1", "volume": <num>}}, {{"time": "Week 2", "volume": <num>}},
      {{"time": "Week 3", "volume": <num>}}, {{"time": "Week 4", "volume": <num>}}
    ]
  }},
  
  "betOptions": ["yes", "no", "maybe"],
  
  "oddsComparison": {{
    "yes": {{"polymarket": <num>, "news": <num>, "expert": <num>}},
    "no": {{"polymarket": <num>, "news": <num>, "expert": <num>}},
    "maybe": {{"polymarket": <num>, "news": <num>, "expert": <num>}}
  }},
  
  "shiftTimeline": [
    {{"date": "Nov 1", "polymarket": <num>, "news": <num>}},
    {{"date": "Nov 2", "polymarket": <num>, "news": <num>}},
    {{"date": "Nov 3", "polymarket": <num>, "news": <num>}},
    {{"date": "Nov 4", "polymarket": <num>, "news": <num>}},
    {{"date": "Nov 5", "polymarket": <num>, "news": <num>}},
    {{"date": "Nov 6", "polymarket": <num>, "news": <num>}}
  ],
  
  "news": [
    {{"title": "<actual news title>", "url": "#", "source": "<source>", "date": "<time ago>"}},
    {{"title": "<actual news title>", "url": "#", "source": "<source>", "date": "<time ago>"}},
    {{"title": "<actual news title>", "url": "#", "source": "<source>", "date": "<time ago>"}}
  ],
  
  "largeBets": [
    {{"option": "Yes", "amount": "$<num>", "time": "<ago>", "impact": "+<num>%", "icon": "TrendingUp"}},
    {{"option": "No", "amount": "$<num>", "time": "<ago>", "impact": "-<num>%", "icon": "TrendingDown"}},
    {{"option": "Yes", "amount": "$<num>", "time": "<ago>", "impact": "+<num>%", "icon": "TrendingUp"}}
  ],
  
  "sentimentTimeline": [
    {{"date": "Nov 1", "sentiment": <num>, "events": "<event description>"}},
    {{"date": "Nov 3", "sentiment": <num>, "events": "<event description>"}},
    {{"date": "Nov 5", "sentiment": <num>, "events": "<event description>"}},
    {{"date": "Nov 7", "sentiment": <num>, "events": "<event description>"}}
  ],
  
  "aiSummary": [
    {{"title": "Market Confidence:", "content": "<2-3 sentences>"}},
    {{"title": "Trend Analysis:", "content": "<2-3 sentences>"}},
    {{"title": "Risk Assessment:", "content": "<2-3 sentences>"}},
    {{"title": "Strategic Recommendation:", "content": "<2-3 sentences>"}}
  ]
}}

Use actual news titles. Make volume/odds/sentiment realistic and coherent.
Output ONLY JSON."""

    print(f"[{request_id}] Generating dashboard JSON...")
    try:
        response = await call_claude(system_prompt, user_prompt, temperature=0.3, max_tokens=3500)
        dashboard = extract_first_json_block(response)
        
        if not dashboard or not isinstance(dashboard, dict):
            raise ValueError("Invalid JSON response")
        
        # Validate required fields
        required = ["question", "healthScore", "liquidityScore", "volumeData", 
                   "betOptions", "oddsComparison", "shiftTimeline", "news",
                   "largeBets", "sentimentTimeline", "aiSummary"]
        missing = [f for f in required if f not in dashboard]
        if missing:
            raise ValueError(f"Missing fields: {missing}")
        
        print(f"[{request_id}] ✓ Dashboard complete")
        print(f"[{request_id}]   Health: {dashboard['healthScore']}/100")
        print(f"[{request_id}]   Liquidity: {dashboard['liquidityScore']}/10")
        
        return dashboard
        
    except Exception as e:
        print(f"[{request_id}] ✗ Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")


@app.post("/chat")
async def post_chat(payload: Dict[str, Any]):
    """
    Main chat endpoint
    
    Request: {"query": "...", "market_id": "..."}
    
    Response types:
    - {"type": "chat", "response": "3 sentences"}
    - {"type": "dashboard", "data": {...complete dashboard...}}
    - {"type": "error", "message": "..."}
    """
    request_id = short_id()
    start_ts = time.time()
    
    query = payload.get("query") or payload.get("text")
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query' field")
    
    market_id = payload.get("market_id")
    
    print(f"\n[{request_id}] Chat: {query[:60]}...")
    if market_id:
        print(f"[{request_id}] Market: {market_id}")
    
    # Classify intent
    classification = await classify_chat_intent(query, market_id)
    intent = classification.get("intent", "general_qa")
    
    print(f"[{request_id}] Intent: {intent}")
    
    try:
        if intent == "out_of_scope":
            return {
                "type": "error",
                "message": "I'm designed to help with Polymarket-related questions and market analysis. Please ask about prediction markets or request market analysis."
            }
        
        elif intent == "general_qa":
            response = await handle_general_qa(query, request_id)
            elapsed = time.time() - start_ts
            print(f"[{request_id}] ✓ Completed in {elapsed:.2f}s\n")
            
            return {
                "type": "chat",
                "response": response
            }
        
        elif intent == "dashboard_generation":
            if not market_id:
                return {
                    "type": "error",
                    "message": "To generate a dashboard, please provide a market_id."
                }
            
            dashboard = await handle_dashboard_generation(query, market_id, request_id)
            elapsed = time.time() - start_ts
            print(f"[{request_id}] ✓ Completed in {elapsed:.2f}s\n")
            
            return {
                "type": "dashboard",
                "data": dashboard
            }
        
        else:
            raise HTTPException(status_code=500, detail="Unknown intent")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{request_id}] ✗ Failed: {e}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def get_dashboard(market_id: str = Query(...)):
    """Direct dashboard endpoint"""
    request_id = short_id()
    print(f"\n[{request_id}] Dashboard request: {market_id}")
    
    try:
        dashboard = await handle_dashboard_generation(
            query=f"Generate dashboard for {market_id}",
            market_id=market_id,
            request_id=request_id
        )
        
        return {
            "request_id": request_id,
            "timestamp": utc_now_iso(),
            "dashboard": dashboard,
            "status": "ok"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check"""
    import os
    from mcp import _mcp_manager
    
    return {
        "ok": True,
        "ts": utc_now_iso(),
        "services": {
            "claude_api_key": bool(os.getenv("CLAUDE_API_KEY")),
            "mcp_initialized": _mcp_manager.initialized
        }
    }


@app.get("/")
async def root():
    """API info"""
    return {
        "service": "PolySage API",
        "version": "3.0-production",
        "features": [
            "Two-type chat (Q&A / Dashboard)",
            "Exact dashboard format for frontend",
            "Claude Sonnet 4.5 powered",
            "MCP integration"
        ],
        "endpoints": {
            "POST /chat": "Main endpoint - returns chat or dashboard",
            "GET /dashboard?market_id=X": "Direct dashboard",
            "GET /health": "Health check"
        }
    }