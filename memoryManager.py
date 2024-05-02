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


       def add_process_from_input(self):
        process_id = self.process_id_entry.get()
        arrival_time_text = self.arrival_time_entry.get()
        burst_time_text = self.burst_time_entry.get()

        if process_id and arrival_time_text and burst_time_text:
            try:
                arrival_time = int(arrival_time_text)
                burst_time = int(burst_time_text)
                new_process = Process(process_id, arrival_time, burst_time)
                self.pending_processes.append(new_process)
                self.process_table.insert("", "end", values=(process_id, arrival_time, burst_time))
            except ValueError:
                print("Los valores de tiempo deben ser números enteros.")

        # Limpiar los campos de entrada
        self.process_id_entry.delete(0, tk.END)
        self.arrival_time_entry.delete(0, tk.END)
        self.burst_time_entry.delete(0, tk.END)

    def start_processes(self):
        self.ready_queue = sorted(self.pending_processes, key=lambda p: p.arrival_time)
        self.pending_processes = []  # Limpiar la lista de procesos pendientes

        self.start_scheduler()

    def draw_process(self, start_address, end_address, process_id):
        x1 = start_address * 400 // MEMORY_SIZE
        y1 = 10
        x2 = (end_address + 1) * 400 // MEMORY_SIZE
        y2 = 390
        self.memory_canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black")
        self.memory_canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=process_id)


    def find_free_space(self, size):
        free_regions = []
        start = OS_SPACE
        for occupied_start, occupied_end, _ in self.occupied_regions:
            if occupied_start > start:
                free_regions.append((start, occupied_start - 1))
            start = occupied_end + 1
        if start < MEMORY_SIZE:
            free_regions.append((start, MEMORY_SIZE - 1))

        for start, end in free_regions:
            if end - start + 1 >= size:
                return start
        return None
    def start_scheduler(self):
        if self.running_process is None and self.ready_queue:
            self.schedule_next_process()

    def schedule_next_process(self):
        if self.ready_queue:
            self.running_process = self.ready_queue.pop(0)
            self.running_process.update_state("En ejecución")
            self.running_process.update_start_time(time.time())
            self.update_history()

            process_size = self.running_process.burst_time
            start_address = self.find_free_space(process_size)
            if start_address is not None:
                end_address = start_address + process_size - 1
                self.occupied_regions.append((start_address, end_address, self.running_process))
                self.running_process.base_register = start_address
                self.running_process.limit_register = end_address
                self.update_memory_display()
                self.root.update()  # Actualizar la pantalla
                self.current_instruction = self.running_process.base_register
                self.update_cpu_display()
                threading.Thread(target=self.run_process).start()
            else:
                self.ready_queue.append(self.running_process)
                self.running_process = None

    def run_process(self):
        start_time = time.time()
        while self.running_process and self.running_process.remaining_time > 0:
            time.sleep(10)  # Simular la ejecución de una instrucción más lentamente

            if self.running_process is not None:
                if self.running_process.base_register is not None:
                    self.current_instruction = self.running_process.base_register
                    self.current_instruction += 1
                else:
                    self.current_instruction = None

            self.update_cpu_display()

            self.running_process.remaining_time -= 1
            elapsed_time = time.time() - start_time

            if elapsed_time >= TIME_QUANTUM:
                self.running_process.update_state("Listo")
                self.ready_queue.append(self.running_process)
                self.running_process = None
                self.update_history()
                self.schedule_next_process()
                break

        if self.running_process is not None:
            self.running_process.update_state("Finalizado")
            self.running_process.update_end_time(time.time())
            self.update_history()
            self.remove_process_from_memory(self.running_process)
            self.running_process = None
            self.start_scheduler()

    def update_cpu_display(self):
        if self.running_process is not None:
            if self.current_instruction is not None:
                instruction_address = hex(self.current_instruction)
                self.instruction_label.config(text=f"Dirección de instrucción: {instruction_address}")
                self.program_counter_label.config(text=f"Program Counter: {instruction_address}")

    def update_history(self):
        for process in self.ready_queue + ([self.running_process] if self.running_process else []):
            process_data = (
                process.process_id,
                process.state,
                time.strftime("%H:%M:%S", time.localtime(process.start_time)) if process.start_time else "-",
                time.strftime("%H:%M:%S", time.localtime(process.end_time)) if process.end_time else "-",
            )
            self.history_tree.insert("", "end", values=process_data)

    def remove_process_from_memory(self, process):
        for i, (start, end, p) in enumerate(self.occupied_regions):
            if p == process:
                start_address, end_address, _ = self.occupied_regions.pop(i)
                process.base_register = None
                process.limit_register = None
                x1 = start_address * 400 // MEMORY_SIZE
                y1 = 10
                x2 = (end_address + 1) * 400 // MEMORY_SIZE
                y2 = 390
                self.memory_canvas.delete(self.memory_canvas.find_enclosed(x1, y1, x2, y2))
                self.update_memory_display()
                self.root.update()  # Actualizar la pantalla
                break

    def update_system_clock(self):
        current_time = time.strftime("%H:%M:%S", time.localtime(self.system_clock))
        self.clock_label.config(text=f"Hora del Sistema: {current_time}")
        self.system_clock += 1
        self.root.after(1000, self.update_system_clock)
