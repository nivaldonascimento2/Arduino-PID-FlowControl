## Versão boa para essa etapa Arduino Ok 14/08/2024

import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports

class ArduinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Master Motor V1.0.1")

        # Define o tamanho mínimo da janela
        self.root.minsize(800, 700)
        
        self.serial_port = None
        self.ser = None

        # Lista de portas seriais
        self.port_list = [port.device for port in serial.tools.list_ports.comports()]

        # UI
        self.create_widgets()

    def create_widgets(self):
        # Nome do software
        self.title_label = ttk.Label(self.root, text="Control Master Motor", font=('Arial', 20, 'bold'))
        self.title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

        # Conectar/Desconectar botão
        self.connect_button = ttk.Button(self.root, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        # Selecionar porta serial
        self.port_combobox = ttk.Combobox(self.root, values=self.port_list)
        self.port_combobox.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        # Campo de ajuste de atraso
        self.delay_label = ttk.Label(self.root, text="Ajuste de 0 à 100 (%):")
        self.delay_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.delay_entry = ttk.Entry(self.root)
        self.delay_entry.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        self.delay_button = ttk.Button(self.root, text="Ajustar", command=self.send_delay)
        self.delay_button.grid(row=2, column=2, padx=10, pady=10, sticky='e')

        # Área de log
        self.log_text = tk.Text(self.root, height=10, width=50)
        self.log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        # Frames para dados
        self.data_frame = ttk.Frame(self.root)
        self.data_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

        # Labels para dados
        self.temp1_label = ttk.Label(self.data_frame, text="Temp 1: -- °C", font=('Arial', 16, 'bold'))
        self.temp1_label.pack(side=tk.TOP, pady=5)
        self.temp2_label = ttk.Label(self.data_frame, text="Temp 2: -- °C", font=('Arial', 16, 'bold'))
        self.temp2_label.pack(side=tk.TOP, pady=5)
        self.pressure1_label = ttk.Label(self.data_frame, text="Pressão 1: -- Bar", font=('Arial', 16, 'bold'))
        self.pressure1_label.pack(side=tk.TOP, pady=5)
        self.pressure2_label = ttk.Label(self.data_frame, text="Pressão 2: -- Bar", font=('Arial', 16, 'bold'))
        self.pressure2_label.pack(side=tk.TOP, pady=5)
        self.flow_label = ttk.Label(self.data_frame, text="Vazão: -- l/min", font=('Arial', 16, 'bold'))
        self.flow_label.pack(side=tk.TOP, pady=5)

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

    def send_delay(self):
        if self.ser and self.ser.is_open:
            delay_value = self.delay_entry.get()
            if delay_value.isdigit():
                command = f"delay {delay_value}\n"
                self.ser.write(command.encode())
                self.log(f"Comando 'delay {delay_value}' enviado")
            else:
                self.log("Erro: Valor de atraso inválido")

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
            self.temp1_label.config(text=f"Temp 1: {temp1.strip()} °C")
            self.temp2_label.config(text=f"Temp 2: {temp2.strip()} °C")
            self.pressure1_label.config(text=f"Pressão 1: {pressure1.strip()} Bar")
            self.pressure2_label.config(text=f"Pressão 2: {pressure2.strip()} Bar")
            self.flow_label.config(text=f"Vazão: {flow.strip()} l/min")
        except ValueError:
            self.log("E: Dados recebidos: " + data)

    def log(self, message):
        # Adiciona mensagem ao log apenas se não for uma atualização de dados
        if not message.startswith("Temp") and not message.startswith("Pressão") and not message.startswith("Vazão"):
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoApp(root)
    root.mainloop()
