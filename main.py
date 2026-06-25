'''
Main entry point for the cloth simulation application.
This script initializes the Tkinter root window and hands control over to the ClothApp layout.
'''
import tkinter as tk
from cloth_simulation.app import ClothApp

if __name__ == "__main__":
    # Inizializza la finestra principale di Tkinter
    root = tk.Tk()

    # Istanzia l'applicazione logica/grafica
    app = ClothApp(root)

    # Avvia l'event loop di sistema
    root.mainloop()
