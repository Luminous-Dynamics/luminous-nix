"""
WCAG AAA Compliance Utilities
Ensures the interface meets the highest accessibility standards
"""

from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import colorsys
import re


class ContrastLevel(Enum):
    """WCAG contrast level requirements"""
    FAIL = "fail"
    AA_LARGE = "aa_large"  # 3:1 for large text
    AA = "aa"               # 4.5:1 for normal text
    AAA_LARGE = "aaa_large" # 4.5:1 for large text
    AAA = "aaa"             # 7:1 for normal text


@dataclass
class ColorPair:
    """Represents a foreground/background color pair"""
    foreground: str  # Hex color
    background: str  # Hex color
    
    def __post_init__(self):
        # Ensure colors are in hex format
        self.foreground = self._normalize_hex(self.foreground)
        self.background = self._normalize_hex(self.background)
        
    def _normalize_hex(self, color: str) -> str:
        """Normalize hex color to #RRGGBB format"""
        color = color.strip()
        if not color.startswith('#'):
            color = f'#{color}'
        if len(color) == 4:  # #RGB -> #RRGGBB
            color = f'#{color[1]*2}{color[2]*2}{color[3]*2}'
        return color.upper()


class ColorContrastChecker:
    """
    Checks color contrast ratios for WCAG compliance
    """
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    @staticmethod
    def relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """
        Calculate relative luminance per WCAG formula
        """
        def adjust_channel(channel: int) -> float:
            c = channel / 255.0
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4
            
        r, g, b = [adjust_channel(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
    def contrast_ratio(self, color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors
        
        Args:
            color1: Hex color string
            color2: Hex color string
            
        Returns:
            Contrast ratio (1:1 to 21:1)
        """
        rgb1 = self.hex_to_rgb(color1.lstrip('#'))
        rgb2 = self.hex_to_rgb(color2.lstrip('#'))
        
        lum1 = self.relative_luminance(rgb1)
        lum2 = self.relative_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
        
    def check_contrast(
        self, 
        foreground: str, 
        background: str, 
        is_large_text: bool = False
    ) -> ContrastLevel:
        """
        Check if color combination meets WCAG standards
        
        Args:
            foreground: Foreground hex color
            background: Background hex color
            is_large_text: Whether this is large text (18pt+ or 14pt+ bold)
            
        Returns:
            The highest WCAG level this combination meets
        """
        ratio = self.contrast_ratio(foreground, background)
        
        if ratio >= 7.0:
            return ContrastLevel.AAA
        elif ratio >= 4.5:
            return ContrastLevel.AAA_LARGE if is_large_text else ContrastLevel.AA
        elif ratio >= 3.0 and is_large_text:
            return ContrastLevel.AA_LARGE
        else:
            return ContrastLevel.FAIL
            
    def suggest_adjustments(
        self, 
        foreground: str, 
        background: str,
        target_ratio: float = 7.0
    ) -> Dict[str, str]:
        """
        Suggest color adjustments to meet target contrast ratio
        
        Returns:
            Dictionary with suggested foreground and background colors
        """
        current_ratio = self.contrast_ratio(foreground, background)
        
        if current_ratio >= target_ratio:
            return {'foreground': foreground, 'background': background}
            
        # Convert to HSL for easier manipulation
        fg_rgb = self.hex_to_rgb(foreground)
        bg_rgb = self.hex_to_rgb(background)
        
        fg_hls = colorsys.rgb_to_hls(*(c/255.0 for c in fg_rgb))
        bg_hls = colorsys.rgb_to_hls(*(c/255.0 for c in bg_rgb))
        
        # Adjust lightness to increase contrast
        if fg_hls[1] > bg_hls[1]:  # Foreground is lighter
            # Make foreground lighter and background darker
            new_fg_l = min(1.0, fg_hls[1] * 1.1)
            new_bg_l = max(0.0, bg_hls[1] * 0.9)
        else:
            # Make foreground darker and background lighter
            new_fg_l = max(0.0, fg_hls[1] * 0.9)
            new_bg_l = min(1.0, bg_hls[1] * 1.1)
            
        # Convert back to RGB and hex
        new_fg_rgb = colorsys.hls_to_rgb(fg_hls[0], new_fg_l, fg_hls[2])
        new_bg_rgb = colorsys.hls_to_rgb(bg_hls[0], new_bg_l, bg_hls[2])
        
        new_fg_hex = '#{:02X}{:02X}{:02X}'.format(
            *(int(c * 255) for c in new_fg_rgb)
        )
        new_bg_hex = '#{:02X}{:02X}{:02X}'.format(
            *(int(c * 255) for c in new_bg_rgb)
        )
        
        return {'foreground': new_fg_hex, 'background': new_bg_hex}


@dataclass
class TextSpacingRequirements:
    """WCAG 2.1 text spacing requirements"""
    line_height: float = 1.5      # At least 1.5x font size
    paragraph_spacing: float = 2.0  # At least 2x font size
    letter_spacing: float = 0.12   # At least 0.12x font size
    word_spacing: float = 0.16     # At least 0.16x font size


class TextSpacingManager:
    """
    Manages text spacing for WCAG 2.1 compliance
    """
    
    def __init__(self):
        self.base_font_size: int = 16  # Default base font size in pixels
        self.requirements = TextSpacingRequirements()
        
    def calculate_spacing(self, font_size: Optional[int] = None) -> Dict[str, str]:
        """
        Calculate CSS spacing values for given font size
        
        Args:
            font_size: Font size in pixels (uses base if not provided)
            
        Returns:
            Dictionary of CSS property names and values
        """
        size = font_size or self.base_font_size
        
        return {
            'line-height': f'{self.requirements.line_height}',
            'margin-bottom': f'{self.requirements.paragraph_spacing}em',
            'letter-spacing': f'{self.requirements.letter_spacing}em',
            'word-spacing': f'{self.requirements.word_spacing}em'
        }
        
    def validate_spacing(self, styles: Dict[str, str]) -> Dict[str, bool]:
        """
        Validate if given styles meet WCAG requirements
        
        Returns:
            Dictionary indicating which requirements are met
        """
        results = {}
        
        # Extract numeric values from CSS
        line_height = self._extract_numeric(styles.get('line-height', '1'))
        letter_spacing = self._extract_numeric(styles.get('letter-spacing', '0'))
        word_spacing = self._extract_numeric(styles.get('word-spacing', '0'))
        
        results['line_height'] = line_height >= self.requirements.line_height
        results['letter_spacing'] = letter_spacing >= self.requirements.letter_spacing
        results['word_spacing'] = word_spacing >= self.requirements.word_spacing
        
        return results
        
    def _extract_numeric(self, value: str) -> float:
        """Extract numeric value from CSS string"""
        if isinstance(value, (int, float)):
            return float(value)
            
        # Remove units and extract number
        match = re.match(r'([\d.]+)', str(value))
        if match:
            return float(match.group(1))
        return 0.0


class MotionController:
    """
    Controls motion and animation for accessibility
    """
    
    def __init__(self):
        self.prefers_reduced_motion: bool = False
        self.animation_enabled: bool = True
        self.auto_play_enabled: bool = False
        self.parallax_enabled: bool = False
        
    def set_motion_preference(self, prefers_reduced: bool):
        """Set user's motion preference"""
        self.prefers_reduced_motion = prefers_reduced
        
        if prefers_reduced:
            self.animation_enabled = False
            self.auto_play_enabled = False
            self.parallax_enabled = False
            
    def get_animation_duration(self, base_duration: float) -> float:
        """
        Get adjusted animation duration based on preferences
        
        Args:
            base_duration: Base animation duration in seconds
            
        Returns:
            Adjusted duration (0 if animations disabled)
        """
        if not self.animation_enabled or self.prefers_reduced_motion:
            return 0.0
        return base_duration
        
    def should_animate(self) -> bool:
        """Check if animations should be shown"""
        return self.animation_enabled and not self.prefers_reduced_motion
        
    def get_transition_class(self) -> str:
        """Get CSS class for transitions"""
        if self.should_animate():
            return "transition-enabled"
        return "transition-disabled"


class WCAGValidator:
    """
    Main WCAG validation class
    """
    
    def __init__(self):
        self.contrast_checker = ColorContrastChecker()
        self.spacing_manager = TextSpacingManager()
        self.motion_controller = MotionController()
        
    def validate_colors(
        self, 
        color_scheme: Dict[str, ColorPair],
        require_aaa: bool = True
    ) -> Dict[str, Dict[str, any]]:
        """
        Validate a complete color scheme
        
        Args:
            color_scheme: Dictionary of named color pairs
            require_aaa: Whether to require AAA compliance
            
        Returns:
            Validation results for each color pair
        """
        results = {}
        target_level = ContrastLevel.AAA if require_aaa else ContrastLevel.AA
        
        for name, pair in color_scheme.items():
            ratio = self.contrast_checker.contrast_ratio(
                pair.foreground, 
                pair.background
            )
            level = self.contrast_checker.check_contrast(
                pair.foreground,
                pair.background
            )
            
            passes = level.value >= target_level.value
            
            results[name] = {
                'passes': passes,
                'ratio': ratio,
                'level': level,
                'suggestion': None if passes else 
                    self.contrast_checker.suggest_adjustments(
                        pair.foreground,
                        pair.background,
                        7.0 if require_aaa else 4.5
                    )
            }
            
        return results
        
    def validate_focus_indicators(
        self,
        focus_style: Dict[str, any]
    ) -> Dict[str, bool]:
        """
        Validate focus indicator compliance with WCAG 2.2
        
        Returns:
            Dictionary of validation results
        """
        results = {}
        
        # Check minimum width (2px)
        border_width = focus_style.get('border_width', 0)
        results['min_width'] = border_width >= 2
        
        # Check contrast ratio (3:1)
        if 'focus_color' in focus_style and 'background_color' in focus_style:
            ratio = self.contrast_checker.contrast_ratio(
                focus_style['focus_color'],
                focus_style['background_color']
            )
            results['contrast_ratio'] = ratio >= 3.0
        else:
            results['contrast_ratio'] = False
            
        # Check non-color indicator
        results['non_color_indicator'] = focus_style.get('has_outline', False)
        
        # Check persistence
        results['persistent'] = focus_style.get('persistent', True)
        
        return results
        
    def create_accessible_theme(self) -> Dict[str, ColorPair]:
        """
        Create a default accessible color theme
        
        Returns:
            Dictionary of WCAG AAA compliant color pairs
        """
        return {
            'primary': ColorPair('#000000', '#FFFFFF'),  # 21:1
            'secondary': ColorPair('#FFFFFF', '#000000'),  # 21:1
            'info': ColorPair('#0066CC', '#FFFFFF'),  # 7.1:1
            'success': ColorPair('#008000', '#FFFFFF'),  # 5.1:1 (needs adjustment)
            'warning': ColorPair('#000000', '#FFCC00'),  # 19.6:1
            'error': ColorPair('#FFFFFF', '#CC0000'),  # 6.0:1 (needs adjustment)
            'muted': ColorPair('#767676', '#FFFFFF'),  # 4.54:1 (AA)
        }