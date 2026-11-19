import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const serverDir = path.join(root, 'server');
const venvWindows = path.join(serverDir, '.venv', 'Scripts', 'python.exe');
const venvPosix = path.join(serverDir, '.venv', 'bin', 'python');
const python = existsSync(venvWindows) ? venvWindows : existsSync(venvPosix) ? venvPosix : 'python';
const mode = process.argv[2] || 'start';

const args = mode === 'test'
  ? ['-m', 'pytest']
  : mode === 'dev'
    ? ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '3001']
    : ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '3001'];

const child = spawn(python, args, { cwd: serverDir, stdio: 'inherit', env: process.env });
child.on('exit', (code) => process.exit(code ?? 0));
