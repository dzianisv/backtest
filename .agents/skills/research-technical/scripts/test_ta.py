"""
test_ta.py — pytest tests for pure TA functions in ta.py.
NO network calls. All inputs synthetic/handcrafted.
"""
import numpy as np
import pandas as pd
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ta import sma, ema, rsi, macd, obv, volume_ratio, ma_slope, weinstein_stage, support_resistance, divergence, verdict

def test_sma_basic():
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    result = sma(x, 3)
    assert abs(result.iloc[-1] - 4.0) < 1e-9
    assert np.isnan(result.iloc[0])  # first bar has NaN

def test_ema_converges():
    x = pd.Series([5.0] * 50)
    result = ema(x, 10)
    assert abs(result.iloc[-1] - 5.0) < 1e-6

def test_rsi_rising_series():
    close = pd.Series(np.linspace(100, 200, 100))
    result = rsi(close, 14)
    assert result.iloc[-1] > 70

def test_rsi_falling_series():
    close = pd.Series(np.linspace(200, 100, 100))
    result = rsi(close, 14)
    assert result.iloc[-1] < 30

def test_rsi_neutral():
    np.random.seed(42)
    close = pd.Series(100 + np.cumsum(np.random.choice([-1, 1], 100)))
    result = rsi(close, 14)
    assert 30 < result.iloc[-1] < 70

def test_macd_hist_positive_on_accel():
    t = np.arange(200)
    close = pd.Series(100 + t * 0.5 + 0.01 * t**2)
    line, signal, hist = macd(close, 12, 26, 9)
    assert hist.iloc[-1] > 0

def test_macd_hist_negative_on_decel():
    t = np.arange(200)
    close = pd.Series(200 - 0.01 * (t - 100)**2)
    line, signal, hist = macd(close, 12, 26, 9)
    assert hist.iloc[-1] < 0

def test_obv_hand_computed():
    close = pd.Series([10.0, 11.0, 10.5, 12.0])
    volume = pd.Series([100.0, 200.0, 150.0, 300.0])
    result = obv(close, volume)
    expected = [0, 200, 50, 350]
    for i, exp in enumerate(expected):
        assert abs(result.iloc[i] - exp) < 1e-9

def test_weinstein_stage2_uptrend():
    n = 50
    price = pd.Series(np.linspace(80, 120, n))
    ma = pd.Series(np.linspace(70, 100, n))
    assert weinstein_stage(price, ma) == 2

def test_weinstein_stage4_downtrend():
    n = 50
    price = pd.Series(np.linspace(120, 80, n))
    ma = pd.Series(np.linspace(130, 100, n))
    assert weinstein_stage(price, ma) == 4

def test_weinstein_stage1_basing():
    n = 60
    price_vals = np.concatenate([np.linspace(100, 70, 30), np.ones(30)*70])
    price = pd.Series(price_vals)
    ma = pd.Series(np.ones(n) * 80)
    assert weinstein_stage(price, ma) == 1

def test_weinstein_stage3_topping():
    n = 60
    price_vals = np.concatenate([np.linspace(70, 100, 30), np.ones(30)*100])
    price = pd.Series(price_vals)
    ma = pd.Series(np.ones(n) * 90)
    assert weinstein_stage(price, ma) == 3

def test_divergence_bullish():
    n = 100
    price_vals = np.ones(n) * 100
    price_vals[15:25] = np.linspace(100, 80, 10)
    price_vals[25:40] = np.linspace(80, 100, 15)
    price_vals[70:80] = np.linspace(100, 70, 10)
    price_vals[80:] = np.linspace(70, 85, 20)
    price = pd.Series(price_vals)
    ind_vals = np.ones(n) * 50
    ind_vals[15:25] = np.linspace(50, 30, 10)
    ind_vals[25:40] = np.linspace(30, 50, 15)
    ind_vals[70:80] = np.linspace(50, 35, 10)
    ind_vals[80:] = np.linspace(35, 50, 20)
    ind = pd.Series(ind_vals)
    result = divergence(price, ind, lookback=100)
    assert result == 'bullish'

def test_divergence_bearish():
    n = 100
    price_vals = np.ones(n) * 100
    price_vals[15:25] = np.linspace(100, 120, 10)
    price_vals[25:40] = np.linspace(120, 100, 15)
    price_vals[70:80] = np.linspace(100, 130, 10)
    price_vals[80:] = np.linspace(130, 110, 20)
    price = pd.Series(price_vals)
    ind_vals = np.ones(n) * 50
    ind_vals[15:25] = np.linspace(50, 70, 10)
    ind_vals[25:40] = np.linspace(70, 50, 15)
    ind_vals[70:80] = np.linspace(50, 65, 10)
    ind_vals[80:] = np.linspace(65, 50, 20)
    ind = pd.Series(ind_vals)
    result = divergence(price, ind, lookback=100)
    assert result == 'bearish'

def test_divergence_none():
    n = 100
    price_vals = np.ones(n) * 100
    price_vals[15:25] = np.linspace(100, 120, 10)
    price_vals[25:40] = np.linspace(120, 100, 15)
    price_vals[70:80] = np.linspace(100, 130, 10)
    price_vals[80:] = np.linspace(130, 110, 20)
    price = pd.Series(price_vals)
    ind_vals = np.ones(n) * 50
    ind_vals[15:25] = np.linspace(50, 65, 10)
    ind_vals[25:40] = np.linspace(65, 50, 15)
    ind_vals[70:80] = np.linspace(50, 70, 10)
    ind_vals[80:] = np.linspace(70, 50, 20)
    ind = pd.Series(ind_vals)
    result = divergence(price, ind, lookback=100)
    assert result == 'none'

def test_verdict_avoid_downtrend():
    f = {'stage': 4, 'price': 100, 'dist_50d': -10, 'dist_200d': -15,
         'rsi_w': 35, 'obv_trend': 'falling', 'div': 'none',
         'support': 90, 'resistance': 110, 'ma50': 110, 'ma200': 115}
    v = verdict(f)
    assert v['verdict'] == 'AVOID-DOWNTREND'

def test_verdict_buy_zone():
    f = {'stage': 2, 'price': 105, 'dist_50d': 5, 'dist_200d': 8,
         'rsi_w': 55, 'obv_trend': 'flat', 'div': 'none',
         'support': 100, 'resistance': 120, 'ma50': 100, 'ma200': 95}
    v = verdict(f)
    assert v['verdict'] == 'BUY-ZONE'

def test_verdict_accumulate():
    f = {'stage': 2, 'price': 105, 'dist_50d': 5, 'dist_200d': 8,
         'rsi_w': 55, 'obv_trend': 'rising', 'div': 'bullish',
         'support': 100, 'resistance': 120, 'ma50': 100, 'ma200': 95}
    v = verdict(f)
    assert v['verdict'] == 'ACCUMULATE'

def test_verdict_wait_pullback_extended():
    f = {'stage': 2, 'price': 120, 'dist_50d': 20, 'dist_200d': 25,
         'rsi_w': 65, 'obv_trend': 'rising', 'div': 'none',
         'support': 100, 'resistance': 130, 'ma50': 100, 'ma200': 95}
    v = verdict(f)
    assert v['verdict'] == 'WAIT-PULLBACK'

def test_verdict_wait_breakout():
    f = {'stage': 1, 'price': 90, 'dist_50d': -10, 'dist_200d': -15,
         'rsi_w': 45, 'obv_trend': 'flat', 'div': 'none',
         'support': 85, 'resistance': 100, 'ma50': 95, 'ma200': 100}
    v = verdict(f)
    assert v['verdict'] == 'WAIT-BREAKOUT'

def test_resolve_symbol():
    from ta import resolve_symbol
    assert resolve_symbol('BTC', 'coinbase') == 'BTC/USD'
    assert resolve_symbol('BTC', 'kraken') == 'BTC/USD'
    assert resolve_symbol('BTC', 'binance') == 'BTC/USDT'
    assert resolve_symbol('BTC', 'okx') == 'BTC/USDT'
    assert resolve_symbol('ETH', 'coinbase') == 'ETH/USD'
    assert resolve_symbol('ETH', 'kucoin') == 'ETH/USDT'
