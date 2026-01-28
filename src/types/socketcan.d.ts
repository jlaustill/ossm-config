declare module 'socketcan' {
  export interface RawChannel {
    addListener(event: 'onMessage', callback: (msg: { id: number; data: Buffer; ext: boolean }) => void): void;
    start(): void;
    stop(): void;
    send(msg: { id: number; data: Buffer; ext: boolean }): void;
  }

  export function createRawChannel(ifname: string, timestamps?: boolean): RawChannel;
}
