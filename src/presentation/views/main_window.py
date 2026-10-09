"""
Ventana Principal de la Aplicación (CustomTkinter).
Contenedor principal que orquesta todas las pestañas, controles de tema y exportación.
"""

import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
from src.presentation.controllers import WorkforceController
from .tabs.input_tab import InputTab
from .tabs.stages_tab import StagesTab
from .tabs.optimal_plan_tab import OptimalPlanTab
from .tabs.chart_tab import ChartTab
from .tabs.theory_tab import TheoryTab


class MainWindow(ctk.CTk):
    """Ventana principal de la aplicación gráfica."""

    def __init__(self, controller: WorkforceController) -> None:
        super().__init__()
        self.controller = controller

        # Configuración inicial de ventana
        self.title("Optimización de Fuerza de Trabajo — Programación Dinámica | UJAP")
        self.geometry("1180x780")
        self.minsize(980, 650)

        # Configuración de apariencia
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self._build_ui()
        self._load_and_solve_default()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Encabezado Superior (Header)
        header_frame = ctk.CTkFrame(self, fg_color="#1e2124", corner_radius=0, height=65)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Título y subtítulo
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        main_title = ctk.CTkLabel(
            title_box,
            text="OPTIMIZACIÓN DEL TAMAÑO DE LA FUERZA DE TRABAJO",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#3498db",
        )
        main_title.pack(anchor="w")

        sub_title = ctk.CTkLabel(
            title_box,
            text="Universidad José Antonio Páez — Escuela de Computación | Programación Dinámica",
            font=ctk.CTkFont(size=11),
            text_color="#95a5a6",
        )
        sub_title.pack(anchor="w")

        # Controles a la derecha (Switch de tema)
        right_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_header.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        self.theme_switch = ctk.CTkSwitch(
            right_header,
            text="Modo Oscuro",
            command=self._toggle_theme,
            onvalue="Dark",
            offvalue="Light",
            font=ctk.CTkFont(size=12),
        )
        self.theme_switch.select()
        self.theme_switch.pack(side="right")

        # 2. Contenedor de Pestañas (Tabview)
        self.tabview = ctk.CTkTabview(self, corner_radius=10, fg_color="#282b30")
        self.tabview.grid(row=1, column=0, padx=15, pady=(5, 5), sticky="nsew")

        # Nombres de pestañas
        self.tab_input_name = "⚙️ Parámetros"
        self.tab_stages_name = "📋 Etapas Paso a Paso"
        self.tab_plan_name = "🏆 Plan Óptimo & Costos"
        self.tab_chart_name = "📈 Gráficos Analíticos"
        self.tab_theory_name = "📚 Fundamento Teórico"

        self.tab_input = self.tabview.add(self.tab_input_name)
        self.tab_stages = self.tabview.add(self.tab_stages_name)
        self.tab_plan = self.tabview.add(self.tab_plan_name)
        self.tab_chart = self.tabview.add(self.tab_chart_name)
        self.tab_theory = self.tabview.add(self.tab_theory_name)

        # Instanciar vistas dentro de las pestañas
        self.input_view = InputTab(
            self.tab_input,
            on_solve_callback=self._handle_solve,
            on_reset_callback=self._handle_reset,
        )
        self.input_view.pack(fill="both", expand=True)

        self.stages_view = StagesTab(self.tab_stages)
        self.stages_view.pack(fill="both", expand=True)

        self.plan_view = OptimalPlanTab(self.tab_plan)
        self.plan_view.pack(fill="both", expand=True)

        self.chart_view = ChartTab(self.tab_chart)
        self.chart_view.pack(fill="both", expand=True)

        self.theory_view = TheoryTab(self.tab_theory)
        self.theory_view.pack(fill="both", expand=True)

        # 3. Barra Inferior de Acciones y Estado (Footer)
        footer_frame = ctk.CTkFrame(self, fg_color="#1e2124", corner_radius=0, height=45)
        footer_frame.grid(row=2, column=0, sticky="ew")
        footer_frame.grid_columnconfigure(0, weight=1)

        self.status_lbl = ctk.CTkLabel(
            footer_frame,
            text="Listo para optimizar.",
            font=ctk.CTkFont(size=12),
            text_color="#2ecc71",
        )
        self.status_lbl.grid(row=0, column=0, padx=20, pady=8, sticky="w")

        # Botón Exportar TXT
        self.export_btn = ctk.CTkButton(
            footer_frame,
            text="💾 Exportar Salidas a TXT",
            command=self._handle_export,
            fg_color="#3498db",
            hover_color="#2980b9",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=180,
        )
        self.export_btn.grid(row=0, column=1, padx=20, pady=8, sticky="e")

    def _toggle_theme(self) -> None:
        mode = "Dark" if self.theme_switch.get() == "Dark" else "Light"
        ctk.set_appearance_mode(mode)
        self.theme_switch.configure(text=f"Modo {mode}")

    def _load_and_solve_default(self) -> None:
        """Carga los parámetros por defecto de la UJAP y resuelve automáticamente al iniciar."""
        default_dto = self.controller.get_default_parameters()
        self.input_view.set_inputs(
            demands=list(default_dto.demands),
            excess_cost=default_dto.excess_holding_cost,
            hiring_fixed=default_dto.hiring_fixed_cost,
            hiring_var=default_dto.hiring_variable_cost,
            initial_workforce=default_dto.initial_workforce,
        )
        self._handle_solve()

    def _handle_reset(self) -> None:
        """Restablece los campos a los valores del enunciado UJAP."""
        default_dto = self.controller.get_default_parameters()
        self.input_view.set_inputs(
            demands=list(default_dto.demands),
            excess_cost=default_dto.excess_holding_cost,
            hiring_fixed=default_dto.hiring_fixed_cost,
            hiring_var=default_dto.hiring_variable_cost,
            initial_workforce=default_dto.initial_workforce,
        )
        self.status_lbl.configure(
            text="Valores oficiales restablecidos: [5, 7, 8, 4, 6], C1=$300, K=$400, c=$200, x0=0.",
            text_color="#3498db",
        )

    def _handle_solve(self) -> None:
        """Lee los datos de entrada, ejecuta el algoritmo de P.D. y actualiza todas las vistas."""
        try:
            inputs = self.input_view.get_inputs()
        except Exception as e:
            messagebox.showerror("Error de Entrada", f"Verifique los valores numéricos ingresados:\n{str(e)}")
            return

        result, err = self.controller.solve(
            demands=inputs["demands"],
            excess_cost=inputs["excess_cost"],
            hiring_fixed=inputs["hiring_fixed"],
            hiring_var=inputs["hiring_var"],
            initial_workforce=inputs["initial_workforce"],
        )

        if err is not None:
            messagebox.showerror("Error de Validación", err)
            self.status_lbl.configure(text=err, text_color="#e74c3c")
            return

        if result:
            # Actualizar vistas
            self.stages_view.display_result(result)
            self.plan_view.display_result(result)
            self.chart_view.display_result(result)

            self.status_lbl.configure(
                text=f"✓ Optimización exitosa. Costo total mínimo: ${result.total_minimal_cost:,.2f}",
                text_color="#2ecc71",
            )

    def _handle_export(self) -> None:
        """Abre un diálogo de guardado y exporta el reporte en formato .txt."""
        if not self.controller.last_result:
            messagebox.showwarning("Aviso", "Primero debe resolver el modelo antes de exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile="salidas_problema.txt",
            title="Guardar Salidas del Programa",
        )

        if not file_path:
            return

        success, msg = self.controller.export_report(file_path)
        if success:
            messagebox.showinfo("Exportación Exitosa", msg)
            self.status_lbl.configure(text=f"✓ Archivo exportado: {os.path.basename(file_path)}", text_color="#2ecc71")
        else:
            messagebox.showerror("Error de Exportación", msg)
            self.status_lbl.configure(text=msg, text_color="#e74c3c")
