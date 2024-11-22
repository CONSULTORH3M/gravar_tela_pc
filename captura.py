import cv2
import pyautogui
import numpy as np
import time
import tkinter as tk
from threading import Thread
import os

# Variáveis globais
video_gravando = False
start_time = None
fps = 5
tamanho_tela = pyautogui.size()  # Resolução da tela
codec = cv2.VideoWriter_fourcc(*"XVID")
video = None

# Carregar a imagem do cursor (substitua 'cursor.png' pela imagem do seu cursor)
cursor_img = cv2.imread('cursor.png', cv2.IMREAD_UNCHANGED)

# Verificar se a imagem foi carregada corretamente
if cursor_img is None:
    print("Falha ao carregar a imagem do cursor. Verifique o caminho e o formato da imagem.")
else:
    print("Imagem do cursor carregada com sucesso!")
    
    # Verificar se a imagem tem 4 canais (RGBA) ou 3 canais (RGB)
    if cursor_img.shape[2] == 4:  # Imagem com transparência
        print("Imagem do cursor tem transparência (canal alfa).")
        has_alpha = True
    elif cursor_img.shape[2] == 3:  # Imagem sem transparência
        print("Imagem do cursor é RGB (sem transparência).")
        has_alpha = False
    else:
        print("Formato de imagem inválido. A imagem precisa ter 3 ou 4 canais.")
        has_alpha = False

# Função para atualizar o cronômetro na interface
def atualizar_cronometro():
    if video_gravando:
        tempo_decorrido = int(time.time() - start_time)
        minutos = tempo_decorrido // 60
        segundos = tempo_decorrido % 60
        tempo_formatado = f"{minutos:02}:{segundos:02}"
        cronometro_label.config(text=tempo_formatado)
    root.after(1000, atualizar_cronometro)  # Atualiza o cronômetro a cada 1 segundo

# Função para iniciar a gravação
def iniciar_gravacao():
    global video_gravando, start_time, video
    video_gravando = True
    start_time = time.time()  # Marca o início da gravação
    video = cv2.VideoWriter("Video.avi", codec, fps, tamanho_tela)
    gravar_video()

# Função para parar a gravação
def parar_gravacao():
    global video_gravando, video
    video_gravando = False
    video.release()
    cv2.destroyAllWindows()

# Função para capturar e gravar o vídeo em um loop
def gravar_video():
    while video_gravando:
        # Captura da tela
        frame = pyautogui.screenshot()
        frame = np.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Posição do mouse
        mouse_x, mouse_y = pyautogui.position()

        # Verificar se a imagem do cursor tem transparência ou não
        if has_alpha:
            # A imagem tem 4 canais (RGBA), podemos usar o canal alfa
            h, w = cursor_img.shape[:2]

            # Colocar o cursor sobre o frame, verificando limites para evitar overflow
            if mouse_x + w <= tamanho_tela[0] and mouse_y + h <= tamanho_tela[1]:
                # Sobrepor a imagem do cursor na posição correta usando transparência
                for c in range(0, 3):
                    frame[mouse_y:mouse_y+h, mouse_x:mouse_x+w, c] = \
                        frame[mouse_y:mouse_y+h, mouse_x:mouse_x+w, c] * (1 - cursor_img[:, :, 3] / 255.0) + \
                        cursor_img[:, :, c] * (cursor_img[:, :, 3] / 255.0)

        else:
            # A imagem é RGB, não tem canal alfa, então colocamos o cursor sem transparência
            h, w = cursor_img.shape[:2]

            # Colocar o cursor sobre o frame, verificando limites para evitar overflow
            if mouse_x + w <= tamanho_tela[0] and mouse_y + h <= tamanho_tela[1]:
                frame[mouse_y:mouse_y+h, mouse_x:mouse_x+w] = cursor_img

        # Gravando o frame no vídeo
        video.write(frame)
        time.sleep(1 / fps)  # Controla a taxa de FPS

# Função para iniciar a gravação em uma thread separada (para não travar a interface)
def iniciar_gravacao_thread():
    thread = Thread(target=iniciar_gravacao)
    thread.start()

# Função para parar a gravação em uma thread separada
def parar_gravacao_thread():
    thread = Thread(target=parar_gravacao)
    thread.start()

# Função para encerrar o programa e fechar a janela
def encerrar_programa():
    parar_gravacao()  # Parar a gravação se estiver ativa
    root.destroy()  # Fecha a janela do Tkinter

# Configuração da interface gráfica (Tkinter)
root = tk.Tk()
root.title("Gravador")
root.geometry('220x210')

# Botões de Iniciar e Parar
iniciar_button = tk.Button(root, text="Iniciar Gravacao", width=15, command=iniciar_gravacao_thread, bg='green')
iniciar_button.pack(pady=10)

parar_button = tk.Button(root, text="Encerrar VIDEO", width=15, command=parar_gravacao_thread, bg="blue")
parar_button.pack(pady=10)

# Botão de Fechar (Destruir a janela)
fechar_button = tk.Button(root, text="Fechar", width=15, command=encerrar_programa, bg='white')
fechar_button.pack(pady=10)

# Label para mostrar o cronômetro
cronometro_label = tk.Label(root, text="00:00", font=("Helvetica", 24))
cronometro_label.pack(pady=20)

# Atualiza o cronômetro
atualizar_cronometro()

# Rodar a interface gráfica
root.mainloop()
