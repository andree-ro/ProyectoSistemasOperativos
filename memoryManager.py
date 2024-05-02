import tkinter as tk
from tkinter import ttk
import threading
import time
from process import Process

# Constantes
MEMORY_SIZE = 102  # Tamaño de la memoria principal en bytes
OS_SPACE = 25  # Espacio reservado para el sistema operativo
TIME_QUANTUM = 2  # Tiempo de ráfaga (quantum) para Round-robin


# Clase para manejar la memoria principal y la planificación de procesos
class MemoryManager:
    def __init__(self, root):
        self.root = root
        self.memory = bytearray(MEMORY_SIZE)
        self.occupied_regions = []
        self.ready_queue = []
        self.running_process = None
        self.current_instruction = 0
        self.process_history = []
        self.system_clock = time.time()
        self.pending_processes = []  # Lista para almacenar los procesos ingresados

        # Configurar la interfaz gráfica
        self.setup_gui()

        # Iniciar el reloj del sistema
        self.update_system_clock()

    def setup_gui(self):
        # Ventana principal
        self.root.title("Simulación de Planificación y Control de Procesos")
        self.root.geometry("800x600")

        # Memoria principal
        memory_frame = tk.Frame(self.root)
        memory_frame.pack(side=tk.LEFT, padx=10, pady=10)

        memory_label = tk.Label(memory_frame, text="Memoria Principal")
        memory_label.pack()

        self.memory_canvas = tk.Canvas(memory_frame, width=400, height=400, bg="white")
        self.memory_canvas.pack()

        # Dibujar el espacio reservado para el sistema operativo
        os_start = 0
        os_end = OS_SPACE
        self.draw_process(os_start, os_end, "SO")

        # CPU
        cpu_frame = tk.Frame(self.root)
        cpu_frame.pack(side=tk.LEFT, padx=10, pady=10)

        cpu_label = tk.Label(cpu_frame, text="CPU")
        cpu_label.pack()

        self.instruction_label = tk.Label(cpu_frame, text="")
        self.instruction_label.pack()

        self.program_counter_label = tk.Label(cpu_frame, text="")
        self.program_counter_label.pack()

        # Reloj del sistema
        clock_frame = tk.Frame(self.root)
        clock_frame.pack(side=tk.TOP, padx=10, pady=10)

        clock_label = tk.Label(clock_frame, text="Reloj del Sistema")
        clock_label.pack()

        self.clock_label = tk.Label(clock_frame, text="")
        self.clock_label.pack()

        # Historial de procesos
        history_frame = tk.Frame(self.root)
        history_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        history_label = tk.Label(history_frame, text="Historial de Procesos")
        history_label.pack()

        self.history_tree = ttk.Treeview(history_frame, columns=("process_id", "state", "start_time", "end_time"))
        #self.history_tree.heading("#0", text="ID")
        self.history_tree.heading("process_id", text="ID")
        self.history_tree.heading("state", text="Estado")
        self.history_tree.heading("start_time", text="Hora de Inicio")
        self.history_tree.heading("end_time", text="Hora de Finalización")
        self.history_tree.pack()
        process_table_frame = tk.Frame(self.root)
        process_table_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        process_table_label = tk.Label(process_table_frame, text="Procesos Ingresados")
        process_table_label.pack()

        self.process_table = ttk.Treeview(process_table_frame, columns=("process_id", "arrival_time", "burst_time"))
        self.process_table.heading("process_id", text="ID")
        self.process_table.heading("arrival_time", text="Tiempo de Llegada")
        self.process_table.heading("burst_time", text="Tiempo de Consumo")
        self.process_table.pack()

        # Campos de entrada para agregar procesos
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.TOP, padx=10, pady=10)

        process_id_label = tk.Label(input_frame, text="ID del Proceso:")
        process_id_label.pack(side=tk.LEFT)
        self.process_id_entry = tk.Entry(input_frame)
        self.process_id_entry.pack(side=tk.LEFT)

        arrival_time_label = tk.Label(input_frame, text="Tiempo de Llegada (s):")
        arrival_time_label.pack(side=tk.LEFT)
        self.arrival_time_entry = tk.Entry(input_frame)
        self.arrival_time_entry.pack(side=tk.LEFT)

        burst_time_label = tk.Label(input_frame, text="Tiempo de Consumo (s):")
        burst_time_label.pack(side=tk.LEFT)
        self.burst_time_entry = tk.Entry(input_frame)
        self.burst_time_entry.pack(side=tk.LEFT)

        add_process_button = tk.Button(input_frame, text="Agregar Proceso", command=self.add_process_from_input)
        add_process_button.pack(side=tk.LEFT)

        start_processes_button = tk.Button(input_frame, text="Iniciar Procesos", command=self.start_processes)
        start_processes_button.pack(side=tk.LEFT)

    def update_memory_display(self):
        # Limpiar la representación gráfica de la memoria
        self.memory_canvas.delete("all")

        # Dibujar el espacio reservado para el sistema operativo
        os_start = 0
        os_end = OS_SPACE
        self.draw_process(os_start, os_end, "SO")

        # Dibujar los procesos en la memoria
        for start, end, process in self.occupied_regions:
            self.draw_process(start, end, process.process_id)


   
