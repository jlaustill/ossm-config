// J1939 protocol encoding/decoding for OSSM communication
import { CanBus, CanFrame } from '../can/socketcan';

// OSSM proprietary PGNs
const PGN_COMMAND = 65280;   // 0xFF00 - Commands TO OSSM
const PGN_RESPONSE = 65281;  // 0xFF01 - Responses FROM OSSM

// Standard J1939 PGNs for sensor data
export const PGN = {
  ENGINE_TEMP_1: 65262,      // 0xFEEE - Coolant, fuel, oil temps
  ENGINE_FLUID_PRESS: 65263, // 0xFEEF - Fuel, oil, coolant pressures
  AMBIENT_COND: 65269,       // 0xFEF5 - Baro, ambient temp
  INLET_EXHAUST: 65270,      // 0xFEF6 - Air inlet, EGT, boost
  ENGINE_TEMP_2: 65129,      // 0xFE69 - Additional temps
  TURBO_INFO_1: 65189,       // 0xFEA5 - Turbo temps
  TURBO_INFO_2: 65190,       // 0xFEA6 - Turbo pressures
  EEC6: 65164,               // 0xFE8C - Engine bay temp, humidity
};

// Command IDs
export const CMD = {
  ENABLE_SPN: 1,
  SET_PRESSURE_RANGE: 3,
  SET_TC_TYPE: 4,
  QUERY: 5,
  SAVE: 6,
  RESET: 7,
  NTC_PRESET: 8,
  PRESSURE_PRESET: 9,
};

// Default OSSM source address
const OSSM_SOURCE_ADDRESS = 149;  // 0x95

export interface SensorData {
  // Temperatures (Celsius)
  coolantTemp?: number;
  fuelTemp?: number;
  oilTemp?: number;
  ambientTemp?: number;
  airInletTemp?: number;
  egtTemp?: number;
  boostTemp?: number;
  cacInletTemp?: number;
  transferPipeTemp?: number;
  engineBayTemp?: number;

  // Pressures (kPa)
  oilPressure?: number;
  fuelPressure?: number;
  coolantPressure?: number;
  boostPressure?: number;
  airInletPressure?: number;
  cacInletPressure?: number;

  // Ambient
  barometricPressure?: number;
  humidity?: number;
}

export class J1939Protocol {
  private can: CanBus;
  private responseResolve: ((data: Buffer) => void) | null = null;
  private sensorData: SensorData = {};
  private sensorHandler: ((data: SensorData) => void) | null = null;

  constructor(can: CanBus) {
    this.can = can;
    this.can.onMessage(this.handleFrame.bind(this));
  }

  private handleFrame(frame: CanFrame): void {
    if (!frame.ext) return;  // J1939 uses extended IDs

    const pgn = this.extractPgn(frame.id);
    const sourceAddr = frame.id & 0xFF;

    // Only process frames from OSSM
    if (sourceAddr !== OSSM_SOURCE_ADDRESS) return;

    // Handle command response
    if (pgn === PGN_RESPONSE && this.responseResolve) {
      this.responseResolve(frame.data);
      this.responseResolve = null;
      return;
    }

    // Handle sensor data PGNs
    this.decodeSensorData(pgn, frame.data);
  }

  private extractPgn(canId: number): number {
    // J1939 PGN is in bits 8-25 of the 29-bit ID
    const pf = (canId >> 16) & 0xFF;  // PDU Format
    const ps = (canId >> 8) & 0xFF;   // PDU Specific

    if (pf >= 240) {
      // PDU2 format: PGN = PF * 256 + PS
      return (pf << 8) | ps;
    } else {
      // PDU1 format: PGN = PF * 256
      return pf << 8;
    }
  }

  private buildCanId(pgn: number, sourceAddr: number = 0xFE, priority: number = 6): number {
    // Build 29-bit J1939 CAN ID
    return (priority << 26) | (pgn << 8) | sourceAddr;
  }

  private decodeSensorData(pgn: number, data: Buffer): void {
    switch (pgn) {
      case PGN.ENGINE_TEMP_1:
        // Byte 0: Coolant temp (offset -40)
        // Byte 2: Fuel temp (offset -40)
        // Byte 3: Oil temp (offset -40)
        if (data[0] !== 0xFF) this.sensorData.coolantTemp = data[0] - 40;
        if (data[2] !== 0xFF) this.sensorData.fuelTemp = data[2] - 40;
        if (data[3] !== 0xFF) this.sensorData.oilTemp = data[3] - 40;
        break;

      case PGN.ENGINE_FLUID_PRESS:
        // Byte 0-1: Fuel delivery pressure (4 kPa/bit)
        // Byte 3: Oil pressure (4 kPa/bit)
        // Byte 4: Coolant pressure (2 kPa/bit)
        if (data[3] !== 0xFF) this.sensorData.oilPressure = data[3] * 4;
        if (data[4] !== 0xFF) this.sensorData.coolantPressure = data[4] * 2;
        const fuelPress = data[0] | (data[1] << 8);
        if (fuelPress !== 0xFFFF) this.sensorData.fuelPressure = fuelPress * 4;
        break;

      case PGN.AMBIENT_COND:
        // Byte 0: Barometric pressure (0.5 kPa/bit)
        // Byte 3-4: Ambient temp (0.03125 C/bit, offset -273)
        if (data[0] !== 0xFF) this.sensorData.barometricPressure = data[0] * 0.5;
        const ambientRaw = data[3] | (data[4] << 8);
        if (ambientRaw !== 0xFFFF) this.sensorData.ambientTemp = ambientRaw * 0.03125 - 273;
        break;

      case PGN.INLET_EXHAUST:
        // Byte 1: Boost pressure (2 kPa/bit)
        // Byte 2-3: EGT (0.03125 C/bit, offset -273)
        // Byte 4: Air inlet temp (offset -40)
        // Byte 5: Air inlet pressure (2 kPa/bit)
        if (data[1] !== 0xFF) this.sensorData.boostPressure = data[1] * 2;
        if (data[4] !== 0xFF) this.sensorData.airInletTemp = data[4] - 40;
        if (data[5] !== 0xFF) this.sensorData.airInletPressure = data[5] * 2;
        const egtRaw = data[2] | (data[3] << 8);
        if (egtRaw !== 0xFFFF) this.sensorData.egtTemp = egtRaw * 0.03125 - 273;
        break;

      case PGN.ENGINE_TEMP_2:
        // Byte 0-1: Boost temp (0.03125 C/bit, offset -273)
        const boostTempRaw = data[0] | (data[1] << 8);
        if (boostTempRaw !== 0xFFFF) this.sensorData.boostTemp = boostTempRaw * 0.03125 - 273;
        break;

      case PGN.TURBO_INFO_1:
        // Byte 0: CAC inlet temp (offset -40)
        // Byte 1: Transfer pipe temp (offset -40)
        // Byte 2: Engine bay temp (offset -40)
        if (data[0] !== 0xFF) this.sensorData.cacInletTemp = data[0] - 40;
        if (data[1] !== 0xFF) this.sensorData.transferPipeTemp = data[1] - 40;
        if (data[2] !== 0xFF) this.sensorData.engineBayTemp = data[2] - 40;
        break;

      case PGN.TURBO_INFO_2:
        // Byte 2: CAC inlet pressure (2 kPa/bit)
        if (data[2] !== 0xFF) this.sensorData.cacInletPressure = data[2] * 2;
        break;

      case PGN.EEC6:
        // Byte 0: Engine bay temp (offset -40)
        // Byte 6: Humidity (0.5%/bit)
        if (data[0] !== 0xFF) this.sensorData.engineBayTemp = data[0] - 40;
        if (data[6] !== 0xFF) this.sensorData.humidity = data[6] * 0.5;
        break;
    }

    // Notify listener
    if (this.sensorHandler) {
      this.sensorHandler(this.sensorData);
    }
  }

  onSensorData(handler: (data: SensorData) => void): void {
    this.sensorHandler = handler;
  }

  getSensorData(): SensorData {
    return { ...this.sensorData };
  }

  private async sendCommand(cmdId: number, data: number[] = []): Promise<Buffer> {
    const buf = Buffer.alloc(8, 0xFF);
    buf[0] = cmdId;
    data.forEach((byte, i) => {
      if (i < 7) buf[i + 1] = byte;
    });

    const canId = this.buildCanId(PGN_COMMAND);

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.responseResolve = null;
        reject(new Error('No response from OSSM - check connection'));
      }, 2000);

      this.responseResolve = (responseData) => {
        clearTimeout(timeout);
        resolve(responseData);
      };

      this.can.send({ id: canId, data: buf, ext: true });
    });
  }

  async enableSpn(spn: number, enable: boolean, input: number = 0): Promise<boolean> {
    const spnHi = (spn >> 8) & 0xFF;
    const spnLo = spn & 0xFF;
    const response = await this.sendCommand(CMD.ENABLE_SPN, [spnHi, spnLo, enable ? 1 : 0, input]);
    return response[0] === 0;  // 0 = OK
  }

  async setNtcPreset(input: number, preset: number): Promise<boolean> {
    const response = await this.sendCommand(CMD.NTC_PRESET, [input, preset]);
    return response[0] === 0;
  }

  async setPressurePreset(input: number, preset: number): Promise<boolean> {
    const response = await this.sendCommand(CMD.PRESSURE_PRESET, [input, preset]);
    return response[0] === 0;
  }

  async setThermocoupleType(tcType: number): Promise<boolean> {
    const response = await this.sendCommand(CMD.SET_TC_TYPE, [tcType]);
    return response[0] === 0;
  }

  async query(): Promise<Buffer> {
    return this.sendCommand(CMD.QUERY);
  }

  async save(): Promise<boolean> {
    const response = await this.sendCommand(CMD.SAVE);
    return response[0] === 0;
  }

  async reset(): Promise<boolean> {
    const response = await this.sendCommand(CMD.RESET);
    return response[0] === 0;
  }
}
