"""Mock trust metrics for testing without numpy"""

class TrustMetrics:
    """Simplified trust metrics without numpy dependency"""
    
    def __init__(self):
        self.vulnerability_score = 0.7
        self.consistency_score = 0.8
        self.transparency_score = 0.9
        
    def calculate_overall_trust(self):
        """Simple average calculation"""
        scores = [self.vulnerability_score, self.consistency_score, self.transparency_score]
        return sum(scores) / len(scores)
        
    def to_dict(self):
        return {
            "vulnerability": self.vulnerability_score,
            "consistency": self.consistency_score,
            "transparency": self.transparency_score,
            "overall": self.calculate_overall_trust()
        }
