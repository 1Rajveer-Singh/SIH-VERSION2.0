#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

async function build() {
  console.log('Starting custom build process...');
  
  try {
    // Make vite binary executable
    const viteBin = path.join(__dirname, 'node_modules', '.bin', 'vite');
    if (fs.existsSync(viteBin)) {
      fs.chmodSync(viteBin, '755');
      console.log('Fixed vite binary permissions');
    }

    // Try different build approaches
    const buildCommands = [
      ['npx', ['vite', 'build', '--mode', 'production']],
      ['node', [path.join(__dirname, 'node_modules', 'vite', 'bin', 'vite.js'), 'build', '--mode', 'production']],
      ['./node_modules/.bin/vite', ['build', '--mode', 'production']]
    ];

    for (const [command, args] of buildCommands) {
      try {
        console.log(`Trying: ${command} ${args.join(' ')}`);
        
        await new Promise((resolve, reject) => {
          const child = spawn(command, args, {
            stdio: 'inherit',
            cwd: __dirname,
            env: { ...process.env, NODE_ENV: 'production' }
          });
          
          child.on('exit', (code) => {
            if (code === 0) {
              resolve();
            } else {
              reject(new Error(`Command failed with exit code ${code}`));
            }
          });
          
          child.on('error', reject);
        });
        
        console.log('Build successful!');
        process.exit(0);
        
      } catch (error) {
        console.log(`Failed with ${command}: ${error.message}`);
        continue;
      }
    }
    
    throw new Error('All build attempts failed');
    
  } catch (error) {
    console.error('Build failed:', error.message);
    process.exit(1);
  }
}

build();