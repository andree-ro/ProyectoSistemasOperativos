
# Clase para representar un proceso
class Process:
    def __init__(self, process_id, arrival_time, burst_time):
        self.process_id = process_id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.end_time = None
        self.state = "ready"
        self.base_register = None  # Inicializar base_register como None
        self.limit_register = None  # Inicializar limit_register como None

    def update_state(self, new_state):
        self.state = new_state

    def update_start_time(self, start_time):
        self.start_time = start_time

    def update_end_time(self, end_time):
        self.end_time = end_time