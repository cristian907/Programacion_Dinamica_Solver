# Modelo de Tamaño de la Fuerza de Trabajo — Programación Dinámica

**Universidad José Antonio Páez**  
**Facultad de Ingeniería — Escuela de Computación**  
**Asignatura:** Métodos Cuantitativos / Investigación de Operaciones  
**Evaluación:** Modelo de tamaño de la fuerza de trabajo (3 ptos)

---

## 📌 1. Descripción del Problema

Un contratista estima que el tamaño de la fuerza de trabajo necesaria durante las siguientes 5 semanas es de **5, 7, 8, 4 y 6 trabajadores**, respectivamente. 

* **Demandas mínimas semanales:**
  $$\begin{matrix} b_1 = 5, & b_2 = 7, & b_3 = 8, & b_4 = 4, & b_5 = 6 \end{matrix}$$
* **Costo de mano de obra excedente:** $\$300$ por trabajador por semana (personal ocioso retenido para evitar despidos o futuras contrataciones).
* **Costo de contratación:** Incurre en un **costo fijo de $\$400$** más **$\$200$ por trabajador** contratado por semana.
* **Fuerza de trabajo inicial ($x_0$):** $0$ trabajadores al comenzar el horizonte.

**Objetivo:** Determinar la política óptima de contratación y tamaño de plantilla para cada semana que minimice el costo total acumulado del proyecto utilizando **Programación Dinámica Determinística**.

---

## 📐 2. Formulación Matemática del Modelo

El modelo se descompone en etapas según el Principio de Optimalidad de Richard Bellman:

1. **Etapas ($i$):** Representan cada una de las semanas del horizonte de planificación ($i = 1, 2, 3, 4, 5$).
2. **Variable de Estado ($x_{i-1}$):** Número de trabajadores disponibles provenientes de la semana anterior ($i-1$). Condición inicial: $x_0 = 0$.
3. **Variable de Decisión ($x_i$):** Número de trabajadores asignados/empleados durante la semana $i$.
   $$\text{Restricción de factibilidad: } x_i \ge b_i \quad (\text{satisface la demanda requerida})$$
   $$\text{Cota superior práctica: } x_i \le \max_{k \ge i}\{b_k\} = 8$$
4. **Funciones de Costo Inmediato:**
   * **Costo de Excedente:**
     $$C_{\text{exceso}}(x_i) = 300 \cdot (x_i - b_i)$$
   * **Costo de Contratación:**
     $$C_{\text{contr}}(x_{i-1}, x_i) = \begin{cases} 400 + 200 \cdot (x_i - x_{i-1}) & \text{si } x_i > x_{i-1} \\ 0 & \text{si } x_i \le x_{i-1} \end{cases}$$
   * **Costo Directo de la Etapa:**
     $$g_i(x_{i-1}, x_i) = C_{\text{exceso}}(x_i) + C_{\text{contr}}(x_{i-1}, x_i)$$
5. **Ecuación Recursiva de Bellman (Hacia Atrás):**
   $$f_i(x_{i-1}) = \min_{x_i \ge b_i} \left\{ g_i(x_{i-1}, x_i) + f_{i+1}(x_i) \right\}$$
   con condición terminal de frontera:
   $$f_{6}(x_5) = 0$$

---

## 🏆 3. Resumen de la Solución y Plan Óptimo

### Costo Mínimo Total: **$3,300.00**

| Semana ($i$) | Demanda ($b_i$) | Personal Inicial ($x_{i-1}$) | Personal Asignado ($x_i^*$) | Contrataciones | Excedente | Costo Contratación | Costo Excedente | Costo Semanal | Costo Acumulado |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 5 | 0 | **5** | 5 | 0 | $1,400.00 | $0.00 | $1,400.00 | $1,400.00 |
| **2** | 7 | 5 | **8** | 3 | 1 | $1,000.00 | $300.00 | $1,300.00 | $2,700.00 |
| **3** | 8 | 8 | **8** | 0 | 0 | $0.00 | $0.00 | $0.00 | $2,700.00 |
| **4** | 4 | 8 | **6** | 0 | 2 | $0.00 | $600.00 | $600.00 | $3,300.00 |
| **5** | 6 | 6 | **6** | 0 | 0 | $0.00 | $0.00 | $0.00 | **$3,300.00** |

### Análisis Gerencial del Trade-off:
* **Semana 2:** Se eleva la plantilla a **8 trabajadores** en lugar de solo los 7 requeridos. Aunque se incurre en un excedente de $\$300$, se evita pagar el costo fijo de contratación de $\$400$ al iniciar la Semana 3 (demanda 8). **Ahorro neto: $\$100$**.
* **Semana 4:** Se reduce la plantilla a **6 trabajadores** en lugar de bajarla hasta 4. Mantener 2 obreros ociosos cuesta $\$600$, pero evita tener que recontratar 2 obreros en la Semana 5 (demanda 6), lo cual habría costado $\$400 + 2 \times \$200 = \$800$. **Ahorro neto: $\$200$**.

---

## 🏛️ 4. Arquitectura del Software (Clean Architecture + POO)

El proyecto fue diseñado bajo los principios de **Clean Architecture** (Robert C. Martin), separando estrictamente responsabilidades en capas concéntricas e independientes de frameworks externos:

```
Tarea5_ProgramacionDinamica/
├── src/
│   ├── domain/                  # CAPA 1: Reglas de negocio puras y entidades
│   │   ├── entities.py          # WorkforceParameters, DecisionEvaluation, StageTable, OptimizationResult
│   │   └── exceptions.py        # DomainValidationError, InvalidDemandError, etc.
│   ├── application/             # CAPA 2: Casos de uso y contratos abstractos (Protocolos)
│   │   ├── interfaces.py        # IWorkforceSolver, IReportExporter (Inversión de dependencias)
│   │   ├── dtos.py              # SolveProblemDTO, ExportReportDTO
│   │   └── use_cases.py         # SolveWorkforceModelUseCase, ExportReportUseCase
│   ├── infrastructure/          # CAPA 3: Algoritmos concretos y servicios externos
│   │   ├── dp_solver.py         # DynamicProgrammingWorkforceSolver (Backward recursion)
│   │   ├── text_exporter.py     # TextReportExporter (Generador del informe .txt)
│   │   └── chart_service.py     # ChartService (Visualizaciones analíticas con Matplotlib)
│   ├── presentation/            # CAPA 4: Interfaz de usuario (CustomTkinter + CLI)
│   │   ├── controllers.py       # WorkforceController
│   │   └── views/
│   │       ├── main_window.py   # Ventana principal moderna con pestañas y selector de temas
│   │       ├── tabs/            # Pestañas modulares (Parámetros, Etapas, Plan, Gráficos, Teoría)
│   │       └── components/      # ModernTableView (Tabla ttk estilizada con scrollbars)
│   └── main.py                  # Entrypoint: Inyección de dependencias y bootstrap
├── tests/                       # Pruebas unitarias automatizadas (Pytest)
│   ├── test_domain.py           # Validaciones de dominio e invariantes
│   ├── test_dp_solver.py        # Verificación rigurosa del costo $3,300 y etapas
│   └── test_use_cases.py        # Pruebas de integración de casos de uso
├── salidas_problema.txt         # Salidas paso por paso generadas por el programa (Requisito 2)
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Documentación académica y técnica
```

---

## 🚀 5. Instalación y Ejecución

### Requisitos Previos
* Python 3.10 o superior (compatible con Python 3.11, 3.12, 3.13, 3.14).
* Entorno virtual de Python recomendado.

### Instalación de Dependencias
```bash
# Crear y activar entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate  # En Linux / macOS
# .venv\Scripts\activate   # En Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar la Aplicación Gráfica (GUI)
Para abrir la interfaz gráfica moderna interactiva:
```bash
python src/main.py
```
* **Características de la GUI:**
  * Modo Oscuro / Modo Claro dinámico.
  * Inspección interactiva etapa por etapa (Etapa 5 a 1) con decisiones óptimas destacadas en verde.
  * Cronograma semanal con tarjetas de indicadores (KPIs).
  * Gráficos analíticos integrados de demanda vs personal y estructura de costos.
  * Botón para exportar el reporte `.txt` con selector de archivo.

### Ejecutar en Modo Consola (CLI)
Si estás en un servidor sin pantalla o deseas imprimir directamente las tablas paso por paso en la terminal:
```bash
python src/main.py --cli
```
Este comando ejecuta el modelo, muestra todas las tablas detalladas en consola y actualiza automáticamente el archivo `salidas_problema.txt`.

### Ejecutar las Pruebas Unitarias
```bash
pytest -v
```
Se ejecutan 12 pruebas automatizadas que validan:
* Invariantes del dominio y manejo de excepciones.
* Exactitud matemática de cada tabla de etapa y del costo total ($3,300.00).
* Correcto funcionamiento de los casos de uso y la exportación de archivos.

---

## 📄 6. Archivo de Salidas (`salidas_problema.txt`)

De acuerdo con la **Pauta 2** del enunciado (*«Subir las salidas del programa en un archivo txt»*), el archivo [`salidas_problema.txt`](salidas_problema.txt) contiene:
1. Encabezado institucional de la UJAP.
2. Definición formal de parámetros.
3. Formulación de las ecuaciones de Bellman.
4. **Tablas paso a paso de cada etapa (Etapas 5, 4, 3, 2 y 1)** con evaluación de excesos, contrataciones, costos inmediatos y costos futuros.
5. Cuadro resumen de la trayectoria y política óptima semana a semana.
6. Justificación gerencial del plan adoptado.
