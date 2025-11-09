"""
Dashboard Processor - PRODUCTION VERSION (No Fallbacks)

Transforms MCP tool outputs into exact dashboard format using Claude.
Raises errors if data is missing - no fallbacks.
"""

import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


# Claude prompt for dashboard transformation
DASHBOARD_TRANSFORM_PROMPT = """You are a financial data analyst. Transform market analysis data into structured dashboard format.

You will receive REAL market analysis from multiple data sources. Parse and structure it EXACTLY as specified.

OUTPUT FORMAT (JSON only, no other text):
{
  "question": "string - the market question",
  "healthScore": number (0-100, where 100 is healthiest),
  "liquidityScore": number (0-10 with one decimal, based on total liquidity),
  "volumeData": {
    "24h": [{"time": "HH:00", "volume": number}, ... 6 data points],
    "7d": [{"time": "DayName", "volume": number}, ... 7 days],
    "1m": [{"time": "Week N", "volume": number}, ... 4 weeks]
  },
  "betOptions": ["yes", "no"] or ["yes", "no", "maybe"],
  "oddsComparison": {
    "yes": {"polymarket": number %, "news": number %, "expert": number %},
    "no": {"polymarket": number %, "news": number %, "expert": number %}
  },
  "shiftTimeline": [
    {"date": "Mon DD", "polymarket": number %, "news": number %}, ... 6 points
  ],
  "news": [
    {"title": "string", "url": "string", "source": "string", "date": "string"}, ... 3-5 articles
  ],
  "largeBets": [
    {"option": "Yes/No", "amount": "$XXX,XXX", "time": "X hours ago", "impact": "+/-X.X%", "icon": "TrendingUp/Down"}, ... 3-5 bets
  ],
  "sentimentTimeline": [
    {"date": "Mon DD", "sentiment": number (0-100), "events": "string"}, ... 4 points
  ],
  "aiSummary": [
    {"title": "Market Confidence:", "content": "detailed analysis"},
    {"title": "Trend Analysis:", "content": "detailed analysis"},
    {"title": "Risk Assessment:", "content": "detailed analysis"},
    {"title": "Strategic Recommendation:", "content": "detailed recommendation"}
  ]
}

CRITICAL INSTRUCTIONS:
1. healthScore: Use the Overall Score from health data (0-100). If it's inverted (lower=better), invert it.
2. liquidityScore: Total Liquidity / $100,000, capped at 10.0
3. volumeData: Extract actual volume data. For 24h, sample every 4 hours. For 7d, daily. For 1m, weekly.
4. oddsComparison: 
   - polymarket = current market price (%)
   - news = sentiment score converted to % (positive sentiment = higher %)
   - expert = average of polymarket and news
5. shiftTimeline: Create 6-day progression showing how odds changed
6. news: Extract REAL news articles with proper metadata
7. largeBets: Use suspicious trader pairs from wash trading analysis as "large bets"
8. sentimentTimeline: Show 4 key dates with sentiment progression
9. aiSummary: Generate 4 comprehensive sections analyzing all data

IMPORTANT: 
- Use ONLY real data from the analysis provided
- DO NOT make up data
- Calculate values from actual metrics
- Be precise with numbers
- Return ONLY valid JSON, no markdown, no explanation"""


async def transform_mcp_to_dashboard(
    mcp_result: Dict[str, Any],
    market_title: str,
    call_claude_function
) -> Dict[str, Any]:
    """
    Transform MCP analysis into dashboard format using Claude.
    
    NO FALLBACKS - Raises exceptions if data is insufficient.
    
    Args:
        mcp_result: Complete MCP manipulation report with all tool outputs
        market_title: The market question/title
        call_claude_function: Async function to call Claude API
        
    Returns:
        Dashboard data in exact frontend format
        
    Raises:
        ValueError: If MCP data is missing or invalid
        json.JSONDecodeError: If Claude doesn't return valid JSON
    """
    
    # Validate MCP result
    if not mcp_result or not isinstance(mcp_result, dict):
        raise ValueError("Invalid MCP result - must be a dictionary")
    
    details = mcp_result.get("details")
    if not details:
        raise ValueError("MCP result missing 'details' key")
    
    # Extract all tool outputs
    market_data = details.get("market_data", {}).get("raw", "")
    volume_analysis = details.get("volume_analysis", {}).get("raw", "")
    wash_trading = details.get("wash_trading", {}).get("raw", "")
    health_score = details.get("health_score", {}).get("raw", "")
    trader_concentration = details.get("trader_concentration", {}).get("raw", "")
    news_articles = details.get("news", {}).get("raw", "")
    sentiment = details.get("sentiment", {}).get("raw", "")
    news_correlation = details.get("news_correlation", {}).get("raw", "")
    volume_comparison = details.get("volume_comparison", {}).get("raw", "")
    
    # Validate we have essential data
    if not health_score:
        raise ValueError("Missing health score data from MCP")
    if not market_data:
        raise ValueError("Missing market data from MCP")
    
    logger.info(f"Transforming MCP data for market: {market_title}")
    
    # Build the comprehensive prompt
    analysis_prompt = f"""{DASHBOARD_TRANSFORM_PROMPT}

=== MARKET DATA ===
{market_data}

=== VOLUME ANALYSIS ===
{volume_analysis}

=== WASH TRADING ANALYSIS ===
{wash_trading}

=== HEALTH SCORE ===
{health_score}

=== TRADER CONCENTRATION ===
{trader_concentration}

=== NEWS ARTICLES ===
{news_articles}

=== SENTIMENT ANALYSIS ===
{sentiment}

=== NEWS-PRICE CORRELATION ===
{news_correlation}

=== VOLUME COMPARISON ===
{volume_comparison}

Market Question: {market_title}

Transform this REAL data into the dashboard JSON format. Return ONLY the JSON object."""

    # Call Claude
    system_prompt = "You are a data transformation expert specializing in financial markets. Convert market analysis into structured JSON format. Return ONLY valid JSON with no other text or formatting."
    
    logger.info("Calling Claude for dashboard transformation...")
    
    claude_response = await call_claude_function(
        system_prompt=system_prompt,
        user_prompt=analysis_prompt,
        model="claude-sonnet-4-20250514",
        temperature=0.1,  # Low temperature for consistent structured output
        max_tokens=4000
    )
    
    # Parse Claude's response - STRICT parsing, no fallbacks
    logger.info("Parsing Claude response...")
    
    # Try to extract JSON if Claude wrapped it in markdown
    response_text = claude_response.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith("```json"):
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif response_text.startswith("```"):
        response_text = response_text.split("```")[1].split("```")[0].strip()
    
    # Remove any leading/trailing whitespace
    response_text = response_text.strip()
    
    # Parse JSON - this will raise JSONDecodeError if invalid
    dashboard_data = json.loads(response_text)
    
    # Validate structure - STRICT validation
    required_keys = [
        "question", "healthScore", "liquidityScore", "volumeData",
        "betOptions", "oddsComparison", "shiftTimeline", "news",
        "largeBets", "sentimentTimeline", "aiSummary"
    ]
    
    missing_keys = [key for key in required_keys if key not in dashboard_data]
    if missing_keys:
        raise ValueError(f"Claude output missing required keys: {missing_keys}")
    
    # Validate data types
    if not isinstance(dashboard_data["healthScore"], (int, float)):
        raise ValueError("healthScore must be a number")
    if not isinstance(dashboard_data["liquidityScore"], (int, float)):
        raise ValueError("liquidityScore must be a number")
    if not isinstance(dashboard_data["volumeData"], dict):
        raise ValueError("volumeData must be an object")
    if not isinstance(dashboard_data["news"], list):
        raise ValueError("news must be an array")
    if not isinstance(dashboard_data["aiSummary"], list):
        raise ValueError("aiSummary must be an array")
    
    # Validate ranges
    if not 0 <= dashboard_data["healthScore"] <= 100:
        raise ValueError(f"healthScore must be 0-100, got {dashboard_data['healthScore']}")
    if not 0 <= dashboard_data["liquidityScore"] <= 10:
        raise ValueError(f"liquidityScore must be 0-10, got {dashboard_data['liquidityScore']}")
    
    logger.info(f"✓ Dashboard data validated successfully")
    logger.info(f"  Health Score: {dashboard_data['healthScore']}/100")
    logger.info(f"  Liquidity Score: {dashboard_data['liquidityScore']}/10")
    logger.info(f"  News Articles: {len(dashboard_data['news'])}")
    logger.info(f"  Large Bets: {len(dashboard_data['largeBets'])}")
    
    return dashboard_data


async def process_chat_for_dashboard(
    mcp_result: Dict[str, Any],
    market: Dict[str, Any],
    call_claude_func
) -> Dict[str, Any]:
    """
    Main entry point for dashboard processing.
    
    Use this in your API endpoints:
    
    dashboard_data = await process_chat_for_dashboard(
        mcp_result=mcp_result,
        market=market,
        call_claude_func=call_claude
    )
    
    Args:
        mcp_result: Complete MCP manipulation report
        market: Market information dict with 'title' key
        call_claude_func: Async function to call Claude API
        
    Returns:
        Dashboard data in exact frontend format
        
    Raises:
        ValueError: If data is missing or invalid
        Exception: If Claude call fails or returns invalid data
    """
    
    market_title = market.get("title")
    if not market_title:
        raise ValueError("Market must have a 'title' key")
    
    dashboard_data = await transform_mcp_to_dashboard(
        mcp_result=mcp_result,
        market_title=market_title,
        call_claude_function=call_claude_func
    )
    
    return dashboard_data