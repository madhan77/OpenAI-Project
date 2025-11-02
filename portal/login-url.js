#!/usr/bin/env node
'use strict';

const { loadFirebaseEnv } = require('./env-utils');

const PORT = process.env.PORT ? Number(process.env.PORT) : 5173;
const ROOT_DIR = __dirname;
const DEFAULT_PROJECT_ID = 'open-ai-project-723a7';

function resolveProjectId(envRecord) {
  if (!envRecord) {
    return DEFAULT_PROJECT_ID;
  }
  if (envRecord.VITE_FIREBASE_PROJECT_ID) {
    return envRecord.VITE_FIREBASE_PROJECT_ID;
  }
  return DEFAULT_PROJECT_ID;
}

function main() {
  const envRecord = loadFirebaseEnv(ROOT_DIR);
  const projectId = resolveProjectId(envRecord);

  const localUrl = `http://localhost:${PORT}/`;
  const hostedWebAppUrl = `https://${projectId}.web.app/`;
  const hostedFirebaseAppUrl = `https://${projectId}.firebaseapp.com/`;

  console.log('Claims Processing Portal login URLs');
  console.log('-----------------------------------');
  console.log('Local development:');
  console.log(`  ${localUrl}`);
  console.log('Firebase Hosting:');
  console.log(`  ${hostedWebAppUrl}`);
  console.log(`  ${hostedFirebaseAppUrl}`);

  if (!envRecord) {
    console.log('\nNote: Using the shared demo Firebase project. Provide portal/.env.local to override.');
  }

  console.log('\nIf the hosted URL shows "Site Not Found", deploy the portal with:');
  console.log('  cd portal && npm run deploy');
}

main();
