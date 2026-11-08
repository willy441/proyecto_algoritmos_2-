"""Punto de entrada al sistema del taller automotriz."""
from pathlib import Path
from inventario.app import SistemaInventario

if __name__ == "__main__":
    SistemaInventario(Path(__file__).resolve().parent / "datos" / "inventario.csv").ejecutar()
