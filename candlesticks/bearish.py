from typing import Any, Dict, Optional
import pandas as pd
from candlesticks.base import Pattern

class ShootingStar(Pattern):
    """
    Bearish reversal pattern with small body and long upper shadow.
    Typically appears at the top of an uptrend.
    """
    @property
    def name(self) -> str: return "shooting_star"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Bearish reversal with small body at bottom and long upper shadow (2x+ body length)"
    @property
    def required_bars(self) -> int: return 1
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        last = df.iloc[-1]
        
        body = abs(last['close'] - last['open'])
        lower_shadow = min(last['open'], last['close']) - last['low']
        upper_shadow = last['high'] - max(last['open'], last['close'])
        
        # Shooting star criteria:
        # 1. Long upper shadow (at least 2x body)
        # 2. Small or no lower shadow (< 0.3x body)
        # 3. Body in lower half of range
        if (upper_shadow >= 2 * body and 
            lower_shadow <= 0.3 * body and
            body > 0):
            
            confidence = min(1.0, upper_shadow / (3 * body))
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': round(confidence, 2),
                'bar_index': len(df) - 1
            }
        
        return None


class EveningStar(Pattern):
    """
    Three-bar bearish reversal pattern.
    First bar: Large bullish
    Second bar: Small body (gap up)
    Third bar: Large bearish (closes below midpoint of first bar)
    """
    @property
    def name(self) -> str: return "evening_star"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Three-bar bearish reversal: large bullish, small body, large bearish"
    @property
    def required_bars(self) -> int: return 3
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        bars = df.iloc[-3:].reset_index(drop=True)
        first, second, third = bars.iloc[0], bars.iloc[1], bars.iloc[2]
        
        # First bar: bullish
        first_body = first['close'] - first['open']
        if first_body <= 0: return None
        
        # Third bar: bearish
        third_body = third['close'] - third['open']
        if third_body >= 0: return None
        
        first_body_abs = abs(first_body)
        second_body_abs = abs(second['close'] - second['open'])
        third_body_abs = abs(third_body)
        
        # Evening star criteria
        first_midpoint = (first['open'] + first['close']) / 2
        
        if (first_body_abs > 1.5 * second_body_abs and
            third_body_abs > 1.5 * second_body_abs and
            third['close'] < first_midpoint):
            
            confidence = min(1.0, 0.7 + 0.3 * (first_midpoint - third['close']) / first_body_abs)
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': round(confidence, 2),
                'bar_index': len(df) - 1
            }
        
        return None


class BearishEngulfing(Pattern):
    """
    Two-bar bearish reversal where second bearish bar engulfs first bullish bar.
    """
    @property
    def name(self) -> str: return "bearish_engulfing"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Two-bar reversal where bearish bar completely engulfs prior bullish bar"
    @property
    def required_bars(self) -> int: return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        bars = df.iloc[-2:].reset_index(drop=True)
        first, second = bars.iloc[0], bars.iloc[1]
        
        # First bar: bullish
        if first['close'] <= first['open']: return None
        
        # Second bar: bearish
        if second['close'] >= second['open']: return None
        
        # Engulfing criteria
        if (second['open'] > first['close'] and
            second['close'] < first['open']):
            
            first_body = abs(first['close'] - first['open'])
            second_body = abs(second['close'] - second['open'])
            confidence = min(1.0, 0.6 + 0.4 * (second_body / first_body - 1))
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': round(max(0.6, confidence), 2),
                'bar_index': len(df) - 1
            }
        
        return None


class ThreeBlackCrows(Pattern):
    """
    Three consecutive long bearish candles, each closing lower than previous.
    Strong bearish reversal. Requires checking the bar before the pattern to ensure
    it's a reversal and not a continuation.
    """
    @property
    def name(self) -> str: return "three_black_crows"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Three consecutive long bearish candles closing progressively lower (reversal pattern)"
    @property
    def required_bars(self) -> int: return 4  # Need 4th bar for context
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        # Get last 4 bars - the 4th is for context validation
        bars = df.iloc[-4:].reset_index(drop=True)
        fourth_bar = bars.iloc[0]
        crows = bars.iloc[-3:]  # Last 3 bars are the potential crows
        
        # All three crows must be bearish
        if any(b['close'] >= b['open'] for _, b in crows.iterrows()):
            return None
            
        # Check consecutive lower closes
        if not (crows.iloc[1]['close'] < crows.iloc[0]['close'] and
                crows.iloc[2]['close'] < crows.iloc[1]['close']):
            return None
            
        # Bodies should be relatively large
        bodies = [abs(b['close'] - b['open']) for _, b in crows.iterrows()]
        avg_body = sum(bodies) / 3
        if any(b < 0.5 * avg_body for b in bodies):
            return None
        
        # CONTEXT CHECK: The 4th bar should NOT be a strong bearish candle
        # This ensures we're detecting a reversal, not a continuation
        fourth_body = fourth_bar['close'] - fourth_bar['open']
        
        # If 4th bar is strongly bearish (similar to crows), reject - it's a continuation
        if fourth_body < 0 and abs(fourth_body) >= avg_body * 0.7:
            return None  # Already in downtrend, not a reversal
            
        return {
            'name': self.name,
            'classification': self.classification,
            'confidence': 0.9,
            'bar_index': len(df) - 1
        }


class BearishHarami(Pattern):
    """
    Two-bar pattern: Large bullish candle followed by small candle contained in previous body.
    """
    @property
    def name(self) -> str: return "bearish_harami"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Small candle contained within prior large bullish candle body"
    @property
    def required_bars(self) -> int: return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        bars = df.iloc[-2:].reset_index(drop=True)
        first, second = bars.iloc[0], bars.iloc[1]
        
        # First bar large bullish
        if first['close'] <= first['open']: return None
        
        first_body = abs(first['close'] - first['open'])
        second_body = abs(second['close'] - second['open'])
        
        # Second bar small
        if second_body > 0.5 * first_body: return None
        
        # Contained within first body
        first_top = first['close']
        first_bottom = first['open']
        second_top = max(second['open'], second['close'])
        second_bottom = min(second['open'], second['close'])
        
        if second_top < first_top and second_bottom > first_bottom:
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.7,
                'bar_index': len(df) - 1
            }
        return None


class DarkCloudCover(Pattern):
    """
    Two-bar pattern: Bullish candle followed by bearish candle that opens higher 
    but closes more than 50% into the previous body.
    """
    @property
    def name(self) -> str: return "dark_cloud_cover"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Bearish candle opens higher but closes >50% into prior bullish body"
    @property
    def required_bars(self) -> int: return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        bars = df.iloc[-2:].reset_index(drop=True)
        first, second = bars.iloc[0], bars.iloc[1]
        
        if first['close'] <= first['open']: return None # 1st bullish
        if second['close'] >= second['open']: return None # 2nd bearish
        
        # Open higher than first close (gap up)
        if second['open'] <= first['close']: return None
        
        # Close below midpoint of first body
        first_midpoint = (first['open'] + first['close']) / 2
        
        if second['close'] < first_midpoint and second['close'] > first['open']:
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.8,
                'bar_index': len(df) - 1
            }
        return None


class HangingMan(Pattern):
    """
    Small body at top, long lower shadow. Bearish reversal if found in uptrend.
    Identical shape to Hammer but bearish context.
    """
    @property
    def name(self) -> str: return "hanging_man"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Small body at top range, long lower shadow (bearish context)"
    @property
    def required_bars(self) -> int: return 1
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        last = df.iloc[-1]
        
        body = abs(last['close'] - last['open'])
        lower_shadow = min(last['open'], last['close']) - last['low']
        upper_shadow = last['high'] - max(last['open'], last['close'])
        total_range = last['high'] - last['low']

        if total_range == 0: return None
        
        # Same criteria as Hammer
        if (body > 0 and 
            lower_shadow >= 2 * body and
            upper_shadow <= lower_shadow * 0.5 and
            lower_shadow >= total_range * 0.5):
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.65,
                'bar_index': len(df) - 1
            }
        return None


class BearishMarubozu(Pattern):
    """
    Long bearish candle with little to no shadows. Shows strong selling pressure.
    """
    @property
    def name(self) -> str: return "bearish_marubozu"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Long bearish candle with no shadows"
    @property
    def required_bars(self) -> int: return 1
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        last = df.iloc[-1]
        
        if last['close'] >= last['open']: return None
        
        body = last['open'] - last['close']
        total_len = last['high'] - last['low']
        
        if total_len == 0: return None
        
        if body / total_len > 0.9:
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.9,
                'bar_index': len(df) - 1
            }
        return None


class TweezerTop(Pattern):
    """
    Two candles with matching highs.
    """
    @property
    def name(self) -> str: return "tweezer_top"
    @property
    def classification(self) -> str: return "bearish"
    @property
    def description(self) -> str: return "Two candles with matching highs"
    @property
    def required_bars(self) -> int: return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        bars = df.iloc[-2:].reset_index(drop=True)
        b1, b2 = bars.iloc[0], bars.iloc[1]
        
        # Highs are almost identical
        if abs(b1['high'] - b2['high']) / b1['high'] < 0.001:
             return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.75,
                'bar_index': len(df) - 1
            }
        return None
