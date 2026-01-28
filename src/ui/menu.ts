// BBS-style menu interface
import * as readline from 'readline';
import { J1939Protocol, SensorData } from '../protocol/j1939';

const NTC_PRESETS = ['AEM', 'Bosch', 'GM'];
const PRESSURE_PRESETS_BAR = [
  '1 Bar', '1.5 Bar', '2 Bar', '2.5 Bar', '3 Bar', '4 Bar', '5 Bar',
  '7 Bar', '10 Bar', '50 Bar', '100 Bar', '150 Bar', '200 Bar',
  '1000 Bar', '2000 Bar', '3000 Bar'
];
const PRESSURE_PRESETS_PSI = [
  '15 PSI', '30 PSI', '50 PSI', '100 PSI', '150 PSI', '200 PSI',
  '250 PSI', '300 PSI', '350 PSI', '400 PSI', '500 PSI'
];
const TC_TYPES = ['B', 'E', 'J', 'K', 'N', 'R', 'S', 'T'];

export class Menu {
  private rl: readline.Interface;
  private protocol: J1939Protocol;
  private canInterface: string;

  constructor(protocol: J1939Protocol, canInterface: string) {
    this.protocol = protocol;
    this.canInterface = canInterface;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  private prompt(question: string): Promise<string> {
    return new Promise(resolve => {
      this.rl.question(question, resolve);
    });
  }

  private clear(): void {
    console.clear();
  }

  async run(): Promise<void> {
    while (true) {
      this.clear();
      console.log(`=== OSSM Config (${this.canInterface}) ===\n`);
      console.log('1. Query configuration');
      console.log('2. Enable/Disable SPN');
      console.log('3. NTC Sensor Preset');
      console.log('4. Pressure Sensor Preset');
      console.log('5. Thermocouple Type');
      console.log('6. Monitor live data');
      console.log('7. Save to EEPROM');
      console.log('8. Reset to defaults');
      console.log('0. Exit\n');

      const choice = await this.prompt('Choice: ');

      try {
        switch (choice.trim()) {
          case '1': await this.queryConfig(); break;
          case '2': await this.enableSpn(); break;
          case '3': await this.ntcPreset(); break;
          case '4': await this.pressurePreset(); break;
          case '5': await this.thermocoupleType(); break;
          case '6': await this.monitorLiveData(); break;
          case '7': await this.saveConfig(); break;
          case '8': await this.resetConfig(); break;
          case '0':
            this.rl.close();
            return;
          default:
            console.log('Invalid choice');
            await this.prompt('Press Enter to continue...');
        }
      } catch (err) {
        console.log(`\nError: ${(err as Error).message}`);
        await this.prompt('Press Enter to continue...');
      }
    }
  }

  private async queryConfig(): Promise<void> {
    console.log('\nQuerying configuration...');
    const response = await this.protocol.query();
    console.log('\nConfiguration received (raw bytes):');
    console.log(response.toString('hex'));
    await this.prompt('\nPress Enter to continue...');
  }

  private async enableSpn(): Promise<void> {
    console.log('\n=== Enable/Disable SPN ===\n');

    const spnStr = await this.prompt('Enter SPN number: ');
    const spn = parseInt(spnStr, 10);
    if (isNaN(spn) || spn < 1) {
      console.log('Invalid SPN number');
      await this.prompt('Press Enter to continue...');
      return;
    }

    const enableStr = await this.prompt('Enable or disable? (e/d): ');
    const enable = enableStr.toLowerCase().startsWith('e');

    let input = 0;
    if (enable) {
      console.log('\nInput assignment:');
      console.log('  0 = BME280 (ambient sensors)');
      console.log('  1-8 = Temperature inputs');
      console.log('  1-7 = Pressure inputs');
      const inputStr = await this.prompt('Input number: ');
      input = parseInt(inputStr, 10);
      if (isNaN(input)) input = 0;
    }

    const success = await this.protocol.enableSpn(spn, enable, input);
    console.log(success ? `\nOK: SPN ${spn} ${enable ? 'enabled' : 'disabled'}` : '\nFailed');
    await this.prompt('Press Enter to continue...');
  }

  private async ntcPreset(): Promise<void> {
    console.log('\n=== NTC Sensor Preset ===\n');

    const inputStr = await this.prompt('Temperature input (1-8): ');
    const input = parseInt(inputStr, 10);
    if (isNaN(input) || input < 1 || input > 8) {
      console.log('Invalid input number');
      await this.prompt('Press Enter to continue...');
      return;
    }

    console.log('\nPresets:');
    NTC_PRESETS.forEach((p, i) => console.log(`  ${i}. ${p}`));
    const presetStr = await this.prompt('Preset number: ');
    const preset = parseInt(presetStr, 10);
    if (isNaN(preset) || preset < 0 || preset >= NTC_PRESETS.length) {
      console.log('Invalid preset');
      await this.prompt('Press Enter to continue...');
      return;
    }

    const success = await this.protocol.setNtcPreset(input, preset);
    console.log(success ? `\nOK: Input ${input} set to ${NTC_PRESETS[preset]}` : '\nFailed');
    await this.prompt('Press Enter to continue...');
  }

  private async pressurePreset(): Promise<void> {
    console.log('\n=== Pressure Sensor Preset ===\n');

    const inputStr = await this.prompt('Pressure input (1-7): ');
    const input = parseInt(inputStr, 10);
    if (isNaN(input) || input < 1 || input > 7) {
      console.log('Invalid input number');
      await this.prompt('Press Enter to continue...');
      return;
    }

    console.log('\nBar presets (absolute/PSIA):');
    PRESSURE_PRESETS_BAR.forEach((p, i) => console.log(`  ${i}. ${p}`));
    console.log('\nPSI presets (gauge/PSIG):');
    PRESSURE_PRESETS_PSI.forEach((p, i) => console.log(`  ${i + 20}. ${p}`));

    const presetStr = await this.prompt('Preset number: ');
    const preset = parseInt(presetStr, 10);
    if (isNaN(preset)) {
      console.log('Invalid preset');
      await this.prompt('Press Enter to continue...');
      return;
    }

    const success = await this.protocol.setPressurePreset(input, preset);
    console.log(success ? '\nOK: Preset applied' : '\nFailed');
    await this.prompt('Press Enter to continue...');
  }

  private async thermocoupleType(): Promise<void> {
    console.log('\n=== Thermocouple Type ===\n');

    console.log('Types:');
    TC_TYPES.forEach((t, i) => console.log(`  ${i}. Type ${t}`));

    const typeStr = await this.prompt('Type number: ');
    const tcType = parseInt(typeStr, 10);
    if (isNaN(tcType) || tcType < 0 || tcType >= TC_TYPES.length) {
      console.log('Invalid type');
      await this.prompt('Press Enter to continue...');
      return;
    }

    const success = await this.protocol.setThermocoupleType(tcType);
    console.log(success ? `\nOK: Set to Type ${TC_TYPES[tcType]}` : '\nFailed');
    await this.prompt('Press Enter to continue...');
  }

  private async monitorLiveData(): Promise<void> {
    console.log('\n=== Live Data (press Enter to stop) ===\n');

    let running = true;

    // Set up sensor data handler
    this.protocol.onSensorData((data: SensorData) => {
      if (!running) return;
      this.printSensorData(data);
    });

    // Wait for Enter key
    await this.prompt('');
    running = false;
    this.protocol.onSensorData(() => {});  // Clear handler
  }

  private printSensorData(data: SensorData): void {
    const time = new Date().toLocaleTimeString();
    const lines: string[] = [];

    // Temperatures
    const temps: string[] = [];
    if (data.coolantTemp !== undefined) temps.push(`Coolant: ${data.coolantTemp.toFixed(1)}C`);
    if (data.oilTemp !== undefined) temps.push(`Oil: ${data.oilTemp.toFixed(1)}C`);
    if (data.fuelTemp !== undefined) temps.push(`Fuel: ${data.fuelTemp.toFixed(1)}C`);
    if (data.boostTemp !== undefined) temps.push(`Boost: ${data.boostTemp.toFixed(1)}C`);
    if (temps.length > 0) lines.push(`[${time}] Temps: ${temps.join(' | ')}`);

    // More temps
    const temps2: string[] = [];
    if (data.airInletTemp !== undefined) temps2.push(`AirInlet: ${data.airInletTemp.toFixed(1)}C`);
    if (data.cacInletTemp !== undefined) temps2.push(`CAC: ${data.cacInletTemp.toFixed(1)}C`);
    if (data.egtTemp !== undefined) temps2.push(`EGT: ${data.egtTemp.toFixed(0)}C`);
    if (temps2.length > 0) lines.push(`[${time}] Temps: ${temps2.join(' | ')}`);

    // Pressures
    const press: string[] = [];
    if (data.oilPressure !== undefined) press.push(`Oil: ${data.oilPressure}kPa`);
    if (data.fuelPressure !== undefined) press.push(`Fuel: ${data.fuelPressure}kPa`);
    if (data.boostPressure !== undefined) press.push(`Boost: ${data.boostPressure}kPa`);
    if (press.length > 0) lines.push(`[${time}] Press: ${press.join(' | ')}`);

    // Ambient
    const ambient: string[] = [];
    if (data.ambientTemp !== undefined) ambient.push(`Ambient: ${data.ambientTemp.toFixed(1)}C`);
    if (data.barometricPressure !== undefined) ambient.push(`Baro: ${data.barometricPressure.toFixed(1)}kPa`);
    if (data.humidity !== undefined) ambient.push(`Humidity: ${data.humidity.toFixed(0)}%`);
    if (ambient.length > 0) lines.push(`[${time}] Ambient: ${ambient.join(' | ')}`);

    lines.forEach(line => console.log(line));
  }

  private async saveConfig(): Promise<void> {
    console.log('\nSaving configuration to EEPROM...');
    const success = await this.protocol.save();
    console.log(success ? 'OK: Configuration saved' : 'Failed to save');
    await this.prompt('Press Enter to continue...');
  }

  private async resetConfig(): Promise<void> {
    const confirm = await this.prompt('Reset to factory defaults? (y/n): ');
    if (!confirm.toLowerCase().startsWith('y')) {
      console.log('Cancelled');
      await this.prompt('Press Enter to continue...');
      return;
    }

    console.log('\nResetting configuration...');
    const success = await this.protocol.reset();
    console.log(success ? 'OK: Configuration reset' : 'Failed to reset');
    await this.prompt('Press Enter to continue...');
  }
}
