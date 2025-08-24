"""
Binance API Integration - Real Trading Execution
Scientific trading with mathematical rigor and real capital.
"""

import os
import time
import hmac
import hashlib
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()  # Loads from .env up the directory tree
except ImportError:
    pass


@dataclass
class MarketData:
    """Market data point for API compatibility."""
    timestamp: float
    close: float
    volume: float


@dataclass
class BinanceCredentials:
    """Secure credential management for Binance API."""
    api_key: str
    api_secret: str
    testnet: bool = True  # Start with testnet for safety


@dataclass
class OrderResult:
    """Result of order execution."""
    success: bool
    order_id: Optional[str]
    filled_qty: float
    avg_price: float
    error_message: Optional[str]


@dataclass
class AccountBalance:
    """Account balance information."""
    asset: str
    free: float
    locked: float
    total: float


class BinanceConnector:
    """
    Binance API connector for micro-trading strategy execution.
    Implements the $64.10 capital deployment with risk controls.
    """
    
    def __init__(self, credentials: BinanceCredentials):
        self.credentials = credentials
        self.base_url = "https://testnet.binance.vision" if credentials.testnet else "https://api.binance.com"
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': credentials.api_key
        })
        
        # Trading parameters from TRADING_DEPLOYMENT.md
        self.max_risk_per_trade = 0.02  # 2% max risk
        self.stop_loss_threshold = 0.01  # 1% stop loss
        self.position_size_range = (10.0, 20.0)  # $10-20 per trade
        self.emergency_stop_threshold = 50.0  # Emergency stop if capital < $50
        self.max_concurrent_positions = 5
        self.target_pairs = ["BTCUSDC", "ETHUSDC"]  # USDC only - USDC being phased out
        
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature for authenticated requests."""
        return hmac.new(
            self.credentials.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """Make authenticated request to Binance API."""
        if params is None:
            params = {}
            
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            params['signature'] = self._generate_signature(query_string)
        
        url = f"{self.base_url}/api/v3/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_account_info(self) -> Dict[str, AccountBalance]:
        """Get current account balances."""
        result = self._make_request("GET", "account", signed=True)
        
        if "error" in result:
            return {}
            
        balances = {}
        for balance in result.get("balances", []):
            asset = balance["asset"]
            free = float(balance["free"])
            locked = float(balance["locked"])
            
            if free > 0 or locked > 0:  # Only include non-zero balances
                balances[asset] = AccountBalance(
                    asset=asset,
                    free=free,
                    locked=locked,
                    total=free + locked
                )
        
        return balances
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a trading pair."""
        result = self._make_request("GET", "ticker/price", {"symbol": symbol})
        
        if "error" in result or "price" not in result:
            return None
            
        return float(result["price"])
    
    def get_kline_data(self, symbol: str, interval: str = "1m", limit: int = 100) -> List[Dict]:
        """Get historical kline/candlestick data."""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        result = self._make_request("GET", "klines", params)
        
        if "error" in result:
            return []
            
        klines = []
        for kline in result:
            klines.append({
                "open_time": int(kline[0]),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": int(kline[6])
            })
        
        return klines
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """Place a market order."""
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "MARKET",
            "quantity": f"{quantity:.6f}",
            "newOrderRespType": "FULL"
        }
        
        result = self._make_request("POST", "order", params, signed=True)
        
        if "error" in result:
            return OrderResult(
                success=False,
                order_id=None,
                filled_qty=0.0,
                avg_price=0.0,
                error_message=result["error"]
            )
        
        # Parse successful order response
        filled_qty = float(result.get("executedQty", 0))
        avg_price = 0.0
        
        if "fills" in result and result["fills"]:
            total_value = sum(float(fill["price"]) * float(fill["qty"]) for fill in result["fills"])
            avg_price = total_value / filled_qty if filled_qty > 0 else 0.0
        
        return OrderResult(
            success=True,
            order_id=result.get("orderId"),
            filled_qty=filled_qty,
            avg_price=avg_price,
            error_message=None
        )
    
    def test_connectivity(self) -> bool:
        """Test connection to Binance API."""
        result = self._make_request("GET", "ping")
        return "error" not in result


def create_binance_connector() -> Optional[BinanceConnector]:
    """Create Binance connector with credentials from environment."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ Missing BINANCE_API_KEY or BINANCE_API_SECRET in environment")
        return None
    
    # Use mainnet for real data - testnet has fake volumes and unrealistic market conditions
    use_testnet = os.getenv("BINANCE_USE_TESTNET", "false").lower() == "true"
    
    credentials = BinanceCredentials(
        api_key=api_key,
        api_secret=api_secret,
        testnet=use_testnet
    )
    
    connector = BinanceConnector(credentials)
    
    # Test connectivity
    if connector.test_connectivity():
        print(f"✅ Connected to Binance {'Testnet' if use_testnet else 'Mainnet'}")
        return connector
    else:
        print("❌ Failed to connect to Binance")
        return None