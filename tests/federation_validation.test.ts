import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, it } from 'node:test';

const repoRoot = join(__dirname, '..');

function loadSchema(name: 'federation.schema.json' | 'handover.schema.json') {
  return JSON.parse(readFileSync(join(repoRoot, 'schemas', name), 'utf8'));
}

describe('federation validation schemas', () => {
  it('federation.schema.json declares the federation manifest contract', () => {
    const schema = loadSchema('federation.schema.json');

    assert.equal(schema.$schema, 'https://json-schema.org/draft/2020-12/schema');
    assert.equal(schema.type, 'object');
    assert.ok(schema.required.includes('federation_id'));
    assert.ok(schema.required.includes('participants'));
    assert.ok(schema.required.includes('validation'));
  });

  it('handover.schema.json declares current handover status requirements', () => {
    const schema = loadSchema('handover.schema.json');

    assert.equal(schema.$schema, 'https://json-schema.org/draft/2020-12/schema');
    assert.equal(schema.type, 'object');
    assert.ok(schema.required.includes('wave'));
    assert.ok(schema.required.includes('status'));
    assert.ok(schema.required.includes('completed_tasks'));
  });
});
