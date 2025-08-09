"""
Test the enhanced 10-style personality system
"""

import pytest
from nix_humanity.core.personality import (
    PersonalityStyle, PersonalityManager, PERSONALITY_PRESETS
)


class TestPersonalityStyles:
    """Test all 10 personality styles"""
    
    def test_all_styles_exist(self):
        """Verify all 10 styles are defined"""
        expected_styles = [
            PersonalityStyle.MINIMAL,
            PersonalityStyle.FRIENDLY,
            PersonalityStyle.ENCOURAGING,
            PersonalityStyle.PLAYFUL,
            PersonalityStyle.SACRED,
            PersonalityStyle.PROFESSIONAL,
            PersonalityStyle.TEACHER,
            PersonalityStyle.COMPANION,
            PersonalityStyle.HACKER,
            PersonalityStyle.ZEN
        ]
        
        assert len(PersonalityStyle) == 10
        for style in expected_styles:
            assert style in PersonalityStyle
            
    def test_all_styles_have_presets(self):
        """Verify each style has personality traits defined"""
        for style in PersonalityStyle:
            assert style in PERSONALITY_PRESETS
            preset = PERSONALITY_PRESETS[style]
            
            # Check all required traits are present
            assert hasattr(preset, 'verbosity')
            assert hasattr(preset, 'emotiveness')
            assert hasattr(preset, 'formality')
            assert hasattr(preset, 'encouragement')
            assert hasattr(preset, 'playfulness')
            assert hasattr(preset, 'spirituality')
            assert hasattr(preset, 'technicality')
            assert hasattr(preset, 'patience')
            
            # Check trait values are in valid range
            for attr in ['verbosity', 'emotiveness', 'formality', 'encouragement',
                        'playfulness', 'spirituality', 'technicality', 'patience']:
                value = getattr(preset, attr)
                assert 0.0 <= value <= 1.0


class TestPersonalityManager:
    """Test personality management and adaptation"""
    
    def test_initialization(self):
        """Test default initialization"""
        pm = PersonalityManager()
        assert pm.get_current_style() == PersonalityStyle.FRIENDLY
        
    def test_style_switching(self):
        """Test manual style switching"""
        pm = PersonalityManager()
        
        for style in PersonalityStyle:
            pm.set_style(style)
            assert pm.get_current_style() == style
            
    def test_response_generation(self):
        """Test response generation for each style"""
        pm = PersonalityManager()
        
        # Test each style generates appropriate responses
        style_expectations = {
            PersonalityStyle.MINIMAL: "Done.",
            PersonalityStyle.FRIENDLY: "done!",
            PersonalityStyle.ENCOURAGING: "Great",
            PersonalityStyle.PLAYFUL: "🎉",
            PersonalityStyle.SACRED: "✨",
            PersonalityStyle.PROFESSIONAL: "complete",
            PersonalityStyle.TEACHER: "Let",
            PersonalityStyle.COMPANION: "together",
            PersonalityStyle.HACKER: "pwn",
            PersonalityStyle.ZEN: "Complete"
        }
        
        for style, expected_word in style_expectations.items():
            pm.set_style(style)
            response = pm.get_response('success')
            # Check that response contains style-appropriate content
            if style in [PersonalityStyle.PLAYFUL, PersonalityStyle.SACRED]:
                # These styles use emojis
                assert any(ord(c) > 127 for c in response) or expected_word in response
            else:
                assert expected_word in response or response.endswith('.')
                
    def test_adaptive_learning(self):
        """Test personality adaptation from interactions"""
        pm = PersonalityManager()
        pm.set_style(PersonalityStyle.FRIENDLY)
        
        # Simulate frustrated user - should become more encouraging
        initial_encouragement = pm.current_traits.encouragement
        pm.learn_from_interaction(
            "this isn't working", 
            response_accepted=False,
            emotional_state='frustrated'
        )
        assert pm.current_traits.encouragement > initial_encouragement
        
        # Simulate fast user - should become more minimal
        initial_verbosity = pm.current_traits.verbosity
        pm.learn_from_interaction(
            "install firefox",
            response_accepted=True,
            interaction_speed='fast'
        )
        assert pm.current_traits.verbosity < initial_verbosity
        
    def test_language_detection(self):
        """Test style detection from user language"""
        pm = PersonalityManager()
        
        # Technical language should increase technicality
        initial_tech = pm.current_traits.technicality
        pm.learn_from_interaction("install package", True)
        assert pm.current_traits.technicality > initial_tech
        
        # Polite language should increase friendliness
        initial_emotive = pm.current_traits.emotiveness
        pm.learn_from_interaction("could you please help me", True)
        assert pm.current_traits.emotiveness > initial_emotive
        
        # Playful language should increase playfulness
        initial_playful = pm.current_traits.playfulness
        pm.learn_from_interaction("let's have some fun! 😊", True)
        assert pm.current_traits.playfulness > initial_playful
        
    def test_trait_persistence(self):
        """Test import/export of personality traits"""
        pm = PersonalityManager()
        pm.set_style(PersonalityStyle.HACKER)
        
        # Modify some traits
        pm._adjust_trait('verbosity', 0.2)
        pm._adjust_trait('technicality', -0.1)
        
        # Export traits
        exported = pm.export_traits()
        assert exported['style'] == 'hacker'
        assert 'traits' in exported
        
        # Create new manager and import
        pm2 = PersonalityManager()
        pm2.import_traits(exported)
        
        assert pm2.get_current_style() == PersonalityStyle.HACKER
        assert abs(pm2.current_traits.verbosity - pm.current_traits.verbosity) < 0.01
        
    def test_style_descriptions(self):
        """Test that all styles have descriptions"""
        pm = PersonalityManager()
        
        for style in PersonalityStyle:
            pm.set_style(style)
            description = pm.get_style_description()
            assert description != "Unknown style"
            assert style.value in description.lower()
            
    def test_learning_toggle(self):
        """Test enabling/disabling adaptive learning"""
        pm = PersonalityManager()
        
        # Disable learning
        pm.set_learning_enabled(False)
        initial_traits = pm.current_traits.verbosity
        
        pm.learn_from_interaction("be minimal", True, interaction_speed='fast')
        assert pm.current_traits.verbosity == initial_traits  # No change
        
        # Enable learning
        pm.set_learning_enabled(True)
        pm.learn_from_interaction("be minimal", True, interaction_speed='fast')
        assert pm.current_traits.verbosity < initial_traits  # Changed
        
    def test_personality_boundaries(self):
        """Test that traits stay within valid bounds"""
        pm = PersonalityManager()
        
        # Try to push traits beyond bounds
        for _ in range(20):
            pm._adjust_trait('verbosity', 0.1)
            pm._adjust_trait('emotiveness', -0.1)
            
        # Check bounds are respected
        assert pm.current_traits.verbosity <= 1.0
        assert pm.current_traits.emotiveness >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])