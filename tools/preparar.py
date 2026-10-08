"""Transcreve áudios/vídeos e extrai frames, SOB DEMANDA (nunca em segundo plano).

Uso: py -3 tools/preparar.py --db wa.db --chat <jid> --desde <ts_unix> [--modelo small] [--frames 6]
Grava msgs.transcricao e msgs.frames no próprio banco.
"""
import argparse
import glob
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile


def achar_ffmpeg():
    exe = os.environ.get("WA_FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    achados = glob.glob(os.path.join(base, "Gyan.FFmpeg*", "**", "bin", "ffmpeg.exe"), recursive=True)
    if achados:
        return achados[0]
    sys.exit("ffmpeg nao encontrado (defina WA_FFMPEG).")


def duracao(ffmpeg, arq):
    r = subprocess.run([ffmpeg, "-hide_banner", "-i", arq], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--chat", required=True)
    ap.add_argument("--desde", type=int, default=0)
    ap.add_argument("--modelo", default=os.environ.get("WA_MODELO", "small"))
    ap.add_argument("--frames", type=int, default=6)
    a = ap.parse_args()

    ffmpeg = achar_ffmpeg()
    db = sqlite3.connect(a.db, timeout=10)
    db.execute("PRAGMA busy_timeout = 5000")
    rows = db.execute(
        "SELECT id, tipo, arquivo, dur FROM msgs WHERE chat=? AND ts>=? AND tipo IN ('audio','video') "
        "AND arquivo IS NOT NULL AND (transcricao IS NULL OR (tipo='video' AND frames IS NULL)) ORDER BY ts",
        (a.chat, a.desde),
    ).fetchall()
    if not rows:
        print("Nada pendente para preparar.")
        return

    from faster_whisper import WhisperModel  # só carrega quando há trabalho

    print(f"Carregando modelo '{a.modelo}' (CPU, int8) para {len(rows)} item(ns)...")
    modelo = WhisperModel(a.modelo, device="cpu", compute_type="int8", cpu_threads=4)

    for id_, tipo, arq, dur in rows:
        if not os.path.exists(arq):
            print(f"  {id_}: arquivo sumiu, pulando")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "a.wav")
            subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", arq, "-vn", "-ar", "16000", "-ac", "1", wav], check=False)
            texto = ""
            if os.path.exists(wav):
                segs, _ = modelo.transcribe(wav, language="pt", vad_filter=True)
                texto = " ".join(s.text.strip() for s in segs).strip()
        db.execute("UPDATE msgs SET transcricao=? WHERE chat=? AND id=?", (texto or "(sem fala detectada)", a.chat, id_))

        if tipo == "video":
            total = duracao(ffmpeg, arq) or float(dur or 0)
            pasta = os.path.splitext(arq)[0] + "_frames"
            os.makedirs(pasta, exist_ok=True)
            n = max(1, a.frames)
            for i in range(n):
                t = total * (i + 0.5) / n if total else 0
                saida = os.path.join(pasta, f"f{i + 1:02d}.jpg")
                subprocess.run(
                    [ffmpeg, "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", arq, "-frames:v", "1", "-vf", "scale=720:-2", "-q:v", "4", saida],
                    check=False,
                )
            db.execute("UPDATE msgs SET frames=? WHERE chat=? AND id=?", (pasta, a.chat, id_))
        db.commit()
        print(f"  {id_}: ok")
    print("Pronto.")


if __name__ == "__main__":
    main()
