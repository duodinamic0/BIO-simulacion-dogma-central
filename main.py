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
from typing import Dict, Any, List, Optional, Tuple

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


def input_editable(prompt: str, texto_inicial: str = "") -> str:
    """
    Permite al usuario editar una cadena pre-rellenada directamente en la consola.
    Soporta Backspace, escritura y Enter manteniendo el texto previo editable.
    """
    if not sys.stdin.isatty():
        resp = safe_input(f"{prompt} (ENTER para conservar '{texto_inicial}'): ").strip()
        return resp if resp else texto_inicial

    # Intentar con readline en entornos que lo soportan
    try:
        import readline
        readline.set_startup_hook(lambda: readline.insert_text(texto_inicial))
        try:
            return input(prompt).strip()
        finally:
            readline.set_startup_hook()
    except Exception:
        pass

    # En Windows interactivo usando msvcrt nativo
    if sys.platform.startswith("win"):
        try:
            import msvcrt
            sys.stdout.write(prompt)
            sys.stdout.write(texto_inicial)
            sys.stdout.flush()

            buffer = list(texto_inicial)

            while True:
                ch = msvcrt.getwch()
                if ch in ('\r', '\n'):  # Enter
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return "".join(buffer).strip()
                elif ch == '\x08':  # Backspace
                    if buffer:
                        buffer.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch in ('\x00', '\xe0'):  # Tecla especial (flechas, etc.)
                    _ = msvcrt.getwch()
                elif ch == '\x03':  # Ctrl+C
                    sys.stdout.write("\n")
                    raise KeyboardInterrupt
                elif ch.isprintable():
                    buffer.append(ch)
                    sys.stdout.write(ch)
                    sys.stdout.flush()
        except (KeyboardInterrupt, EOFError):
            return ""
        except Exception:
            pass

    # Fallback estándar
    resp = safe_input(f"{prompt} [ENTER para mantener '{texto_inicial}']: ").strip()
    return resp if resp else texto_inicial


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
# 2. Señal molde TAC -> AUG en ARNm (codón de inicio).
# 3. Varios aminoácidos con distintas propiedades (apolares, polares, cargados).
# 4. Señal de parada ATT -> UAA en ARNm.
SECUENCIA_DEMO = "TACCGGTTGCATGCAAGTCTACTTCGGATGATT"


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


def leer_archivo_fasta(ruta_archivo: str) -> Tuple[str, str]:
    """
    Lee un archivo en formato FASTA sin librerías externas.
    Soporta rutas con comillas, espacios y múltiples líneas de secuencia.
    Retorna una tupla: (cabecera, secuencia_adn_limpia).
    """
    ruta_limpia = os.path.expanduser(ruta_archivo.strip().strip('"').strip("'"))
    if not os.path.exists(ruta_limpia):
        raise FileNotFoundError(f"No se encontró ningún archivo en la ruta: '{ruta_limpia}'")

    cabecera = ""
    lineas_secuencia = []

    with open(ruta_limpia, "r", encoding="utf-8", errors="replace") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            if linea.startswith(">"):
                if not cabecera:
                    cabecera = linea[1:].strip()
            else:
                lineas_secuencia.append(linea)

    secuencia = "".join(lineas_secuencia).upper().replace(" ", "").replace("\t", "").replace("\r", "")
    if not secuencia:
        raise ValueError("El archivo FASTA no contiene secuencia de nucleótidos.")

    return cabecera, secuencia


def insertar_o_modificar_arnm(arnm_actual: str) -> str:
    """
    Permite al usuario interactuar directamente con la cadena de ARNm para colocar el codón AUG:
    - [1] Añadir 'AUG' al principio de la cadena (5'-AUG...).
    - [2] Modificar directamente la cadena de ARNm en la consola (precargada con el texto previo de ARN).
    """
    # Garantizar que la cadena de muestra sea formalmente ARN (reemplazando cualquier residuo T por U)
    arnm_actual = arnm_actual.upper().replace('T', 'U').strip()
    bases_arn_validas = set("AUCG")

    while True:
        print(f"\n{C.BOLD}Molécula de ARNm transcrita (sin codón de inicio AUG):{C.RESET}")
        print(f"  ARNm (5' -> 3'): 5'- {colorear_bases_arn(arnm_actual)} -3'  (Longitud: {len(arnm_actual)} ribonucleótidos)")
        print(f"\n{C.BOLD}¿Cómo deseas incorporar el codón de inicio 'AUG' para la traducción?{C.RESET}")
        print(f"  {C.CYAN}[1]{C.RESET} Añadir 'AUG' automáticamente al inicio del ARNm (5'-AUG...)")
        print(f"  {C.CYAN}[2]{C.RESET} Modificar directamente la cadena de ARNm en la consola")
        sub_op = safe_input(f"{C.BOLD}Selecciona opción (1/2, por defecto 1): {C.RESET}").strip()

        if sub_op in ["", "1"]:
            nuevo_arn = "AUG" + arnm_actual
            print(f"\n{C.GREEN}✔ Codón de inicio 'AUG' añadido al extremo 5' del ARNm con éxito:{C.RESET}")
            print(f"  ARNm resultante: 5'- {colorear_bases_arn(nuevo_arn)} -3'")
            return nuevo_arn

        elif sub_op == "2":
            print(f"\n{C.WHITE}Modifica la cadena de ARNm (coloca 'AUG' donde desees):{C.RESET}")
            print(f"{C.DIM}Cadena de ARNm precargada. Usa Backspace para borrar y escribe donde quieras poner el AUG:{C.RESET}")
            nuevo_arn = input_editable(f"{C.BOLD}ARNm (5'->3'): {C.RESET}", texto_inicial=arnm_actual).strip().upper()

            # Si el usuario escribe 'T' por inercia (ej. ATG), se convierte automáticamente a ribonucleótido 'U'
            if 'T' in nuevo_arn:
                nuevo_arn = nuevo_arn.replace('T', 'U')
                print(f"{C.DIM}(Se convirtieron automáticamente las 'T' introducidas a ribonucleótidos 'U'){C.RESET}")

            if not nuevo_arn or not set(nuevo_arn).issubset(bases_arn_validas):
                print(f"{C.RED}Error: La cadena contiene caracteres no válidos para ARN (solo se admiten A, U, C, G).{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
            elif "AUG" not in nuevo_arn:
                print(f"{C.YELLOW}Aviso: La cadena aún no contiene el codón de inicio 'AUG'.{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
            else:
                print(f"\n{C.GREEN}✔ Cadena de ARNm modificada con éxito:{C.RESET}")
                print(f"  ARNm resultante: 5'- {colorear_bases_arn(nuevo_arn)} -3'")
                return nuevo_arn


CODONES_STOP_INFO = {
    "UAA": "Ocre",
    "UAG": "Ámbar",
    "UGA": "Ópalo"
}


def buscar_stop_en_fase(arnm: str, idx_aug: int) -> Tuple[bool, int, Optional[str]]:
    """
    Busca si existe un codón de parada (UAA, UAG, UGA) en fase de lectura abierta (ORF)
    a partir del codón AUG (avanzando de 3 en 3 nucleótidos).
    """
    for i in range(idx_aug + 3, len(arnm) - 2, 3):
        triplete = arnm[i:i+3]
        if triplete in CODONES_STOP_INFO:
            return True, i, triplete
    return False, -1, None


def verificar_y_asegurar_codon_parada(arnm: str) -> str:
    """
    Comprueba si existe un codón de parada (UAA, UAG, UGA) en fase de lectura a partir del AUG.
    Si no existe, ofrece al usuario 2 opciones pedagógicas:
      [1] Añadir al final un codón de parada (a elegir entre UAA, UAG, UGA),
          solicitando los 1 o 2 nucleótidos que falten para completar el codón anterior.
      [2] Añadir/modificar directamente la cadena de ARNm para colocar el codón de parada,
          mostrando los codones posibles y solicitando los 1 o 2 nucleótidos que falten si no está en fase.
    """
    arnm = arnm.upper().replace('T', 'U').strip()
    bases_arn_validas = set("AUCG")
    idx_aug = arnm.find("AUG")

    if idx_aug == -1:
        return arnm

    tiene_stop, pos_stop, codon_stop = buscar_stop_en_fase(arnm, idx_aug)
    if tiene_stop:
        print(f"\n{C.GREEN}✔ Codón de parada detectado en fase de lectura:{C.RESET} {C.BOLD}{codon_stop}{C.RESET} ({CODONES_STOP_INFO[codon_stop]}) en posición {pos_stop + 1}.")
        return arnm

    print(f"\n{C.YELLOW}{C.BOLD}══════════════════════════════════════════════════════════════════════════════════{C.RESET}")
    print(f"{C.RED}{C.BOLD}⚠ AVISO BIOLÓGICO: No se ha detectado ningún codón de parada en fase de lectura.{C.RESET}")
    print(f"{C.WHITE}A partir del codón de inicio AUG, la cadena carece de señal de terminación (UAA, UAG o UGA).{C.RESET}")
    print(f"{C.WHITE}El ribosoma requiere un codón de parada para finalizar la síntesis y liberar la proteína.{C.RESET}")
    print(f"{C.YELLOW}{C.BOLD}══════════════════════════════════════════════════════════════════════════════════{C.RESET}")

    while True:
        print(f"\n{C.BOLD}¿Cómo deseas incorporar el codón de parada (frenada)?{C.RESET}")
        print(f"  {C.CYAN}[1]{C.RESET} Añadir al final un codón de parada (a elegir entre UAA, UAG, UGA)")
        print(f"  {C.CYAN}[2]{C.RESET} Añadir tú mismo el codón de parada directamente en la secuencia de ARNm")
        sub_op = safe_input(f"{C.BOLD}Selecciona opción (1/2, por defecto 1): {C.RESET}").strip()

        if sub_op in ["", "1"]:
            # Opción 1: Elegir codón de parada para añadir al final
            print(f"\n{C.BOLD}Elige el codón de parada que deseas añadir al final:{C.RESET}")
            print(f"  {C.CYAN}[1]{C.RESET} UAA (Codón Ocre - Señal universal más frecuente)")
            print(f"  {C.CYAN}[2]{C.RESET} UAG (Codón Ámbar)")
            print(f"  {C.CYAN}[3]{C.RESET} UGA (Codón Ópalo)")
            op_cod = safe_input(f"{C.BOLD}Selecciona codón de parada (1-3, por defecto 1 [UAA]): {C.RESET}").strip()
            
            mapeo_stops = {"1": "UAA", "2": "UAG", "3": "UGA", "": "UAA"}
            stop_elegido = mapeo_stops.get(op_cod, "UAA")

            # Comprobar si los nucleótidos desde AUG hasta el final completan codones de 3
            orf_actual = arnm[idx_aug:]
            sobrante = len(orf_actual) % 3
            arnm_ajustado = arnm

            if sobrante == 1:
                nuc_incompleto = arnm[-1]
                print(f"\n{C.YELLOW}⚠ Aviso de marco de lectura:{C.RESET}")
                print(f"  La secuencia de ARNm tras el AUG no completa el último codón antes del codón de parada.")
                print(f"  El último triplete solo tiene 1 nucleótido: {C.BOLD}'{nuc_incompleto}'{C.RESET}.")
                print(f"  Faltan {C.BOLD}2 nucleótidos{C.RESET} (A, U, C, G) para completar este codón antes de añadir '{stop_elegido}'.")
                
                while True:
                    nucs_add = safe_input(f"{C.BOLD}Introduce los 2 nucleótidos que faltan (ej. CG): {C.RESET}").strip().upper().replace('T', 'U')
                    if len(nucs_add) == 2 and set(nucs_add).issubset(bases_arn_validas):
                        arnm_ajustado = arnm + nucs_add
                        print(f"{C.GREEN}✔ Codón anterior completado: '{arnm_ajustado[-3:]}' con éxito.{C.RESET}")
                        break
                    print(f"{C.RED}Error: Debes introducir exactamente 2 nucleótidos válidos para ARN (A, U, C, G).{C.RESET}")

            elif sobrante == 2:
                nucs_incompletos = arnm[-2:]
                print(f"\n{C.YELLOW}⚠ Aviso de marco de lectura:{C.RESET}")
                print(f"  La secuencia de ARNm tras el AUG no completa el último codón antes del codón de parada.")
                print(f"  El último triplete solo tiene 2 nucleótidos: {C.BOLD}'{nucs_incompletos}'{C.RESET}.")
                print(f"  Falta {C.BOLD}1 nucleótido{C.RESET} (A, U, C, G) para completar este codón antes de añadir '{stop_elegido}'.")
                
                while True:
                    nuc_add = safe_input(f"{C.BOLD}Introduce el nucleótido que falta (A, U, C, G): {C.RESET}").strip().upper().replace('T', 'U')
                    if len(nuc_add) == 1 and nuc_add in bases_arn_validas:
                        arnm_ajustado = arnm + nuc_add
                        print(f"{C.GREEN}✔ Codón anterior completado: '{arnm_ajustado[-3:]}' con éxito.{C.RESET}")
                        break
                    print(f"{C.RED}Error: Debes introducir exactamente 1 nucleótido válido para ARN (A, U, C, G).{C.RESET}")

            arnm_final = arnm_ajustado + stop_elegido
            print(f"\n{C.GREEN}✔ Codón de parada '{stop_elegido}' ({CODONES_STOP_INFO[stop_elegido]}) añadido al final con éxito:{C.RESET}")
            print(f"  ARNm resultante: 5'- {colorear_bases_arn(arnm_final)} -3'")
            return arnm_final

        elif sub_op == "2":
            # Opción 2: El usuario escribe/modifica el codón de parada en la consola
            print(f"\n{C.WHITE}Modifica la cadena de ARNm para colocar el codón de parada donde desees:{C.RESET}")
            print(f"{C.BOLD}Codones de parada disponibles en el código genético:{C.RESET}")
            print(f"  • {C.YELLOW}UAA{C.RESET} (Ocre)   • {C.YELLOW}UAG{C.RESET} (Ámbar)   • {C.YELLOW}UGA{C.RESET} (Ópalo)")
            print(f"{C.DIM}Cadena de ARNm precargada. Usa Backspace para borrar y escribe donde quieras poner el codón de parada:{C.RESET}")

            nuevo_arn = input_editable(f"{C.BOLD}ARNm (5'->3'): {C.RESET}", texto_inicial=arnm).strip().upper()

            if 'T' in nuevo_arn:
                nuevo_arn = nuevo_arn.replace('T', 'U')
                print(f"{C.DIM}(Se convirtieron automáticamente las 'T' introducidas a ribonucleótidos 'U'){C.RESET}")

            if not nuevo_arn or not set(nuevo_arn).issubset(bases_arn_validas):
                print(f"{C.RED}Error: La cadena contiene caracteres no válidos para ARN (solo se admiten A, U, C, G).{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
                continue

            idx_aug_n = nuevo_arn.find("AUG")
            if idx_aug_n == -1:
                print(f"{C.RED}Error: Has eliminado el codón de inicio 'AUG'. El ARNm debe conservar el codón 'AUG'.{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
                continue

            # Buscar apariciones de codones de parada tras el AUG
            paradas_encontradas = []
            for stop_cod in CODONES_STOP_INFO:
                p = nuevo_arn.find(stop_cod, idx_aug_n + 3)
                while p != -1:
                    paradas_encontradas.append((p, stop_cod))
                    p = nuevo_arn.find(stop_cod, p + 1)

            if not paradas_encontradas:
                print(f"{C.YELLOW}Aviso: No se ha detectado ningún codón de parada (UAA, UAG, UGA) después del AUG.{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
                continue

            # Tomar el primer codón de parada que encuentre el ribosoma tras el AUG
            paradas_encontradas.sort(key=lambda x: x[0])
            pos_p, stop_p = paradas_encontradas[0]

            dist = pos_p - idx_aug_n
            sobrante_n = dist % 3

            if sobrante_n == 0:
                print(f"\n{C.GREEN}✔ Codón de parada '{stop_p}' ({CODONES_STOP_INFO[stop_p]}) detectado en fase de lectura perfecta (posición {pos_p + 1}):{C.RESET}")
                print(f"  ARNm resultante: 5'- {colorear_bases_arn(nuevo_arn)} -3'")
                return nuevo_arn

            elif sobrante_n == 1:
                nuc_incompleto = nuevo_arn[pos_p - 1]
                print(f"\n{C.YELLOW}⚠ Aviso de marco de lectura:{C.RESET}")
                print(f"  El codón de parada '{stop_p}' en posición {pos_p + 1} no completa el codón anterior.")
                print(f"  El triplete previo solo tiene 1 nucleótido: {C.BOLD}'{nuc_incompleto}'{C.RESET}.")
                print(f"  Faltan {C.BOLD}2 nucleótidos{C.RESET} (A, U, C, G) para completar ese codón antes de '{stop_p}'.")
                
                while True:
                    nucs_add = safe_input(f"{C.BOLD}Introduce los 2 nucleótidos que faltan (ej. CG): {C.RESET}").strip().upper().replace('T', 'U')
                    if len(nucs_add) == 2 and set(nucs_add).issubset(bases_arn_validas):
                        nuevo_arn = nuevo_arn[:pos_p] + nucs_add + nuevo_arn[pos_p:]
                        print(f"{C.GREEN}✔ Codón anterior completado: '{nuevo_arn[pos_p-1:pos_p+2]}'.{C.RESET}")
                        print(f"{C.GREEN}✔ Codón de parada '{stop_p}' ahora en fase de lectura correcta.{C.RESET}")
                        print(f"  ARNm resultante: 5'- {colorear_bases_arn(nuevo_arn)} -3'")
                        return nuevo_arn
                    print(f"{C.RED}Error: Debes introducir exactamente 2 nucleótidos válidos (A, U, C, G).{C.RESET}")

            elif sobrante_n == 2:
                nucs_incompletos = nuevo_arn[pos_p - 2 : pos_p]
                print(f"\n{C.YELLOW}⚠ Aviso de marco de lectura:{C.RESET}")
                print(f"  El codón de parada '{stop_p}' en posición {pos_p + 1} no completa el codón anterior.")
                print(f"  El triplete previo solo tiene 2 nucleótidos: {C.BOLD}'{nucs_incompletos}'{C.RESET}.")
                print(f"  Falta {C.BOLD}1 nucleótido{C.RESET} (A, U, C, G) para completar ese codón antes de '{stop_p}'.")
                
                while True:
                    nuc_add = safe_input(f"{C.BOLD}Introduce el nucleótido que falta (A, U, C, G): {C.RESET}").strip().upper().replace('T', 'U')
                    if len(nuc_add) == 1 and nuc_add in bases_arn_validas:
                        nuevo_arn = nuevo_arn[:pos_p] + nuc_add + nuevo_arn[pos_p:]
                        print(f"{C.GREEN}✔ Codón anterior completado: '{nuevo_arn[pos_p-2:pos_p+1]}'.{C.RESET}")
                        print(f"{C.GREEN}✔ Codón de parada '{stop_p}' ahora en fase de lectura correcta.{C.RESET}")
                        print(f"  ARNm resultante: 5'- {colorear_bases_arn(nuevo_arn)} -3'")
                        return nuevo_arn
                    print(f"{C.RED}Error: Debes introducir exactamente 1 nucleótido válido (A, U, C, G).{C.RESET}")


# ==============================================================================
# EJECUCIÓN VISUAL: ETAPA 1 - REPLICACIÓN DEL ADN
# ==============================================================================
def ejecutar_replicacion(cadena_adn: str, modo_auto: bool = False, es_5a3: bool = True) -> Dict[str, Any]:
    seccion_header(
        titulo="Etapa 1: Replicación Semiconservativa del ADN",
        subtitulo="Demostración de horquilla, síntesis continua (líder) y síntesis discontinua (Okazaki)",
        icono="🧬",
        color=C.CYAN
    )

    print(f"\n{C.BOLD}Molécula de ADN Bicatenario Original:{C.RESET}")
    cadena_comp = obtener_cadena_complementaria(cadena_adn)
    if es_5a3:
        cadena_5_3 = cadena_adn
        cadena_3_5 = cadena_comp
        indicador_5_3 = f" {C.GREEN}(Secuencia introducida){C.RESET}"
        indicador_3_5 = ""
    else:
        cadena_3_5 = cadena_adn
        cadena_5_3 = cadena_comp
        indicador_5_3 = ""
        indicador_3_5 = f" {C.GREEN}(Secuencia introducida){C.RESET}"

    print(f"  Hebra 1 (5' -> 3'): 5'- {colorear_bases_dna(cadena_5_3)} -3'{indicador_5_3}")
    print(f"  Apareamiento bases:     {'|' * len(cadena_adn)}")
    print(f"  Hebra 2 (3' -> 5'): 3'- {colorear_bases_dna(cadena_3_5)} -5'{indicador_3_5}")
    
    pausar(modo_auto, delay=1.0, mensaje="Pulsar [ENTER] para activar la HELICASA y abrir la horquilla...")

    # Simular modelo biológico
    datos = simular_replicacion(cadena_adn, tam_okazaki=10, tam_primer=3, es_5a3=es_5a3)

    for i, paso in enumerate(datos["pasos"], 1):
        color_badge = C.MAGENTA if "Helicasa" in paso["enzima"] else (
            C.BLUE if "Primasa" in paso["enzima"] else (
                C.GREEN if "ADN Polimerasa III" in paso["enzima"] else (
                    C.YELLOW if "ADN Polimerasa I" in paso["enzima"] else (
                        C.RED if "Ligasa" in paso["enzima"] else C.CYAN
                    )
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

    # Resumen de replicación con visualización molecular de las dos dobles hélices
    print(f"\n{C.GREEN}{C.BOLD}✔ REPLICACIÓN COMPLETADA: Se obtienen 2 moléculas bicatenarias idénticas (Semiconservativa):{C.RESET}")
    m1 = datos["resultado_final"]["molecula_1"]
    m2 = datos["resultado_final"]["molecula_2"]

    adn_lider = datos["cadena_lider"]
    adn_rezagada = datos["cadena_rezagada"]

    print(f"\n  {C.BOLD}{C.CYAN}┌── Molécula Hija 1 (Hebra Parental 1 + Nueva Cadena Rezagada Ligada):{C.RESET}")
    print(f"  │  Hebra Parental 1 (5'->3') : 5'- {colorear_bases_dna(datos['hebra_original_5_3'])} -3'")
    print(f"  │  Puentes de Hidrógeno      :     {'|' * len(datos['hebra_original_5_3'])}")
    print(f"  │  Cadena Rezagada (3'<-5')  : 3'- {colorear_bases_dna(adn_rezagada)} -5'  ({m1['tipo_sintesis']})")
    print(f"  {C.CYAN}└───────────────────────────────────────────────────────────────────────────────────{C.RESET}")

    print(f"\n  {C.BOLD}{C.GREEN}┌── Molécula Hija 2 (Hebra Parental 2 + Nueva Cadena Líder Madurada):{C.RESET}")
    print(f"  │  Hebra Parental 2 (3'->5') : 3'- {colorear_bases_dna(datos['hebra_original_3_5'])} -5'")
    print(f"  │  Puentes de Hidrógeno      :     {'|' * len(datos['hebra_original_3_5'])}")
    print(f"  │  Cadena Líder (5'->3')     : 5'- {colorear_bases_dna(adn_lider)} -3'  ({m2['tipo_sintesis']})")
    print(f"  │  * Cebador de ARN retirado y sustituido por ADN por la ADN Polimerasa I")
    print(f"  {C.GREEN}└───────────────────────────────────────────────────────────────────────────────────{C.RESET}")

    pausar(modo_auto, delay=1.5, mensaje="Pulsar [ENTER] para pasar a la TRANSCRIPCIÓN...")
    return datos


# ==============================================================================
# EJECUCIÓN VISUAL: ETAPA 2 - TRANSCRIPCIÓN DEL ADN
# ==============================================================================
def ejecutar_transcripcion(cadena_adn: str, modo_auto: bool = False, es_5a3: bool = True) -> Dict[str, Any]:
    seccion_header(
        titulo="Etapa 2: Transcripción del ADN a ARN Mensajero (ARNm)",
        subtitulo="Reconocimiento del promotor, lectura de cadena molde (3'->5') y síntesis 5'->3'",
        icono="🌀",
        color=C.MAGENTA
    )

    usar_molde = (not es_5a3)
    datos = simular_transcripcion(cadena_adn, usar_cadena_como_molde=usar_molde)
    cadena_codificante = datos.get("cadena_codificante_5_3", datos.get("cadena_codificante", ""))
    cadena_molde = datos.get("cadena_molde_3_5", datos.get("cadena_molde", ""))

    print(f"{C.BOLD}Doble hebra antes de transcribir:{C.RESET}")
    tag_cod = f" {C.GREEN}(Secuencia introducida){C.RESET}" if es_5a3 else ""
    tag_mol = f" {C.GREEN}(Secuencia introducida){C.RESET}" if not es_5a3 else ""
    print(f" Cadena Codificante (sentido 5'->3')     : 5'- {colorear_bases_dna(cadena_codificante)} -3'{tag_cod}")
    print(f" Apareamiento bases                      :     {'|' * len(cadena_adn)}")
    print(f" Cadena Molde (leída por ARN Pol 3'->5') : 3'- {colorear_bases_dna(cadena_molde)} -5'{tag_mol}")

    pausar(modo_auto, delay=1.0, mensaje="Pulsar [ENTER] para acoplar la ARN POLIMERASA...")

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

    datos = simular_traduccion(arnm)

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
        print(f"  #{item['ciclo']:<6} | 5'- {c_arn} -3'    | 3'- {c_anti} -5'      | {aa:<12} | {prop}")

    print(f"\n{C.GREEN}{C.BOLD}✔ CADENA POLIPEPTÍDICA FINAL SINTETIZADA:{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}{datos['cadena_proteica']}{C.RESET}")
    print(f"  Secuencia 1 letra: {C.BOLD}{datos['aminoacidos_1']}{C.RESET}")

    pausar(modo_auto, delay=1.5, mensaje="Pulsar [ENTER] para ver el Gran Resumen Integrado...")
    return datos


# ==============================================================================
# RESUMEN INTEGRADO FINAL (DOGMA COMPLETO)
# ==============================================================================
def mostrar_gran_resumen(dna_original: str, res_rep: Dict, res_trans: Dict, res_trad: Dict, es_5a3: bool = True):
    seccion_header(
        titulo="Gran Resumen: Flujo Completo de la Información Biológica",
        subtitulo="Verificación de la continuidad del Dogma Central de la Biología Molecular",
        icono="🏆",
        color=C.GREEN
    )

    cad_5_3 = res_rep.get("hebra_original_5_3", dna_original if es_5a3 else obtener_cadena_complementaria(dna_original))
    cad_3_5 = res_rep.get("hebra_original_3_5", obtener_cadena_complementaria(dna_original) if es_5a3 else dna_original)
    tag_53 = f" {C.GREEN}(Secuencia introducida){C.RESET}" if es_5a3 else ""
    tag_35 = f" {C.GREEN}(Secuencia introducida){C.RESET}" if not es_5a3 else ""

    print(f"{C.BOLD}1. NIVEL ADN (Genoma original):{C.RESET}")
    print(f"   5'- {colorear_bases_dna(cad_5_3)} -3'{tag_53}")
    print(f"   3'- {colorear_bases_dna(cad_3_5)} -5'{tag_35}")

    print(f"\n{C.BOLD}2. NIVEL REPLICACIÓN (ADN -> ADN):{C.RESET}")
    print(f"   - Helicasa abrió la horquilla de replicación.")
    print(f"   - Síntesis continua en cadena líder sobre molde 3'->5'.")
    print(f"   - Síntesis discontinua con {len(res_rep['fragmentos_okazaki'])} Fragmentos de Okazaki en cadena rezagada.")
    print(f"   - Reemplazo de cebadores de ARN (en cadena líder y fragmentos de Okazaki) por ADN Pol I.")
    print(f"   - Sellado de muescas por ADN Ligasa y obtención de 2 dobles hélices semiconservativas completas.")

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
            <pre class="bubble-pre">{['burbuja_ascii']}</pre>

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
        print(f"  {C.CYAN}[1]{C.RESET} Ejecutar Simulación Completa con Secuencia de ADN Manual (escrita por teclado)")
        print(f"  {C.CYAN}[2]{C.RESET} Ejecutar Simulación Completa desde Archivo FASTA (.fasta / .fa)")
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

        # Secuencia a utilizar según la opción
        secuencia_adn = SECUENCIA_DEMO
        bases_validas = set("ATCG")
        es_5a3 = True

        if opcion == "1":
            print(f"\n{C.WHITE}Introduce la secuencia de ADN (solo bases A, T, C, G):{C.RESET}")
            print(f"{C.DIM}[Pulsa ENTER sin escribir nada para usar la secuencia de prueba: {SECUENCIA_DEMO}]{C.RESET}")
            sec_usr = safe_input(f"{C.BOLD}ADN: {C.RESET}").strip().upper()
            if not sec_usr:
                print(f"{C.YELLOW}→ Usando secuencia demostrativa por defecto.{C.RESET}")
                secuencia_adn = SECUENCIA_DEMO
            elif not set(sec_usr).issubset(bases_validas):
                print(f"{C.RED}Error: La secuencia contiene caracteres no válidos. Solo se admiten A, T, C, G.{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
                continue
            else:
                secuencia_adn = sec_usr

            print(f"\n{C.BOLD}Indica la dirección / sentido de la secuencia de ADN introducida:{C.RESET}")
            print(f"  {C.CYAN}[1]{C.RESET} 5' -> 3' (Cadena Codificante / Sentido)")
            print(f"  {C.CYAN}[2]{C.RESET} 3' -> 5' (Cadena Molde / Antisentido)")
            dir_op = safe_input(f"{C.BOLD}Selecciona la dirección (1/2, por defecto 1 [5'->3']): {C.RESET}").strip()
            es_5a3 = False if dir_op == "2" else True

        elif opcion == "2":
            print(f"\n{C.WHITE}Introduce la ruta del archivo FASTA (.fasta, .fa, .txt):{C.RESET}")
            print(f"{C.DIM}[Ejemplo: ejemplo.fasta o ruta completa al archivo]{C.RESET}")
            ruta_usr = safe_input(f"{C.BOLD}Ruta FASTA: {C.RESET}").strip()
            if not ruta_usr:
                print(f"{C.RED}Error: La ruta no puede estar vacía.{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
                continue
            try:
                cabecera, sec_fasta = leer_archivo_fasta(ruta_usr)
                if not set(sec_fasta).issubset(bases_validas):
                    print(f"{C.RED}Error: La secuencia del archivo FASTA contiene bases no válidas (solo se admiten A, T, C, G).{C.RESET}")
                    safe_input("Pulsa ENTER para reintentar...")
                    continue
                secuencia_adn = sec_fasta
                print(f"\n{C.GREEN}✔ Archivo FASTA cargado con éxito:{C.RESET}")
                if cabecera:
                    print(f"  {C.CYAN}Cabecera:{C.RESET} >{cabecera}")
                print(f"  {C.CYAN}Longitud:{C.RESET} {len(secuencia_adn)} pares de bases")

                print(f"\n{C.BOLD}Indica la dirección / sentido de la secuencia contenida en el FASTA:{C.RESET}")
                print(f"  {C.CYAN}[1]{C.RESET} 5' -> 3' (Cadena Codificante / Sentido)")
                print(f"  {C.CYAN}[2]{C.RESET} 3' -> 5' (Cadena Molde / Antisentido)")
                dir_op = safe_input(f"{C.BOLD}Selecciona la dirección (1/2, por defecto 1 [5'->3']): {C.RESET}").strip()
                es_5a3 = False if dir_op == "2" else True

                pausar(modo_auto=False, delay=0.5, mensaje="Pulsar [ENTER] para comenzar la simulación...")
            except Exception as e:
                print(f"{C.RED}Error al cargar el archivo FASTA: {e}{C.RESET}")
                safe_input("Pulsa ENTER para reintentar...")
                continue

        limpiar_pantalla()

        # Ejecución según opción
        if opcion in ["1", "2"]:
            while True:
                res_rep = ejecutar_replicacion(secuencia_adn, modo_auto=modo_auto, es_5a3=es_5a3)
                res_trans = ejecutar_transcripcion(secuencia_adn, modo_auto=modo_auto, es_5a3=es_5a3)
                arnm = res_trans["arnm_5_3"]

                # Comprobación de la presencia del codón de inicio AUG antes de la traducción
                if "AUG" not in arnm:
                    print(f"\n{C.YELLOW}{C.BOLD}══════════════════════════════════════════════════════════════════════════════════{C.RESET}")
                    print(f"{C.RED}{C.BOLD}⚠ AVISO BIOLÓGICO: No se ha detectado el codón de inicio 'AUG' en el ARNm.{C.RESET}")
                    print(f"{C.WHITE}El ribosoma requiere el codón universal 5'-AUG-3' (Metionina) para iniciar la síntesis de proteínas.{C.RESET}")
                    print(f"{C.YELLOW}{C.BOLD}══════════════════════════════════════════════════════════════════════════════════{C.RESET}")

                    if opcion == "1":
                        # Caso 1 (Entrada manual): Modificar directamente la cadena de ARNm transcrita
                        arnm = insertar_o_modificar_arnm(arnm)
                        res_trans["arnm_5_3"] = arnm
                        # Va DIRECTO a traducción sin repetir replicación ni transcripción
                        break

                    elif opcion == "2":
                        # Caso 2: Archivo FASTA
                        print(f"\n{C.BOLD}Elige cómo deseas proceder:{C.RESET}")
                        print(f"  {C.CYAN}[1]{C.RESET} Añadir 'AUG' al inicio o modificar el ARNm (pasa directo a traducción)")
                        print(f"  {C.CYAN}[2]{C.RESET} Cambiar de archivo FASTA (carga el nuevo FASTA y pasa directo a traducción)")
                        resp_c2 = safe_input(f"{C.BOLD}Opción (1/2, por defecto 1): {C.RESET}").strip()

                        if resp_c2 in ["", "1"]:
                            arnm = insertar_o_modificar_arnm(arnm)
                            res_trans["arnm_5_3"] = arnm
                            # Va DIRECTO a traducción sin repetir ningún paso previo
                            break
                        else:
                            print(f"\n{C.WHITE}Introduce la nueva ruta del archivo FASTA (.fasta, .fa, .txt):{C.RESET}")
                            nueva_ruta = safe_input(f"{C.BOLD}Nueva ruta FASTA: {C.RESET}").strip()
                            try:
                                cab, sec_f = leer_archivo_fasta(nueva_ruta)
                                if not set(sec_f).issubset(bases_validas):
                                    print(f"{C.RED}Error: El archivo FASTA contiene bases no válidas. Pulsa ENTER...{C.RESET}")
                                    safe_input()
                                    continue
                                secuencia_adn = sec_f
                                print(f"\n{C.GREEN}✔ Nuevo archivo FASTA cargado con éxito ({len(secuencia_adn)} pb).{C.RESET}")
                                if cab:
                                    print(f"  {C.CYAN}Cabecera:{C.RESET} >{cab}")
                                print(f"\n{C.BOLD}Indica la dirección del nuevo archivo FASTA:{C.RESET}")
                                print(f"  {C.CYAN}[1]{C.RESET} 5' -> 3' (Cadena Codificante / Sentido)")
                                print(f"  {C.CYAN}[2]{C.RESET} 3' -> 5' (Cadena Molde / Antisentido)")
                                dir_f2 = safe_input(f"{C.BOLD}Opción (1/2, por defecto 1): {C.RESET}").strip()
                                es_5a3 = False if dir_f2 == "2" else True

                                # Transcribir la nueva secuencia directamente para obtener el ARNm
                                res_trans = simular_transcripcion(secuencia_adn, usar_cadena_como_molde=(not es_5a3))
                                arnm = res_trans["arnm_5_3"]
                                if "AUG" not in arnm:
                                    print(f"\n{C.YELLOW}Aviso: El nuevo FASTA tampoco contiene 'AUG'. Se añade 'AUG' al inicio para traducir.{C.RESET}")
                                    arnm = "AUG" + arnm
                                    res_trans["arnm_5_3"] = arnm
                                print(f"\n{C.GREEN}✔ ARNm del nuevo FASTA listo: 5'- {colorear_bases_arn(arnm)} -3'{C.RESET}")
                                pausar(modo_auto=False, delay=0.5, mensaje="Pulsar [ENTER] para pasar directo a la TRADUCCIÓN...")
                                # Va DIRECTO a traducción sin repetir pasos
                                break
                            except Exception as e:
                                print(f"{C.RED}Error al leer el archivo FASTA: {e}{C.RESET}")
                                safe_input("Pulsa ENTER para reintentar...")
                                continue
                else:
                    break

            # Comprobación del codón de parada (frenada) tras asegurar el codón AUG
            arnm = verificar_y_asegurar_codon_parada(arnm)
            res_trans["arnm_5_3"] = arnm

            res_trad = ejecutar_traduccion(arnm, modo_auto=modo_auto)
            mostrar_gran_resumen(secuencia_adn, res_rep, res_trans, res_trad, es_5a3=es_5a3)
            
            # Ofrecer exportación a visor HTML
            print(f"{C.BOLD}¿Deseas exportar el reporte gráfico interactivo en HTML? (s/n, por defecto s): {C.RESET}", end="")
            resp_html = safe_input().strip().lower()
            if resp_html in ["", "s", "si", "y", "yes"]:
                generar_reporte_html(secuencia_adn, res_rep, res_trans, res_trad)

        elif opcion == "3":
            ejecutar_replicacion(secuencia_adn, modo_auto=modo_auto, es_5a3=es_5a3)

        elif opcion == "4":
            ejecutar_transcripcion(secuencia_adn, modo_auto=modo_auto, es_5a3=es_5a3)

        elif opcion == "5":
            arn_trans = simular_transcripcion(secuencia_adn, usar_cadena_como_molde=(not es_5a3))["arnm_5_3"]
            if "AUG" not in arn_trans:
                arn_trans = insertar_o_modificar_arnm(arn_trans)
            arn_trans = verificar_y_asegurar_codon_parada(arn_trans)
            ejecutar_traduccion(arn_trans, modo_auto=modo_auto)

        print(f"\n{C.CYAN}Fin de la simulación. Pulsa [ENTER] para volver al menú principal...{C.RESET}")
        safe_input()


if __name__ == "__main__":
    main()
