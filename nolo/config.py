"""Configuration schemas and institutional preset profiles for Nolo Bot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from nolo.types import RiskModel, StrategyMode


@dataclass
class SymbolSpec:
    """Instrument specification for accurate pip, tick, and lot sizing."""

    symbol: str
    digits: int = 5
    point: float = 0.00001
    pip_size: float = 0.0001
    tick_size: float = 0.00001
    tick_value: float = 1.0
    contract_size: float = 100000.0
    min_lot: float = 0.01
    max_lot: float = 100.0
    lot_step: float = 0.01
    commission_per_lot: float = 7.0
    max_spread_points: int = 20

    @property
    def base_currency(self) -> str:
        return self.symbol[:3].upper()

    @property
    def quote_currency(self) -> str:
        return self.symbol[3:6].upper()


DEFAULT_SYMBOL_SPECS: Dict[str, SymbolSpec] = {
    "EURUSD": SymbolSpec("EURUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "GBPUSD": SymbolSpec("GBPUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "USDJPY": SymbolSpec("USDJPY", digits=3, point=0.001, pip_size=0.01, tick_size=0.001, tick_value=0.68),
    "AUDUSD": SymbolSpec("AUDUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "USDCAD": SymbolSpec("USDCAD", digits=5, point=0.00001, pip_size=0.0001, tick_value=0.74),
    "USDCHF": SymbolSpec("USDCHF", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.12),
    "NZDUSD": SymbolSpec("NZDUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "EURJPY": SymbolSpec("EURJPY", digits=3, point=0.001, pip_size=0.01, tick_size=0.001, tick_value=0.68),
    "GBPJPY": SymbolSpec("GBPJPY", digits=3, point=0.001, pip_size=0.01, tick_size=0.001, tick_value=0.68, max_spread_points=30),
    "XAUUSD": SymbolSpec("XAUUSD", digits=2, point=0.01, pip_size=0.10, tick_size=0.01, tick_value=1.0, contract_size=100.0, max_spread_points=35),
}


@dataclass
class IndicatorConfig:
    """Parameters for technical, statistical, and state-space indicators."""

    fast_ma_period: int = 8
    slow_ma_period: int = 21
    trend_ma_period: int = 50
    rsi_period: int = 14
    rsi_upper: float = 70.0
    rsi_lower: float = 30.0
    stoch_k: int = 5
    stoch_d: int = 3
    stoch_slowing: int = 3
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bollinger_period: int = 20
    bollinger_std: float = 2.0
    keltner_period: int = 20
    keltner_atr_mult: float = 1.5
    atr_period: int = 14
    adx_period: int = 14
    supertrend_mult: float = 2.5
    ichimoku_tenkan: int = 9
    ichimoku_kijun: int = 26
    ichimoku_senkou_b: int = 52
    hurst_window: int = 64
    kalman_process_noise: float = 1e-4
    kalman_measurement_noise: float = 1e-2


@dataclass
class SMCConfig:
    """Parameters for institutional Smart Money Concepts detection."""

    swing_length: int = 5
    fvg_min_atr_fraction: float = 0.25
    ob_impulse_atr_mult: float = 1.4
    max_active_zones: int = 15
    liquidity_sweep_wick_ratio: float = 0.45
    equal_hl_tolerance_pips: float = 2.5


@dataclass
class RiskConfig:
    """Parameters for position sizing, drawdown protection, and trade exits."""

    risk_model: RiskModel = RiskModel.BAYESIAN_KELLY
    max_risk_pct: float = 1.0
    min_risk_pct: float = 0.20
    adaptive_risk_multiplier: float = 1.4
    kelly_fraction: float = 0.35
    atr_sl_multiplier: float = 2.0
    min_sl_pips: float = 8.0
    max_sl_pips: float = 65.0
    risk_reward_ratio: float = 2.2
    max_daily_drawdown_pct: float = 4.5
    max_total_drawdown_pct: float = 9.0
    max_daily_trades: int = 6
    min_bars_between_trades: int = 3
    max_open_positions: int = 4
    max_currency_exposure_pct: float = 2.5
    max_pair_correlation: float = 0.78
    use_equity_curve_filter: bool = True
    equity_ma_period: int = 15
    use_breakeven: bool = True
    breakeven_trigger_pips: float = 20.0
    breakeven_plus_pips: float = 3.0
    use_partial_tp: bool = True
    tp1_r_multiple: float = 1.0
    tp1_close_fraction: float = 0.40
    tp2_r_multiple: float = 1.8
    tp2_close_fraction: float = 0.30
    use_smart_trailing: bool = True
    trailing_activation_pips: float = 28.0
    trailing_distance_pips: float = 18.0
    max_holding_bars: int = 96


@dataclass
class MLConfig:
    """Parameters for the online neural signal scorer and contextual bandit."""

    learning_rate: float = 0.015
    l2_penalty: float = 1e-4
    min_signal_probability: float = 0.54
    strong_signal_probability: float = 0.68
    bandit_exploration_c: float = 0.65
    bandit_discount_gamma: float = 0.97


@dataclass
class BotConfig:
    """Master configuration container for the Nolo Trading Bot."""

    strategy_mode: StrategyMode = StrategyMode.ADAPTIVE
    main_timeframe: str = "M5"
    higher_timeframe: str = "H1"
    use_volatility_filter: bool = True
    use_price_momentum: bool = True
    use_market_structure: bool = True
    use_multi_timeframe: bool = True
    use_order_flow: bool = True
    use_currency_strength: bool = True
    use_news_filter: bool = True
    avoid_rollover_hours: Tuple[int, ...] = (22, 23)
    magic_number: int = 202504
    indicators: IndicatorConfig = field(default_factory=IndicatorConfig)
    smc: SMCConfig = field(default_factory=SMCConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    ml: MLConfig = field(default_factory=MLConfig)
