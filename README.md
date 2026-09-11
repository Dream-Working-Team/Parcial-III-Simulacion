# Parcial III: Simulación de Sistemas y Métodos Cuantitativos
### Universidad José Antonio Páez — Facultad de Ingeniería — Escuela de Ingeniería en Computación

Sistema profesional e integral de **Simulación de Sistemas** desarrollado en Python bajo el paradigma de **Programación Orientada a Objetos (POO)**. Modela dos problemas de alta complejidad (Eventos Discretos y Simulación Continua con Ecuaciones Diferenciales Ordinarias), integra diagnóstico inteligente mediante APIs de **Inteligencia Artificial (Google Gemini Flash / OpenAI / Ollama)**, exporta trazas detalladas y reportes ejecutivos a disco, e incluye una **interfaz gráfica interactiva y animada desarrollada en Pygame** como resolución del problema bonus.

---

## 📋 Tabla de Contenidos
1. [Modelos Matemáticos y Problemas Implementados](#-modelos-matemáticos-y-problemas-implementados)
   - [Problema 1: Simulación de Eventos Discretos (Fábrica de Laptops)](#1-problema-1-simulación-de-eventos-discretos-8-puntos)
   - [Problema 2: Simulación Continua (Clúster Térmico de Servidores)](#2-problema-2-simulación-continua-8-puntos)
   - [Pregunta Bonus: Animación Gráfica Interactiva en Pygame](#3-pregunta-bonus-animación-interactiva-en-pygame-2-puntos)
2. [Arquitectura del Software (POO y Principios SOLID)](#-arquitectura-del-software-poo-y-principios-solid)
3. [Integración con Inteligencia Artificial y Optimización de Tokens](#-integración-con-inteligencia-artificial-y-optimización-de-tokens)
4. [Instalación y Configuración](#-instalación-y-configuración)
5. [Guía de Uso del Menú Interactivo](#-guía-de-uso-del-menú-interactivo)
6. [Estructura de Trazas y Reportes Generados](#-estructura-de-trazas-y-reportes-generados)
7. [Cumplimiento de Pautas de Evaluación](#-cumplimiento-de-pautas-de-evaluación)

---

## 🔬 Modelos Matemáticos y Problemas Implementados

### 1. Problema 1: Simulación de Eventos Discretos (8 puntos)
**Contexto**: Una línea de producción de laptops cuenta con una estación de ensamblaje única y un inventario crítico de procesadores de alta gama.

* **Proceso de Llegadas**: Proceso estocástico de Poisson con tasa $\lambda = 10 \text{ órdenes/hora}$.
  $$T_{\text{arribo}} \sim \text{Exponencial}\left(\lambda = \frac{10}{3600} \text{ seg}^{-1}\right)$$
* **Proceso de Ensamble (Servicio)**: Distribución Exponencial con media $\mu_{\text{servicio}} = 5 \text{ minutos}$ ($300\text{ s}$).
  $$T_{\text{servicio}} \sim \text{Exponencial}\left(\frac{1}{300} \text{ seg}^{-1}\right)$$
* **Política de Inventario $(s, Q)$**:
  - Umbral crítico de reorden: $s = 10 \text{ unidades}$.
  - Tamaño de lote del proveedor: $Q = 50 \text{ unidades}$.
  - Tiempo de entrega del proveedor (*Lead Time*): $L = 15 \text{ minutos}$.
  - Condición de parada de línea: Si el stock llega a 0 al momento de ensamblar una orden, la estación se bloquea (`DETENIDA_SIN_STOCK`), registrando la detención y el tiempo fuera de servicio. Al recibir el lote del proveedor, la línea se reactiva inmediatamente.
* **Métricas Clave Calculadas**:
  - Tiempo de espera promedio en cola ($\bar{W}_q$).
  - Tiempo total promedio en el sistema ($\bar{W}$).
  - Tiempo medio de despacho por lote de 50 laptops.
  - Cantidad de detenciones de línea por desabastecimiento y duración total detenida.
  - Órdenes retrasadas por falta de procesador y porcentaje de eficiencia en el reabastecimiento (*Fill Rate*).

---

### 2. Problema 2: Simulación Continua (8 puntos)
**Contexto**: Clúster de servidores de alto rendimiento sujeto a carga continua de red con balance térmico y disipación líquida.

* **Tráfico Entrante**: Variable continua $R_{\text{tráfico}}(t) \sim \mathcal{N}(\mu = 3.0 \text{ Gbps}, \sigma = 1.0 \text{ Gbps})$, acotado físicamente en el intervalo $[1.0, 5.0] \text{ Gbps}$ mediante un proceso Ornstein-Uhlenbeck para asegurar continuidad temporal suave.
* **Ecuación Diferencial de Balance Térmico**:
  $$\frac{dT}{dt} = \dot{Q}_{\text{generado}}(t) - \dot{Q}_{\text{disipado}}(t)$$
  $$\dot{Q}_{\text{generado}}(t) = k_{\text{heat}} \cdot R_{\text{procesado}}(t)$$
  $$\dot{Q}_{\text{disipado}}(t) = k_{\text{cool}} \cdot \left(T(t) - T_{\text{refrigerante}}\right)$$
  - Calibración en equilibrio: A tráfico nominal de $3.0 \text{ Gbps}$, la generación iguala la disipación a la temperatura operativa de $70^\circ\text{C}$ con refrigerante líquido a $25^\circ\text{C}$.
  - Método de Resolución: Integración numérica **Runge-Kutta de 4to Orden (RK4)** con paso temporal $\Delta t = 2.0\text{ s}$.
* **Estrangulamiento Térmico (*Thermal Throttling*)**:
  - Si $T \le 70^\circ\text{C}$: El clúster opera a eficiencia nominal del $90\%$ ($\eta = 0.90$).
  - Si $T > 70^\circ\text{C}$: Se activa *Thermal Throttling* para evitar daño en hardware, reduciendo la eficiencia linealmente hasta un piso mínimo del $20\%$:
    $$\eta(T) = \max\left(0.20, 0.90 - 0.06 \cdot (T - 70.0)\right)$$
* **Métricas Clave Calculadas**:
  - Total de Terabytes recibidos vs. efectivamente procesados (*Throughput*).
  - Eficiencia global de red ($\%$).
  - Temperatura promedio, mínima, máxima y desviación estándar ($\sigma_T$).
  - Tiempo acumulado bajo estrangulamiento térmico y diagnóstico de viabilidad operativa continua.

---

### 3. Pregunta Bonus: Animación Interactiva en Pygame (2 puntos)
Interfaz gráfica con estética moderna en modo oscuro, renderizado dinámico a 60 FPS y desacoplamiento POO:
* **Problema 1 (Fábrica)**: Cinta de laptops en cola, estación de ensamble con estados de color dinámico (**Verde** = Libre, **Amarillo** = Ensamblando, **Rojo Pulsante** = Parada por Falta de Stock) y medidor vertical de stock de procesadores con línea de umbral crítico ($< 10$).
* **Problema 2 (Clúster)**: Rack de servidores con actividad de LEDs de CPUs, aspas de refrigeración líquida giratorias, termómetro vertical dinámico (degradado azul a rojo crítico) y osciloscopio en tiempo real con la evolución temporal de la temperatura y la línea límite de 70°C.
* **Controles Interactivos**:
  - `[ESPACIO]`: Pausar o reanudar la animación sin congelar el hilo lógico.
  - `[TAB]`: Alternar instantáneamente entre la vista de la Fábrica (P1) y del Servidor (P2).
  - `[1] - [5]`: Control dinámico de velocidad (1x, 5x, 20x, 50x, 150x).
  - `[R]`: Reiniciar simulación.
  - `[ESC]`: Regresar al menú de consola.

---

## 🏛️ Arquitectura del Software (POO y Principios SOLID)

El sistema aplica estrictamente el paradigma orientado a objetos, separando la lógica matemática de la presentación y los servicios de infraestructura:

```text
Parcial-III-Simulacion/
├── config.py                        # Configuración centralizada y lectura de .env
├── main.py                          # Menú principal interactivo y validaciones
├── requirements.txt                 # Dependencias del proyecto
├── .env                             # Variables de entorno locales y claves de API
├── .env.example                     # Plantilla de variables de entorno
│
├── core/                            # Servicios transversales
│   ├── logger.py                    # Gestor de trazas con marcas de tiempo [HH:MM:SS]
│   └── validator.py                 # Validador de consola con rangos y defaults al pulsar Enter
│
├── simulation_discrete/             # Problema 1: Eventos Discretos
│   ├── models.py                    # LaptopOrder, AssemblyStation, InventoryManager
│   ├── events.py                    # Event, OrderArrivalEvent, AssemblyCompleteEvent, RestockArrivalEvent
│   ├── engine.py                    # DiscreteEventSimulator (min-heap priority queue)
│   └── metrics.py                   # DiscreteMetricsCollector
│
├── simulation_continuous/           # Problema 2: Simulación Continua EDO
│   ├── models.py                    # TrafficGenerator, ThermalModel (RK4), ServerCluster
│   ├── engine.py                    # ContinuousSimulator
│   └── metrics.py                   # ContinuousMetricsCollector
│
├── ai_service/                      # Conectores de Inteligencia Artificial (4 puntos)
│   ├── base.py                      # BaseAIProvider (Interfaz abstracta)
│   ├── prompts.py                   # AIPromptBuilder (Prompts predeterminados de alta densidad y bajo token)
│   ├── gemini_provider.py           # Conector Google Gemini REST API (gemini-flash-latest)
│   ├── openai_provider.py           # Conector OpenAI REST API (gpt-4o-mini)
│   ├── ollama_provider.py           # Conector Ollama local (llama3)
│   ├── fallback_provider.py         # Analista cuantitativo offline (Garantía de cero caídas)
│   └── factory.py                   # AIFactory con RobustAIWrapper
│
├── visualization/                   # Módulo Bonus en Pygame
│   ├── common.py                    # Paleta de colores, geometría y HUD superior
│   ├── discrete_view.py             # Renderizador visual de la Fábrica de Laptops
│   ├── continuous_view.py           # Renderizador visual del Clúster Térmico
│   └── visualizer.py                # Controlador de ventana, bucle de eventos y reloj
│
├── reports/                         # Gestión de reportes y trazas en disco
│   ├── reporter.py                  # Escritura de archivos .txt estructurados
│   └── output/                      # Directorio de almacenamiento de salidas
│
└── tests/                           # Pruebas automatizadas unitarias
    └── test_simulations.py          # Verificación con pytest
```

---

## 🤖 Integración con Inteligencia Artificial y Optimización de Tokens

La integración cumple a cabalidad con la pauta de 4 puntos:
1. **Consumo de API Real**: Conectado a la API oficial de Google Gemini (`gemini-flash-latest`), admitiendo también OpenAI y Ollama.
2. **Optimización de Tokens**: Mediante `ai_service/prompts.py`, los datos cuantitativos se serializan en un formato JSON compacto y se envían muestras representativas de trazas (inicio, eventos críticos y final), reduciendo el costo de entrada a ~300 tokens y la respuesta a ~350-450 tokens.
3. **Resiliencia Operativa (`RobustAIWrapper`)**: Si la API externa experimenta saturación de cuota temporal (HTTP 503/429) o no hay conexión a internet, el sistema activa automáticamente su **motor analista cuantitativo offline**, generando conclusiones analíticas completas sin interrumpir la ejecución ni generar errores fatales.

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone git@github.com:Dream-Working-Team/Parcial-III-Simulacion.git
cd Parcial-III-Simulacion
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar API Key en el archivo `.env`
El archivo `.env` ya viene configurado con el proveedor Gemini:
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=tu_clave_de_gemini_aqui
GEMINI_MODEL=gemini-flash-latest
```

---

## 💻 Guía de Uso del Menú Interactivo

Ejecute la aplicación principal:
```bash
python main.py
```

Se desplegará el menú interactivo:
* **Opción [1]**: Ejecuta la simulación de eventos discretos. Al solicitar la duración en horas, presione `[Enter]` para aceptar el valor de prueba por defecto (8 horas de turno laboral). Muestra trazas, métricas, conclusión de la IA y genera los archivos de texto en disco.
* **Opción [2]**: Ejecuta la simulación continua. Presione `[Enter]` para aceptar el valor por defecto (24 horas de operación continua del clúster). Muestra balance térmico, Terabytes procesados, análisis de IA y guarda el reporte.
* **Opción [3]**: Lanza la ventana gráfica interactiva de **Pygame**. Utilice `[TAB]` para alternar entre la Fábrica y el Servidor, y `[ESPACIO]` para pausar.
* **Opción [4]**: Realiza un test de diagnóstico de conectividad con la API de IA.
* **Opción [5]**: Lista los reportes y archivos de trazas almacenados en la carpeta `reports/output/`.

---

## 📊 Cumplimiento de Pautas de Evaluación

| # | Pauta del Examen | Estado de Cumplimiento en el Proyecto |
| :---: | :--- | :--- |
| **1** | Evaluación individual o equipo de hasta 3 personas. | Cumplido. |
| **2** | Usar paradigma de programación orientada a objetos (POO). | Cumplido rigurosamente con clases de dominio, encapsulamiento, interfaces abstractas y desacoplamiento. |
| **3** | Consumir API de la IA y generar conclusión y archivos de texto (4 ptos). | Cumplido: Se consulta Gemini Flash, se imprime conclusión en pantalla y se guarda en `reports/output/*.txt`. |
| **4** | Utilizar repositorio GitHub. | Cumplido: Estructurado directamente dentro del repositorio `Parcial-III-Simulacion`. |
| **5** | Código original sin duplicidad ni plagio. | Cumplido: Diseño propio, modular y estructurado según principios DRY/SOLID. |
| **6** | Entrega y defensa presencial. | Cumplido: Código ordenado, comentado y autodocumentado para defensa en clase. |
| **7** | Validaciones de datos introducidos por el usuario en comandos. | Cumplido: Módulo `core/validator.py` con validación estricta de rangos y tipos numéricos. |
| **8** | Código comentado. | Cumplido: Docstrings detallados en español en todos los módulos, clases y métodos. |
| **9** | Datos por defecto para tomarlos como prueba. | Cumplido: Todas las entradas admiten valores predeterminados recomendados con solo presionar `Enter`. |
| **+** | **Pregunta Bonus: Animación interactiva en Pygame (2 ptos)**. | **Cumplido al 100%**: HUD en vivo, sincronización de clases POO, animación de ambos problemas y controles por teclado. |
