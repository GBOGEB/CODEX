export const eventBus = {
  handlers: new Map(),
  on(event, handler) {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.push(handler);
    } else {
      this.handlers.set(event, [handler]);
    }
  },
  emit(event, payload) {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.forEach((handler) => handler(payload));
    }
  }
};
