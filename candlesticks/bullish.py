from typing import Any, Dict, Optional
import pandas as pd
from candlesticks.base import Pattern

class Hammer(Pattern):
    """
    Bullish reversal pattern with small body and long lower shadow.
    Typically appears at the bottom of a downtrend.
    """
    
    @property
    def name(self) -> str:
        return "hammer"
    
    @property
    def classification(self) -> str:
        return "bullish"
    
    @property
    def description(self) -> str:
        return "Bullish reversal with small body at top and long lower shadow (2x+ body length)"
    
    @property
    def required_bars(self) -> int:
        return 1  # Single bar pattern
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        # Analyze the last bar
        last = df.iloc[-1]
        
        body = abs(last['close'] - last['open'])
        lower_shadow = min(last['open'], last['close']) - last['low']
        upper_shadow = last['high'] - max(last['open'], last['close'])
        total_range = last['high'] - last['low']
        
        if total_range == 0:
            return None
        
        # Hammer criteria:
        # 1. Long lower shadow (at least 2x body)
        # 2. Small or no upper shadow (< half of lower shadow)
        # 3. Body should be small relative to range
        # 4. Lower shadow should be significant part of range
        
        # More lenient criteria for hammer
        if (body > 0 and  # Not a doji
            lower_shadow >= 2 * body and
            upper_shadow <= lower_shadow * 0.5 and
            lower_shadow >= total_range * 0.5):  # Lower shadow at least half of range
            
            # Confidence based on how pronounced the pattern is
            lower_to_body_ratio = lower_shadow / max(body, 0.001)
            confidence = min(1.0, 0.6 + 0.1 * lower_to_body_ratio)
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': round(confidence, 2),
                'bar_index': len(df) - 1
            }
        
        return None


class MorningStar(Pattern):
    """
    Three-bar bullish reversal pattern.
    First bar: Large bearish
    Second bar: Small body (gap down)
    Third bar: Large bullish (closes above midpoint of first bar)
    """
    
    @property
    def name(self) -> str:
        return "morning_star"
    
    @property
    def classification(self) -> str:
        return "bullish"
    
    @property
    def description(self) -> str:
        return "Three-bar bullish reversal: large bearish, small body, large bullish"
    
    @property
    def required_bars(self) -> int:
        return 3
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        # Get last 3 bars
        bars = df.iloc[-3:].reset_index(drop=True)
        first, second, third = bars.iloc[0], bars.iloc[1], bars.iloc[2]
        
        # First bar: bearish
        first_body = first['close'] - first['open']
        if first_body >= 0:  # Not bearish
            return None
        
        # Third bar: bullish
        third_body = third['close'] - third['open']
        if third_body <= 0:  # Not bullish
            return None
        
        # Check sizes
        first_body_abs = abs(first_body)
        second_body_abs = abs(second['close'] - second['open'])
        third_body_abs = abs(third_body)
        
        # Morning star criteria:
        # 1. First bar has large bearish body
        # 2. Second bar has small body
        # 3. Third bar has large bullish body
        # 4. Third bar closes above midpoint of first bar
        first_midpoint = (first['open'] + first['close']) / 2
        
        if (first_body_abs > 1.5 * second_body_abs and
            third_body_abs > 1.5 * second_body_abs and
            third['close'] > first_midpoint):
            
            # Confidence based on how far third bar closes above first midpoint
            confidence = min(1.0, 0.7 + 0.3 * (third['close'] - first_midpoint) / first_body_abs)
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': round(confidence, 2),
                'bar_index': len(df) - 1
            }
        
        return None


class BullishEngulfing(Pattern):
    """
    Two-bar bullish reversal where second bullish bar engulfs first bearish bar.
    """
    
    @property
    def name(self) -> str:
        return "bullish_engulfing"
    
    @property
    def classification(self) -> str:
        return "bullish"
    
    @property
    def description(self) -> str:
        return "Two-bar reversal where bullish bar completely engulfs prior bearish bar"
    
    @property
    def required_bars(self) -> int:
        return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        # Get last 2 bars
        bars = df.iloc[-2:].reset_index(drop=True)
        first, second = bars.iloc[0], bars.iloc[1]
        
        # First bar: bearish
        if first['close'] >= first['open']:
            return None
        
        # Second bar: bullish
        if second['close'] <= second['open']:
            return None
        
        # Engulfing criteria:
        # Second open < first close AND second close > first open
        if (second['open'] < first['close'] and
            second['close'] > first['open']):
            
            # Confidence based on size of engulfing
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


class ThreeWhiteSoldiers(Pattern):
    """
    Three consecutive long bullish candles, each closing higher than the previous one.
    Strong bullish reversal signal. Requires checking the bar before the pattern to ensure
    it's a reversal and not a continuation.
    """
    @property
    def name(self) -> str: return "three_white_soldiers"
    @property
    def classification(self) -> str: return "bullish"
    @property
    def description(self) -> str: return "Three consecutive long bullish candles closing progressively higher (reversal pattern)"
    @property
    def required_bars(self) -> int: return 4  # Need 4th bar for context
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        # Get last 4 bars - the 4th is for context validation
        bars = df.iloc[-4:].reset_index(drop=True)
        fourth_bar = bars.iloc[0]
        soldiers = bars.iloc[-3:]  # Last 3 bars are the potential soldiers
        
        # All three soldiers must be bullish
        if any(b['close'] <= b['open'] for _, b in soldiers.iterrows()):
            return None
            
        # Check consecutive higher closes
        if not (soldiers.iloc[1]['close'] > soldiers.iloc[0]['close'] and
                soldiers.iloc[2]['close'] > soldiers.iloc[1]['close']):
            return None
            
        # Check consecutive higher opens
        if not (soldiers.iloc[1]['open'] > soldiers.iloc[0]['open'] and 
                soldiers.iloc[2]['open'] > soldiers.iloc[1]['open']):
            return None
            
        # Bodies should be relatively large (not dojis)
        bodies = [abs(b['close'] - b['open']) for _, b in soldiers.iterrows()]
        avg_body = sum(bodies) / 3
        if any(b < 0.5 * avg_body for b in bodies):
            return None
        
        # CONTEXT CHECK: The 4th bar should NOT be a strong bullish candle
        # This ensures we're detecting a reversal, not a continuation
        fourth_body = fourth_bar['close'] - fourth_bar['open']
        
        # If 4th bar is strongly bullish (similar to soldiers), reject - it's a continuation
        if fourth_body > 0 and fourth_body >= avg_body * 0.7:
            return None  # Already in uptrend, not a reversal
            
        return {
            'name': self.name,
            'classification': self.classification,
            'confidence': 0.9,
            'bar_index': len(df) - 1
        }


class BullishHarami(Pattern):
    """
    Two-bar pattern: Large bearish candle followed by a small bullish (or bearish) candle
    contained entirely within the previous body.
    """
    @property
    def name(self) -> str: return "bullish_harami"
    @property
    def classification(self) -> str: return "bullish"
    @property
    def description(self) -> str: return "Small candle contained within prior large bearish candle body"
    @property
    def required_bars(self) -> int: return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        bars = df.iloc[-2:].reset_index(drop=True)
        first, second = bars.iloc[0], bars.iloc[1]
        
        # First bar large bearish
        if first['close'] >= first['open']: return None
        
        first_body = abs(first['close'] - first['open'])
        second_body = abs(second['close'] - second['open'])
        
        # Second bar small
        if second_body > 0.5 * first_body: return None
        
        # Contained within first body
        first_top = first['open']
        first_bottom = first['close']
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


class PiercingLine(Pattern):
    """
    Two-bar pattern: Bearish candle followed by bullish candle that opens lower 
    but closes more than 50% into the previous body.
    """
    @property
    def name(self) -> str: return "piercing_line"
    @property
    def classification(self) -> str: return "bullish"
    @property
    def description(self) -> str: return "Bullish candle opens lower but closes >50% into prior bearish body"
    @property
    def required_bars(self) -> int: return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        bars = df.iloc[-2:].reset_index(drop=True)
        first, second = bars.iloc[0], bars.iloc[1]
        
        if first['close'] >= first['open']: return None # 1st bearish
        if second['close'] <= second['open']: return None # 2nd bullish
        
        # Open lower than first close (gap down)
        if second['open'] >= first['close']: return None
        
        # Close above midpoint of first body
        first_midpoint = (first['open'] + first['close']) / 2
        
        if second['close'] > first_midpoint and second['close'] < first['open']:
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.8,
                'bar_index': len(df) - 1
            }
        return None


class InvertedHammer(Pattern):
    """
    Inverted hammer: Small body at bottom, long upper shadow. 
    Bullish reversal if found in downtrend.
    """
    @property
    def name(self) -> str: return "inverted_hammer"
    @property
    def classification(self) -> str: return "bullish"
    @property
    def description(self) -> str: return "Small body at bottom range, long upper shadow"
    @property
    def required_bars(self) -> int: return 1
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        last = df.iloc[-1]
        
        body = abs(last['close'] - last['open'])
        upper_shadow = last['high'] - max(last['open'], last['close'])
        lower_shadow = min(last['open'], last['close']) - last['low']
        
        if body == 0: return None
        
        # Long upper shadow (>2x body), small lower shadow
        if (upper_shadow >= 2 * body and 
            lower_shadow <= body * 0.5):
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.65,
                'bar_index': len(df) - 1
            }
        return None


class BullishMarubozu(Pattern):
    """
    Long bullish candle with little to no shadows. Shows strong buying pressure.
    """
    @property
    def name(self) -> str: return "bullish_marubozu"
    @property
    def classification(self) -> str: return "bullish"
    @property
    def description(self) -> str: return "Long bullish candle with no shadows"
    @property
    def required_bars(self) -> int: return 1
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        last = df.iloc[-1]
        
        if last['close'] <= last['open']: return None
        
        body = last['close'] - last['open']
        total_len = last['high'] - last['low']
        
        if total_len == 0: return None
        
        # Body takes up almost entire range (>90%)
        if body / total_len > 0.9:
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.9,
                'bar_index': len(df) - 1
            }
        return None


class TweezerBottom(Pattern):
    """
    Two candles with matching lows.
    """
    @property
    def name(self) -> str: return "tweezer_bottom"
    @property
    def classification(self) -> str: return "bullish"
    @property
    def description(self) -> str: return "Two candles with matching lows"
    @property
    def required_bars(self) -> int: return 2
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        bars = df.iloc[-2:].reset_index(drop=True)
        b1, b2 = bars.iloc[0], bars.iloc[1]
        
        # Lows are almost identical (within 0.1%)
        if abs(b1['low'] - b2['low']) / b1['low'] < 0.001:
             return {
                'name': self.name,
                'classification': self.classification,
                'confidence': 0.75,
                'bar_index': len(df) - 1
            }
        return None
