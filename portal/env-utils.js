'use strict';

const fs = require('fs');
const path = require('path');

const ENV_FILE_CANDIDATES = ['.env.local', '.env'];

function parseEnv(content) {
  return content.split(/\r?\n/).reduce((acc, line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) {
      return acc;
    }
    const equalsIndex = trimmed.indexOf('=');
    if (equalsIndex === -1) {
      return acc;
    }
    const key = trimmed.slice(0, equalsIndex).trim();
    let value = trimmed.slice(equalsIndex + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    acc[key] = value;
    return acc;
  }, {});
}

function loadFirebaseEnv(rootDir) {
  for (const fileName of ENV_FILE_CANDIDATES) {
    const fullPath = path.join(rootDir, fileName);
    if (!fs.existsSync(fullPath)) {
      continue;
    }
    try {
      const content = fs.readFileSync(fullPath, 'utf8');
      const parsed = parseEnv(content);
      const firebaseKeys = Object.fromEntries(
        Object.entries(parsed).filter(([key]) => key.startsWith('VITE_FIREBASE_'))
      );
      if (Object.keys(firebaseKeys).length > 0) {
        return firebaseKeys;
      }
    } catch (error) {
      console.warn(`Failed to read ${fileName}:`, error.message);
    }
  }
  return null;
}

module.exports = {
  ENV_FILE_CANDIDATES,
  parseEnv,
  loadFirebaseEnv,
};
