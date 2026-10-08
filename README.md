# wa-leitor

Leitor **local** de WhatsApp (Baileys). Recebe mensagens e mídia, grava num SQLite e deixa o Claude
ler, transcrever áudios e olhar frames de vídeos. Também envia (ou programa) mensagens e anexos,
**mas só quando o Davi pede**: nada é enviado por conta própria, e não há respostas automáticas.

O dia a dia é pelo chat do Claude Code ("liga", "lê o João", "manda o robô às 16:30"); os atalhos
`.cmd` existem só como reserva.

## Liga / desliga
Nada sobe sozinho. Reiniciou o PC = desligado.

| Ação | Comando | Atalho |
|---|---|---|
| Ligar (desliga sozinho em 8 h) | `wa ligar --horas 8` | duplo clique em `ligar.cmd` |
| Desligar | `wa desligar` | duplo clique em `desligar.cmd` |
| Ver estado | `wa status` | |

Ligado ocupa ~100–150 MB de RAM e CPU quase zero. Transcrição (Whisper) e frames só rodam quando
alguém executa `wa preparar`, nunca em segundo plano.

## Primeiro uso (uma vez)
```
npm install
wa parear 55DDDNUMERO     # mostra um código de 8 dígitos
```
No celular: WhatsApp > Configurações > Dispositivos conectados > Conectar dispositivo >
**Conectar com número de telefone** e digite o código.

## Dia a dia
```
wa chats [filtro]             # conversas recentes
wa ler <nome> --horas 24      # texto + transcrições + caminhos de fotos/vídeos/frames
wa preparar <nome> --horas 24 # transcreve áudios/vídeos e extrai frames (sob demanda)
```
O Claude usa esses mesmos comandos: lê o texto, abre as fotos e os frames pelos caminhos
e sugere a resposta.

## Enviar e programar (só a pedido do Davi)
```
wa enviar <nome> --texto "Recebemos, já vamos analisar"
wa enviar <nome> --texto "Segue o robô" --arquivo "C:\...\EA X v1.01.zip" --arquivo "C:\...\EA X.ex5" --em 16:30
wa fila               # pendentes e enviados nas últimas 24 h
wa cancelar <id>
```
- Sem `--em`, o envio é imediato e exige o leitor ligado.
- Com `--em` ("16:30" hoje, ou "AAAA-MM-DD HH:MM"), fica na fila e o leitor envia na hora. **O leitor
  precisa estar ligado nesse horário**; o auto-desligamento é adiado enquanto houver envio pendente.
- Se o horário passar com o leitor desligado por mais de 30 min (`WA_ATRASO_MAX_MIN`), o envio vira
  `atrasada` e **não sai** (evita mandar robô fora de hora). Veja em `wa fila`.
- Um arquivo vai com o texto como legenda; vários arquivos vão em mensagens separadas após o texto.

## Onde ficam os dados
`%LOCALAPPDATA%\wa-leitor` (**fora** do OneDrive e do git): `auth/` (credenciais = chave da conta),
`midia/`, `wa.db`, `wa.log`. Para mudar: variável `WA_DATA`.

## Ajustes (variáveis de ambiente)
- `WA_MODELO` modelo do Whisper (`small` padrão; `medium` é mais preciso e mais pesado)
- `WA_MAX_MIDIA_MB` limite de download por mídia (padrão 60)
- `WA_FFMPEG` caminho do ffmpeg, se não estiver no PATH

## Cuidados
- Baileys é **não oficial**: existe risco de bloqueio do número, menor por ser só leitura.
- Quem copiar `auth/` lê as conversas. Nunca versionar nem sincronizar.
- Desconectar pelo celular (Dispositivos conectados) corta o acesso na hora.
- Histórico antigo vem só em parte; mídia só é baixada a partir do pareamento.
