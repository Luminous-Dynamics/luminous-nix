import { test } from 'node:test';
import assert from 'node:assert';

test('learning module exports', async () => {
  const module = await import('../dist/index.js');
  assert.ok(module, 'Module should export something');
});
