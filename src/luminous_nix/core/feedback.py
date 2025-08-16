"""Feedback collection module."""

class FeedbackCollector:
    """Collect user feedback."""
    
    def __init__(self):
        self.feedback = []
    
    def collect(self, feedback):
        self.feedback.append(feedback)
    
    def get_all(self):
        return self.feedback
