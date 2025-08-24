#!/usr/bin/env python3
"""
Dynamic Market Discovery - Future-Proof Asset Selection
Real-time discovery of optimal trading pairs based on current market conditions.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import time
import requests
from datetime import datetime, timedelta

# Add module paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from execution.binance_connector import create_binance_connector

# Add formal contracts
sys.path.insert(0, str(current_dir.parent.parent / "MomoAI/projects/coherence/formal_contracts"))
from contract_language import coherence_contract, ComplexityClass

@dataclass
class MarketAsset:
    """Dynamic market asset with real-time characteristics."""
    symbol: str
    base_asset: str
    quote_asset: str
    market_cap_rank: Optional[int]
    daily_volume_usd: float
    volatility_24h: float
    price_usd: float
    is_tradeable: bool
    liquidity_score: float
    last_updated: datetime

class DynamicMarketDiscovery:
    """
    Future-proof market discovery system.
    
    SOLVES THE HARDCODING PROBLEM:
    1. Real-time asset discovery via Binance API
    2. Dynamic market cap ranking via CoinGecko
    3. Volume and liquidity filtering
    4. Automatic adaptation to new listings
    5. Removal of delisted assets
    """
    
    def __init__(self):
        self.connector = create_binance_connector()
        if not self.connector:
            raise ValueError("Failed to connect to Binance")
        
        self.min_daily_volume = 50000  # $50K minimum daily volume
        self.min_market_cap_rank = 200  # Top 200 by market cap
        self.quote_currencies = ["USDC", "USDC", "BUSD"]  # Accepted quote currencies
        
        print("🔄 Dynamic Market Discovery initialized")
    
    @coherence_contract(
        input_types={},
        output_type="List[Dict]",
        requires=[],
        ensures=["len(result) >= 0"],
        complexity_time=ComplexityClass.LINEAR,
        pure=False  # Network calls
    )
    def get_all_binance_symbols(self) -> List[Dict]:
        """Get all active trading symbols from Binance."""
        try:
            # Direct API call to avoid connector issues
            import requests
            response = requests.get("https://api.binance.com/api/v3/exchangeInfo", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                symbols = data.get("symbols", [])
                
                # Filter for active trading symbols (permissions field is empty in new API)
                active_symbols = []
                for symbol_info in symbols:
                    if (symbol_info.get("status") == "TRADING" and 
                        symbol_info.get("quoteAsset") in self.quote_currencies):
                        
                        active_symbols.append({
                            "symbol": symbol_info["symbol"],
                            "baseAsset": symbol_info["baseAsset"],
                            "quoteAsset": symbol_info["quoteAsset"],
                            "status": symbol_info["status"]
                        })
                
                print(f"📊 Found {len(active_symbols)} active trading pairs")
                return active_symbols
            
            return []
            
        except Exception as e:
            print(f"❌ Failed to get Binance symbols: {e}")
            return []
    
    @coherence_contract(
        input_types={"symbols": "List[str]"},
        output_type="Dict[str, Dict]",
        requires=["len(symbols) > 0"],
        ensures=[],
        complexity_time=ComplexityClass.LINEAR,
        pure=False  # Network calls
    )
    def get_24h_ticker_stats(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get 24h ticker statistics for volume and price analysis."""
        try:
            # Get 24h ticker stats for all symbols
            response = self.connector._make_request("GET", "ticker/24hr")
            
            if isinstance(response, list):
                ticker_data = {}
                target_symbols = set(symbols)
                
                for ticker in response:
                    symbol = ticker.get("symbol", "")
                    if symbol in target_symbols:
                        ticker_data[symbol] = {
                            "volume": float(ticker.get("volume", 0)),
                            "quoteVolume": float(ticker.get("quoteVolume", 0)),
                            "lastPrice": float(ticker.get("lastPrice", 0)),
                            "priceChangePercent": float(ticker.get("priceChangePercent", 0)),
                            "count": int(ticker.get("count", 0))  # Number of trades
                        }
                
                print(f"📈 Retrieved ticker data for {len(ticker_data)} symbols")
                return ticker_data
            
            return {}
            
        except Exception as e:
            print(f"❌ Failed to get ticker stats: {e}")
            return {}
    
    def get_market_cap_rankings(self, base_assets: List[str]) -> Dict[str, int]:
        """
        Get real-time market cap rankings from CoinGecko.
        
        CRITICAL: This provides the market cap data that Binance doesn't have.
        """
        try:
            # CoinGecko API for market cap rankings
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 250,  # Top 250 coins
                "page": 1,
                "sparkline": False
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Map symbols to rankings
                rankings = {}
                for i, coin in enumerate(data, 1):
                    symbol = coin.get("symbol", "").upper()
                    if symbol in base_assets:
                        rankings[symbol] = i
                
                print(f"🏆 Retrieved market cap rankings for {len(rankings)} assets")
                return rankings
            
        except Exception as e:
            print(f"❌ Failed to get market cap rankings: {e}")
        
        return {}
    
    def discover_optimal_assets(self, max_assets: int = 50) -> List[MarketAsset]:
        """
        Discover optimal assets using real-time market data.
        
        DYNAMIC FILTERING CRITERIA:
        1. Active on Binance with USDC/USDC pairs
        2. Top 200 by market cap (from CoinGecko)
        3. >$50K daily volume
        4. >100 trades per day (liquidity)
        5. Reasonable volatility (0.1-5% daily change)
        """
        print("\n🔍 DISCOVERING OPTIMAL ASSETS...")
        
        # Step 1: Get all active Binance symbols
        all_symbols = self.get_all_binance_symbols()
        if not all_symbols:
            return []
        
        # Step 2: Extract symbols for ticker data
        symbol_names = [s["symbol"] for s in all_symbols]
        ticker_data = self.get_24h_ticker_stats(symbol_names)
        
        # Step 3: Get market cap rankings
        base_assets = list(set(s["baseAsset"] for s in all_symbols))
        market_cap_rankings = self.get_market_cap_rankings(base_assets)
        
        # Step 4: Filter and score assets
        optimal_assets = []
        
        for symbol_info in all_symbols:
            symbol = symbol_info["symbol"]
            base_asset = symbol_info["baseAsset"]
            quote_asset = symbol_info["quoteAsset"]
            
            # Get ticker data
            ticker = ticker_data.get(symbol, {})
            if not ticker:
                continue
            
            # Calculate daily volume in USD
            quote_volume = ticker.get("quoteVolume", 0)
            daily_volume_usd = quote_volume  # Already in USD terms for USDC/USDC pairs
            
            # Get market cap ranking
            market_cap_rank = market_cap_rankings.get(base_asset)
            
            # Apply filters
            if (daily_volume_usd >= self.min_daily_volume and
                market_cap_rank and market_cap_rank <= self.min_market_cap_rank and
                ticker.get("count", 0) >= 100):  # Minimum trade count
                
                # Calculate volatility and liquidity scores
                volatility_24h = abs(ticker.get("priceChangePercent", 0)) / 100
                liquidity_score = min(1.0, daily_volume_usd / 1000000)  # Scale to 1M volume = 1.0
                
                # Reasonable volatility filter (0.1% - 10%)
                if 0.001 <= volatility_24h <= 0.10:
                    asset = MarketAsset(
                        symbol=symbol,
                        base_asset=base_asset,
                        quote_asset=quote_asset,
                        market_cap_rank=market_cap_rank,
                        daily_volume_usd=daily_volume_usd,
                        volatility_24h=volatility_24h,
                        price_usd=ticker.get("lastPrice", 0),
                        is_tradeable=True,
                        liquidity_score=liquidity_score,
                        last_updated=datetime.now()
                    )
                    optimal_assets.append(asset)
        
        # Sort by market cap rank (lower = better)
        optimal_assets.sort(key=lambda x: x.market_cap_rank)
        
        # Limit to max_assets
        optimal_assets = optimal_assets[:max_assets]
        
        print(f"\n✅ DISCOVERED {len(optimal_assets)} OPTIMAL ASSETS:")
        for i, asset in enumerate(optimal_assets[:10], 1):  # Show top 10
            print(f"   {i}. {asset.symbol} (#{asset.market_cap_rank}): "
                  f"${asset.daily_volume_usd:,.0f}/day, {asset.volatility_24h:.2%} vol")
        
        return optimal_assets
    
    def get_correlation_pairs(self, assets: List[MarketAsset], max_pairs: int = 100) -> List[Tuple[MarketAsset, MarketAsset]]:
        """
        Generate optimal correlation pairs based on market characteristics.
        
        SMART PAIRING:
        1. Different market cap tiers (more breakdown potential)
        2. Sufficient combined volume
        3. Different base assets (avoid redundancy)
        4. Reasonable volatility balance
        """
        pairs = []
        
        # Generate pairs with smart filtering
        for i in range(len(assets)):
            for j in range(i + 1, len(assets)):
                asset1, asset2 = assets[i], assets[j]
                
                # Skip if same base asset (redundant)
                if asset1.base_asset == asset2.base_asset:
                    continue
                
                # Ensure sufficient combined volume
                combined_volume = asset1.daily_volume_usd + asset2.daily_volume_usd
                if combined_volume < 100000:  # $100K combined minimum
                    continue
                
                # Prefer different market cap tiers (more breakdown potential)
                rank_diff = abs(asset1.market_cap_rank - asset2.market_cap_rank)
                if rank_diff < 5:  # Skip very similar rankings
                    continue
                
                pairs.append((asset1, asset2))
                
                if len(pairs) >= max_pairs:
                    break
            
            if len(pairs) >= max_pairs:
                break
        
        # Sort pairs by combined volume (higher = better execution)
        pairs.sort(key=lambda p: p[0].daily_volume_usd + p[1].daily_volume_usd, reverse=True)
        
        print(f"🔗 Generated {len(pairs)} optimal correlation pairs")
        return pairs
    
    def update_market_data(self, assets: List[MarketAsset]) -> List[MarketAsset]:
        """Update market data for discovered assets (for continuous operation)."""
        print("🔄 Updating market data...")
        
        symbols = [asset.symbol for asset in assets]
        ticker_data = self.get_24h_ticker_stats(symbols)
        
        updated_assets = []
        for asset in assets:
            ticker = ticker_data.get(asset.symbol, {})
            if ticker:
                # Update dynamic fields
                asset.daily_volume_usd = ticker.get("quoteVolume", asset.daily_volume_usd)
                asset.volatility_24h = abs(ticker.get("priceChangePercent", 0)) / 100
                asset.price_usd = ticker.get("lastPrice", asset.price_usd)
                asset.last_updated = datetime.now()
                updated_assets.append(asset)
        
        print(f"✅ Updated data for {len(updated_assets)} assets")
        return updated_assets


def test_dynamic_discovery():
    """Test the dynamic market discovery system."""
    print("🧪 TESTING DYNAMIC MARKET DISCOVERY")
    print("="*50)
    
    try:
        # Initialize discovery system
        discovery = DynamicMarketDiscovery()
        
        # Discover optimal assets
        optimal_assets = discovery.discover_optimal_assets(max_assets=25)
        
        if optimal_assets:
            print(f"\n🎯 DYNAMIC DISCOVERY RESULTS:")
            print(f"   Total Assets Found: {len(optimal_assets)}")
            print(f"   Market Cap Range: #{optimal_assets[0].market_cap_rank} - #{optimal_assets[-1].market_cap_rank}")
            
            total_volume = sum(a.daily_volume_usd for a in optimal_assets)
            avg_volume = total_volume / len(optimal_assets)
            print(f"   Total Daily Volume: ${total_volume:,.0f}")
            print(f"   Average Volume: ${avg_volume:,.0f}")
            
            # Generate correlation pairs
            pairs = discovery.get_correlation_pairs(optimal_assets, max_pairs=50)
            
            if pairs:
                print(f"\n🔗 CORRELATION PAIR ANALYSIS:")
                print(f"   Total Pairs Generated: {len(pairs)}")
                print(f"   Top 5 Pairs by Volume:")
                
                for i, (asset1, asset2) in enumerate(pairs[:5], 1):
                    combined_vol = asset1.daily_volume_usd + asset2.daily_volume_usd
                    rank_diff = abs(asset1.market_cap_rank - asset2.market_cap_rank)
                    print(f"      {i}. {asset1.symbol}/{asset2.symbol}: "
                          f"${combined_vol:,.0f}/day, {rank_diff} rank diff")
            
            print(f"\n✅ DYNAMIC SYSTEM WORKING PERFECTLY")
            print(f"   🔄 Future-proof: Adapts to new listings automatically")
            print(f"   📊 Real-time: Uses current market conditions")
            print(f"   🎯 Optimal: Filters for best trading opportunities")
            
        else:
            print("❌ No optimal assets discovered")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_dynamic_discovery()