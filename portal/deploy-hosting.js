#!/usr/bin/env node
'use strict';

const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '..');
const firebaseConfigPath = path.resolve(repoRoot, 'firebase.json');
const firebasercPath = path.resolve(repoRoot, '.firebaserc');

function readFirebasercProject() {
  try {
    const raw = fs.readFileSync(firebasercPath, 'utf8');
    const parsed = JSON.parse(raw);
    if (parsed && parsed.projects && parsed.projects.default) {
      return parsed.projects.default;
    }
  } catch (error) {
    // Ignore missing or malformed .firebaserc
  }
  return null;
}

const envProject =
  process.env.FIREBASE_PROJECT_ID ||
  process.env.GCLOUD_PROJECT ||
  process.env.VITE_FIREBASE_PROJECT_ID ||
  readFirebasercProject() ||
  'open-ai-project-723a7';

if (!fs.existsSync(firebaseConfigPath)) {
  console.error(
    'firebase.json was not found in the repository root. Make sure you run this command from the cloned project.'
  );
  process.exit(1);
}

const firebaseExecutableName = process.platform === 'win32' ? 'firebase.cmd' : 'firebase';
const firebaseExecutablePath = path.resolve(
  __dirname,
  'node_modules',
  '.bin',
  firebaseExecutableName
);

const args = [
  'deploy',
  '--only',
  'hosting',
  '--project',
  envProject,
  '--config',
  firebaseConfigPath
];

console.log('Deploying the reviewer portal to Firebase Hosting...');
console.log(`Using project: ${envProject}`);
console.log(`firebase.json: ${firebaseConfigPath}`);

let command = firebaseExecutablePath;
const spawnOptions = {
  stdio: 'inherit',
  cwd: repoRoot,
  env: process.env,
  shell: false
};

if (!fs.existsSync(firebaseExecutablePath)) {
  console.warn(
    'firebase-tools was not found in node_modules/.bin. Falling back to the globally installed "firebase" command.'
  );
  command = firebaseExecutableName;
  if (process.platform === 'win32') {
    spawnOptions.shell = true;
  }
}

const child = spawn(command, args, spawnOptions);

child.on('error', (error) => {
  console.error('\n❌ Unable to launch the Firebase CLI.');
  console.error(
    'Install it globally with "npm install -g firebase-tools" or run "npm install firebase-tools" inside the portal directory.'
  );
  console.error('Original error:', error.message);
});

child.on('exit', (code) => {
  if (code === 0) {
    console.log('\n✅ Firebase Hosting deploy complete.');
    console.log(
      'Your portal should now be available at https://' +
        `${envProject}.web.app/` +
        ' (or the associated firebaseapp.com domain).'
    );
  } else {
    console.error('\n❌ Firebase Hosting deploy failed. Review the output above for details.');
  }
  process.exit(code);
});
