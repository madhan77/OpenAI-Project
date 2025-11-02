#!/usr/bin/env node
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT ? Number(process.env.PORT) : 5173;
const ROOT_DIR = __dirname;
const ENV_FILE_CANDIDATES = [".env.local", ".env"];
const DEFAULT_FIREBASE_ENV = {
  VITE_FIREBASE_API_KEY: "AIzaSyB-bo4wgmeLm0Wg1eTiiFe69l6fuXRGCns",
  VITE_FIREBASE_AUTH_DOMAIN: "open-ai-project-723a7.firebaseapp.com",
  VITE_FIREBASE_PROJECT_ID: "open-ai-project-723a7",
  VITE_FIREBASE_APP_ID: "project-299553862015"
};
const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon"
};

function parseEnv(content) {
  return content.split(/\r?\n/).reduce((acc, line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      return acc;
    }
    const equalsIndex = trimmed.indexOf("=");
    if (equalsIndex === -1) {
      return acc;
    }
    const key = trimmed.slice(0, equalsIndex).trim();
    let value = trimmed.slice(equalsIndex + 1).trim();
    if ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    acc[key] = value;
    return acc;
  }, {});
}

function loadFirebaseEnv() {
  for (const fileName of ENV_FILE_CANDIDATES) {
    const fullPath = path.join(ROOT_DIR, fileName);
    if (fs.existsSync(fullPath)) {
      try {
        const content = fs.readFileSync(fullPath, "utf8");
        const parsed = parseEnv(content);
        const firebaseKeys = Object.fromEntries(
          Object.entries(parsed).filter(([key]) => key.startsWith("VITE_FIREBASE_"))
        );
        if (Object.keys(firebaseKeys).length > 0) {
          return firebaseKeys;
        }
      } catch (error) {
        console.warn(`Failed to read ${fileName}:`, error);
      }
    }
  }
  return null;
}

function toFirebaseConfigObject(envRecord) {
  if (!envRecord) {
    return null;
  }
  const mapping = {
    VITE_FIREBASE_API_KEY: "apiKey",
    VITE_FIREBASE_AUTH_DOMAIN: "authDomain",
    VITE_FIREBASE_PROJECT_ID: "projectId",
    VITE_FIREBASE_APP_ID: "appId"
  };
  const config = {};
  let hasValue = false;
  for (const [envKey, configKey] of Object.entries(mapping)) {
    if (envRecord[envKey]) {
      config[configKey] = envRecord[envKey];
      hasValue = true;
    }
  }
  return hasValue ? config : null;
}

function serveFirebaseEnv(res) {
  const envRecord = loadFirebaseEnv() || DEFAULT_FIREBASE_ENV;
  const firebaseConfig = toFirebaseConfigObject(envRecord);
  let body;
  if (firebaseConfig) {
    body = `window.FIREBASE_ENV = ${JSON.stringify(envRecord)};\nwindow.FIREBASE_CONFIG = ${JSON.stringify(firebaseConfig)};`;
  } else {
    body = "console.warn('Firebase environment variables not found. Provide a .env file with VITE_FIREBASE_* keys.');";
  }
  res.writeHead(200, {
    "Content-Type": "application/javascript; charset=utf-8",
    "Cache-Control": "no-store"
  });
  res.end(body);
}

function resolveFilePath(requestPath) {
  const sanitizedPath = decodeURI(requestPath.split("?")[0]);
  if (sanitizedPath === "/" || sanitizedPath === "") {
    return path.join(ROOT_DIR, "index.html");
  }
  return path.join(ROOT_DIR, sanitizedPath);
}

function serveStaticFile(res, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || "application/octet-stream";
  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === "ENOENT") {
        res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        res.end("Not found");
        return;
      }
      res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Internal server error");
      return;
    }
    res.writeHead(200, { "Content-Type": contentType });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  if (!req.url) {
    res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Bad request");
    return;
  }

  if (req.url === "/firebase-env.js") {
    serveFirebaseEnv(res);
    return;
  }

  const filePath = resolveFilePath(req.url);
  const normalizedRoot = path.normalize(ROOT_DIR + path.sep);
  const normalizedPath = path.normalize(filePath);

  if (!normalizedPath.startsWith(normalizedRoot)) {
    res.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Forbidden");
    return;
  }

  fs.stat(normalizedPath, (err, stats) => {
    if (err) {
      if (err.code === "ENOENT") {
        res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        res.end("Not found");
        return;
      }
      res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Internal server error");
      return;
    }

    if (stats.isDirectory()) {
      serveStaticFile(res, path.join(normalizedPath, "index.html"));
    } else {
      serveStaticFile(res, normalizedPath);
    }
  });
});

server.listen(PORT, () => {
  console.log(`Reviewer portal available at http://localhost:${PORT}`);
});
