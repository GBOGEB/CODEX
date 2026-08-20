import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { JobQueue } from '../src/job_queue';

describe('JobQueue', () => {
  it('enqueue appends jobs and reports queue length', () => {
    const queue = new JobQueue<string>();

    assert.equal(queue.enqueue('render-federation'), 1);
    assert.equal(queue.enqueue('validate-handover'), 2);
    assert.equal(queue.length, 2);
  });

  it('dequeue returns jobs in FIFO order', () => {
    const queue = new JobQueue<string>();

    queue.enqueue('first');
    queue.enqueue('second');

    assert.equal(queue.dequeue(), 'first');
    assert.equal(queue.dequeue(), 'second');
    assert.equal(queue.length, 0);
  });

  it('empty queue returns undefined when dequeued', () => {
    const queue = new JobQueue<string>();

    assert.equal(queue.dequeue(), undefined);
    assert.equal(queue.length, 0);
  });
});
