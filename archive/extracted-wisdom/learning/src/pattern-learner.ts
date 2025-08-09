// Learn patterns from user interactions

export class PatternLearner {
  private patterns: Map<string, PatternData> = new Map();

  async recordPattern(input: string, result: string, success: boolean): Promise<void> {
    const key = this.generatePatternKey(input);
    const existing = this.patterns.get(key) || {
      count: 0,
      successRate: 0,
      lastUsed: new Date()
    };

    existing.count++;
    existing.successRate = (existing.successRate * (existing.count - 1) + (success ? 1 : 0)) / existing.count;
    existing.lastUsed = new Date();

    this.patterns.set(key, existing);
  }

  async getSuggestion(input: string): Promise<string | null> {
    const key = this.generatePatternKey(input);
    const pattern = this.patterns.get(key);

    if (pattern && pattern.count > 3 && pattern.successRate > 0.8) {
      return `Based on your history, you might want to...`;
    }

    return null;
  }

  private generatePatternKey(input: string): string {
    // Simple pattern key generation
    return input.toLowerCase().split(' ').slice(0, 2).join('-');
  }
}

interface PatternData {
  count: number;
  successRate: number;
  lastUsed: Date;
}

export { PatternLearner as default };