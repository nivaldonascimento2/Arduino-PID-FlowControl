## Versão boa para essa etapa Arduino
## Modificar para´poder gravar dados a cada 1 segundos

import tkinter as tk
from tkinter import ttk, PhotoImage
import serial
import serial.tools.list_ports
import os
import pandas as pd
import time
from threading import Thread

class ArduinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Motor e Pressão")
        self.root.minsize(700, 600)
        
        self.serial_port = None
        self.ser = None
        self.port_list = [port.device for port in serial.tools.list_ports.comports()]

        base_path = r"C:\Users\Equatorial Sistemas\Documents\01 - Projeto fluxo agua\01 - FIRMWARE\SerialControl_Pressure_Termopar_Vazao_5"
        self.temp_icon_path = os.path.join(base_path, "temp_icon.png")
        self.pressure_icon_path = os.path.join(base_path, "pressure_icon.png")
        self.flow_icon_path = os.path.join(base_path, "flow_icon.png")

        try:
            self.temp_icon = PhotoImage(file=self.temp_icon_path)
            self.pressure_icon = PhotoImage(file=self.pressure_icon_path)
            self.flow_icon = PhotoImage(file=self.flow_icon_path)
        except Exception as e:
            print(f"Erro ao carregar as imagens: {e}")
            self.temp_icon = None
            self.pressure_icon = None
            self.flow_icon = None

        self.save_directory = r"C:\Users\Equatorial Sistemas\Documents\01 - Projeto fluxo agua\01 - FIRMWARE\SerialControl_Pressure_Termopar_Vazao_5\Dados_Gravacao"
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        self.create_widgets()

        self.recording = False
        self.data = {"Timestamp": [], "Temp1": [], "Temp2": [], "Pressure1": [], "Pressure2": [], "Flow": []}
        self.file_path = None

    def create_widgets(self):
        self.connect_button = ttk.Button(self.root, text="Conectar", command=self.toggle_connection, width=15)
        self.connect_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.port_combobox = ttk.Combobox(self.root, values=self.port_list, width=20)
        self.port_combobox.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        self.set_label = ttk.Label(self.root, text="Ajuste de 0.0 à 30.0 (l/min):")
        self.set_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.set_entry = ttk.Entry(self.root, width=10)
        self.set_entry.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        self.set_button = ttk.Button(self.root, text="Ajustar", command=self.send_set, width=10)
        self.set_button.grid(row=2, column=2, padx=10, pady=10, sticky='e')

        self.log_text = tk.Text(self.root, height=8, width=50)
        self.log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.data_frame = ttk.Frame(self.root)
        self.data_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

        row_index = 0
        if self.temp_icon:
            self.temp1_icon_label = ttk.Label(self.data_frame, image=self.temp_icon)
            self.temp1_icon_label.grid(row=row_index, column=0, padx=5, pady=5, sticky='e')
        self.temp1_label = ttk.Label(self.data_frame, text="Temp 1: -- °C", font=('Arial', 12))
        self.temp1_label.grid(row=row_index, column=1, padx=5, pady=5, sticky='w')

        self.temp1_canvas = tk.Canvas(self.data_frame, width=200, height=16, bg='white', bd=2, relief='sunken')
        self.temp1_canvas.grid(row=row_index, column=2, padx=5, pady=5, sticky='w')

        row_index += 1
        if self.temp_icon:
            self.temp2_icon_label = ttk.Label(self.data_frame, image=self.temp_icon)
            self.temp2_icon_label.grid(row=row_index, column=0, padx=5, pady=5, sticky='e')
        self.temp2_label = ttk.Label(self.data_frame, text="Temp 2: -- °C", font=('Arial', 12))
        self.temp2_label.grid(row=row_index, column=1, padx=5, pady=5, sticky='w')

        self.temp2_canvas = tk.Canvas(self.data_frame, width=200, height=16, bg='white', bd=2, relief='sunken')
        self.temp2_canvas.grid(row=row_index, column=2, padx=5, pady=5, sticky='w')

        row_index += 1

        self.delta_label = ttk.Label(self.data_frame, text="ΔTemp: -- °C", font=('Arial', 10))
        self.delta_label.grid(row=row_index, column=1, padx=5, pady=5, sticky='w')

        if self.pressure_icon:
            self.pressure1_icon_label = ttk.Label(self.data_frame, image=self.pressure_icon)
            self.pressure1_icon_label.grid(row=row_index + 1, column=0, padx=5, pady=5, sticky='e')
        self.pressure1_label = ttk.Label(self.data_frame, text="Pressão 1: -- Bar", font=('Arial', 12))
        self.pressure1_label.grid(row=row_index + 1, column=1, padx=5, pady=5, sticky='w')

        if self.pressure_icon:
            self.pressure2_icon_label = ttk.Label(self.data_frame, image=self.pressure_icon)
            self.pressure2_icon_label.grid(row=row_index + 2, column=0, padx=5, pady=5, sticky='e')
        self.pressure2_label = ttk.Label(self.data_frame, text="Pressão 2: -- Bar", font=('Arial', 12))
        self.pressure2_label.grid(row=row_index + 2, column=1, padx=5, pady=5, sticky='w')

        if self.flow_icon:
            self.flow_icon_label = ttk.Label(self.data_frame, image=self.flow_icon)
            self.flow_icon_label.grid(row=row_index + 3, column=0, padx=5, pady=5, sticky='e')
        self.flow_label = ttk.Label(self.data_frame, text="Vazão: -- l/min", font=('Arial', 12))
        self.flow_label.grid(row=row_index + 3, column=1, padx=5, pady=5, sticky='w')

        self.emergency_button = tk.Button(self.root, text="Emergência", command=self.send_emergency, bg='red', fg='white', font=('Arial', 16, 'bold'), width=15)
        self.emergency_button.grid(row=5, column=0, padx=10, pady=10, sticky='n', ipady=5)

        self.record_frame = ttk.Frame(self.root)
        self.record_frame.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky='w')

        self.start_record_button = tk.Button(self.record_frame, text="Gravar", command=self.start_recording, bg='green', fg='white', font=('Arial', 12, 'bold'), width=10)
        self.start_record_button.grid(row=0, column=0, padx=5, pady=5)
        self.stop_record_button = tk.Button(self.record_frame, text="Parar", command=self.stop_recording, bg='red', fg='white', font=('Arial', 12, 'bold'), width=10, state=tk.DISABLED)
        self.stop_record_button.grid(row=0, column=1, padx=5, pady=5)

    def toggle_connection(self):
        if not self.ser:
            try:
                self.serial_port = self.port_combobox.get()
                self.ser = serial.Serial(self.serial_port, 9600, timeout=1)
                self.connect_button.config(text="Desconectar")
                self.log("Conectado à porta serial.")
            except Exception as e:
                self.log(f"Erro ao conectar: {e}")
        elif self.ser:
            self.ser.close()
            self.ser = None
            self.connect_button.config(text="Conectar")
            self.log("Desconectado da porta serial.")

    def send_set(self):
        value = self.set_entry.get()
        if self.ser and value:
            try:
                self.ser.write(f"set {value}\n".encode())
                self.log(f"Comando enviado: set {value}")
            except Exception as e:
                self.log(f"Erro ao enviar comando: {e}")

    def send_emergency(self):
        if self.ser:
            try:
                self.ser.write(b"emergency\n")
                self.log("Comando de emergência enviado!")
            except Exception as e:
                self.log(f"Erro ao enviar comando de emergência: {e}")

    def start_recording(self):
        if self.ser and not self.recording:
            self.recording = True
            self.start_record_button.config(state=tk.DISABLED)
            self.stop_record_button.config(state=tk.NORMAL)
            
            # Cria o arquivo de gravação uma única vez
            self.file_name = f"water_block_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
            self.file_path = os.path.join(self.save_directory, self.file_name)

            self.record_thread = Thread(target=self.record_data)
            self.record_thread.start()
            self.log(f"Início da gravação. Salvando em: {self.file_path}")

    def stop_recording(self):
        self.recording = False
        self.start_record_button.config(state=tk.NORMAL)
        self.stop_record_button.config(state=tk.DISABLED)
        self.log("Gravação interrompida.")
###############################################################
    def record_data(self):
        data = {"Timestamp": [], "Temp1": [], "Temp2": [], "Pressure1": [], "Pressure2": [], "Flow": []}
        start_time = time.time()  # Marca o início da gravação
        file_path = os.path.join(self.save_directory, "water_block.xlsx")  # Caminho do arquivo único

        while self.recording:
            if not self.ser or not self.ser.is_open:
                self.log("Arduino não está conectado. Pausando gravação.")
                time.sleep(5)
                continue

            try:
                line = self.ser.readline().decode().strip()
                if line:
                    values = line.split(';')
                    if len(values) >= 5:
                        # Calcula o tempo decorrido em segundos desde o início da gravação
                        current_time = time.time()
                        elapsed_time = round(current_time - start_time, 2)  # Arredonda para 2 casas decimais
                        data["Timestamp"].append(elapsed_time)
                        
                        temp1, temp2, pressure1, pressure2, flow = map(float, values[:5])
                        data["Temp1"].append(temp1)
                        data["Temp2"].append(temp2)
                        data["Pressure1"].append(pressure1)
                        data["Pressure2"].append(pressure2)
                        data["Flow"].append(flow)

                        # Salva os dados a cada 1 segundo
                        if len(data["Timestamp"]) % 10 == 0:  # Ajuste o número para salvar a cada X entradas
                            self.save_to_excel(file_path, data)
                    else:
                        self.log("Dados insuficientes recebidos.")
                else:
                    self.log("Linha vazia recebida.")
            except Exception as e:
                self.log(f"Erro na leitura dos dados: {e}")

            time.sleep(0.1)  # Diminui o tempo de espera para melhorar a resposta

    def save_to_excel(self, file_path, data):
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        self.log(f"Dados salvos em {file_path}")


    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoApp(root)
    root.mainloop()
