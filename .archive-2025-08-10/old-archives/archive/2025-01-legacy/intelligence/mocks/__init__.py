"""Mock implementations for testing without heavy dependencies."""

# REMOVED MOCK IMPORT: MockSymbioticKnowledgeGraph
# REMOVED MOCK IMPORT: MockTrustEngine
# REMOVED MOCK IMPORT: MockMetricsCollector


class MockActivityMonitor:
    """Mock activity monitor"""

    def __init__(self, skg=None):
        self.skg = skg
        self.enabled = False

    def get_current_context(self):
        return {"apps": [], "focus_app": None}


class MockConsciousnessGuard:
    """Mock consciousness guard"""

    def __init__(self):
        self.active = True

    def sacred_context(self, intention=""):
        class MockContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return MockContext()


class MockSacredMetricsCollector:
    """Mock sacred metrics collector"""

    def __init__(self, skg=None):
        self.skg = skg

    def collect_current_metrics(self, session_data):
        from types import SimpleNamespace

        return SimpleNamespace(
            wellbeing_score=0.75,
            attention_state=SimpleNamespace(value="focused"),
            flow_state=True,
        )


__all__ = [
    "MockSymbioticKnowledgeGraph",
    "MockTrustEngine",
    "MockMetricsCollector",
    "MockActivityMonitor",
    "MockConsciousnessGuard",
    "MockSacredMetricsCollector",
]
