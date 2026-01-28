// SocketCAN wrapper for J1939 communication
import { createRawChannel, RawChannel } from 'socketcan';

export interface CanFrame {
  id: number;
  data: Buffer;
  ext: boolean;  // Extended (29-bit) ID
}

export class CanBus {
  private channel: RawChannel | null = null;
  private readonly interfaceName: string;
  private messageHandler: ((frame: CanFrame) => void) | null = null;

  constructor(interfaceName: string = 'can0') {
    this.interfaceName = interfaceName;
  }

  connect(): void {
    try {
      this.channel = createRawChannel(this.interfaceName, true);  // true = timestamps

      this.channel.addListener('onMessage', (msg: { id: number; data: Buffer; ext: boolean }) => {
        if (this.messageHandler) {
          this.messageHandler({
            id: msg.id,
            data: msg.data,
            ext: msg.ext
          });
        }
      });

      this.channel.start();
    } catch (err) {
      throw new Error(
        `Failed to open CAN interface '${this.interfaceName}'. ` +
        `Make sure it exists and is up:\n` +
        `  sudo ip link set ${this.interfaceName} type can bitrate 250000\n` +
        `  sudo ip link set ${this.interfaceName} up`
      );
    }
  }

  disconnect(): void {
    if (this.channel) {
      this.channel.stop();
      this.channel = null;
    }
  }

  send(frame: CanFrame): void {
    if (!this.channel) {
      throw new Error('CAN bus not connected');
    }
    this.channel.send({
      id: frame.id,
      data: frame.data,
      ext: frame.ext
    });
  }

  onMessage(handler: (frame: CanFrame) => void): void {
    this.messageHandler = handler;
  }

  get isConnected(): boolean {
    return this.channel !== null;
  }
}
