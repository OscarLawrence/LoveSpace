#!/usr/bin/env python3
"""
Mathematical Framework for Coherent Trading
Advanced mathematical models for crypto market inefficiency exploitation.
"""

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.fft import fft, fftfreq
import networkx as nx
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class MarketRegime:
    """Market regime classification."""
    regime_type: str  # "trending", "mean_reverting", "volatile", "stable"
    confidence: float
    expected_duration: int  # minutes
    mathematical_properties: Dict[str, float]


class FourierMarketAnalyzer:
    """Use Fourier analysis to detect market cycles and predict reversals."""
    
    def __init__(self, window_size: int = 1440):  # 24 hours of minute data
        self.window_size = window_size
        
    def decompose_price_cycles(self, prices: List[float]) -> Dict[str, float]:
        """Decompose price series into frequency components."""
        if len(prices) < self.window_size:
            return {}
        
        # Apply Fourier Transform
        price_series = np.array(prices[-self.window_size:])
        fft_values = fft(price_series)
        frequencies = fftfreq(len(price_series))
        
        # Analyze dominant frequencies
        power_spectrum = np.abs(fft_values) ** 2
        dominant_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
        dominant_frequency = frequencies[dominant_freq_idx]
        
        # Calculate cycle characteristics
        cycle_period = 1 / abs(dominant_frequency) if dominant_frequency != 0 else 0
        cycle_strength = power_spectrum[dominant_freq_idx] / np.sum(power_spectrum)
        
        return {
            "dominant_cycle_period": cycle_period,
            "cycle_strength": cycle_strength,
            "trend_component": np.mean(price_series),
            "volatility_component": np.std(price_series),
            "phase_angle": np.angle(fft_values[dominant_freq_idx])
        }
    
    def predict_next_reversal(self, cycles: Dict[str, float], current_price: float) -> Optional[Tuple[float, int]]:
        """Predict next price reversal using cycle analysis."""
        if not cycles or cycles["cycle_strength"] < 0.1:
            return None
        
        period = cycles["dominant_cycle_period"]
        phase = cycles["phase_angle"]
        amplitude = cycles["volatility_component"]
        
        # Calculate time to next reversal
        time_to_reversal = (period / 2) - (phase / (2 * np.pi) * period)
        if time_to_reversal < 0:
            time_to_reversal += period / 2
        
        # Predict reversal price
        reversal_price = current_price + amplitude * np.sin(phase + np.pi)
        
        return reversal_price, int(time_to_reversal)


class InformationTheoryAnalyzer:
    """Apply information theory to measure market predictability."""
    
    def calculate_market_entropy(self, price_changes: List[float], bins: int = 20) -> float:
        """Calculate Shannon entropy of price changes."""
        if not price_changes:
            return 0
        
        # Discretize price changes
        hist, _ = np.histogram(price_changes, bins=bins, density=True)
        hist = hist[hist > 0]  # Remove zero probabilities
        
        # Calculate Shannon entropy
        entropy = -np.sum(hist * np.log2(hist))
        return entropy
    
    def calculate_mutual_information(self, x: List[float], y: List[float]) -> float:
        """Calculate mutual information between two time series."""
        # Discretize both series
        x_bins = np.histogram_bin_edges(x, bins=10)
        y_bins = np.histogram_bin_edges(y, bins=10)
        
        x_discrete = np.digitize(x, x_bins)
        y_discrete = np.digitize(y, y_bins)
        
        # Calculate joint and marginal histograms
        joint_hist, _, _ = np.histogram2d(x_discrete, y_discrete, bins=[10, 10], density=True)
        x_hist, _ = np.histogram(x_discrete, bins=10, density=True)
        y_hist, _ = np.histogram(y_discrete, bins=10, density=True)
        
        # Calculate mutual information
        mi = 0
        for i in range(len(x_hist)):
            for j in range(len(y_hist)):
                if joint_hist[i, j] > 0 and x_hist[i] > 0 and y_hist[j] > 0:
                    mi += joint_hist[i, j] * np.log2(joint_hist[i, j] / (x_hist[i] * y_hist[j]))
        
        return mi
    
    def detect_information_asymmetry(self, volume: List[float], price_changes: List[float]) -> float:
        """Detect information asymmetry using volume-price relationship."""
        if len(volume) != len(price_changes) or len(volume) < 10:
            return 0
        
        # Calculate mutual information between volume and price changes
        mi = self.calculate_mutual_information(volume, price_changes)
        
        # Normalize by maximum possible mutual information
        entropy_volume = self.calculate_market_entropy(volume)
        entropy_price = self.calculate_market_entropy(price_changes)
        max_mi = min(entropy_volume, entropy_price)
        
        if max_mi > 0:
            return mi / max_mi
        return 0


class NetworkAnalyzer:
    """Analyze crypto market as a network system."""
    
    def __init__(self):
        self.correlation_threshold = 0.5
        
    def build_correlation_network(self, price_data: Dict[str, List[float]]) -> nx.Graph:
        """Build network graph from asset correlations."""
        G = nx.Graph()
        assets = list(price_data.keys())
        
        # Add nodes
        for asset in assets:
            G.add_node(asset)
        
        # Add edges based on correlations
        for i in range(len(assets)):
            for j in range(i + 1, len(assets)):
                asset1, asset2 = assets[i], assets[j]
                
                if len(price_data[asset1]) == len(price_data[asset2]):
                    correlation = np.corrcoef(price_data[asset1], price_data[asset2])[0, 1]
                    
                    if abs(correlation) > self.correlation_threshold:
                        G.add_edge(asset1, asset2, weight=abs(correlation))
        
        return G
    
    def calculate_network_centrality(self, G: nx.Graph) -> Dict[str, float]:
        """Calculate centrality measures for network analysis."""
        centrality_measures = {}
        
        if len(G.nodes()) == 0:
            return centrality_measures
        
        # Degree centrality
        degree_centrality = nx.degree_centrality(G)
        
        # Betweenness centrality
        betweenness_centrality = nx.betweenness_centrality(G)
        
        # Eigenvector centrality
        try:
            eigenvector_centrality = nx.eigenvector_centrality(G)
        except:
            eigenvector_centrality = {node: 0 for node in G.nodes()}
        
        # Combine measures
        for node in G.nodes():
            centrality_measures[node] = {
                "degree": degree_centrality.get(node, 0),
                "betweenness": betweenness_centrality.get(node, 0),
                "eigenvector": eigenvector_centrality.get(node, 0)
            }
        
        return centrality_measures
    
    def detect_network_anomalies(self, G: nx.Graph, historical_centrality: Dict[str, Dict[str, float]]) -> List[str]:
        """Detect anomalies in network structure."""
        current_centrality = self.calculate_network_centrality(G)
        anomalies = []
        
        for asset in current_centrality:
            if asset in historical_centrality:
                current = current_centrality[asset]
                historical = historical_centrality[asset]
                
                # Check for significant changes in centrality
                for measure in ["degree", "betweenness", "eigenvector"]:
                    current_val = current.get(measure, 0)
                    historical_val = historical.get(measure, 0)
                    
                    if historical_val > 0:
                        change = abs(current_val - historical_val) / historical_val
                        if change > 0.5:  # 50% change threshold
                            anomalies.append(f"{asset}_{measure}")
        
        return anomalies


class StochasticOptimalControl:
    """Optimal control theory for position sizing and risk management."""
    
    def __init__(self, risk_aversion: float = 2.0):
        self.risk_aversion = risk_aversion
        
    def hamilton_jacobi_bellman_solution(self, expected_return: float, volatility: float, 
                                       current_wealth: float, time_horizon: float) -> float:
        """Solve HJB equation for optimal portfolio allocation."""
        # Simplified Merton solution for log utility
        # Optimal fraction = (μ - r) / (γ * σ²)
        # where μ = expected return, r = risk-free rate, γ = risk aversion, σ = volatility
        
        risk_free_rate = 0.02  # 2% annual risk-free rate
        excess_return = expected_return - risk_free_rate
        
        if volatility <= 0:
            return 0
        
        optimal_fraction = excess_return / (self.risk_aversion * volatility ** 2)
        
        # Apply practical constraints
        optimal_fraction = max(0, min(optimal_fraction, 0.5))  # Cap at 50%
        
        return optimal_fraction
    
    def calculate_optimal_leverage(self, sharpe_ratio: float, max_drawdown: float) -> float:
        """Calculate optimal leverage using Kelly criterion with drawdown constraint."""
        # Kelly fraction: f = μ/σ² for log-normal returns
        kelly_fraction = sharpe_ratio ** 2 / 2
        
        # Adjust for maximum acceptable drawdown
        if max_drawdown > 0:
            drawdown_adjustment = 1 / (1 + max_drawdown * 5)  # Conservative adjustment
            kelly_fraction *= drawdown_adjustment
        
        # Convert to leverage (assuming 40% correlation with market)
        optimal_leverage = kelly_fraction * 2.5
        
        return max(1.0, min(optimal_leverage, 3.0))  # Leverage between 1x and 3x


class RegimeDetectionSystem:
    """Detect market regimes using mathematical models."""
    
    def __init__(self):
        self.regime_history = []
        
    def detect_current_regime(self, prices: List[float], volumes: List[float]) -> MarketRegime:
        """Detect current market regime using multiple mathematical indicators."""
        if len(prices) < 20:
            return MarketRegime("unknown", 0.0, 0, {})
        
        # Calculate regime indicators
        returns = np.diff(np.log(prices))
        volatility = np.std(returns) * np.sqrt(1440)  # Annualized volatility
        trend_strength = self._calculate_trend_strength(prices)
        mean_reversion_strength = self._calculate_mean_reversion(returns)
        volume_trend = self._calculate_volume_trend(volumes)
        
        # Classify regime
        regime_scores = {
            "trending": trend_strength * (1 - mean_reversion_strength),
            "mean_reverting": mean_reversion_strength * (1 - trend_strength),
            "volatile": volatility * (1 - trend_strength),
            "stable": (1 - volatility) * (1 - trend_strength)
        }
        
        # Find dominant regime
        dominant_regime = max(regime_scores, key=regime_scores.get)
        confidence = regime_scores[dominant_regime]
        
        # Estimate regime duration based on historical patterns
        expected_duration = self._estimate_regime_duration(dominant_regime, confidence)
        
        # Mathematical properties
        properties = {
            "volatility": volatility,
            "trend_strength": trend_strength,
            "mean_reversion": mean_reversion_strength,
            "volume_trend": volume_trend,
            "sharpe_ratio": np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        }
        
        regime = MarketRegime(
            regime_type=dominant_regime,
            confidence=confidence,
            expected_duration=expected_duration,
            mathematical_properties=properties
        )
        
        self.regime_history.append(regime)
        return regime
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength using linear regression."""
        if len(prices) < 10:
            return 0
        
        x = np.arange(len(prices))
        slope, _, r_value, _, _ = stats.linregress(x, prices)
        
        # Normalize trend strength
        trend_strength = abs(r_value) * (1 if slope > 0 else -1)
        return max(0, trend_strength)
    
    def _calculate_mean_reversion(self, returns: np.ndarray) -> float:
        """Calculate mean reversion strength using autocorrelation."""
        if len(returns) < 10:
            return 0
        
        # Calculate first-order autocorrelation
        autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
        
        # Mean reversion indicated by negative autocorrelation
        mean_reversion = max(0, -autocorr)
        return mean_reversion
    
    def _calculate_volume_trend(self, volumes: List[float]) -> float:
        """Calculate volume trend strength."""
        if len(volumes) < 10:
            return 0
        
        x = np.arange(len(volumes))
        slope, _, r_value, _, _ = stats.linregress(x, volumes)
        
        return abs(r_value)
    
    def _estimate_regime_duration(self, regime_type: str, confidence: float) -> int:
        """Estimate regime duration based on historical patterns."""
        base_durations = {
            "trending": 240,      # 4 hours
            "mean_reverting": 120,  # 2 hours
            "volatile": 60,       # 1 hour
            "stable": 480         # 8 hours
        }
        
        base_duration = base_durations.get(regime_type, 120)
        confidence_multiplier = 0.5 + confidence
        
        return int(base_duration * confidence_multiplier)


class MathematicalTradingFramework:
    """Integrated mathematical framework for coherent trading."""
    
    def __init__(self):
        self.fourier_analyzer = FourierMarketAnalyzer()
        self.info_analyzer = InformationTheoryAnalyzer()
        self.network_analyzer = NetworkAnalyzer()
        self.optimal_control = StochasticOptimalControl()
        self.regime_detector = RegimeDetectionSystem()
        
    def comprehensive_market_analysis(self, market_data: Dict[str, List[float]]) -> Dict[str, any]:
        """Perform comprehensive mathematical analysis of market data."""
        
        # Extract main asset data
        main_asset = list(market_data.keys())[0]
        prices = market_data[main_asset]
        
        if len(prices) < 50:
            return {}
        
        # Fourier analysis
        fourier_cycles = self.fourier_analyzer.decompose_price_cycles(prices)
        
        # Information theory analysis
        returns = np.diff(np.log(prices))
        market_entropy = self.info_analyzer.calculate_market_entropy(returns.tolist())
        
        # Network analysis (if multiple assets)
        network_anomalies = []
        if len(market_data) > 1:
            correlation_network = self.network_analyzer.build_correlation_network(market_data)
            # Would compare with historical centrality
            
        # Regime detection
        volumes = [1000000] * len(prices)  # Placeholder - would use real volume data
        current_regime = self.regime_detector.detect_current_regime(prices, volumes)
        
        # Optimal control calculations
        expected_return = np.mean(returns) if len(returns) > 0 else 0
        volatility = np.std(returns) if len(returns) > 0 else 0
        optimal_allocation = self.optimal_control.hamilton_jacobi_bellman_solution(
            expected_return, volatility, 10000, 1.0
        )
        
        return {
            "fourier_analysis": fourier_cycles,
            "market_entropy": market_entropy,
            "network_anomalies": network_anomalies,
            "current_regime": current_regime,
            "optimal_allocation": optimal_allocation,
            "mathematical_edge": self._calculate_mathematical_edge(fourier_cycles, market_entropy, current_regime)
        }
    
    def _calculate_mathematical_edge(self, fourier_cycles: Dict, entropy: float, regime: MarketRegime) -> float:
        """Calculate overall mathematical edge for trading."""
        edge_components = []
        
        # Fourier edge
        if fourier_cycles.get("cycle_strength", 0) > 0.1:
            edge_components.append(fourier_cycles["cycle_strength"] * 0.3)
        
        # Entropy edge (lower entropy = more predictable = higher edge)
        if entropy > 0:
            entropy_edge = max(0, (5 - entropy) / 5 * 0.2)  # Normalize entropy
            edge_components.append(entropy_edge)
        
        # Regime edge
        regime_edge = regime.confidence * 0.2
        edge_components.append(regime_edge)
        
        # Combined edge
        total_edge = sum(edge_components)
        return min(total_edge, 0.8)  # Cap at 80% edge


# Example usage and testing
if __name__ == "__main__":
    # Initialize framework
    framework = MathematicalTradingFramework()
    
    # Generate sample data
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(1000) * 0.01) + 50000
    sample_data = {"BTC": prices.tolist()}
    
    # Perform analysis
    analysis = framework.comprehensive_market_analysis(sample_data)
    
    print("🧮 Mathematical Trading Framework Analysis")
    print("=" * 50)
    print(f"Market Entropy: {analysis.get('market_entropy', 0):.3f}")
    print(f"Regime: {analysis.get('current_regime').regime_type if analysis.get('current_regime') else 'Unknown'}")
    print(f"Mathematical Edge: {analysis.get('mathematical_edge', 0):.2%}")
    print(f"Optimal Allocation: {analysis.get('optimal_allocation', 0):.2%}")
    print("=" * 50)