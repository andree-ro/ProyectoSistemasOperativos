import tkinter as tk
from memoryManager import MemoryManager

# Función principal
def main():
    root = tk.Tk()
    memory_manager = MemoryManager(root)

    root.mainloop()


if __name__ == "__main__":
    main()