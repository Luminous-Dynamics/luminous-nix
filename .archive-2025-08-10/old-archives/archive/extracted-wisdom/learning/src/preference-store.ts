// Store and retrieve user preferences
import type { UserPreferences } from '@nix-humanity/core';

export class PreferenceStore {
  private preferences: Map<string, any> = new Map();

  async get(key: string): Promise<any> {
    return this.preferences.get(key);
  }

  async set(key: string, value: any): Promise<void> {
    this.preferences.set(key, value);
  }

  async getAll(): Promise<UserPreferences> {
    return {
      personalityStyle: this.preferences.get('personalityStyle') || 'friendly',
      commandHistory: this.preferences.get('commandHistory') || [],
      aliases: this.preferences.get('aliases') || {}
    };
  }

  async updateCommandHistory(command: string): Promise<void> {
    const history = this.preferences.get('commandHistory') || [];
    history.push(command);
    // Keep last 100 commands
    if (history.length > 100) {
      history.shift();
    }
    this.preferences.set('commandHistory', history);
  }
}

export { PreferenceStore as default };