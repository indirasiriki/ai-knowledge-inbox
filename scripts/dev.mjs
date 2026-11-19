// Starts FastAPI and the Vite dev server, and prefixes each line with its process name.
import readline from 'node:readline';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const children = [];
let stopping = false;

function prefix(name, stream, output) {
  const lines = readline.createInterface({ input: stream });
  lines.on('line', (line) => output.write(`[${name}] ${line}\n`));
}

function start(command, name, args, cwd) {
  const child = spawn(command, args, { cwd, env: process.env });
  prefix(name, child.stdout, process.stdout);
  prefix(name, child.stderr, process.stderr);
  child.on('exit', (code, signal) => {
    if (stopping || signal) return;
    if (code && code !== 0) {
      console.error(`${name} exited with code ${code}`);
      stop(code);
    }
  });
  children.push(child);
}

function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) {
    if (!child.killed) child.kill();
  }
  setTimeout(() => process.exit(code), 50);
}

process.on('SIGINT', () => stop(0));
process.on('SIGTERM', () => stop(0));

const venvWindows = path.join(root, 'server', '.venv', 'Scripts', 'python.exe');
const venvPosix = path.join(root, 'server', '.venv', 'bin', 'python');
const python = existsSync(venvWindows) ? venvWindows : existsSync(venvPosix) ? venvPosix : 'python';

start(python, 'server', [
  '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '3001',
], path.join(root, 'server'));

start(process.execPath, 'client', [
  path.join(root, 'node_modules', 'vite', 'bin', 'vite.js'),
], path.join(root, 'client'));
