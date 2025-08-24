#!/usr/bin/env python3
"""
Altcoin Correlation Matrix - Multi-Asset Inefficiency Detection
Finds correlation breakdowns across top crypto assets for maximum profit.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import itertools

# Add formal contracts
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "MomoAI/projects/coherence/formal_contracts"))
from contract_language import coherence_contract, ComplexityClass

@dataclass
class AltcoinPair:
    """Altcoin trading pair with market data."""
    symbol: str
    market_cap_rank: int
    typical_correlation: float  # Historical average correlation
    volatility: float  # Expected volatility
    liquidity_score: float  # Trading volume/market cap ratio

@dataclass
class CorrelationBreakdown:
    """Multi-asset correlation breakdown opportunity."""
    pair1: str
    pair2: str
    historical_correlation: float
    current_correlation: float
    breakdown_magnitude: float
    confidence: float
    expected_return: float
    risk_level: float
    mathematical_proof: str

class AltcoinCorrelationDetector:
    """Detects correlation breakdowns across multiple altcoin pairs."""
    
    def __init__(self, min_confidence: float = 0.75):
        self.min_confidence = min_confidence
        self.altcoin_universe = self._initialize_altcoin_universe()
    
    def _initialize_altcoin_universe(self) -> Dict[str, AltcoinPair]:
        """
        Initialize top altcoins by market cap with expected characteristics.
        
        Focus on top 10-20 for now, can expand to top 100 later.
        """
        return {
            # Top tier - most liquid
            "BTC": AltcoinPair("BTCUSDC", 1, 1.0, 0.04, 0.8),  # Bitcoin
            "ETH": AltcoinPair("ETHUSDC", 2, 0.85, 0.05, 0.9),  # Ethereum
            
            # Major alts - high liquidity, different use cases
            "BNB": AltcoinPair("BNBUSDC", 3, 0.65, 0.06, 0.7),  # Binance Coin
            "SOL": AltcoinPair("SOLUSDC", 4, 0.70, 0.08, 0.6),  # Solana
            "ADA": AltcoinPair("ADAUSDC", 5, 0.75, 0.07, 0.5),  # Cardano
            "AVAX": AltcoinPair("AVAXUSDC", 6, 0.72, 0.09, 0.4), # Avalanche
            "DOT": AltcoinPair("DOTUSDC", 7, 0.68, 0.08, 0.4),   # Polkadot
            "LINK": AltcoinPair("LINKUSDC", 8, 0.60, 0.07, 0.5), # Chainlink
            "MATIC": AltcoinPair("MATICUSDC", 9, 0.73, 0.09, 0.3), # Polygon
            "UNI": AltcoinPair("UNIUSDC", 10, 0.68, 0.10, 0.3),   # Uniswap
            
            # Mid-tier alts - higher volatility, more inefficiencies
            "ATOM": AltcoinPair("ATOMUSDC", 11, 0.55, 0.12, 0.2), # Cosmos
            "FTM": AltcoinPair("FTMUSDC", 12, 0.58, 0.14, 0.2),   # Fantom  
            "ALGO": AltcoinPair("ALGOUSDC", 13, 0.52, 0.13, 0.2), # Algorand
            "VET": AltcoinPair("VETUSDC", 14, 0.48, 0.15, 0.1),   # VeChain
        }
    
    @coherence_contract(
        input_types={"assets": "List[str]"},
        output_type="List[Tuple[str, str]]",
        requires=["len(assets) >= 2"],
        ensures=["len(result) == len(assets) * (len(assets) - 1) // 2"],
        complexity_time=ComplexityClass.QUADRATIC,
        pure=True
    )
    def generate_asset_pairs(self, assets: List[str]) -> List[Tuple[str, str]]:
        """Generate all possible pairs from asset list."""
        return list(itertools.combinations(assets, 2))
    
    @coherence_contract(
        input_types={"pair1": "str", "pair2": "str"},
        output_type="float",
        requires=["len(pair1) > 0", "len(pair2) > 0"],
        ensures=["0.0 <= result <= 1.0"],
        complexity_time=ComplexityClass.CONSTANT,
        pure=True
    )
    def calculate_expected_correlation(self, pair1: str, pair2: str) -> float:
        """
        Calculate expected correlation based on asset characteristics.
        
        Higher correlation expected between:
        - Same blockchain ecosystems (ETH/ERC-20 tokens)
        - Similar use cases (DeFi tokens, Layer 1s)
        - Similar market cap tiers
        """
        if pair1 not in self.altcoin_universe or pair2 not in self.altcoin_universe:
            return 0.5  # Default correlation
        
        asset1 = self.altcoin_universe[pair1]
        asset2 = self.altcoin_universe[pair2]
        
        # Base correlation from typical correlations
        base_corr = (asset1.typical_correlation + asset2.typical_correlation) / 2
        
        # Adjust for market cap similarity (closer ranks = higher correlation)
        rank_diff = abs(asset1.market_cap_rank - asset2.market_cap_rank)
        rank_adjustment = max(0, 1 - rank_diff / 10)  # Closer ranks boost correlation
        
        # Combine factors
        expected_correlation = base_corr * (0.7 + 0.3 * rank_adjustment)
        
        return min(1.0, max(0.0, expected_correlation))
    
    @coherence_contract(
        input_types={"pair1": "str", "pair2": "str"},
        output_type="float",
        requires=["len(pair1) > 0", "len(pair2) > 0"],
        ensures=["result > 0.0"],
        complexity_time=ComplexityClass.CONSTANT,
        pure=True
    )
    def calculate_profit_potential(self, pair1: str, pair2: str) -> float:
        """
        Calculate profit potential for correlation breakdown.
        
        Higher profit potential for:
        - Lower market cap assets (more inefficient)
        - Higher volatility assets
        - Lower liquidity assets (wider spreads)
        """
        if pair1 not in self.altcoin_universe or pair2 not in self.altcoin_universe:
            return 0.1  # Default return
        
        asset1 = self.altcoin_universe[pair1]
        asset2 = self.altcoin_universe[pair2]
        
        # Higher rank = lower market cap = higher potential
        market_cap_factor = (asset1.market_cap_rank + asset2.market_cap_rank) / 20
        
        # Higher volatility = higher potential
        volatility_factor = (asset1.volatility + asset2.volatility) / 2
        
        # Lower liquidity = higher spreads = higher potential (but also higher risk)
        liquidity_factor = 2.0 - (asset1.liquidity_score + asset2.liquidity_score) / 2
        
        # Combine factors
        profit_potential = 0.05 + (market_cap_factor * 0.02) + (volatility_factor * 0.5) + (liquidity_factor * 0.05)
        
        return min(0.3, max(0.05, profit_potential))  # Cap between 5-30%
    
    def find_best_opportunities(self, market_data: Dict[str, List[Dict]], 
                               max_opportunities: int = 5) -> List[CorrelationBreakdown]:
        """
        Scan all altcoin pairs and find the best correlation breakdown opportunities.
        
        Strategy: Focus on smaller altcoins with higher inefficiencies.
        """
        opportunities = []
        available_assets = [asset for asset in self.altcoin_universe.keys() if asset in market_data]
        
        if len(available_assets) < 2:
            return opportunities
        
        pairs_to_check = self.generate_asset_pairs(available_assets)
        
        for asset1, asset2 in pairs_to_check:
            data1 = market_data[asset1]
            data2 = market_data[asset2]
            
            if len(data1) < 50 or len(data2) < 50:
                continue
            
            # Calculate correlations (using same logic as single-pair detector)
            recent_prices1 = [d['close'] for d in data1[-20:]]
            recent_prices2 = [d['close'] for d in data2[-20:]]
            
            hist_prices1 = [d['close'] for d in data1[-50:-20]]
            hist_prices2 = [d['close'] for d in data2[-50:-20]]
            
            # Calculate returns and correlations
            recent_returns1 = self._calculate_returns(recent_prices1)
            recent_returns2 = self._calculate_returns(recent_prices2)
            hist_returns1 = self._calculate_returns(hist_prices1)
            hist_returns2 = self._calculate_returns(hist_prices2)
            
            if len(recent_returns1) < 10 or len(hist_returns1) < 20:
                continue
            
            current_corr = self._calculate_correlation(recent_returns1, recent_returns2)
            historical_corr = self._calculate_correlation(hist_returns1, hist_returns2)
            
            breakdown_magnitude = abs(historical_corr - current_corr)
            
            # Threshold adjusted for altcoin volatility (slightly lower than BTC/ETH)
            if breakdown_magnitude > 0.35:  # Slightly lower than BTC/ETH (0.4) due to higher volatility
                confidence = min(breakdown_magnitude * 1.5, 0.9)  # Unified confidence calculation
                expected_return = self.calculate_profit_potential(asset1, asset2)
                
                # Risk adjustment based on asset characteristics
                base_risk = 0.15
                if asset1 in self.altcoin_universe and asset2 in self.altcoin_universe:
                    vol_adjustment = (self.altcoin_universe[asset1].volatility + 
                                    self.altcoin_universe[asset2].volatility) / 2
                    risk_level = base_risk + (vol_adjustment * 0.5)
                else:
                    risk_level = base_risk * 1.5  # Higher risk for unknown assets
                
                if confidence >= self.min_confidence:
                    opportunity = CorrelationBreakdown(
                        pair1=asset1,
                        pair2=asset2,
                        historical_correlation=historical_corr,
                        current_correlation=current_corr,
                        breakdown_magnitude=breakdown_magnitude,
                        confidence=confidence,
                        expected_return=expected_return,
                        risk_level=min(risk_level, 0.25),  # Cap risk at 25%
                        mathematical_proof=f"Altcoin correlation breakdown: {asset1}/{asset2} "
                                         f"correlation changed {breakdown_magnitude:.2%} from "
                                         f"{historical_corr:.3f} to {current_corr:.3f}. "
                                         f"Expected profit: {expected_return:.1%} (higher volatility assets)"
                    )
                    opportunities.append(opportunity)
        
        # Sort by expected profit-adjusted confidence
        opportunities.sort(key=lambda x: x.confidence * x.expected_return, reverse=True)
        
        return opportunities[:max_opportunities]
    
    def _calculate_returns(self, prices: List[float]) -> List[float]:
        """Calculate percentage returns."""
        if len(prices) < 2:
            return []
        return [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] != 0]
    
    def _calculate_correlation(self, returns1: List[float], returns2: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(returns1) != len(returns2) or len(returns1) < 2:
            return 0.0
        
        n = len(returns1)
        mean1 = sum(returns1) / n
        mean2 = sum(returns2) / n
        
        numerator = sum((returns1[i] - mean1) * (returns2[i] - mean2) for i in range(n))
        
        sum_sq1 = sum((returns1[i] - mean1) ** 2 for i in range(n))
        sum_sq2 = sum((returns2[i] - mean2) ** 2 for i in range(n))
        
        if sum_sq1 == 0 or sum_sq2 == 0:
            return 0.0
        
        denominator = (sum_sq1 * sum_sq2) ** 0.5
        return numerator / denominator if denominator != 0 else 0.0


def create_altcoin_detector(min_confidence: float = 0.75) -> AltcoinCorrelationDetector:
    """Factory function to create altcoin correlation detector."""
    return AltcoinCorrelationDetector(min_confidence=min_confidence)