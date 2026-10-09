"""
Componente reutilizable de Tabla Moderna.
Utiliza ttk.Treeview estilizado para integrarse perfectamente con CustomTkinter.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import List, Tuple, Any, Dict


class ModernTableView(ctk.CTkFrame):
    """
    Tabla estilizada con scrollbars vertical y horizontal,
    filas alternadas y resaltado de filas óptimas.
    """

    def __init__(
        self,
        master: Any,
        columns: List[Tuple[str, str, int]],  # (column_id, header_text, width)
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)
        self.column_configs = columns
        self._setup_style()
        self._build_tree()

    def _setup_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        # Configuración de apariencia oscura/elegante para el Treeview
        style.configure(
            "Modern.Treeview",
            background="#23272a",
            foreground="#f0f0f0",
            fieldbackground="#23272a",
            rowheight=28,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#1e2124",
            foreground="#3498db",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
            relief="flat",
        )
        style.map(
            "Modern.Treeview.Heading",
            background=[("active", "#2c3e50")],
            foreground=[("active", "#5dade2")],
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", "#2980b9")],
            foreground=[("selected", "#ffffff")],
        )

    def _build_tree(self) -> None:
        col_ids = [c[0] for c in self.column_configs]
        self.tree = ttk.Treeview(
            self,
            columns=col_ids,
            show="headings",
            style="Modern.Treeview",
            selectmode="browse",
        )

        for col_id, title, width in self.column_configs:
            self.tree.heading(col_id, text=title)
            self.tree.column(col_id, width=width, anchor="center", stretch=True)

        # Scrollbars
        v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.tree.yview)
        h_scroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tags de color para filas
        self.tree.tag_configure("even", background="#282b30")
        self.tree.tag_configure("odd", background="#23272a")
        self.tree.tag_configure(
            "optimal",
            background="#145a32",
            foreground="#a9dfbf",
            font=("Segoe UI", 10, "bold"),
        )
        self.tree.tag_configure(
            "highlight_plan",
            background="#1b4f72",
            foreground="#d4e6f1",
            font=("Segoe UI", 10, "bold"),
        )

    def set_rows(self, rows_data: List[Tuple[Any, ...]], is_optimal_flags: List[bool] = None) -> None:
        """Limpia e inserta nuevas filas."""
        self.clear()
        for idx, row in enumerate(rows_data):
            if is_optimal_flags and idx < len(is_optimal_flags) and is_optimal_flags[idx]:
                tag = "optimal"
            else:
                tag = "even" if idx % 2 == 0 else "odd"

            self.tree.insert("", "end", values=row, tags=(tag,))

    def clear(self) -> None:
        """Elimina todos los elementos del Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
