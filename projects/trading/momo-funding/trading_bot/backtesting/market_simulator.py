"""
Market Simulator - Realistic Execution Modeling

Simulates real market conditions including:
- Bid-ask spreads based on volatility
- Slippage modeling (non-linear with order size)
- Latency effects (signal-to-execution delay)
- Partial fills and market impact
- Transaction costs (maker/taker fees)
- Liquidity constraints
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types for execution simulation."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"

class OrderSide(Enum):
    """Order side for buy/sell."""
    BUY = "buy"
    SELL = "sell"

@dataclass
class MarketConditions:
    """Current market conditions affecting execution."""
    timestamp: datetime
    bid: float
    ask: float
    spread_bps: float  # Spread in basis points
    volume_24h: float
    volatility_1h: float  # 1-hour realized volatility
    liquidity_score: float  # 0-1, higher is better
    
    @property
    def mid_price(self) -> float:
        """Mid-point between bid and ask."""
        return (self.bid + self.ask) / 2
    
    @property
    def spread_absolute(self) -> float:
        """Absolute spread in price units."""
        return self.ask - self.bid

@dataclass
class OrderRequest:
    """Order request for execution simulation."""
    timestamp: datetime
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"  # Good Till Cancelled
    
@dataclass
class Fill:
    """Individual fill from order execution."""
    timestamp: datetime
    price: float
    quantity: float
    fee: float
    fee_asset: str
    is_maker: bool

@dataclass
class ExecutionResult:
    """Result of order execution simulation."""
    order_id: str
    original_request: OrderRequest
    fills: List[Fill]
    status: str  # "filled", "partial", "rejected"
    total_filled_qty: float
    average_fill_price: float
    total_fees: float
    slippage_bps: float  # Slippage in basis points
    execution_time_ms: float  # Time from signal to execution
    market_impact_bps: float  # Estimated market impact
    
    @property
    def is_fully_filled(self) -> bool:
        """Check if order was fully filled."""
        return self.status == "filled"
    
    @property
    def fill_rate(self) -> float:
        """Percentage of order that was filled."""
        return self.total_filled_qty / self.original_request.quantity if self.original_request.quantity > 0 else 0

class LiquidityModel:
    """Model for simulating market liquidity and depth."""
    
    def __init__(self):
        # Liquidity parameters based on market tier
        self.tier_params = {
            "tier1": {"base_spread_bps": 2, "depth_factor": 1.0, "impact_factor": 0.5},    # BTC, ETH
            "tier2": {"base_spread_bps": 5, "depth_factor": 0.7, "impact_factor": 0.8},    # Top 10 alts
            "tier3": {"base_spread_bps": 10, "depth_factor": 0.4, "impact_factor": 1.2},   # Mid-cap alts
            "tier4": {"base_spread_bps": 25, "depth_factor": 0.2, "impact_factor": 2.0},   # Small-cap alts
        }
    
    def get_market_conditions(self, symbol: str, base_price: float, 
                            volume_24h: float, volatility: float) -> MarketConditions:
        """
        Generate realistic market conditions based on asset characteristics.
        
        Args:
            symbol: Trading pair symbol
            base_price: Current market price
            volume_24h: 24-hour trading volume
            volatility: Recent volatility measure
            
        Returns:
            MarketConditions with realistic bid/ask spread
        """
        # Determine asset tier based on volume
        tier = self._classify_asset_tier(volume_24h)
        params = self.tier_params[tier]
        
        # Calculate dynamic spread based on volatility
        base_spread_bps = params["base_spread_bps"]
        volatility_multiplier = 1 + (volatility * 10)  # Higher volatility = wider spreads
        dynamic_spread_bps = base_spread_bps * volatility_multiplier
        
        # Convert to absolute spread
        spread_absolute = base_price * (dynamic_spread_bps / 10000)
        
        # Calculate bid/ask
        bid = base_price - (spread_absolute / 2)
        ask = base_price + (spread_absolute / 2)
        
        # Liquidity score based on volume and tier
        liquidity_score = min(1.0, (volume_24h / 1000000) * params["depth_factor"])
        
        return MarketConditions(
            timestamp=datetime.now(),
            bid=bid,
            ask=ask,
            spread_bps=dynamic_spread_bps,
            volume_24h=volume_24h,
            volatility_1h=volatility,
            liquidity_score=liquidity_score
        )
    
    def _classify_asset_tier(self, volume_24h: float) -> str:
        """Classify asset tier based on 24h volume."""
        if volume_24h >= 1000000000:  # $1B+
            return "tier1"
        elif volume_24h >= 100000000:  # $100M+
            return "tier2"
        elif volume_24h >= 10000000:   # $10M+
            return "tier3"
        else:
            return "tier4"

class SlippageModel:
    """Model for realistic slippage calculation."""
    
    def __init__(self):
        # Slippage parameters: [linear_factor, square_root_factor, liquidity_adjustment]
        self.slippage_params = {
            "tier1": [0.001, 0.002, 0.5],   # Very low slippage
            "tier2": [0.002, 0.004, 0.7],   # Low slippage
            "tier3": [0.005, 0.008, 1.0],   # Medium slippage
            "tier4": [0.015, 0.025, 1.5],   # High slippage
        }
    
    def calculate_slippage(self, order_size_usd: float, market_conditions: MarketConditions,
                          symbol: str) -> float:
        """
        Calculate realistic slippage based on order size and market conditions.
        
        Uses a combination of linear and square-root impact models:
        Slippage = (linear_factor * size + sqrt_factor * sqrt(size)) * liquidity_adjustment
        
        Args:
            order_size_usd: Order size in USD
            market_conditions: Current market conditions
            symbol: Trading pair symbol
            
        Returns:
            Slippage in basis points
        """
        # Determine tier
        tier = self._classify_asset_tier(market_conditions.volume_24h)
        linear_factor, sqrt_factor, liquidity_adj = self.slippage_params[tier]
        
        # Base slippage calculation
        size_millions = order_size_usd / 1000000
        linear_component = linear_factor * size_millions
        sqrt_component = sqrt_factor * np.sqrt(size_millions)
        base_slippage = linear_component + sqrt_component
        
        # Adjust for current liquidity conditions
        liquidity_multiplier = liquidity_adj / max(0.1, market_conditions.liquidity_score)
        
        # Adjust for volatility (higher volatility = more slippage)
        volatility_multiplier = 1 + (market_conditions.volatility_1h * 2)
        
        # Final slippage in basis points
        slippage_bps = base_slippage * liquidity_multiplier * volatility_multiplier * 10000
        
        return min(slippage_bps, 500)  # Cap at 5% (500 bps)
    
    def _classify_asset_tier(self, volume_24h: float) -> str:
        """Classify asset tier based on 24h volume."""
        if volume_24h >= 1000000000:  # $1B+
            return "tier1"
        elif volume_24h >= 100000000:  # $100M+
            return "tier2"
        elif volume_24h >= 10000000:   # $10M+
            return "tier3"
        else:
            return "tier4"

class LatencyModel:
    """Model for execution latency simulation."""
    
    def __init__(self):
        # Latency parameters in milliseconds
        self.base_latency_ms = 50  # Base network latency
        self.processing_latency_ms = 20  # Order processing time
        self.volatility_factor = 100  # Additional latency during high volatility
        
    def calculate_execution_delay(self, market_conditions: MarketConditions) -> float:
        """
        Calculate realistic execution delay based on market conditions.
        
        Args:
            market_conditions: Current market conditions
            
        Returns:
            Execution delay in milliseconds
        """
        base_delay = self.base_latency_ms + self.processing_latency_ms
        
        # Additional delay during high volatility periods
        volatility_delay = market_conditions.volatility_1h * self.volatility_factor
        
        # Random component (network jitter)
        random_delay = np.random.exponential(20)  # Exponential distribution
        
        total_delay = base_delay + volatility_delay + random_delay
        
        return min(total_delay, 2000)  # Cap at 2 seconds

class FeeModel:
    """Model for trading fees calculation."""
    
    def __init__(self):
        # Binance fee structure (as of 2024)
        self.maker_fee_rate = 0.001   # 0.1%
        self.taker_fee_rate = 0.001   # 0.1%
        self.bnb_discount = 0.25      # 25% discount with BNB
        
    def calculate_fees(self, fill_price: float, fill_quantity: float, 
                      is_maker: bool, use_bnb_discount: bool = True) -> Tuple[float, str]:
        """
        Calculate trading fees for a fill.
        
        Args:
            fill_price: Price of the fill
            fill_quantity: Quantity filled
            is_maker: Whether this was a maker order
            use_bnb_discount: Whether to apply BNB discount
            
        Returns:
            Tuple of (fee_amount, fee_asset)
        """
        notional_value = fill_price * fill_quantity
        
        # Select fee rate
        fee_rate = self.maker_fee_rate if is_maker else self.taker_fee_rate
        
        # Apply BNB discount if applicable
        if use_bnb_discount:
            fee_rate *= (1 - self.bnb_discount)
        
        # Calculate fee
        fee_amount = notional_value * fee_rate
        fee_asset = "USDC"  # Assume fees paid in quote currency
        
        return fee_amount, fee_asset

class MarketSimulator:
    """
    Main market simulator for realistic backtesting.
    
    Combines all models to provide realistic execution simulation:
    - Liquidity modeling
    - Slippage calculation
    - Latency simulation
    - Fee calculation
    - Partial fill simulation
    """
    
    def __init__(self, use_realistic_execution: bool = True):
        self.liquidity_model = LiquidityModel()
        self.slippage_model = SlippageModel()
        self.latency_model = LatencyModel()
        self.fee_model = FeeModel()
        self.use_realistic_execution = use_realistic_execution
        
        # Execution statistics
        self.total_orders = 0
        self.filled_orders = 0
        self.partial_fills = 0
        self.rejected_orders = 0
        
    def execute_order(self, order: OrderRequest, market_price: float,
                     volume_24h: float, volatility: float) -> ExecutionResult:
        """
        Simulate realistic order execution.
        
        Args:
            order: Order request to execute
            market_price: Current market price
            volume_24h: 24-hour trading volume
            volatility: Recent volatility measure
            
        Returns:
            ExecutionResult with realistic execution details
        """
        self.total_orders += 1
        order_id = f"order_{self.total_orders}"
        
        # Get current market conditions
        market_conditions = self.liquidity_model.get_market_conditions(
            order.symbol, market_price, volume_24h, volatility
        )
        
        # Calculate execution delay
        execution_delay_ms = self.latency_model.calculate_execution_delay(market_conditions)
        
        # Determine execution price based on order type
        execution_price = self._determine_execution_price(
            order, market_conditions, execution_delay_ms
        )
        
        if execution_price is None:
            # Order rejected (e.g., limit order not filled)
            self.rejected_orders += 1
            return ExecutionResult(
                order_id=order_id,
                original_request=order,
                fills=[],
                status="rejected",
                total_filled_qty=0,
                average_fill_price=0,
                total_fees=0,
                slippage_bps=0,
                execution_time_ms=execution_delay_ms,
                market_impact_bps=0
            )
        
        # Calculate order size in USD for slippage calculation
        order_size_usd = order.quantity * execution_price
        
        # Calculate slippage
        slippage_bps = self.slippage_model.calculate_slippage(
            order_size_usd, market_conditions, order.symbol
        ) if self.use_realistic_execution else 0
        
        # Apply slippage to execution price
        slippage_factor = 1 + (slippage_bps / 10000)
        if order.side == OrderSide.BUY:
            final_price = execution_price * slippage_factor
        else:
            final_price = execution_price / slippage_factor
        
        # Determine fill quantity (simulate partial fills for large orders)
        fill_quantity = self._determine_fill_quantity(
            order.quantity, order_size_usd, market_conditions
        )
        
        # Calculate fees
        is_maker = (order.order_type == OrderType.LIMIT)
        fee_amount, fee_asset = self.fee_model.calculate_fees(
            final_price, fill_quantity, is_maker
        )
        
        # Create fill
        fill = Fill(
            timestamp=order.timestamp + timedelta(milliseconds=execution_delay_ms),
            price=final_price,
            quantity=fill_quantity,
            fee=fee_amount,
            fee_asset=fee_asset,
            is_maker=is_maker
        )
        
        # Determine order status
        if fill_quantity >= order.quantity * 0.999:  # 99.9% filled = fully filled
            status = "filled"
            self.filled_orders += 1
        else:
            status = "partial"
            self.partial_fills += 1
        
        # Calculate market impact
        market_impact_bps = min(slippage_bps * 0.5, 100)  # Market impact is typically less than slippage
        
        return ExecutionResult(
            order_id=order_id,
            original_request=order,
            fills=[fill],
            status=status,
            total_filled_qty=fill_quantity,
            average_fill_price=final_price,
            total_fees=fee_amount,
            slippage_bps=slippage_bps,
            execution_time_ms=execution_delay_ms,
            market_impact_bps=market_impact_bps
        )
    
    def _determine_execution_price(self, order: OrderRequest, 
                                 market_conditions: MarketConditions,
                                 delay_ms: float) -> Optional[float]:
        """Determine execution price based on order type and market conditions."""
        if order.order_type == OrderType.MARKET:
            # Market orders execute at bid/ask
            if order.side == OrderSide.BUY:
                return market_conditions.ask
            else:
                return market_conditions.bid
                
        elif order.order_type == OrderType.LIMIT:
            # Limit orders only execute if price is favorable
            if order.limit_price is None:
                return None
                
            if order.side == OrderSide.BUY:
                # Buy limit executes if market ask <= limit price
                return order.limit_price if market_conditions.ask <= order.limit_price else None
            else:
                # Sell limit executes if market bid >= limit price
                return order.limit_price if market_conditions.bid >= order.limit_price else None
                
        elif order.order_type == OrderType.STOP_LOSS:
            # Simplified stop loss execution
            if order.stop_price is None:
                return None
            return market_conditions.mid_price
            
        return None
    
    def _determine_fill_quantity(self, requested_qty: float, order_size_usd: float,
                               market_conditions: MarketConditions) -> float:
        """Determine fill quantity, simulating partial fills for large orders."""
        if not self.use_realistic_execution:
            return requested_qty
        
        # Large orders (>$100k) may get partial fills
        if order_size_usd > 100000:
            # Probability of partial fill increases with order size and decreases with liquidity
            partial_fill_prob = min(0.5, order_size_usd / 1000000) * (1 - market_conditions.liquidity_score)
            
            if np.random.random() < partial_fill_prob:
                # Partial fill: 70-95% of requested quantity
                fill_rate = 0.7 + (np.random.random() * 0.25)
                return requested_qty * fill_rate
        
        return requested_qty
    
    def get_execution_statistics(self) -> Dict[str, float]:
        """Get execution statistics for analysis."""
        if self.total_orders == 0:
            return {}
        
        return {
            "total_orders": self.total_orders,
            "fill_rate": self.filled_orders / self.total_orders,
            "partial_fill_rate": self.partial_fills / self.total_orders,
            "rejection_rate": self.rejected_orders / self.total_orders
        }

def create_market_simulator(realistic_execution: bool = True) -> MarketSimulator:
    """Factory function to create a configured market simulator."""
    return MarketSimulator(use_realistic_execution=realistic_execution)