"""
================================================================================
SIMULADOR INTERACTIVO DEL DOGMA CENTRAL DE LA BIOLOGÍA MOLECULAR
================================================================================
Práctica 1 de Bioinformática
Flujo integrado: ADN -> ADN (Replicación) -> ARN (Transcripción) -> Proteína (Traducción)

Este programa coordina los módulos:
  - replicacion.py : Helicasa, Primasa, Cadena líder, Fragmentos de Okazaki y Ligasa.
  - transcripcion.py: Cadena molde vs codificante, Burbuja de transcripción y ARNm.
  - traduccion.py  : Ribosoma, sitios A/P/E, ARNt, codones y síntesis de polipéptidos.

Autores/Defensa: Diseñado para máxima claridad docente ante el tribunal/profesor.
================================================================================
"""

import sys
import os
import time
from typing import Dict, Any, List, Optional

# Habilitar soporte para secuencias ANSI y codificación UTF-8 en Windows
if sys.platform.startswith("win"):
    os.system("")
    try:
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Importar la lógica de los 3 módulos biológicos
from replicacion import simular_replicacion, obtener_cadena_complementaria
from transcripcion import simular_transcripcion
from traduccion import simular_traduccion

# ==============================================================================
# PALETA DE COLORES ANSI Y FORMATO DE CONSOLA
# ==============================================================================
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    UNDER   = "\033[4m"
    
    # Colores de texto
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    
    # Fondos
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_GREEN   = "\033[42m"
    BG_DARK    = "\033[100m"


def limpiar_pantalla():
    """Limpia la pantalla según el sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar(modo_auto: bool = False, delay: float = 0.8, mensaje: str = "Pulsar [ENTER] para continuar..."):
    """Gestiona el ritmo de la presentación (automático con delay o manual para defensa)."""
    if modo_auto:
        time.sleep(delay)
    else:
        print(f"\n{C.DIM}  ▶ {mensaje}{C.RESET}", end="", flush=True)
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass


def safe_input(prompt: str = "") -> str:
    """Lee entrada del usuario de forma segura ante Ctrl+C o EOF."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return ""


def banner_principal():
    print(f"{C.CYAN}{C.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                                       ║")
    print("║             SIMULADOR BIOMOLECULAR DEL DOGMA CENTRAL                                  ║")
    print("║               Flujo de la Información Genética Celular                                ║")
    print("║                                                                                       ║")
    print("║       [ ADN ]  ====== (Replicación) ======>  [ ADN ]                                  ║")
    print("║          │                                                                            ║")
    print("║          └──────── (Transcripción) ───────>  [ ARNm ]                                 ║")
    print("║                                                 │                                     ║")
    print("║                                                 └───── (Traducción) ──> [ PROTEÍNA ]  ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════════════╝")
    print(f"{C.RESET}")


def seccion_header(titulo: str, subtitulo: str, icono: str = "🔬", color: str = C.CYAN):
    ancho = 87
    print("\n" + color + C.BOLD + "═" * ancho + C.RESET)
    print(f"{color}{C.BOLD} {icono}  {titulo.upper()} {C.RESET}")
    print(f"{C.WHITE}    {subtitulo}{C.RESET}")
    print(color + C.BOLD + "─" * ancho + C.RESET)


def mostrar_tarjeta_enzima(enzima: str, etapa: str, descripcion: str, visual: str, color_enzima: str = C.YELLOW):
    """Muestra un panel informativo de lo que está haciendo una enzima en tiempo real."""
    print(f"\n{C.BOLD}┌── {color_enzima}[ ENZIMA / FACTOR: {enzima} ]{C.RESET}{C.BOLD} ─────────────────────────────{C.RESET}")
    print(f"│ {C.CYAN}Etapa:{C.RESET} {C.BOLD}{etapa}{C.RESET}")
    
    # Formatear la descripción con sangría limpia
    for linea in descripcion.split("\n"):
        print(f"│ {C.WHITE}{linea}{C.RESET}")
    
    print(f"│")
    print(f"│ {C.GREEN}{C.BOLD}Representación molecular en tiempo real:{C.RESET}")
    for linea in visual.split("\n"):
        print(f"│   {C.YELLOW}{linea}{C.RESET}")
    print(f"{C.BOLD}└───────────────────────────────────────────────────────────────────────────────────{C.RESET}")


# ==============================================================================
# SECUENCIA DEMOSTRATIVA ÓPTIMA PARA DOCENCIA Y DEFENSA
# ==============================================================================
# Esta secuencia posee:
# 1. Longitud adecuada (~40 pb) para observar con claridad la apertura de horquilla y 3 fragmentos de Okazaki.
# 2. Codón de inicio ATG -> AUG en ARNm.
# 3. Varios aminoácidos con distintas propiedades (apolares, polares, cargados).
# 4. Codón de parada TAA -> UAA.
SECUENCIA_DEMO = "ATGGCCAACGTACGTTCAGATGAAGCCTACTAA"


def colorear_bases_dna(secuencia: str) -> str:
    """Colorea nucleótidos de ADN (A: Verde, T: Rojo, C: Azul, G: Amarillo)."""
    colores = {
        'A': f"{C.GREEN}A{C.RESET}",
        'T': f"{C.RED}T{C.RESET}",
        'C': f"{C.CYAN}C{C.RESET}",
        'G': f"{C.YELLOW}G{C.RESET}",
    }
    return "".join(colores.get(b, b) for b in secuencia)


def colorear_bases_arn(secuencia: str) -> str:
    """Colorea nucleótidos de ARN (A: Verde, U: Magenta, C: Azul, G: Amarillo)."""
    colores = {
        'A': f"{C.GREEN}A{C.RESET}",
        'U': f"{C.MAGENTA}U{C.RESET}",
        'C': f"{C.CYAN}C{C.RESET}",
        'G': f"{C.YELLOW}G{C.RESET}",
    }
    return "".join(colores.get(b, b) for b in secuencia)


# ==============================================================================
# EJECUCIÓN VISUAL: ETAPA 1 - REPLICACIÓN DEL ADN
# ==============================================================================
def ejecutar_replicacion(cadena_adn: str, modo_auto: bool = False) -> Dict[str, Any]:
    seccion_header(
        titulo="Etapa 1: Replicación Semiconservativa del ADN",
        subtitulo="Demostración de horquilla, síntesis continua (líder) y síntesis discontinua (Okazaki)",
        icono="🧬",
        color=C.CYAN
    )

    print(f"\n{C.BOLD}Molécula de ADN Bicatenario Original:{C.RESET}")
    cadena_comp = obtener_cadena_complementaria(cadena_adn)
    print(f"  Hebra 1 (5' -> 3'): 5'- {colorear_bases_dna(cadena_adn)} -3'")
    print(f"  Apareamiento bases:     {'|' * len(cadena_adn)}")
    print(f"  Hebra 2 (3' -> 5'): 3'- {colorear_bases_dna(cadena_comp)} -5'")
    
    pausar(modo_auto, delay=1.0, mensaje="Pulsar [ENTER] para activar la HELICASA y abrir la horquilla...")

    # Simular modelo biológico
    datos = simular_replicacion(cadena_adn, tam_okazaki=10, tam_primer=3)

    for i, paso in enumerate(datos["pasos"], 1):
        color_badge = C.MAGENTA if "Helicasa" in paso["enzima"] else (
            C.BLUE if "Primasa" in paso["enzima"] else (
                C.GREEN if "ADN Polimerasa III" in paso["enzima"] else (
                    C.YELLOW if "ADN Polimerasa I" in paso["enzima"] else C.CYAN
                )
            )
        )
        mostrar_tarjeta_enzima(
            enzima=paso["enzima"],
            etapa=f"[{i}/{len(datos['pasos'])}] {paso['etapa']}",
            descripcion=paso["descripcion"],
            visual=paso["visual"],
            color_enzima=color_badge
        )
        pausar(modo_auto, delay=1.2, mensaje="Pulsar [ENTER] para el siguiente evento enzimático...")

    # Resumen de replicación
    print(f"\n{C.GREEN}{C.BOLD}✔ REPLICACIÓN COMPLETADA: Se obtienen 2 moléculas bicatenarias idénticas (Semiconservativa):{C.RESET}")
    m1 = datos["resultado_final"]["molecula_1"]
    m2 = datos["resultado_final"]["molecula_2"]
    print(f"  {C.BOLD}Molécula Hija 1:{C.RESET}")
    print(f"    - Hebra antigua conservada : {m1['hebra_antigua']}")
    print(f"    - Hebra nueva sintetizada  : {m1['hebra_nueva']}  ({C.YELLOW}{m1['tipo_sintesis']}{C.RESET})")
    print(f"  {C.BOLD}Molécula Hija 2:{C.RESET}")
    print(f"    - Hebra antigua conservada : {m2['hebra_antigua']}")
    print(f"    - Hebra nueva sintetizada  : {m2['hebra_nueva']}  ({C.CYAN}{m2['tipo_sintesis']}{C.RESET})")

    pausar(modo_auto, delay=1.5, mensaje="Pulsar [ENTER] para pasar a la TRANSCRIPCIÓN...")
    return datos


# ==============================================================================
# EJECUCIÓN VISUAL: ETAPA 2 - TRANSCRIPCIÓN DEL ADN
# ==============================================================================
def ejecutar_transcripcion(cadena_adn: str, modo_auto: bool = False) -> Dict[str, Any]:
    seccion_header(
        titulo="Etapa 2: Transcripción del ADN a ARN Mensajero (ARNm)",
        subtitulo="Reconocimiento del promotor, lectura de cadena molde (3'->5') y síntesis 5'->3'",
        icono="🌀",
        color=C.MAGENTA
    )

    print(f"{C.BOLD}Doble hebra antes de transcribir:{C.RESET}")
    cadena_molde = obtener_cadena_complementaria(cadena_adn)
    print(f"  Cadena Codificante (sentido, 5'->3')   : 5'- {colorear_bases_dna(cadena_adn)} -3'")
    print(f"  Cadena Molde (antisentido leída, 3'->5'): 3'- {colorear_bases_dna(cadena_molde)} -5'")

    pausar(modo_auto, delay=1.0, mensaje="Pulsar [ENTER] para acoplar la ARN POLIMERASA...")

    datos = simular_transcripcion(cadena_adn, usar_cadena_como_molde=False)

    for i, paso in enumerate(datos["pasos"], 1):
        mostrar_tarjeta_enzima(
            enzima=paso["enzima"],
            etapa=f"[{i}/{len(datos['pasos'])}] {paso['etapa']}",
            descripcion=paso["descripcion"],
            visual=paso["visual"],
            color_enzima=C.MAGENTA
        )
        pausar(modo_auto, delay=1.2, mensaje="Pulsar [ENTER] para el siguiente paso de transcripción...")

    # Tabla comparativa didáctica (primeros 15 pb para no saturar)
    print(f"\n{C.BOLD}Comparativa de fidelidad de la información genética (primeras bases):{C.RESET}")
    print(f"  {'Posición':<10} | {'ADN Codificante':<16} | {'ADN Molde':<12} | {'ARNm Transcrito':<15}")
    print(f"  {'-'*10}-|-{'-'*16}-|-{'-'*12}-|-{'-'*15}")
    limite = min(12, len(datos["alineamiento"]))
    for item in datos["alineamiento"][:limite]:
        pos = item['posicion']
        cod = item['adn_codificante']
        mol = item['adn_molde']
        arn = item['arnm']
        print(f"  {pos:<10} | 5'- {cod} -3'         | 3'- {mol} -5'   | 5'- {C.MAGENTA}{arn}{C.RESET} -3'")
    if len(datos["alineamiento"]) > limite:
        print(f"  ... ({len(datos['alineamiento']) - limite} nucleótidos adicionales transcritos idénticamente)")

    print(f"\n{C.GREEN}{C.BOLD}✔ ARNm MADURO RESULTANTE (5' -> 3'):{C.RESET}")
    print(f"  5'- {colorear_bases_arn(datos['arnm_5_3'])} -3'")

    pausar(modo_auto, delay=1.5, mensaje="Pulsar [ENTER] para pasar a la TRADUCCIÓN...")
    return datos


# ==============================================================================
# EJECUCIÓN VISUAL: ETAPA 3 - TRADUCCIÓN DEL ARNm A PROTEÍNA
# ==============================================================================
def ejecutar_traduccion(arnm: str, modo_auto: bool = False) -> Dict[str, Any]:
    seccion_header(
        titulo="Etapa 3: Traducción y Síntesis de Proteínas",
        subtitulo="Ensamblaje del ribosoma, lectura de codones en sitios A-P-E y polimerización peptídica",
        icono="🏭",
        color=C.YELLOW
    )

    print(f"{C.BOLD}ARNm entrante al ribosoma:{C.RESET}")
    print(f"  5'- {colorear_bases_arn(arnm)} -3'")

    pausar(modo_auto, delay=1.0, mensaje="Pulsar [ENTER] para que la subunidad ribosómica menor escanee el ARNm...")

    datos = simular_traduccion(arnm, requerir_aug=True)

    if not datos["inicio_encontrado"]:
        print(f"\n{C.RED}{C.BOLD}⚠ AVISO BIOLÓGICO:{C.RESET} {datos['pasos'][0]['descripcion']}")
        return datos

    # Mostrar paso de iniciación
    mostrar_tarjeta_enzima(
        enzima=datos["pasos"][0]["enzima"],
        etapa="Iniciación del Ribosoma",
        descripcion=datos["pasos"][0]["descripcion"],
        visual=datos["pasos"][0]["visual"],
        color_enzima=C.GREEN
    )
    pausar(modo_auto, delay=1.0, mensaje="Pulsar [ENTER] para iniciar la elongación paso a paso...")

    # Mostrar los ciclos de elongación
    pasos_elongacion = [p for p in datos["pasos"] if "Elongación" in p["etapa"]]
    for paso in pasos_elongacion:
        mostrar_tarjeta_enzima(
            enzima=paso["enzima"],
            etapa=paso["etapa"],
            descripcion=paso["descripcion"],
            visual=paso["visual"],
            color_enzima=C.YELLOW
        )
        pausar(modo_auto, delay=0.8, mensaje="Pulsar [ENTER] para el siguiente codón/enlace peptídico...")

    # Mostrar paso de terminación
    paso_term = datos["pasos"][-1]
    mostrar_tarjeta_enzima(
        enzima=paso_term["enzima"],
        etapa=paso_term["etapa"],
        descripcion=paso_term["descripcion"],
        visual=paso_term["visual"],
        color_enzima=C.RED
    )

    # Detalle de la tabla de codones procesados
    print(f"\n{C.BOLD}Desglose de Codones y Aminoácidos:{C.RESET}")
    print(f"  {'Ciclo':<7} | {'Codón (ARNm)':<14} | {'Anticodón (ARNt)':<16} | {'Aminoácido':<12} | {'Propiedad'}")
    print(f"  {'-'*7}-|-{'-'*14}-|-{'-'*16}-|-{'-'*12}-|{'-'*25}")
    for item in datos["codones_leidos"]:
        c_arn = item['codon']
        c_anti = item['anticodon']
        aa = f"{item['aminoacido_3']} ({item['aminoacido_1']})"
        prop = item['propiedad']
        print(f"  #{item['ciclo']:<6} | 5'- {c_arn} -3'    | 3'- {c_anti} -5'     | {aa:<12} | {prop}")

    print(f"\n{C.GREEN}{C.BOLD}✔ CADENA POLIPEPTÍDICA FINAL SINTETIZADA:{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}{datos['cadena_proteica']}{C.RESET}")
    print(f"  Secuencia 1 letra: {C.BOLD}{datos['aminoacidos_1']}{C.RESET}")

    pausar(modo_auto, delay=1.5, mensaje="Pulsar [ENTER] para ver el Gran Resumen Integrado...")
    return datos


# ==============================================================================
# RESUMEN INTEGRADO FINAL (DOGMA COMPLETO)
# ==============================================================================
def mostrar_gran_resumen(dna_original: str, res_rep: Dict, res_trans: Dict, res_trad: Dict):
    seccion_header(
        titulo="Gran Resumen: Flujo Completo de la Información Biológica",
        subtitulo="Verificación de la continuidad del Dogma Central de la Biología Molecular",
        icono="🏆",
        color=C.GREEN
    )

    print(f"{C.BOLD}1. NIVEL ADN (Genoma original):{C.RESET}")
    print(f"   5'- {colorear_bases_dna(dna_original)} -3'")
    print(f"   3'- {colorear_bases_dna(obtener_cadena_complementaria(dna_original))} -5'")

    print(f"\n{C.BOLD}2. NIVEL REPLICACIÓN (ADN -> ADN):{C.RESET}")
    print(f"   - Helicasa abrió la horquilla de replicación.")
    print(f"   - Síntesis continua en cadena líder sobre molde 3'->5'.")
    print(f"   - Síntesis discontinua con {len(res_rep['fragmentos_okazaki'])} Fragmentos de Okazaki en cadena rezagada.")
    print(f"   - Reemplazo de cebadores por ADN Pol I y ligación covalente por ADN Ligasa.")
    print(f"   - Resultado: 2 dúplex de ADN bicatenario semiconservativo.")

    print(f"\n{C.BOLD}3. NIVEL TRANSCRIPCIÓN (ADN -> ARNm):{C.RESET}")
    print(f"   - ARN Polimerasa utilizó la cadena molde 3'->5'.")
    print(f"   - Incorporación de Uracilo (U) frente a Adenina (A).")
    print(f"   - Transcrito ARNm: 5'- {colorear_bases_arn(res_trans['arnm_5_3'])} -3'")

    print(f"\n{C.BOLD}4. NIVEL TRADUCCIÓN (ARNm -> Proteína):{C.RESET}")
    if res_trad["inicio_encontrado"]:
        print(f"   - Marco de lectura iniciado en codón AUG (Metionina).")
        print(f"   - Lectura de codones en sitios ribosomales A, P, E.")
        print(f"   - Terminación controlada por codón de parada.")
        print(f"   - Proteína madura: {C.BOLD}{C.CYAN}{res_trad['cadena_proteica']}{C.RESET}")
    else:
        print(f"   - Sin traducción por ausencia de codón de inicio.")

    print(f"\n{C.GREEN}{C.BOLD}¡Flujo del Dogma Central simulado con éxito y respaldado biológicamente!{C.RESET}\n")


# ==============================================================================
# GENERADOR OPCIONAL DE VISUALIZADOR WEB INTERACTIVO (HTML)
# ==============================================================================
def generar_reporte_html(dna_original: str, res_rep: Dict, res_trans: Dict, res_trad: Dict, archivo_salida: str = "simulador_dogma.html"):
    """
    Genera un archivo HTML interactivo con diseño moderno y esquemas visuales
    para que el alumno pueda abrirlo en el navegador y enseñárselo al profesor.
    """
    okazaki_cards = ""
    for f in res_rep["fragmentos_okazaki"]:
        okazaki_cards += f"""
        <div class="okazaki-box">
            <h4>Fragmento Okazaki #{f['numero']}</h4>
            <p><strong>Cebador ARN:</strong> <span class="arn-badge">{f['cebador_arn']}</span></p>
            <p><strong>ADN Pol III:</strong> <span class="dna-badge">{f['adn_sintetizado']}</span></p>
            <p><strong>ADN Maduro (tras Ligasa):</strong> <code>{f['dna_maduro']}</code></p>
        </div>
        """

    codones_rows = ""
    for item in res_trad.get("codones_leidos", []):
        codones_rows += f"""
        <tr>
            <td>#{item['ciclo']}</td>
            <td><strong>5'-{item['codon']}-3'</strong></td>
            <td>3'-{item['anticodon']}-5'</td>
            <td><span class="aa-pill">{item['aminoacido_3']} ({item['aminoacido_1']})</span></td>
            <td>{item['nombre']}</td>
            <td>{item['propiedad']}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador del Dogma Central de la Biología Molecular</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --primary: #38bdf8;
            --secondary: #818cf8;
            --accent: #34d399;
            --warning: #fbbf24;
            --text: #f1f5f9;
            --border: #334155;
        }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            padding: 2rem 0;
            border-bottom: 2px solid var(--border);
            margin-bottom: 2rem;
        }}
        h1 {{
            color: var(--primary);
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
        }}
        .subtitle {{
            color: #94a3b8;
            font-size: 1.1rem;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
        }}
        .card h2 {{
            margin-top: 0;
            color: var(--secondary);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .seq-box {{
            background: #090d16;
            padding: 1rem;
            border-radius: 8px;
            font-family: monospace;
            font-size: 1.1rem;
            overflow-x: auto;
            letter-spacing: 2px;
        }}
        .okazaki-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        .okazaki-box {{
            background: #111827;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid var(--warning);
        }}
        .arn-badge {{
            background: #ec4899;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .dna-badge {{
            background: #0284c7;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .aa-pill {{
            background: #10b981;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        th, td {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #0f172a;
            color: var(--primary);
        }}
        .bubble-pre {{
            background: #090d16;
            color: #38bdf8;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.95rem;
        }}
        .badge-enzima {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Simulación del Dogma Central de la Biología Molecular</h1>
            <p class="subtitle">Práctica 1 de Bioinformática | Replicación · Transcripción · Traducción</p>
        </header>

        <!-- SECUENCIA INICIAL -->
        <div class="card">
            <h2>🧬 Molécula de ADN Original</h2>
            <div class="seq-box">
                <span style="color: #64748b;">5'-</span> <strong>{dna_original}</strong> <span style="color: #64748b;">-3'</span> (Cadena Codificante)<br>
                <span style="color: #64748b;">3'-</span> <strong>{obtener_cadena_complementaria(dna_original)}</strong> <span style="color: #64748b;">-5'</span> (Cadena Molde)
            </div>
        </div>

        <!-- REPLICACIÓN -->
        <div class="card">
            <h2>⚡ Etapa 1: Replicación Semiconservativa</h2>
            <p><span class="badge-enzima">Helicasa</span> Desenrolla y rompe puentes de hidrógeno creando la horquilla.</p>
            <p><span class="badge-enzima">Cadena Líder</span> Síntesis continua en sentido 5'->3' sobre molde 3'->5'.</p>
            <p><span class="badge-enzima">Cadena Rezagada</span> Síntesis discontinua mediada por fragmentos de Okazaki, cebadores de ARN primasa y sellado final por ADN Ligasa.</p>
            
            <h3>Fragmentos de Okazaki Generados:</h3>
            <div class="okazaki-grid">
                {okazaki_cards}
            </div>
        </div>

        <!-- TRANSCRIPCIÓN -->
        <div class="card">
            <h2>🌀 Etapa 2: Transcripción a ARN Mensajero</h2>
            <p><span class="badge-enzima">ARN Polimerasa</span> Lee la cadena molde de 3' a 5' e incorpora Uracilo (U) frente a Adenina (A).</p>
            
            <h3>Esquema de la Burbuja de Transcripción:</h3>
            <pre class="bubble-pre">{res_trans['burbuja_ascii']}</pre>

            <h3>Secuencia de ARNm Madura (5' -> 3'):</h3>
            <div class="seq-box" style="color: #f472b6;">
                5'- {res_trans['arnm_5_3']} -3'
            </div>
        </div>

        <!-- TRADUCCIÓN -->
        <div class="card">
            <h2>🏭 Etapa 3: Traducción y Síntesis Proteica</h2>
            <p><span class="badge-enzima">Ribosoma (Sitios A, P, E)</span> Escaneo 5'-UTR, reconocimiento de codón de inicio <strong>AUG (Metionina)</strong> y elongación hasta codón de parada.</p>
            
            <h3>Proteína Sintetizada:</h3>
            <div class="seq-box" style="color: #34d399; font-size: 1.25rem;">
                {res_trad.get('cadena_proteica', 'N/A')}
            </div>

            <h3>Desglose de Codones leídos por el Ribosoma:</h3>
            <table>
                <thead>
                    <tr>
                        <th>Ciclo</th>
                        <th>Codón (ARNm)</th>
                        <th>Anticodón (ARNt)</th>
                        <th>Aminoácido</th>
                        <th>Nombre</th>
                        <th>Propiedad Química</th>
                    </tr>
                </thead>
                <tbody>
                    {codones_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n{C.GREEN}{C.BOLD}✔ Reporte visual interactivo exportado en: {archivo_salida}{C.RESET}")


# ==============================================================================
# MENÚ INTERACTIVO PRINCIPAL
# ==============================================================================
def main():
    while True:
        limpiar_pantalla()
        banner_principal()
        print(f"{C.BOLD}OPCIONES DEL SIMULADOR:{C.RESET}")
        print(f"  {C.CYAN}[1]{C.RESET} Ejecutar Simulación Completa con Secuencia Demostrativa (Recomendado para defensa)")
        print(f"  {C.CYAN}[2]{C.RESET} Ejecutar Simulación Completa con Secuencia de ADN Personalizada")
        print(f"  {C.CYAN}[3]{C.RESET} Ejecutar solo Replicación del ADN (Horquilla y Okazaki)")
        print(f"  {C.CYAN}[4]{C.RESET} Ejecutar solo Transcripción (ADN a ARNm)")
        print(f"  {C.CYAN}[5]{C.RESET} Ejecutar solo Traducción (ARNm a Proteína)")
        print(f"  {C.CYAN}[6]{C.RESET} Salir")
        print()

        opcion = safe_input(f"{C.BOLD}Selecciona una opción (1-6): {C.RESET}").strip()

        if opcion in ["6", ""]:
            print(f"\n{C.CYAN}¡Hasta pronto! Mucho éxito en tu defensa de Bioinformática.{C.RESET}\n")
            break

        if opcion not in ["1", "2", "3", "4", "5"]:
            print(f"{C.RED}Opción no válida. Presiona ENTER para continuar...{C.RESET}")
            safe_input()
            continue

        # Modo de ritmo de avance
        print(f"\n{C.BOLD}Elige el ritmo de la presentación:{C.RESET}")
        print(f"  {C.GREEN}[1]{C.RESET} Modo Paso a Paso interactivo (Pulsar ENTER para avanzar, ideal para defender)")
        print(f"  {C.YELLOW}[2]{C.RESET} Modo Automático Cinemático (Avanza con pausas en tiempo real)")
        modo_ritmo = safe_input(f"{C.BOLD}Opción (1/2, por defecto 1): {C.RESET}").strip()
        modo_auto = (modo_ritmo == "2")

        # Secuencia a utilizar
        secuencia_adn = SECUENCIA_DEMO
        if opcion == "2":
            print(f"\n{C.WHITE}Introduce la secuencia de ADN (sentido 5'->3', solo bases A, T, C, G):{C.RESET}")
            sec_usr = safe_input(f"{C.BOLD}ADN: {C.RESET}").strip().upper()
            bases_validas = set("ATCG")
            if not sec_usr or not set(sec_usr).issubset(bases_validas):
                print(f"{C.RED}Error: La secuencia contiene caracteres no válidos o está vacía.{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
                continue
            secuencia_adn = sec_usr

        limpiar_pantalla()

        # Ejecución según opción
        if opcion in ["1", "2"]:
            res_rep = ejecutar_replicacion(secuencia_adn, modo_auto=modo_auto)
            res_trans = ejecutar_transcripcion(secuencia_adn, modo_auto=modo_auto)
            res_trad = ejecutar_traduccion(res_trans["arnm_5_3"], modo_auto=modo_auto)
            mostrar_gran_resumen(secuencia_adn, res_rep, res_trans, res_trad)
            
            # Ofrecer exportación a visor HTML
            print(f"{C.BOLD}¿Deseas exportar el reporte gráfico interactivo en HTML? (s/n, por defecto s): {C.RESET}", end="")
            resp_html = safe_input().strip().lower()
            if resp_html in ["", "s", "si", "y", "yes"]:
                generar_reporte_html(secuencia_adn, res_rep, res_trans, res_trad)

        elif opcion == "3":
            ejecutar_replicacion(secuencia_adn, modo_auto=modo_auto)

        elif opcion == "4":
            ejecutar_transcripcion(secuencia_adn, modo_auto=modo_auto)

        elif opcion == "5":
            if opcion == "5" and opcion != "2":
                # Convertir demo a ARN o pedir ARN
                arn_demo = SECUENCIA_DEMO.replace("T", "U")
                ejecutar_traduccion(arn_demo, modo_auto=modo_auto)
            else:
                arn_trans = simular_transcripcion(secuencia_adn)["arnm_5_3"]
                ejecutar_traduccion(arn_trans, modo_auto=modo_auto)

        print(f"\n{C.CYAN}Fin de la simulación. Pulsa [ENTER] para volver al menú principal...{C.RESET}")
        safe_input()


if __name__ == "__main__":
    main()
