## Versão boa para essa etapa Arduino

import tkinter as tk
from tkinter import ttk, PhotoImage
import serial
import serial.tools.list_ports
import os

class ArduinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Motor e Pressão")

        # Define o tamanho mínimo da janela
        self.root.minsize(800, 600)
        
        self.serial_port = None
        self.ser = None

        # Lista de portas seriais
        self.port_list = [port.device for port in serial.tools.list_ports.comports()]

        # Caminho das imagens
        base_path = r"C:\Users\Equatorial Sistemas\Documents\01 - Projeto fluxo agua\01 - FIRMWARE\SerialControl_Pressure_Termopar_Vazao_2"
        self.temp_icon_path = os.path.join(base_path, "temp_icon.png")
        self.pressure_icon_path = os.path.join(base_path, "pressure_icon.png")
        self.flow_icon_path = os.path.join(base_path, "flow_icon.png")

        # Verifique se o caminho das imagens está correto
        print(f"Caminho das imagens:")
        print(f"Temp Icon: {self.temp_icon_path}")
        print(f"Pressure Icon: {self.pressure_icon_path}")
        print(f"Flow Icon: {self.flow_icon_path}")

        # Tenta carregar as imagens e trata erros
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

        # UI
        self.create_widgets()

    def create_widgets(self):
        # Nome do software
        self.title_label = ttk.Label(self.root, text="ControlMaster", font=('Arial', 20, 'bold'))
        self.title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

        # Conectar/Desconectar botão
        self.connect_button = ttk.Button(self.root, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        # Selecionar porta serial
        self.port_combobox = ttk.Combobox(self.root, values=self.port_list)
        self.port_combobox.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        # Campo de ajuste de atraso
        self.set_label = ttk.Label(self.root, text="Ajuste de 0.0 à 30.0 (l/min):")
        self.set_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.set_entry = ttk.Entry(self.root)
        self.set_entry.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        self.set_button = ttk.Button(self.root, text="Ajustar", command=self.send_set)
        self.set_button.grid(row=2, column=2, padx=10, pady=10, sticky='e')

        # Área de log
        self.log_text = tk.Text(self.root, height=8, width=50)  # Ajuste a altura para garantir que o log seja visível
        self.log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        # Frames para dados
        self.data_frame = ttk.Frame(self.root)
        self.data_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

        # Labels e barras de termômetro
        row_index = 0
        if self.temp_icon:
            self.temp1_icon_label = ttk.Label(self.data_frame, image=self.temp_icon)
            self.temp1_icon_label.grid(row=row_index, column=0, padx=5, pady=5, sticky='e')
        self.temp1_label = ttk.Label(self.data_frame, text="Temp 1: -- °C", font=('Arial', 12))
        self.temp1_label.grid(row=row_index, column=1, padx=5, pady=5, sticky='w')

        # Canvas para barra de temperatura
        self.temp1_canvas = tk.Canvas(self.data_frame, width=200, height=16, bg='white', bd=2, relief='sunken')
        self.temp1_canvas.grid(row=row_index, column=2, padx=5, pady=5, sticky='w')

        row_index += 1
        if self.temp_icon:
            self.temp2_icon_label = ttk.Label(self.data_frame, image=self.temp_icon)
            self.temp2_icon_label.grid(row=row_index, column=0, padx=5, pady=5, sticky='e')
        self.temp2_label = ttk.Label(self.data_frame, text="Temp 2: -- °C", font=('Arial', 12))
        self.temp2_label.grid(row=row_index, column=1, padx=5, pady=5, sticky='w')

        # Canvas para barra de temperatura
        self.temp2_canvas = tk.Canvas(self.data_frame, width=200, height=16, bg='white', bd=2, relief='sunken')
        self.temp2_canvas.grid(row=row_index, column=2, padx=5, pady=5, sticky='w')

        row_index += 1

        # Diferença entre Temp 1 e Temp 2
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

        # Botão de Emergência
        self.emergency_button = tk.Button(self.root, text="Emergência", command=self.send_emergency, bg='red', fg='white', font=('Arial', 16, 'bold'), width=15)
        self.emergency_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='n', ipady=5)

        # Ajustar o comportamento das colunas e linhas
        self.root.grid_rowconfigure(3, weight=1)  # Linha do log expandirá
        self.root.grid_rowconfigure(5, weight=0)  # Linha do botão de emergência não expandirá
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        
        # Iniciar a leitura dos dados
        self.read_serial_data()

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connect_button.config(text="Conectar")
            self.log("Desconectado")
        else:
            port = self.port_combobox.get()
            if port:
                try:
                    self.ser = serial.Serial(port, 9600, timeout=1)
                    self.connect_button.config(text="Desconectar")
                    self.log("Conectado")
                except serial.SerialException as e:
                    self.log(f"Erro ao conectar: {e}")

    def send_emergency(self):
        if self.ser and self.ser.is_open:
            self.ser.write(b"emergency\n")
            self.log("Comando 'emergency' enviado")

    def send_set(self):
        if self.ser and self.ser.is_open:
            set_value = self.set_entry.get()
            try:
                # Converte o valor para float e multiplica por 10
                set_value_float = float(set_value)
                set_value_multipled = int(set_value_float * 10)
                
                # Cria o comando com o valor multiplicado
                command = f"set {set_value_multipled}\n"
                self.ser.write(command.encode())
                self.log(f"Comando 'set {set_value_multipled}' enviado")
            except ValueError:
                self.log("Erro: Valor de set inválido")

    def read_serial_data(self):
        if self.ser and self.ser.is_open:
            try:
                while self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        # Remove caracteres inesperados e divide os dados
                        cleaned_line = line.replace('\r', '').replace('\n', '')
                        self.update_data_display(cleaned_line)
            except serial.SerialException as e:
                self.log(f"Erro de leitura: {e}")
        self.root.after(100, self.read_serial_data)

    def update_data_display(self, data):
        # Divide a string de dados para obter Temp 1, Temp 2, Pressão 1, Pressão 2 e Vazão
        try:
            temp1, temp2, pressure1, pressure2, flow = data.split(';')
            temp1_value = float(temp1.strip())
            temp2_value = float(temp2.strip())
            pressure1_value = float(pressure1.strip())
            pressure2_value = float(pressure2.strip())
            flow_value = float(flow.strip())

            self.temp1_label.config(text=f"Temp 1: {temp1_value} °C")
            self.temp2_label.config(text=f"Temp 2: {temp2_value} °C")
            self.pressure1_label.config(text=f"Pressão 1: {pressure1_value} Bar")
            self.pressure2_label.config(text=f"Pressão 2: {pressure2_value} Bar")
            self.flow_label.config(text=f"Vazão: {flow_value} l/min")

            # Calcula a diferença entre Temp 1 e Temp 2
            delta_temp = temp1_value - temp2_value
            self.delta_label.config(text=f"ΔTemp: {delta_temp:.1f} °C")

            # Atualiza as barras de temperatura
            self.update_temperature_bar(self.temp1_canvas, temp1_value)
            self.update_temperature_bar(self.temp2_canvas, temp2_value)
        except ValueError:
            self.log("Erro: Dados inválidos recebidos: " + data)

    def update_temperature_bar(self, canvas, temp_value):
        # Limpa o canvas
        canvas.delete("all")
        
        # Calcula a altura da barra com base na temperatura
        temp_min, temp_max = -20, 100
        bar_length = 200
        temp_range = temp_max - temp_min
        position = (temp_value - temp_min) / temp_range * bar_length

        # Define a cor da barra com base na temperatura
        if temp_value < 10:
            color = "blue"
        elif temp_value < 30:
            color = "yellow"
        elif temp_value < 70:
            color = "orange"
        else:
            color = "red"
        
        # Desenha a barra colorida
        canvas.create_rectangle(0, 0, position, 20, fill=color, outline="black")
        
        # Adiciona o texto do valor da temperatura na barra
        canvas.create_text(position + 10, 10, text=f"{temp_value} °C", fill="black", anchor='w')

    def log(self, message):
        # Adiciona mensagem ao log apenas se não for uma atualização de dados
        if not message.startswith("Temp") and not message.startswith("Pressão") and not message.startswith("Vazão"):
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoApp(root)
    root.mainloop()
