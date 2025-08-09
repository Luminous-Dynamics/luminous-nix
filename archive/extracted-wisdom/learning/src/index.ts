// @nix-humanity/learning - User preference learning system

import type { UserPreferences } from '@nix-humanity/core';

export class LearningSystem {
  async recordInteraction(command: string, success: boolean): Promise<void> {
    // TODO: Implement learning
  }
  
  async getPreferences(): Promise<UserPreferences> {
    // TODO: Implement preference retrieval
    throw new Error('Not implemented yet');
  }
}

export { PreferenceStore } from './preference-store';
export { PatternLearner } from './pattern-learner';
