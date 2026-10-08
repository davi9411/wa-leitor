// Caminhos e limites. Dados sensíveis (sessão, mídia, banco) ficam FORA do
// OneDrive e do git: %LOCALAPPDATA%\wa-leitor (ou WA_DATA).
import { join } from 'node:path';
import { mkdirSync } from 'node:fs';
import { homedir } from 'node:os';

export const DATA_DIR = process.env.WA_DATA
  || join(process.env.LOCALAPPDATA || join(homedir(), 'AppData', 'Local'), 'wa-leitor');

export const PATHS = {
  data: DATA_DIR,
  auth: join(DATA_DIR, 'auth'),     // credenciais = chave da conta. NUNCA copiar/sincronizar
  midia: join(DATA_DIR, 'midia'),
  db: join(DATA_DIR, 'wa.db'),
  pid: join(DATA_DIR, 'wa.pid'),
  log: join(DATA_DIR, 'wa.log'),
};

// Mídia maior que isso não é baixada (só registrada). Padrão 60 MB.
export const MAX_MIDIA_MB = Number(process.env.WA_MAX_MIDIA_MB || 60);

export function garantirPastas() {
  for (const p of [PATHS.data, PATHS.auth, PATHS.midia]) mkdirSync(p, { recursive: true });
}
