# ficou bom com time completo tentar reduzir para segundos 02/09/24
## time ficou bom. agora tentar colocar botão para iniciar aquisição e gravação ou não.
import tkinter as tk
from tkinter import ttk, PhotoImage
import serial
import serial.tools.list_ports
import os
import pandas as pd
from datetime import datetime

class ArduinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Motor e Pressão")

        # Define o tamanho mínimo da janela
        self.root.minsize(800, 600)

        # Inicializa o tempo de início como None
        self.start_time = None###################################
        
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

        # Caminho do diretório para salvar os dados
        self.save_directory = r"C:\Users\Equatorial Sistemas\Documents\01 - Projeto fluxo agua\01 - FIRMWARE\SerialControl_Pressure_Termopar_Vazao_5\Dados_Gravacao"

        # Data storage
        self.data_storage = []

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
                # Converte o valor para float e multiplica por 10
                set_value_float = float(set_value)
                set_value_multipled = int(set_value_float * 10)
                
                # Cria o comando com o valor multiplicado
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
            try:
                data = self.ser.readline().decode().strip()
                if data:
                    self.process_data(data)
            except serial.SerialException as e:
                self.log(f"Erro ao ler dados: {e}")

        self.root.after(100, self.read_serial_data)

    def process_data(self, data):
        self.log(data)
        try:
            # Supondo que os dados sejam separados por ponto e vírgula
            parts = data.split(';')
            if len(parts) == 5:
                self.temp1_label.config(text=f"Temp 1: {parts[0]} °C")
                self.temp2_label.config(text=f"Temp 2: {parts[1]} °C")
                self.pressure1_label.config(text=f"Pressão 1: {parts[2]} Bar")
                self.pressure2_label.config(text=f"Pressão 2: {parts[3]} Bar")
                self.flow_label.config(text=f"Vazão: {parts[4]} l/min")

               # timestamp = datetime.now().strftime('%H:%M:%S') se der ruim voltar neste
               # Obtém o timestamp atual e converte para segundos
                #now = datetime.now()
                #seconds = now.hour * 3600 + now.minute * 60 + now.second

                # Define o tempo de início, se ainda não estiver definido
                if self.start_time is None:
                    self.start_time = datetime.now()

                # Calcula o tempo decorrido desde o início em segundos
                now = datetime.now()
                seconds = (now - self.start_time).total_seconds()

                # Arredonda o tempo decorrido para 3 casas decimais
                seconds_rounded = round(seconds, 3)

                ##################################################################################################################
                # Adiciona os dados ao armazenamento
                self.data_storage.append({
                    'Time (s)': seconds_rounded,
                    'Temp1': self.temp1_label.cget("text").split(": ")[1],
                    'Temp2': self.temp2_label.cget("text").split(": ")[1],
                    'Pressão1': self.pressure1_label.cget("text").split(": ")[1],
                    'Pressão2': self.pressure2_label.cget("text").split(": ")[1],
                    'Vazão': self.flow_label.cget("text").split(": ")[1]
                })
                
                # Salva os dados em Excel
                self.save_to_excel()
                
            else:
                self.log("Dados recebidos no formato incorreto.")
                
        except Exception as e:
            self.log(f"Erro ao processar dados: {e}")

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.yview(tk.END)

 # Função para salvar dados em Excel
    def save_to_excel(self):
        if self.data_storage:
            df = pd.DataFrame(self.data_storage)
            file_path = os.path.join(self.save_directory, "dados_reais.xlsx")
            
            # Verifica se o diretório existe, se não, cria o diretório
            if not os.path.exists(self.save_directory):
                try:
                    os.makedirs(self.save_directory)
                    print(f"Diretório criado: {self.save_directory}")
                except Exception as e:
                    self.log(f"Erro ao criar diretório: {e}")
                    return

            try:
                df.to_excel(file_path, index=False)
                print(f"Dados salvos em {file_path}")
            except Exception as e:
                self.log(f"Erro ao salvar dados: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoApp(root)
    root.mainloop()
