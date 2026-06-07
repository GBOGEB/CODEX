export class JobQueue<T> {
  private readonly items: T[] = [];

  enqueue(job: T): number {
    this.items.push(job);
    return this.items.length;
  }

  dequeue(): T | undefined {
    return this.items.shift();
  }

  get length(): number {
    return this.items.length;
  }
}
