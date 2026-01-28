#!/usr/bin/env node
// OSSM Config - Configuration tool for Open Source Sensor Module
import { CanBus } from './can/socketcan';
import { J1939Protocol } from './protocol/j1939';
import { Menu } from './ui/menu';

function parseArgs(): { interface: string } {
  const args = process.argv.slice(2);
  let canInterface = 'can0';

  for (let i = 0; i < args.length; i++) {
    if ((args[i] === '-i' || args[i] === '--interface') && args[i + 1]) {
      canInterface = args[i + 1];
      i++;
    } else if (args[i] === '-h' || args[i] === '--help') {
      console.log('OSSM Config - Configuration tool for Open Source Sensor Module\n');
      console.log('Usage: ossm-config [options]\n');
      console.log('Options:');
      console.log('  -i, --interface <name>  CAN interface name (default: can0)');
      console.log('  -h, --help              Show this help message');
      process.exit(0);
    }
  }

  return { interface: canInterface };
}

async function main(): Promise<void> {
  const config = parseArgs();

  console.log(`OSSM Config - Connecting to ${config.interface}...`);

  const can = new CanBus(config.interface);

  try {
    can.connect();
  } catch (err) {
    console.error((err as Error).message);
    process.exit(1);
  }

  const protocol = new J1939Protocol(can);
  const menu = new Menu(protocol, config.interface);

  // Handle clean shutdown
  process.on('SIGINT', () => {
    console.log('\nDisconnecting...');
    can.disconnect();
    process.exit(0);
  });

  try {
    await menu.run();
  } finally {
    can.disconnect();
  }
}

main().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});
