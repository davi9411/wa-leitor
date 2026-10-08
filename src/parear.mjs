// Pareamento único por código de 8 dígitos (sem QR, sem dependência extra).
// Uso: node src/parear.mjs 5511999999999
import makeWASocket, * as B from '@whiskeysockets/baileys';
import pino from 'pino';
import { PATHS, garantirPastas } from './config.mjs';

const { useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion, Browsers } = B;
const numero = (process.argv[2] || '').replace(/\D/g, '');
if (numero.length < 10) {
  console.error('Informe o número com DDI+DDD, só dígitos. Ex.: wa parear 5511999999999');
  process.exit(1);
}

garantirPastas();
const logger = pino({ level: 'silent' });
let codigoPedido = false;

async function iniciar() {
  const { state, saveCreds } = await useMultiFileAuthState(PATHS.auth);
  if (state.creds.registered) { console.log('Já pareado. Para parear de novo, apague a pasta:', PATHS.auth); process.exit(0); }
  const { version } = await fetchLatestBaileysVersion().catch(() => ({ version: undefined }));
  const sock = makeWASocket({
    version, auth: state, logger,
    browser: Browsers.windows('Chrome'),
    markOnlineOnConnect: false, syncFullHistory: false,
  });
  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async ({ connection, lastDisconnect }) => {
    if (connection === 'connecting' && !codigoPedido && !state.creds.registered) {
      codigoPedido = true;
      setTimeout(async () => {
        try {
          const cod = await sock.requestPairingCode(numero);
          console.log('\nCódigo de pareamento:  ' + cod.match(/.{1,4}/g).join('-'));
          console.log('No celular: WhatsApp > Configurações > Dispositivos conectados > Conectar dispositivo > "Conectar com número de telefone"\n');
        } catch (e) { console.error('Falha ao pedir o código:', e.message); process.exit(1); }
      }, 3000);
    }
    if (connection === 'open') {
      console.log('Pareado com sucesso. Credenciais salvas em', PATHS.auth);
      setTimeout(() => process.exit(0), 4000); // dá tempo de gravar as credenciais
    }
    if (connection === 'close') {
      const cod = lastDisconnect?.error?.output?.statusCode;
      if (cod === DisconnectReason.restartRequired) { iniciar(); return; } // normal logo após parear
      if (cod === DisconnectReason.loggedOut) { console.error('Pareamento recusado.'); process.exit(1); }
      if (!state.creds.registered && cod !== undefined) { console.error('Conexão encerrada (' + cod + ').'); process.exit(1); }
    }
  });
}
iniciar();
