export const eventBus = {
  handlers: new Map(),
  on(event, handler) { this.handlers.set(event, handler); },
  emit(event, payload) { const h = this.handlers.get(event); if (h) h(payload); }
};
