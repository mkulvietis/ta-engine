import pytest
import pandas as pd
from candlesticks.compute import detect_patterns
from candlesticks.registry import pattern_registry
from candlesticks.bullish import (
    ThreeWhiteSoldiers, BullishHarami, PiercingLine, 
    InvertedHammer, BullishMarubozu, TweezerBottom
)
from candlesticks.bearish import (
    ThreeBlackCrows, BearishHarami, DarkCloudCover,
    HangingMan, BearishMarubozu, TweezerTop
)

class TestExtendedPatterns:
    """Test the extended set of candlestick patterns."""
    
    # --- Bullish Patterns ---
    
    def test_three_white_soldiers(self):
        """Test Three White Soldiers pattern."""
        # 4th bar: bearish (showing weakness before reversal)
        # Then 3 consecutive bullish candles
        data = pd.DataFrame({
            'open': [105.0, 100.0, 102.0, 104.0],
            'high': [106.0, 102.5, 104.5, 106.5],
            'low': [99.0, 99.5, 101.5, 103.5],
            'close': [100.0, 102.0, 104.0, 106.0]  # 1st bearish, next 3 bullish
        })
        pattern = ThreeWhiteSoldiers()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'three_white_soldiers'
        assert result['classification'] == 'bullish'

    def test_bullish_harami(self):
        """Test Bullish Harami pattern."""
        data = pd.DataFrame({
            'open': [110.0, 104.0],
            'high': [110.5, 106.0],
            'low': [100.0, 103.0],
            'close': [100.0, 105.0] # Second candle within first
        })
        pattern = BullishHarami()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'bullish_harami'

    def test_piercing_line(self):
        """Test Piercing Line pattern."""
        data = pd.DataFrame({
            'open': [110.0, 100.0], # Second opens gap down
            'high': [110.5, 106.0],
            'low': [100.0, 99.0],
            'close': [102.0, 107.0] # Second closes > 50% into first (midpoint 106)
        })
        pattern = PiercingLine()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'piercing_line'

    def test_inverted_hammer(self):
        """Test Inverted Hammer pattern."""
        data = pd.DataFrame({
            'open': [100.0],
            'high': [105.0], # Long upper shadow
            'low': [99.5],
            'close': [101.0] # Small body
        })
        pattern = InvertedHammer()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'inverted_hammer'

    def test_bullish_marubozu(self):
        """Test Bullish Marubozu pattern."""
        data = pd.DataFrame({
            'open': [100.0],
            'high': [110.0],
            'low': [100.0],
            'close': [110.0] # Open=Low, Close=High
        })
        pattern = BullishMarubozu()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'bullish_marubozu'

    def test_tweezer_bottom(self):
        """Test Tweezer Bottom pattern."""
        data = pd.DataFrame({
            'open': [105.0, 104.0],
            'high': [106.0, 105.0],
            'low': [100.0, 100.0], # Matching lows
            'close': [101.0, 103.0]
        })
        pattern = TweezerBottom()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'tweezer_bottom'

    # --- Bearish Patterns ---
    
    def test_three_black_crows(self):
        """Test Three Black Crows pattern."""
        # 4th bar: bullish (showing strength before reversal)
        # Then 3 consecutive bearish candles
        data = pd.DataFrame({
            'open': [100.0, 106.0, 104.0, 102.0],
            'high': [106.0, 106.5, 104.5, 102.5],
            'low': [99.0, 103.5, 101.5, 99.5],
            'close': [106.0, 104.0, 102.0, 100.0]  # 1st bullish, next 3 bearish
        })
        pattern = ThreeBlackCrows()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'three_black_crows'
        assert result['classification'] == 'bearish'

    def test_bearish_harami(self):
        """Test Bearish Harami pattern."""
        data = pd.DataFrame({
            'open': [100.0, 106.0],
            'high': [110.0, 107.0],
            'low': [99.0, 104.0],
            'close': [110.0, 105.0] # Second candle within first
        })
        pattern = BearishHarami()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'bearish_harami'

    def test_dark_cloud_cover(self):
        """Test Dark Cloud Cover pattern."""
        data = pd.DataFrame({
            'open': [100.0, 110.0], # Second opens gap up
            'high': [108.0, 111.0],
            'low': [99.0, 103.0],
            'close': [108.0, 103.0] # Second closes < 50% into first (midpoint 104)
        })
        pattern = DarkCloudCover()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'dark_cloud_cover'

    def test_hanging_man(self):
        """Test Hanging Man pattern."""
        data = pd.DataFrame({
            'open': [105.2],
            'high': [105.5],
            'low': [100.0], # Long lower shadow
            'close': [105.0] # Small body at top
        })
        pattern = HangingMan()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'hanging_man'

    def test_bearish_marubozu(self):
        """Test Bearish Marubozu pattern."""
        data = pd.DataFrame({
            'open': [110.0],
            'high': [110.0],
            'low': [100.0],
            'close': [100.0] # Open=High, Close=Low
        })
        pattern = BearishMarubozu()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'bearish_marubozu'

    def test_tweezer_top(self):
        """Test Tweezer Top pattern."""
        data = pd.DataFrame({
            'open': [100.0, 102.0],
            'high': [105.0, 105.0], # Matching highs
            'low': [99.0, 100.0], 
            'close': [104.0, 103.0]
        })
        pattern = TweezerTop()
        result = pattern.detect(data)
        assert result is not None
        assert result['name'] == 'tweezer_top'
