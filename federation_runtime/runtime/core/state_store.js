export const stateStore = {
  state: { slideIndex: 0 },
  set(partial) { this.state = { ...this.state, ...partial }; return this.state; },
  get() { return this.state; }
};
