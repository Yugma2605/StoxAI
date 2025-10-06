from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
import datetime
import os

try:
    # Prefer the widely used Alpaca REST SDK
    import alpaca_trade_api as tradeapi  # type: ignore
except Exception:
    tradeapi = None  # SDK not installed; service will fall back to simulation

class TradeRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    shares: Optional[float] = Field(None, gt=0, description="Number of shares to trade")
    notional: Optional[float] = Field(
        None, gt=0, description="Dollar notional to trade (for market orders)"
    )
    price: Optional[float] = Field(None, gt=0, description="Price per share (simulation)")
    time_in_force: str = Field("day", description="Order TIF when using Alpaca")
    order_type: str = Field("market", description="Order type when using Alpaca")

class PortfolioItem(BaseModel):
    shares: float
    purchase_price: float

class TradingService:
    def __init__(self):
        self.portfolio: Dict[str, PortfolioItem] = {}
        self.cash: float = 100000.0  # Starting cash (simulation)

        # Attempt to configure Alpaca client from environment
        self._alpaca_client = None
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_SECRET_KEY")
        base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        if api_key and api_secret and tradeapi is not None:
            try:
                self._alpaca_client = tradeapi.REST(
                    key_id=api_key,
                    secret_key=api_secret,
                    base_url=base_url,
                )
                # Probe the account to validate creds
                _ = self._alpaca_client.get_account()
            except Exception:
                # If any error occurs, remain in simulation mode
                self._alpaca_client = None

    @property
    def using_alpaca(self) -> bool:
        return self._alpaca_client is not None

    def buy(self, trade: TradeRequest):
        if self.using_alpaca:
            # Live/paper trading via Alpaca
            if not trade.shares and not trade.notional:
                return {"status": "error", "message": "Provide either shares or notional for Alpaca order"}
            try:
                order = self._alpaca_client.submit_order(
                    symbol=trade.ticker,
                    qty=str(trade.shares) if trade.shares else None,
                    notional=str(trade.notional) if trade.notional else None,
                    side="buy",
                    type=trade.order_type,
                    time_in_force=trade.time_in_force,
                )
                return {
                    "status": "submitted",
                    "broker": "alpaca",
                    "order": self._serialize_order(order),
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Simulation mode
        if not trade.shares:
            return {"status": "error", "message": "'shares' is required in simulation mode"}
        if not trade.price:
            return {"status": "error", "message": "Price is required for simulated buy"}

        cost = trade.shares * trade.price
        if self.cash < cost:
            return {"status": "error", "message": "Not enough cash"}

        self.cash -= cost
        if trade.ticker in self.portfolio:
            item = self.portfolio[trade.ticker]
            new_total_shares = item.shares + trade.shares
            new_total_cost = (item.shares * item.purchase_price) + cost
            item.purchase_price = new_total_cost / new_total_shares
            item.shares = new_total_shares
        else:
            self.portfolio[trade.ticker] = PortfolioItem(
                shares=trade.shares,
                purchase_price=trade.price,
            )

        return {
            "status": "success",
            "mode": "simulation",
            "ticker": trade.ticker,
            "shares": trade.shares,
            "price": trade.price,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def sell(self, trade: TradeRequest):
        if self.using_alpaca:
            if not trade.shares and not trade.notional:
                return {"status": "error", "message": "Provide either shares or notional for Alpaca order"}
            try:
                order = self._alpaca_client.submit_order(
                    symbol=trade.ticker,
                    qty=str(trade.shares) if trade.shares else None,
                    notional=str(trade.notional) if trade.notional else None,
                    side="sell",
                    type=trade.order_type,
                    time_in_force=trade.time_in_force,
                )
                return {
                    "status": "submitted",
                    "broker": "alpaca",
                    "order": self._serialize_order(order),
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Simulation mode
        if not trade.shares:
            return {"status": "error", "message": "'shares' is required in simulation mode"}
        if trade.ticker not in self.portfolio or self.portfolio[trade.ticker].shares < trade.shares:
            return {"status": "error", "message": "Not enough shares to sell"}
        if not trade.price:
            return {"status": "error", "message": "Price is required for simulated sell"}

        item = self.portfolio[trade.ticker]
        item.shares -= trade.shares
        self.cash += trade.shares * trade.price

        if item.shares == 0:
            del self.portfolio[trade.ticker]

        return {
            "status": "success",
            "mode": "simulation",
            "ticker": trade.ticker,
            "shares": trade.shares,
            "price": trade.price,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def get_portfolio(self):
        if self.using_alpaca:
            try:
                account = self._alpaca_client.get_account()
                positions = self._alpaca_client.list_positions()
                holdings: Dict[str, Any] = {}
                for p in positions:
                    holdings[p.symbol] = {
                        "shares": float(p.qty),
                        "avg_entry_price": float(p.avg_entry_price),
                        "market_value": float(p.market_value),
                        "unrealized_pl": float(p.unrealized_pl),
                    }
                return {
                    "mode": "alpaca",
                    "cash": float(account.cash),
                    "buying_power": float(account.buying_power),
                    "holdings": holdings,
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Simulation mode
        return {"mode": "simulation", "cash": self.cash, "holdings": self.portfolio}

    def _serialize_order(self, order: Any) -> Dict[str, Any]:
        try:
            # Order may be an entity with attributes
            return {
                "id": getattr(order, "id", None),
                "symbol": getattr(order, "symbol", None),
                "qty": getattr(order, "qty", None),
                "notional": getattr(order, "notional", None),
                "side": getattr(order, "side", None),
                "type": getattr(order, "type", None),
                "time_in_force": getattr(order, "time_in_force", None),
                "status": getattr(order, "status", None),
                "submitted_at": getattr(order, "submitted_at", None),
                "filled_at": getattr(order, "filled_at", None),
                "filled_avg_price": getattr(order, "filled_avg_price", None),
            }
        except Exception:
            # Fallback for dict-like objects
            try:
                return dict(order)  # type: ignore
            except Exception:
                return {"raw": str(order)}

trading_service = TradingService()
