import tkinter as tk
from tkinter import ttk, PhotoImage
import serial
import serial.tools.list_ports
import os
import pandas as pd
from datetime import datetime
import re
import time

class ArduinoApp:
    def __init__(self, root):
        self.gravar = False
        self.data_storage = []
        self.start_time = None
        self.serial_port = None
        self.ser = None
        self.read_start_time = None
        self.temp1_values = []
        self.temp2_values = []
        self.pressure1_values = []
        self.pressure2_values = []
        self.flow_values = []
        self.delta_temp_values = []

        self.root = root
        self.root.title("Controle de Motor e Pressão")
        self.root.minsize(800, 600)

        self.port_list = [port.device for port in serial.tools.list_ports.comports()]

        base_path = r"C:\Users\AKAER\Desktop\flowcooler"
        self.temp_icon_path = os.path.join(base_path, "temp_icon.png")
        self.pressure_icon_path = os.path.join(base_path, "pressure_icon.png")
        self.flow_icon_path = os.path.join(base_path, "flow_icon.png")

        print(f"Caminho das imagens:")
        print(f"Temp Icon: {self.temp_icon_path}")
        print(f"Pressure Icon: {self.pressure_icon_path}")
        print(f"Flow Icon: {self.flow_icon_path}")

        try:
            self.temp_icon = PhotoImage(file=self.temp_icon_path)
            self.pressure_icon = PhotoImage(file=self.pressure_icon_path)
            self.flow_icon = PhotoImage(file=self.flow_icon_path)
            print("Imagens carregadas com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar as imagens: {e}")
            self.temp_icon = None
            self.pressure_icon = None
            self.flow_icon = None

        self.create_widgets()
        self.save_directory = r"C:\Users\AKAER\Desktop\flowcooler\Dados_Gravacao"

    def create_widgets(self):
        self.control_frame1 = ttk.Frame(self.root)
        self.control_frame1.grid(row=0, column=0, padx=10, sticky="w")

        self.connect_button = ttk.Button(self.control_frame1, text="Conectar", command=self.toggle_connection)
        self.connect_button.pack(side="left", padx=(1,5))

        self.port_combobox = ttk.Combobox(self.control_frame1, values=self.port_list, width=10)
        self.port_combobox.pack(side="left", padx=(5,20))

        self.control_frame4 = ttk.Frame(self.root)
        self.control_frame4.grid(row=1, column=0, padx=10, sticky="w")

        self.set_label = ttk.Label(self.control_frame4, text="Salva como ? ")
        self.set_label.pack(side="left", padx=(0, 5))

        self.save_entry = ttk.Entry(self.control_frame4, width=20)
        self.save_entry.pack(side="left", padx=(0, 5))
        self.save_entry.insert(0, "WaterCooler_")

        self.set_label = ttk.Label(self.root, text="Ajuste de 0.0 à 30.0 (l/min):")
        self.set_label.grid(row=1, column=1, padx=5, pady=10, sticky='w')

        self.control_frame2 = ttk.Frame(self.root)
        self.control_frame2.grid(row=2, column=1, padx=10, sticky="w")

        self.set_entry = ttk.Entry(self.control_frame2, width=10)
        self.set_entry.pack(side="left", padx=(0, 5))

        self.set_button = ttk.Button(self.control_frame2, text="Ajustar", command=self.send_set)
        self.set_button.pack(side="left", padx=(5, 10))

        self.control_frame3 = ttk.Frame(self.root)
        self.control_frame3.grid(row=2, column=0, padx=10, sticky="w")

        self.gravar_button = ttk.Button(self.control_frame3, text="Gravar", command=self.start_gravar)
        self.gravar_button.pack(side="left", padx=(1,5))

        self.parar_button = ttk.Button(self.control_frame3, text="Parar", command=self.stop_gravar)
        self.parar_button.pack(side="left", padx=(5,10))
        self.parar_button.config(state="disabled")

        self.led_canvas = tk.Canvas(self.control_frame3, width=20, height=20, highlightthickness=0)
        self.led_canvas.pack(side="left", padx=(5, 0))
        self.led = self.led_canvas.create_oval(2, 2, 18, 18, fill="gray")

        self.log_text = tk.Text(self.root, height=8, width=50)
        self.log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.data_frame = ttk.Frame(self.root)
        self.data_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

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

        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(5, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        self.read_serial_data()

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.log("Desconectado")
            self.connect_button.config(text="Conectar")
        else:
            port = self.port_combobox.get()
            if port:
                self.connect_serial(port)
                self.connect_button.config(text="Desconectar")

    def connect_serial(self, port):
        try:
            self.ser = serial.Serial(port, 9600, timeout=1)
            self.log(f"Conectado a {port}")
        except serial.SerialException as e:
            self.log(f"Erro ao conectar: {e}")

    def send_set(self):
        if self.ser and self.ser.is_open:
            set_value = self.set_entry.get()
            try:
                set_value_float = float(set_value)
                set_value_multipled = int(set_value_float * 10)

                command = f"set {set_value_multipled}\n"
                self.ser.write(command.encode())
                self.log(f"Comando 'set {set_value_multipled}' enviado")
            except ValueError:
                self.log("Erro: Valor de set inválido")

    def send_emergency(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(b"emergency\n")
                self.log("Comando de emergência enviado")
            except serial.SerialException as e:
                self.log(f"Erro ao enviar comando de emergência: {e}")

    def read_serial_data(self):
        if self.ser and self.ser.is_open:
            now = time.time()
            if self.read_start_time is None:
                self.read_start_time = now

            if now - self.read_start_time >= 1:
                try:
                    data = self.ser.readline().decode().strip()
                    if data:
                        self.process_data(data)
                except serial.SerialException as e:
                    self.log(f"Erro ao ler dados: {e}")

            if self.gravar and (now - self.read_start_time) % 1 < 0.1:
                self.calculate_and_save_averages()

        self.root.after(100, self.read_serial_data)

    def start_gravar(self):
        self.gravar = True
        self.log("Gravação iniciada.")
        self.led_canvas.itemconfig(self.led, fill="green")
        self.gravar_button.config(state="disabled")
        self.parar_button.config(state="normal")

    def stop_gravar(self):
        self.gravar = False
        self.log("Gravação parada.")
        self.led_canvas.itemconfig(self.led, fill="gray")
        self.gravar_button.config(state="normal")
        self.parar_button.config(state="disabled")

    def process_data(self, data):
        self.log(data)
        try:
            parts = data.split(';')
            if len(parts) == 5:
                if all(self.is_valid_number(part) for part in parts):
                    temp1 = float(parts[0])
                    temp2 = float(parts[1])
                    pressure1 = float(parts[2])
                    pressure2 = float(parts[3])
                    flow = float(parts[4])

                    self.temp1_label.config(text=f"Temp 1: {temp1:.1f} °C")
                    self.temp2_label.config(text=f"Temp 2: {temp2:.1f} °C")
                    self.pressure1_label.config(text=f"Pressão 1: {pressure1:.1f} Bar")
                    self.pressure2_label.config(text=f"Pressão 2: {pressure2:.1f} Bar")
                    self.flow_label.config(text=f"Vazão: {flow:.1f} l/min")

                    # Calcula a diferença entre Temp 1 e Temp 2
                    delta_temp = temp2 - temp1
                    self.delta_label.config(text=f"ΔTemp: {delta_temp:.1f} °C")

                    # Atualiza as barras de temperatura
                    self.update_temperature_bar(self.temp1_canvas, temp1)
                    self.update_temperature_bar(self.temp2_canvas, temp2)

                    if self.start_time is None:
                        self.start_time = datetime.now()

                    now = datetime.now()
                    seconds = (now - self.start_time).total_seconds()
                    seconds_rounded = round(seconds, 3)

                    if self.gravar:
                        self.temp1_values.append(temp1)
                        self.temp2_values.append(temp2)
                        self.pressure1_values.append(pressure1)
                        self.pressure2_values.append(pressure2)
                        self.flow_values.append(flow)
                        self.delta_temp_values.append(delta_temp)

                else:
                    self.log("Dados recebidos contêm valores não numéricos.")
            else:
                self.log("Dados recebidos no formato incorreto.")

        except Exception as e:
            self.log(f"Erro ao processar dados: {e}")

    def update_temperature_bar(self, canvas, temperature):
        max_temp = 30.0  # Define a temperatura máxima para a escala da barra
        bar_width = 200  # Largura da barra
        temp_percentage = min(max(temperature / max_temp, 0), 1)  # Garante que a porcentagem esteja entre 0 e 1
        filled_width = bar_width * temp_percentage
        canvas.delete("all")
        canvas.create_rectangle(0, 0, filled_width, 16, fill="blue", outline="black")

    def calculate_and_save_averages(self):
        if len(self.temp1_values) >= 3 and len(self.temp2_values) >= 3 and len(self.pressure1_values) >= 3 and len(self.pressure2_values) >= 3 and len(self.flow_values) >= 3:
            avg_temp1 = round(sum(self.temp1_values[-3:]) / 3, 2)
            avg_temp2 = round(sum(self.temp2_values[-3:]) / 3, 2)
            avg_pressure1 = round(sum(self.pressure1_values[-3:]) / 3, 2)
            avg_pressure2 = round(sum(self.pressure2_values[-3:]) / 3, 2)
            avg_flow = round(sum(self.flow_values[-3:]) / 3, 2)
            avg_delta_temp = round(sum(self.delta_temp_values[-3:]) / 3, 2)  # Média de delta_temp

            now = datetime.now()
            seconds_rounded = int(round((now - self.start_time).total_seconds()))

            data = {
                'Time (s)': seconds_rounded,
                'Temp1 °C': avg_temp1,
                'Temp2 °C': avg_temp2,
                'Pressão1 Bar': avg_pressure1,
                'Pressão2 Bar': avg_pressure2,
                'Vazão l/min': avg_flow,
                'ΔTemp °C': avg_delta_temp  # Adiciona delta_temp aqui
            }
            self.data_storage.append(data)
            self.save_to_excel()

    def is_valid_number(self, value):
        try:
            if re.match(r'^-?\d+(\.\d+)?$', value):
                return True
        except ValueError:
            pass
        return False

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.yview(tk.END)

    def save_to_excel(self):
        if self.data_storage:
            file_name = self.save_entry.get()
            if not file_name.endswith('.xlsx'):
                file_name += '.xlsx'

            file_path = os.path.join(self.save_directory, file_name)

            if not os.path.exists(self.save_directory):
                try:
                    os.makedirs(self.save_directory)
                    print(f"Diretório criado: {self.save_directory}")
                except Exception as e:
                    self.log(f"Erro ao criar diretório: {e}")
                    return

            try:
                df = pd.DataFrame(self.data_storage)
                df.to_excel(file_path, index=False)
                print(f"Dados salvos em {file_path}")
            except Exception as e:
                self.log(f"Erro ao salvar dados: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoApp(root)
    root.mainloop()
