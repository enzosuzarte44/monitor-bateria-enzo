import psutil
import time
import tkinter as tk
from tkinter import messagebox
import winsound
import threading
import os

# Caminho dos sons
base_path = os.path.dirname(os.path.abspath(__file__))
som_baixa = os.path.join(base_path, "som_baixa.wav")
som_cheia = os.path.join(base_path, "som_cheia.wav")

avisou_baixa = False
avisou_cheia = False

def tocar_som_completo(caminho):
    """Toca o arquivo todo em uma thread (não trava a UI)."""
    def job():
        try:
            winsound.PlaySound(caminho, winsound.SND_FILENAME)  # blocking dentro da thread
        except:
            winsound.MessageBeep()
    threading.Thread(target=job, daemon=True).start()

def tocar_som_por_5s(caminho):
    """Mantive caso queira usar: toca async e força parar após 5s."""
    def job():
        try:
            winsound.PlaySound(caminho, winsound.SND_FILENAME | winsound.SND_ASYNC)
            time.sleep(5)
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            winsound.MessageBeep()
    threading.Thread(target=job, daemon=True).start()

def atualizar_interface():
    bateria = psutil.sensors_battery()
    if not bateria:
        label_percentual.config(text="N/A")
        label_status.config(text="Sensor não encontrado", fg="gray")
        return

    porcentagem = bateria.percent
    carregando = bateria.power_plugged

    label_percentual.config(text=f"{porcentagem}%")

    if carregando:
        label_status.config(text="Carregando...", fg="green")
    else:
        label_status.config(text="Descarregando", fg="orange")

def logica_bateria():
    global avisou_baixa, avisou_cheia
    while True:
        bateria = psutil.sensors_battery()
        if not bateria:
            time.sleep(2)
            continue

        porcentagem = bateria.percent
        carregando = bateria.power_plugged

        # ALERTA ABAIXO DE 75% (toca som completo)
        if porcentagem < 75 and not avisou_baixa:
            # use tocar_som_completo para tocar até o fim
            tocar_som_completo(som_baixa)
            avisou_baixa = True
            avisou_cheia = False

        # ALERTA QUANDO CHEIA (>=95%)
        if porcentagem >= 95 and carregando and not avisou_cheia:
            tocar_som_completo(som_cheia)
            avisou_cheia = True
            avisou_baixa = False

        # reset quando conectar/desconectar
        if carregando:
            avisou_baixa = False

        time.sleep(1)

# ---------------- INTERFACE ----------------

janela = tk.Tk()
janela.title("Monitor de Bateria")
janela.geometry("380x220")
janela.configure(bg="#202020")

titulo = tk.Label(janela, text="Monitor de Bateria", font=("Segoe UI", 16, "bold"), fg="white", bg="#202020")
titulo.pack(pady=10)

label_percentual = tk.Label(janela, text="--%", font=("Segoe UI", 44, "bold"), fg="#00ff99", bg="#202020")
label_percentual.pack()

label_status = tk.Label(janela, text="Iniciando...", font=("Segoe UI", 13), fg="white", bg="#202020")
label_status.pack(pady=10)

# Thread para monitoramento
thread = threading.Thread(target=logica_bateria, daemon=True)
thread.start()

# Atualiza a interface a cada 1s
def loop_ui():
    atualizar_interface()
    janela.after(1000, loop_ui)

loop_ui()
janela.mainloop()
