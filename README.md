# Práctica 1: Simulación del Dogma Central de la Biología Molecular

Este proyecto es un simulador pedagógico e interactivo que modela el flujo completo de la información genética celular:

$$\text{ADN} \xrightarrow{\text{Replicación}} \text{ADN} \xrightarrow{\text{Transcripción}} \text{ARNm} \xrightarrow{\text{Traducción}} \text{Proteína}$$

Desarrollado para la asignatura de **Bioinformática**, diseñado para ser claro, modular, didáctico y fácilmente defendible ante un tribunal o profesor.

---

## 📁 Arquitectura del Código

El proyecto está estructurado modularmente en **4 archivos principales**:

```text
BIO-simulacion-dogma-central/
│
├── replicacion.py      # Lógica de replicación del ADN (helicasa, primasa, líder, rezagada, Okazaki y ligasa)
├── transcripcion.py    # Lógica de transcripción (ADN molde 3'->5' a ARNm 5'->3', complementariedad U-A)
├── traduccion.py       # Código genético, ribosoma (sitios A, P, E), ARNt y síntesis de polipéptidos
├── main.py             # Interfaz de consola interactiva en tiempo real, menús y exportador HTML
│
├── pyproject.toml      # Configuración del entorno
└── README.md           # Guía pedagógica y manual de uso
```

---

## 🧬 Fundamento Biológico y Procesos Simulados

### 1. Replicación Semiconservativa (`replicacion.py`)
- **Apertura de la Horquilla**:
  - **Helicasa**: Rompe los puentes de hidrógeno entre las bases nitrogenadas.
  - **Topoisomerasa / Girasa**: Alivia la tensión torsional por delante de la horquilla.
  - **Proteínas SSB (Single-Stranded Binding)**: Evitan la reasociación prematura de las cadenas sencillas.
- **Cadena Líder / Adelantada (Continuous Strand)**:
  - Sobre el molde $3' \to 5'$, la **ARN Primasa** coloca un cebador inicial y la **ADN Polimerasa III** sintetiza de forma continua en dirección $5' \to 3'$ avanzando hacia la horquilla.
- **Cadena Rezagada / Retrasada (Lagging Strand) y Fragmentos de Okazaki**:
  - Sobre el molde $5' \to 3'$, la síntesis es discontinua en sentido contrario al avance de la horquilla.
  - La **ARN Primasa** añade cebadores periódicos.
  - La **ADN Polimerasa III** elonga cada cebador produciendo los **Fragmentos de Okazaki**.
  - La **ADN Polimerasa I** degrada los cebadores de ARN (actividad exonucleasa $5' \to 3'$) y rellena con nucleótidos de ADN.
  - La **ADN Ligasa** cataliza los enlaces fosfodiéster sellando las muescas (*nicks*) entre fragmentos contiguos.
- **Resultado Semiconservativo**: Se obtienen 2 moléculas bicatenarias idénticas, cada una con una hebra parental original y una hebra de nueva síntesis.

---

### 2. Transcripción (`transcripcion.py`)
- **Cadena Codificante vs. Molde**:
  - **Cadena Molde (antisentido, $3' \to 5'$)**: Es la leída físicamente por la polimerasa.
  - **Cadena Codificante (sentido, $5' \to 3'$)**: Misma secuencia que el ARNm (sustituyendo T por U).
- **ARN Polimerasa**:
  - Reconoce la región promotora (ej. caja TATA) y abre localmente la doble hélice formando la **Burbuja de Transcripción**.
  - Lee el molde de $3' \to 5'$ e incorpora ribonucleótidos trifosfato (rNTPs) en sentido $5' \to 3'$.
  - Regla de complementariedad estricta:
    - $\text{Adenina (molde)} \to \text{Uracilo (ARNm)}$
    - $\text{Timina (molde)} \to \text{Adenina (ARNm)}$
    - $\text{Citosina (molde)} \to \text{Guanina (ARNm)}$
    - $\text{Guanina (molde)} \to \text{Citosina (ARNm)}$
- **Terminación**:
  - Al alcanzar la señal de terminación, se libera el **ARNm maduro** y el ADN recupera su conformación original.

---

### 3. Traducción (`traduccion.py`)
- **Código Genético Universal**:
  - Diccionario completo de 64 codones $\to$ 20 aminoácidos estándar + 3 codones de parada (*Stop*).
- **Iniciación**:
  - La subunidad menor del ribosoma escanea el ARNm en el extremo $5'$ hasta localizar el codón de inicio **AUG**.
  - El primer ARNt iniciador ($3'-\text{UAC}-5'$) cargado con **Metionina (Met)** se acopla directamente en el **Sitio P**.
- **Elongación en los Sitios Ribosomales**:
  - **Sitio A (Aminoacilo)**: Entrada del nuevo aminoacil-ARNt complementario al codón expuesto.
  - **Sitio P (Peptidilo)**: La enzima **peptidil transferasa** cataliza el enlace peptídico transfiriendo la cadena al nuevo aminoácido.
  - **Sitio E (Exit / Salida)**: El ARNt desacilado pasa al sitio E y es expulsado.
  - **Translocación**: El ribosoma avanza 3 nucleótidos ($1 \text{ codón}$) en dirección $5' \to 3'$.
- **Terminación**:
  - Al entrar un codón de parada (`UAA`, `UAG`, `UGA`), los **Factores de Liberación (RF)** inducen la hidrólisis del enlace éster, liberando el polipéptido maduro ($\text{N-terminal} \to \text{C-terminal}$) y disociando el ribosoma.

---

## 🚀 Cómo Ejecutar el Simulador

### Requisitos
- Python 3.10 o superior (compatible con Python 3.14).
- Sin dependencias externas obligatorias (usa únicamente la librería estándar de Python).

### Ejecución
Abre una terminal en el directorio del proyecto y ejecuta:

```bash
python main.py
```
*(o si usas el entorno virtual de uv)*:
```bash
.\.venv\Scripts\python.exe main.py
```

### Modos de Uso Disponibles
1. **Modo Paso a Paso Interactivo (Recomendado para la defensa con el profesor)**:
   - Permite pulsar `[ENTER]` entre cada evento enzimático, dándote tiempo para explicar cada detalle biológico.
2. **Modo Automático Cinemático**:
   - Avanza de forma fluida con pausas cronometradas y animaciones en consola.
3. **Secuencia de Entrada**:
   - **Demostración guiada**: Utiliza una secuencia calibrada pedagógicamente para mostrar múltiples fragmentos de Okazaki, codón AUG y parada.
   - **Personalizada**: Puedes introducir cualquier secuencia arbitraria de ADN para poner a prueba el simulador.
4. **Exportador Gráfico HTML**:
   - Al finalizar, puedes generar automáticamente un archivo `simulador_dogma.html` para visualizarlo con gráficos y tablas interactivas en cualquier navegador web.
