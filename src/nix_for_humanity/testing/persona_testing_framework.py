# src/nix_for_humanity/testing/persona_testing_framework.py
"""
Real-World Persona Testing Framework

This module provides comprehensive testing scenarios for all 10 core personas,
validating that the voice interaction system works authentically for each user type.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import json
import logging
from pathlib import Path

from ..integration.voice_interaction_orchestrator import VoiceInteractionOrchestrator
from ..learning.user_model import UserModel
from ..nlp.intent_engine import IntentEngine
from ..core.types import TestResult, PersonaProfile


logger = logging.getLogger(__name__)


class TestCategory(Enum):
    """Categories of tests for comprehensive validation."""
    FIRST_TIME_USE = auto()        # Initial experience
    ROUTINE_TASKS = auto()         # Common operations
    ERROR_RECOVERY = auto()        # Handling mistakes
    COMPLEX_WORKFLOWS = auto()     # Multi-step processes
    ACCESSIBILITY = auto()         # Special needs
    PERFORMANCE = auto()           # Speed and efficiency
    INTERRUPTION_HANDLING = auto() # Flow state protection
    REPAIR_SCENARIOS = auto()      # Conversational repair


class TestOutcome(Enum):
    """Possible outcomes of persona tests."""
    SUCCESS = auto()               # Task completed successfully
    PARTIAL_SUCCESS = auto()       # Task completed with assistance
    FAILURE = auto()               # Task failed
    ABANDONED = auto()             # User gave up
    CONFUSION = auto()             # System didn't understand


@dataclass
class PersonaTestScenario:
    """Individual test scenario for a persona."""
    name: str
    description: str
    category: TestCategory
    persona_id: str
    user_inputs: List[str]
    expected_outcomes: List[str]
    success_criteria: Dict[str, Any]
    timeout_seconds: int = 30
    requires_voice: bool = True
    setup_commands: List[str] = field(default_factory=list)
    cleanup_commands: List[str] = field(default_factory=list)


@dataclass
class TestExecution:
    """Results from executing a test scenario."""
    scenario: PersonaTestScenario
    start_time: datetime
    end_time: Optional[datetime] = None
    outcome: Optional[TestOutcome] = None
    actual_responses: List[str] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    user_satisfaction_score: Optional[float] = None
    accessibility_violations: List[str] = field(default_factory=list)
    interruptions_count: int = 0
    repair_attempts: int = 0
    final_notes: str = ""


class PersonaProfiles:
    """Detailed profiles for all 10 core personas."""
    
    PROFILES = {
        "grandma_rose": PersonaProfile(
            id="grandma_rose",
            name="Grandma Rose",
            age=75,
            tech_comfort="beginner",
            primary_needs=["simple_language", "patience", "voice_first"],
            disabilities=["mild_hearing_loss", "arthritis"],
            preferred_interaction_style="gentle_conversational",
            max_response_time=3.0,
            typical_commands=[
                "I need that Firefox thing my grandson mentioned",
                "How do I get my emails?",
                "The computer is being slow again",
                "Can you help me with the internet?"
            ],
            stress_triggers=["technical_jargon", "time_pressure", "complex_steps"],
            success_indicators=["feels_supported", "task_completed", "confidence_maintained"]
        ),
        
        "maya_adhd": PersonaProfile(
            id="maya_adhd",
            name="Maya (ADHD)",
            age=16,
            tech_comfort="intermediate",
            primary_needs=["speed", "minimal_text", "clear_progress"],
            disabilities=["ADHD", "working_memory_challenges"],
            preferred_interaction_style="fast_direct",
            max_response_time=1.0,
            typical_commands=[
                "firefox now",
                "install discord",
                "update everything",
                "fix wifi"
            ],
            stress_triggers=["long_explanations", "delays", "too_many_options"],
            success_indicators=["task_done_quickly", "stayed_focused", "no_frustration"]
        ),
        
        "david_tired_parent": PersonaProfile(
            id="david_tired_parent",
            name="David (Tired Parent)",
            age=42,
            tech_comfort="intermediate",
            primary_needs=["reliability", "clear_instructions", "error_prevention"],
            disabilities=["chronic_fatigue", "time_constraints"],
            preferred_interaction_style="patient_helpful",
            max_response_time=2.0,
            typical_commands=[
                "I need to install something for my kid's school project",
                "Why isn't this working? I don't have time for this",
                "Just tell me what to click",
                "Is there an easier way to do this?"
            ],
            stress_triggers=["unexpected_errors", "time_waste", "complex_debugging"],
            success_indicators=["no_additional_problems", "clear_next_steps", "confidence_restored"]
        ),
        
        "dr_sarah": PersonaProfile(
            id="dr_sarah",
            name="Dr. Sarah (Researcher)",
            age=35,
            tech_comfort="advanced",
            primary_needs=["precision", "technical_details", "efficiency"],
            disabilities=[],
            preferred_interaction_style="technical_precise",
            max_response_time=1.5,
            typical_commands=[
                "Install R with these specific packages for statistical analysis",
                "Configure LaTeX environment for academic papers",
                "Set up reproducible research environment",
                "I need Python 3.11 with numpy, scipy, and matplotlib"
            ],
            stress_triggers=["imprecise_information", "missing_details", "version_conflicts"],
            success_indicators=["exact_requirements_met", "technical_accuracy", "workflow_integration"]
        ),
        
        "alex_blind": PersonaProfile(
            id="alex_blind",
            name="Alex (Blind Developer)",
            age=28,
            tech_comfort="expert",
            primary_needs=["screen_reader_compatibility", "keyboard_navigation", "clear_structure"],
            disabilities=["blindness"],
            preferred_interaction_style="structured_descriptive",
            max_response_time=2.0,
            typical_commands=[
                "Install neovim with my usual plugins",
                "Set up development environment for Rust project",
                "Configure screen reader friendly terminal",
                "What keyboard shortcuts are available?"
            ],
            stress_triggers=["visual_only_feedback", "unclear_navigation", "missing_alt_text"],
            success_indicators=["fully_accessible", "keyboard_efficient", "screen_reader_compatible"]
        ),
        
        "carlos_learner": PersonaProfile(
            id="carlos_learner",
            name="Carlos (Career Switcher)",
            age=52,
            tech_comfort="learning",
            primary_needs=["educational_guidance", "encouragement", "step_by_step"],
            disabilities=[],
            preferred_interaction_style="encouraging_educational",
            max_response_time=2.5,
            typical_commands=[
                "I'm trying to learn programming, what do I need?",
                "Can you explain what this error means?",
                "What's the difference between these options?",
                "I want to understand how this works"
            ],
            stress_triggers=["assumed_knowledge", "patronizing_tone", "overwhelming_information"],
            success_indicators=["learned_something", "feels_capable", "motivated_to_continue"]
        ),
        
        "priya_single_mom": PersonaProfile(
            id="priya_single_mom",
            name="Priya (Single Mom)",
            age=34,
            tech_comfort="intermediate",
            primary_needs=["quick_solutions", "context_awareness", "interruption_handling"],
            disabilities=["time_constraints", "frequent_interruptions"],
            preferred_interaction_style="efficient_understanding",
            max_response_time=2.0,
            typical_commands=[
                "I need to install video calling for work meetings",
                "Can you help me quickly? Kids need dinner",
                "Remember I was trying to set up that work thing?",
                "Something broke, I need to fix it fast"
            ],
            stress_triggers=["long_processes", "losing_progress", "complex_setup"],
            success_indicators=["quick_resolution", "resumed_progress", "handled_interruptions"]
        ),
        
        "jamie_privacy": PersonaProfile(
            id="jamie_privacy",
            name="Jamie (Privacy Advocate)",
            age=19,
            tech_comfort="advanced",
            primary_needs=["transparency", "privacy_protection", "control"],
            disabilities=[],
            preferred_interaction_style="transparent_respectful",
            max_response_time=1.5,
            typical_commands=[
                "What data are you collecting about me?",
                "Install privacy-focused browser with ad blocking",
                "Show me exactly what this command does",
                "I want to review all settings before applying"
            ],
            stress_triggers=["hidden_operations", "data_collection", "lack_of_control"],
            success_indicators=["full_transparency", "privacy_respected", "user_in_control"]
        ),
        
        "viktor_esl": PersonaProfile(
            id="viktor_esl",
            name="Viktor (ESL)",
            age=67,
            tech_comfort="beginner",
            primary_needs=["simple_english", "clear_pronunciation", "patience"],
            disabilities=["English_as_second_language", "cultural_differences"],
            preferred_interaction_style="clear_patient",
            max_response_time=3.0,
            typical_commands=[
                "I want program for write letters",
                "Computer not work good, please help",
                "How I make video call to family?",
                "Please speak slow, I learn English"
            ],
            stress_triggers=["complex_grammar", "idioms", "fast_speech"],
            success_indicators=["understood_clearly", "task_completed", "cultural_respect"]
        ),
        
        "luna_autistic": PersonaProfile(
            id="luna_autistic",
            name="Luna (Autistic)",
            age=14,
            tech_comfort="intermediate",
            primary_needs=["predictability", "clear_patterns", "sensory_consideration"],
            disabilities=["autism", "sensory_sensitivities"],
            preferred_interaction_style="consistent_structured",
            max_response_time=2.0,
            typical_commands=[
                "Install Minecraft with the same settings as last time",
                "I need everything to be exactly like before",
                "Can you use the same words you used yesterday?",
                "Please don't change how you say things"
            ],
            stress_triggers=["unexpected_changes", "inconsistent_responses", "sensory_overload"],
            success_indicators=["consistent_experience", "predictable_patterns", "sensory_comfort"]
        )
    }


class PersonaTestSuite:
    """Comprehensive test suite for persona validation."""
    
    def __init__(self):
        self.scenarios = self._create_test_scenarios()
        
    def _create_test_scenarios(self) -> Dict[str, List[PersonaTestScenario]]:
        """Create comprehensive test scenarios for each persona."""
        scenarios = {}
        
        for persona_id in PersonaProfiles.PROFILES.keys():
            scenarios[persona_id] = self._create_persona_scenarios(persona_id)
            
        return scenarios
    
    def _create_persona_scenarios(self, persona_id: str) -> List[PersonaTestScenario]:
        """Create scenarios specific to a persona."""
        profile = PersonaProfiles.PROFILES[persona_id]
        scenarios = []
        
        # First-time use scenario
        scenarios.append(PersonaTestScenario(
            name=f"{profile.name} - First Time Use",
            description=f"Test {profile.name}'s first interaction with the system",
            category=TestCategory.FIRST_TIME_USE,
            persona_id=persona_id,
            user_inputs=self._get_first_time_inputs(persona_id),
            expected_outcomes=self._get_first_time_outcomes(persona_id),
            success_criteria={
                "response_time": profile.max_response_time,
                "completion_rate": 1.0,
                "satisfaction_min": 0.8,
                "accessibility_violations": 0
            }
        ))
        
        # Routine task scenario
        scenarios.append(PersonaTestScenario(
            name=f"{profile.name} - Routine Task",
            description=f"Test {profile.name} performing common tasks",
            category=TestCategory.ROUTINE_TASKS,
            persona_id=persona_id,
            user_inputs=profile.typical_commands[:2],
            expected_outcomes=self._get_routine_outcomes(persona_id),
            success_criteria={
                "response_time": profile.max_response_time,
                "completion_rate": 1.0,
                "efficiency_min": 0.9
            }
        ))
        
        # Error recovery scenario
        scenarios.append(PersonaTestScenario(
            name=f"{profile.name} - Error Recovery",
            description=f"Test {profile.name} recovering from mistakes",
            category=TestCategory.ERROR_RECOVERY,
            persona_id=persona_id,
            user_inputs=self._get_error_inputs(persona_id),
            expected_outcomes=self._get_error_outcomes(persona_id),
            success_criteria={
                "repair_success_rate": 0.9,
                "frustration_level": "low",
                "final_success": True
            }
        ))
        
        # Interruption handling (for applicable personas)
        if "interruptions" in profile.primary_needs or "time_constraints" in profile.disabilities:
            scenarios.append(PersonaTestScenario(
                name=f"{profile.name} - Interruption Handling",
                description=f"Test {profile.name} with interruptions",
                category=TestCategory.INTERRUPTION_HANDLING,
                persona_id=persona_id,
                user_inputs=self._get_interruption_inputs(persona_id),
                expected_outcomes=self._get_interruption_outcomes(persona_id),
                success_criteria={
                    "context_preserved": True,
                    "graceful_resume": True,
                    "minimal_frustration": True
                }
            ))
            
        return scenarios
    
    def _get_first_time_inputs(self, persona_id: str) -> List[str]:
        """Get first-time use inputs for persona."""
        inputs = {
            "grandma_rose": [
                "Hello, I'm new to this computer thing",
                "My grandson said you could help me",
                "I need to get on the internet to see pictures of my grandchildren"
            ],
            "maya_adhd": [
                "hey quick question",
                "need firefox asap",
                "done yet?"
            ],
            "david_tired_parent": [
                "Hi, I need to set up this computer for my kids",
                "I don't have much time so please be direct",
                "What's the easiest way to install educational software?"
            ],
            "dr_sarah": [
                "I need to configure a research environment",
                "Specifically R 4.3.2 with tidyverse and ggplot2",
                "Also LaTeX for manuscript preparation"
            ],
            "alex_blind": [
                "Testing screen reader compatibility",
                "I need clear navigation structure",
                "What keyboard shortcuts are available for quick actions?"
            ],
            "carlos_learner": [
                "I'm completely new to this Linux thing",
                "Can you explain what we're doing as we go?",
                "I want to learn programming but don't know where to start"
            ],
            "priya_single_mom": [
                "I need to set up video calling for work",
                "Something simple that works reliably",
                "I'll probably get interrupted by the kids"
            ],
            "jamie_privacy": [
                "Before we start, what data do you collect?",
                "I want privacy-focused alternatives for everything",
                "Show me exactly what each command does"
            ],
            "viktor_esl": [
                "Hello, please speak slow for me",
                "I need help with computer",
                "My English not so good but I try"
            ],
            "luna_autistic": [
                "I like when things are the same every time",
                "Can you always use the same words?",
                "I want to install Minecraft like my friend has"
            ]
        }
        return inputs.get(persona_id, ["Hello", "I need help", "Thank you"])
    
    def _get_first_time_outcomes(self, persona_id: str) -> List[str]:
        """Get expected outcomes for first-time use."""
        outcomes = {
            "grandma_rose": [
                "Welcome! I'd be happy to help you connect with your grandchildren.",
                "Let me guide you through getting Firefox set up for internet browsing.",
                "I'll explain each step clearly as we go."
            ],
            "maya_adhd": [
                "Got it! Installing Firefox now.",
                "Done! Firefox is ready.",
                "Anything else you need?"
            ],
            "david_tired_parent": [
                "I understand you're busy. Let's get this done efficiently.",
                "For kids' educational software, I recommend starting with these options...",
                "This will take about 5 minutes total."
            ],
            "dr_sarah": [
                "Setting up R 4.3.2 research environment.",
                "Installing tidyverse, ggplot2, and LaTeX packages.",
                "Configuration optimized for statistical analysis workflows."
            ],
            "alex_blind": [
                "Screen reader compatibility confirmed.",
                "Navigation: Tab for next option, Space to select, Escape to cancel.",
                "All functions accessible via keyboard shortcuts."
            ],
            "carlos_learner": [
                "Perfect! I love helping people learn.",
                "I'll explain what we're doing at each step.",
                "For programming, let's start with Python - it's great for beginners."
            ],
            "priya_single_mom": [
                "Setting up reliable video calling for work.",
                "I'll make this quick and simple.",
                "If you get interrupted, just say 'pause' and I'll wait."
            ],
            "jamie_privacy": [
                "I collect no personal data - everything stays on your computer.",
                "Installing privacy-focused alternatives: Firefox with uBlock Origin.",
                "Command preview: This installs Firefox browser package from nixpkgs."
            ],
            "viktor_esl": [
                "Hello Viktor! I will speak slowly and clearly.",
                "I am here to help you with your computer.",
                "What would you like to do today?"
            ],
            "luna_autistic": [
                "I'll always use the same words and patterns.",
                "Installing Minecraft with standard configuration.",
                "Everything will be consistent each time you ask."
            ]
        }
        return outcomes.get(persona_id, ["Hello", "I can help you", "Let's begin"])
    
    def _get_routine_outcomes(self, persona_id: str) -> List[str]:
        """Get expected outcomes for routine tasks."""
        profile = PersonaProfiles.PROFILES[persona_id]
        # Generate based on typical commands and persona needs
        return [f"Completing {cmd}" for cmd in profile.typical_commands[:2]]
    
    def _get_error_inputs(self, persona_id: str) -> List[str]:
        """Get error scenario inputs."""
        return [
            "install firefx",  # Typo
            "no that's wrong",  # Correction
            "I meant firefox"   # Clarification
        ]
    
    def _get_error_outcomes(self, persona_id: str) -> List[str]:
        """Get expected error recovery outcomes."""
        profile = PersonaProfiles.PROFILES[persona_id]
        if "gentle" in profile.preferred_interaction_style:
            return [
                "I think you meant Firefox - let me install that for you.",
                "No worries! I'll correct that.",
                "Perfect! Installing Firefox now."
            ]
        elif "fast" in profile.preferred_interaction_style:
            return [
                "Firefox? Installing.",
                "Fixed.",
                "Done."
            ]
        else:
            return [
                "Did you mean Firefox?",
                "Understood. Correcting now.",
                "Installing Firefox."
            ]
    
    def _get_interruption_inputs(self, persona_id: str) -> List[str]:
        """Get interruption scenario inputs."""
        return [
            "I need to install something for work",
            "[INTERRUPTION: Child needs attention]",
            "Sorry, I'm back. Where were we?"
        ]
    
    def _get_interruption_outcomes(self, persona_id: str) -> List[str]:
        """Get expected interruption handling outcomes."""
        return [
            "Setting up work software installation.",
            "I'll pause here and wait for you.",
            "Welcome back! We were installing work software. Ready to continue?"
        ]


class PersonaTestRunner:
    """Executes persona tests and collects results."""
    
    def __init__(self, voice_orchestrator: VoiceInteractionOrchestrator):
        self.orchestrator = voice_orchestrator
        self.test_suite = PersonaTestSuite()
        self.results: List[TestExecution] = []
        
    async def run_all_tests(self) -> Dict[str, List[TestExecution]]:
        """Run all persona tests."""
        results = {}
        
        for persona_id, scenarios in self.test_suite.scenarios.items():
            logger.info(f"Testing persona: {persona_id}")
            persona_results = []
            
            for scenario in scenarios:
                result = await self.run_single_test(scenario)
                persona_results.append(result)
                
            results[persona_id] = persona_results
            
        return results
    
    async def run_persona_tests(self, persona_id: str) -> List[TestExecution]:
        """Run tests for a specific persona."""
        if persona_id not in self.test_suite.scenarios:
            raise ValueError(f"Unknown persona: {persona_id}")
            
        scenarios = self.test_suite.scenarios[persona_id]
        results = []
        
        for scenario in scenarios:
            result = await self.run_single_test(scenario)
            results.append(result)
            
        return results
    
    async def run_single_test(self, scenario: PersonaTestScenario) -> TestExecution:
        """Run a single test scenario."""
        logger.info(f"Running test: {scenario.name}")
        
        execution = TestExecution(
            scenario=scenario,
            start_time=datetime.now()
        )
        
        try:
            # Setup persona in user model
            await self._setup_persona(scenario.persona_id)
            
            # Run setup commands
            for cmd in scenario.setup_commands:
                await self._execute_command(cmd)
                
            # Execute test inputs
            for i, user_input in enumerate(scenario.user_inputs):
                start_time = datetime.now()
                
                # Handle special inputs like interruptions
                if "[INTERRUPTION:" in user_input:
                    await self._simulate_interruption(user_input)
                    continue
                    
                # Normal input
                await self.orchestrator._handle_user_speech(user_input)
                
                # Wait for response
                await self._wait_for_response(scenario.timeout_seconds)
                
                # Record timing
                response_time = (datetime.now() - start_time).total_seconds()
                execution.response_times.append(response_time)
                
                # Get AI response
                last_response = self._get_last_ai_response()
                if last_response:
                    execution.actual_responses.append(last_response)
                    
            # Evaluate results
            execution.outcome = self._evaluate_test_outcome(execution)
            execution.user_satisfaction_score = self._calculate_satisfaction(execution)
            
            # Check accessibility
            execution.accessibility_violations = self._check_accessibility(execution)
            
        except Exception as e:
            execution.errors.append(str(e))
            execution.outcome = TestOutcome.FAILURE
            logger.error(f"Test failed: {e}")
            
        finally:
            # Cleanup
            for cmd in scenario.cleanup_commands:
                await self._execute_command(cmd)
                
            execution.end_time = datetime.now()
            
        return execution
    
    async def _setup_persona(self, persona_id: str):
        """Configure system for specific persona."""
        profile = PersonaProfiles.PROFILES[persona_id]
        
        # Update user model
        self.orchestrator.user_model.set_current_persona(persona_id)
        self.orchestrator.user_model.update_preferences({
            'interaction_style': profile.preferred_interaction_style,
            'max_response_time': profile.max_response_time,
            'accessibility_needs': profile.disabilities
        })
        
        # Update voice settings
        await self.orchestrator.voice_interface.configure_for_persona(profile)
        
    async def _execute_command(self, command: str):
        """Execute a setup/cleanup command."""
        # This would integrate with your command execution system
        logger.debug(f"Executing command: {command}")
        
    async def _simulate_interruption(self, interruption_text: str):
        """Simulate an interruption scenario."""
        # Extract interruption type
        interruption_type = interruption_text.split(":")[1].split("]")[0].strip()
        
        # Update context to show interruption
        self.orchestrator.context.current_state = InteractionState.INTERRUPTED
        
        # Wait to simulate interruption duration
        await asyncio.sleep(2)
        
        logger.debug(f"Simulated interruption: {interruption_type}")
        
    async def _wait_for_response(self, timeout_seconds: int):
        """Wait for AI response with timeout."""
        end_time = datetime.now() + timedelta(seconds=timeout_seconds)
        
        while datetime.now() < end_time:
            if self.orchestrator.context.current_state == InteractionState.IDLE:
                return
            await asyncio.sleep(0.1)
            
        # Timeout reached
        logger.warning(f"Response timeout after {timeout_seconds} seconds")
        
    def _get_last_ai_response(self) -> Optional[str]:
        """Get the last AI response from conversation history."""
        history = self.orchestrator.context.conversation_context.history
        
        for turn in reversed(history):
            if turn.speaker == 'ai':
                return turn.content
                
        return None
        
    def _evaluate_test_outcome(self, execution: TestExecution) -> TestOutcome:
        """Evaluate whether test succeeded."""
        scenario = execution.scenario
        
        # Check response times
        max_time = max(execution.response_times) if execution.response_times else 0
        if max_time > scenario.success_criteria.get('response_time', 5.0):
            return TestOutcome.PARTIAL_SUCCESS
            
        # Check completion
        if len(execution.actual_responses) < len(scenario.expected_outcomes):
            return TestOutcome.FAILURE
            
        # Check for errors
        if execution.errors:
            return TestOutcome.PARTIAL_SUCCESS
            
        return TestOutcome.SUCCESS
        
    def _calculate_satisfaction(self, execution: TestExecution) -> float:
        """Calculate user satisfaction score."""
        profile = PersonaProfiles.PROFILES[execution.scenario.persona_id]
        score = 1.0
        
        # Response time penalty
        avg_response_time = sum(execution.response_times) / len(execution.response_times) if execution.response_times else 0
        if avg_response_time > profile.max_response_time:
            score -= 0.2
            
        # Error penalty
        if execution.errors:
            score -= 0.3
            
        # Repair penalty (too many repairs indicates poor understanding)
        if execution.repair_attempts > 2:
            score -= 0.2
            
        # Accessibility penalty
        if execution.accessibility_violations:
            score -= 0.4
            
        return max(0.0, score)
        
    def _check_accessibility(self, execution: TestExecution) -> List[str]:
        """Check for accessibility violations."""
        violations = []
        profile = PersonaProfiles.PROFILES[execution.scenario.persona_id]
        
        # Check for persona-specific accessibility needs
        if "blindness" in profile.disabilities:
            # Should have clear structure and navigation
            if not self._has_clear_navigation():
                violations.append("Missing clear navigation structure")
                
        if "hearing_loss" in profile.disabilities:
            # Should have visual indicators
            if not self._has_visual_indicators():
                violations.append("Missing visual feedback")
                
        if "ADHD" in profile.disabilities:
            # Should have minimal distractions
            avg_response_time = sum(execution.response_times) / len(execution.response_times) if execution.response_times else 0
            if avg_response_time > 1.0:
                violations.append("Response too slow for ADHD user")
                
        return violations
        
    def _has_clear_navigation(self) -> bool:
        """Check if system provides clear navigation."""
        # This would check actual interface state
        return True  # Placeholder
        
    def _has_visual_indicators(self) -> bool:
        """Check if system provides visual feedback."""
        # This would check actual interface state
        return True  # Placeholder


class PersonaTestReporter:
    """Generates comprehensive test reports."""
    
    def __init__(self):
        self.report_dir = Path("test_reports/persona_tests")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_report(self, test_results: Dict[str, List[TestExecution]]) -> str:
        """Generate comprehensive test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"persona_test_report_{timestamp}.html"
        
        html_content = self._generate_html_report(test_results)
        
        with open(report_file, 'w') as f:
            f.write(html_content)
            
        # Also generate JSON for programmatic access
        json_file = self.report_dir / f"persona_test_data_{timestamp}.json"
        self._generate_json_report(test_results, json_file)
        
        return str(report_file)
        
    def _generate_html_report(self, results: Dict[str, List[TestExecution]]) -> str:
        """Generate HTML report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Persona Testing Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .persona { margin-bottom: 30px; border: 1px solid #ccc; padding: 15px; }
                .success { background-color: #d4edda; }
                .partial { background-color: #fff3cd; }
                .failure { background-color: #f8d7da; }
                .metrics { display: flex; gap: 20px; }
                .metric { text-align: center; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Persona Testing Report</h1>
            <p>Generated: {timestamp}</p>
        """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Summary metrics
        html += self._generate_summary_section(results)
        
        # Individual persona results
        for persona_id, executions in results.items():
            html += self._generate_persona_section(persona_id, executions)
            
        html += """
        </body>
        </html>
        """
        
        return html
        
    def _generate_summary_section(self, results: Dict[str, List[TestExecution]]) -> str:
        """Generate summary metrics section."""
        total_tests = sum(len(executions) for executions in results.values())
        successful_tests = sum(
            len([e for e in executions if e.outcome == TestOutcome.SUCCESS])
            for executions in results.values()
        )
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        return f"""
        <div class="summary">
            <h2>Summary</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>{total_tests}</h3>
                    <p>Total Tests</p>
                </div>
                <div class="metric">
                    <h3>{successful_tests}</h3>
                    <p>Successful</p>
                </div>
                <div class="metric">
                    <h3>{success_rate:.1f}%</h3>
                    <p>Success Rate</p>
                </div>
            </div>
        </div>
        """
        
    def _generate_persona_section(self, persona_id: str, executions: List[TestExecution]) -> str:
        """Generate section for individual persona."""
        profile = PersonaProfiles.PROFILES[persona_id]
        
        html = f"""
        <div class="persona">
            <h2>{profile.name} (Age {profile.age})</h2>
            <p><strong>Tech Comfort:</strong> {profile.tech_comfort}</p>
            <p><strong>Primary Needs:</strong> {', '.join(profile.primary_needs)}</p>
            <p><strong>Max Response Time:</strong> {profile.max_response_time}s</p>
            
            <h3>Test Results</h3>
            <table>
                <tr>
                    <th>Test</th>
                    <th>Outcome</th>
                    <th>Response Time</th>
                    <th>Satisfaction</th>
                    <th>Issues</th>
                </tr>
        """
        
        for execution in executions:
            outcome_class = execution.outcome.name.lower()
            avg_time = sum(execution.response_times) / len(execution.response_times) if execution.response_times else 0
            satisfaction = execution.user_satisfaction_score or 0
            issues = len(execution.errors) + len(execution.accessibility_violations)
            
            html += f"""
                <tr class="{outcome_class}">
                    <td>{execution.scenario.name}</td>
                    <td>{execution.outcome.name}</td>
                    <td>{avg_time:.2f}s</td>
                    <td>{satisfaction:.2f}</td>
                    <td>{issues}</td>
                </tr>
            """
            
        html += """
            </table>
        </div>
        """
        
        return html
        
    def _generate_json_report(self, results: Dict[str, List[TestExecution]], 
                             output_file: Path):
        """Generate JSON report for programmatic access."""
        json_data = {}
        
        for persona_id, executions in results.items():
            json_data[persona_id] = []
            
            for execution in executions:
                json_data[persona_id].append({
                    'scenario_name': execution.scenario.name,
                    'outcome': execution.outcome.name,
                    'response_times': execution.response_times,
                    'satisfaction_score': execution.user_satisfaction_score,
                    'errors': execution.errors,
                    'accessibility_violations': execution.accessibility_violations,
                    'duration': (execution.end_time - execution.start_time).total_seconds() if execution.end_time else None
                })
                
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)


# Example usage and test execution
async def main():
    """Example of running persona tests."""
    # This would be initialized with real components
    user_model = UserModel("test_user")
    nlp_engine = IntentEngine()
    orchestrator = VoiceInteractionOrchestrator(user_model, nlp_engine)
    
    # Create test runner
    test_runner = PersonaTestRunner(orchestrator)
    
    # Run tests for specific persona
    maya_results = await test_runner.run_persona_tests("maya_adhd")
    
    # Or run all tests
    all_results = await test_runner.run_all_tests()
    
    # Generate report
    reporter = PersonaTestReporter()
    report_file = reporter.generate_report(all_results)
    
    print(f"Test report generated: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())