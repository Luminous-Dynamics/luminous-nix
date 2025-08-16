"""Mock missing imports."""

class Command:
    def __init__(self, text="", context=None):
        self.text = text
        self.context = context or {}

class LearningMetrics:
    def __init__(self):
        self.accuracy = 0.95
        self.response_time = 0.1
        self.user_satisfaction = 0.9
