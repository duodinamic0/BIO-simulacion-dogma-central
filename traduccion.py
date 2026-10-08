"""
================================================================================
MÓDULO DE TRADUCCIÓN DEL ARNm A PROTEÍNA
================================================================================
Este módulo simula la traducción biológica en los ribosomas celulares.

Conceptos y maquinaria molecular simulada:
  1. Código genético universal (64 codones, 20 aminoácidos estándar + Stop).
  2. Búsqueda del marco abierto de lectura (ORF) a partir del codón de inicio (AUG).
  3. Ribosoma (subunidades menor y mayor) y sus tres sitios funcionales:
     - Sitio A (Aminoacil): Entrada del ARNt cargado.
     - Sitio P (Peptidil): Formación del enlace peptídico y retención del péptido naciente.
     - Sitio E (Exit): Expulsión del ARNt desacilado.
  4. Moléculas de ARNt (con anticodón antiparalelo y aminoácido específico).
  5. Señal de terminación (codones de parada: UAA, UAG, UGA) y factores de liberación (RF).
  6. Síntesis direccional: Extremo Amino (N-terminal) al extremo Carboxilo (C-terminal).
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple

# Tabla completa del código genético universal
# Formato: codon: (codigo_3_letras, codigo_1_letra, nombre_completo, propiedad)
TABLA_CODIGO_GENETICO = {
    # U
    'UUU': ('Phe', 'F', 'Fenilalanina', 'Apolar / Hidrófobo'),
    'UUC': ('Phe', 'F', 'Fenilalanina', 'Apolar / Hidrófobo'),
    'UUA': ('Leu', 'L', 'Leucina', 'Apolar / Hidrófobo'),
    'UUG': ('Leu', 'L', 'Leucina', 'Apolar / Hidrófobo'),
    'UCU': ('Ser', 'S', 'Serina', 'Polar neutro'),
    'UCC': ('Ser', 'S', 'Serina', 'Polar neutro'),
    'UCA': ('Ser', 'S', 'Serina', 'Polar neutro'),
    'UCG': ('Ser', 'S', 'Serina', 'Polar neutro'),
    'UAU': ('Tyr', 'Y', 'Tirosina', 'Polar neutro / Aromático'),
    'UAC': ('Tyr', 'Y', 'Tirosina', 'Polar neutro / Aromático'),
    'UAA': ('STOP', '*', 'Codón de Parada (Ocre)', 'Señal de Terminación'),
    'UAG': ('STOP', '*', 'Codón de Parada (Ámbar)', 'Señal de Terminación'),
    'UGU': ('Cys', 'C', 'Cisteína', 'Polar neutro / Tiol'),
    'UGC': ('Cys', 'C', 'Cisteína', 'Polar neutro / Tiol'),
    'UGA': ('STOP', '*', 'Codón de Parada (Ópalo)', 'Señal de Terminación'),
    'UGG': ('Trp', 'W', 'Triptófano', 'Apolar / Aromático'),

    # C
    'CUU': ('Leu', 'L', 'Leucina', 'Apolar / Hidrófobo'),
    'CUC': ('Leu', 'L', 'Leucina', 'Apolar / Hidrófobo'),
    'CUA': ('Leu', 'L', 'Leucina', 'Apolar / Hidrófobo'),
    'CUG': ('Leu', 'L', 'Leucina', 'Apolar / Hidrófobo'),
    'CCU': ('Pro', 'P', 'Prolina', 'Apolar / Rígido'),
    'CCC': ('Pro', 'P', 'Prolina', 'Apolar / Rígido'),
    'CCA': ('Pro', 'P', 'Prolina', 'Apolar / Rígido'),
    'CCG': ('Pro', 'P', 'Prolina', 'Apolar / Rígido'),
    'CAU': ('His', 'H', 'Histidina', 'Carga positiva / Básico'),
    'CAC': ('His', 'H', 'Histidina', 'Carga positiva / Básico'),
    'CAA': ('Gln', 'Q', 'Glutamina', 'Polar neutro'),
    'CAG': ('Gln', 'Q', 'Glutamina', 'Polar neutro'),
    'CGU': ('Arg', 'R', 'Arginina', 'Carga positiva / Básico'),
    'CGC': ('Arg', 'R', 'Arginina', 'Carga positiva / Básico'),
    'CGA': ('Arg', 'R', 'Arginina', 'Carga positiva / Básico'),
    'CGG': ('Arg', 'R', 'Arginina', 'Carga positiva / Básico'),

    # A
    'AUU': ('Ile', 'I', 'Isoleucina', 'Apolar / Hidrófobo'),
    'AUC': ('Ile', 'I', 'Isoleucina', 'Apolar / Hidrófobo'),
    'AUA': ('Ile', 'I', 'Isoleucina', 'Apolar / Hidrófobo'),
    'AUG': ('Met', 'M', 'Metionina (INICIO)', 'Apolar / Inicio universal'),
    'ACU': ('Thr', 'T', 'Treonina', 'Polar neutro'),
    'ACC': ('Thr', 'T', 'Treonina', 'Polar neutro'),
    'ACA': ('Thr', 'T', 'Treonina', 'Polar neutro'),
    'ACG': ('Thr', 'T', 'Treonina', 'Polar neutro'),
    'AAU': ('Asn', 'N', 'Asparagina', 'Polar neutro'),
    'AAC': ('Asn', 'N', 'Asparagina', 'Polar neutro'),
    'AAA': ('Lys', 'K', 'Lisina', 'Carga positiva / Básico'),
    'AAG': ('Lys', 'K', 'Lisina', 'Carga positiva / Básico'),
    'AGU': ('Ser', 'S', 'Serina', 'Polar neutro'),
    'AGC': ('Ser', 'S', 'Serina', 'Polar neutro'),
    'AGA': ('Arg', 'R', 'Arginina', 'Carga positiva / Básico'),
    'AGG': ('Arg', 'R', 'Arginina', 'Carga positiva / Básico'),

    # G
    'GUU': ('Val', 'V', 'Valina', 'Apolar / Hidrófobo'),
    'GUC': ('Val', 'V', 'Valina', 'Apolar / Hidrófobo'),
    'GUA': ('Val', 'V', 'Valina', 'Apolar / Hidrófobo'),
    'GUG': ('Val', 'V', 'Valina', 'Apolar / Hidrófobo'),
    'GCU': ('Ala', 'A', 'Alanina', 'Apolar / Hidrófobo'),
    'GCC': ('Ala', 'A', 'Alanina', 'Apolar / Hidrófobo'),
    'GCA': ('Ala', 'A', 'Alanina', 'Apolar / Hidrófobo'),
    'GCG': ('Ala', 'A', 'Alanina', 'Apolar / Hidrófobo'),
    'GAU': ('Asp', 'D', 'Aspartato', 'Carga negativa / Ácido'),
    'GAC': ('Asp', 'D', 'Aspartato', 'Carga negativa / Ácido'),
    'GAA': ('Glu', 'E', 'Glutamato', 'Carga negativa / Ácido'),
    'GAG': ('Glu', 'E', 'Glutamato', 'Carga negativa / Ácido'),
    'GGU': ('Gly', 'G', 'Glicina', 'Apolar / Estructuralmente flexible'),
    'GGC': ('Gly', 'G', 'Glicina', 'Apolar / Estructuralmente flexible'),
    'GGA': ('Gly', 'G', 'Glicina', 'Apolar / Estructuralmente flexible'),
    'GGG': ('Gly', 'G', 'Glicina', 'Apolar / Estructuralmente flexible')
}

COMPLEMENTO_ARN = {
    'A': 'U', 'U': 'A',
    'C': 'G', 'G': 'C'
}


def obtener_anticodon(codon: str) -> str:
    """
    Obtiene el anticodón de ARNt antiparalelo (3' -> 5') correspondiente al codón (5' -> 3').
    Ejemplo: Codón 5'-AUG-3' -> Anticodón 3'-UAC-5'.
    """
    return "".join(COMPLEMENTO_ARN.get(b, 'N') for b in codon)


def simular_traduccion(arnm_5_3: str) -> Dict[str, Any]:
    """
    Simula la traducción de un ARNm a una cadena polipeptídica (proteína).

    Parámetros:
      arnm_5_3: Secuencia de ARN mensajero (5' -> 3').
      requerir_aug: Si es True, busca el primer codón de inicio AUG para comenzar la lectura.
                    Si es False, traduce directamente desde el principio de 3 en 3.

    Retorna un diccionario completo con:
      - Marco de lectura identificado
      - Pasos detallados del ribosoma (Sitios A, P, E)
      - Codones, anticodones y aminoácidos incorporados
      - Secuencia final de la proteína (código de 3 letras, 1 letra y nombres)
    """
    arnm = arnm_5_3.upper().strip()
    pasos = []

    # --------------------------------------------------------------------------
    # PASO 1: Búsqueda del Codón de Inicio (AUG)
    # --------------------------------------------------------------------------
    indice_inicio = -1
    indice_inicio = arnm.find("AUG")
    if indice_inicio == -1:
        # Si no hay AUG explícito, avisar pedagógicamente
        pasos.append({
            "etapa": "Iniciación Fallida",
            "enzima": "Subunidad menor del ribosoma (40S / 30S)",
            "descripcion": (
                "No se encontró el codón de inicio AUG en la secuencia de ARNm. "
                "En condiciones celulares normales, la traducción requiere AUG (Metionina) "
                "para comenzar el marco abierto de lectura."
            ),
            "visual": f"ARNm analizado: 5'- {arnm} -3' (Sin señal AUG)"
        })
        return {
            "arnm_5_3": arnm,
            "inicio_encontrado": False,
            "indice_inicio": -1,
            "pasos": pasos,
            "aminoacidos_3": [],
            "aminoacidos_1": "",
            "proteina_completa": "Sin síntesis (ausencia de codón AUG)"
        }

    codones_leidos = []
    aminoacidos_3 = []
    aminoacidos_1 = []
    aminoacidos_detalles = []
    codon_stop_encontrado = False
    motivo_parada = "Fin de la secuencia de ARNm (sin codón de parada explícito)"

    arn_5_utr = arnm[:indice_inicio]
    arn_orf = arnm[indice_inicio:]

    pasos.append({
        "etapa": "Iniciación de la Traducción",
        "enzima": "Complejo Ribosomal + ARNt iniciador (Met-ARNt)",
        "descripcion": (
            f"1. La subunidad menor reconoce el extremo 5' y escanea hasta hallar el codón AUG (posición {indice_inicio + 1}).\n"
            f"2. El ARNt iniciador acopla su anticodón (3'-UAC-5') con el codón AUG cargando Metionina (Met).\n"
            f"3. La subunidad mayor se une, ubicando el primer ARNt directamente en el Sitio P (Peptidil)."
        ),
        "visual": (
            f"ARNm 5'-UTR : 5'- [{arn_5_utr}] (Región no traducida previa al inicio)\n"
            f"Codón Inicio: [ AUG ] en posición {indice_inicio + 1}\n"
            f"ARNm 5'-ORF : 5'- [{arn_orf}] (Región a traducir)\n"
            f"Ribosoma    :  [Sitio E: Vacío] [Sitio P: Met-ARNt (UAC)] [Sitio A: Abierto]"
        )
    })

    # --------------------------------------------------------------------------
    # PASO 2: Elongación (Lectura de codones de 3 en 3)
    # --------------------------------------------------------------------------
    i = indice_inicio
    numero_ciclo = 1

    while i + 3 <= len(arnm):
        triplete = arnm[i:i+3]
        info_aa = TABLA_CODIGO_GENETICO.get(triplete, ('???', '?', 'Desconocido', 'Desconocido'))
        codigo_3, codigo_1, nombre, propiedad = info_aa
        anticodon = obtener_anticodon(triplete)

        if codigo_3 == 'STOP':
            codon_stop_encontrado = True
            motivo_parada = f"Codón de Parada encontrado: {triplete} ({nombre})"
            codones_leidos.append({
                "ciclo": numero_ciclo,
                "codon": triplete,
                "anticodon": "---",
                "aminoacido_3": "STOP",
                "aminoacido_1": "*",
                "nombre": nombre,
                "propiedad": propiedad,
                "posicion": i + 1
            })
            break

        codones_leidos.append({
            "ciclo": numero_ciclo,
            "codon": triplete,
            "anticodon": anticodon,
            "aminoacido_3": codigo_3,
            "aminoacido_1": codigo_1,
            "nombre": nombre,
            "propiedad": propiedad,
            "posicion": i + 1
        })

        aminoacidos_3.append(codigo_3)
        aminoacidos_1.append(codigo_1)
        aminoacidos_detalles.append(info_aa)

        # Representación del ciclo de elongación en el ribosoma
        paso_elongacion = {
            "etapa": f"Elongación - Ciclo #{numero_ciclo} (Codón {triplete})",
            "enzima": "Peptidil Transferasa + ARNt específico",
            "descripcion": (
                f"- Sitio A: Ingresa ARNt portando '{codigo_3}' ({nombre}) con anticodón 3'-{anticodon}-5'.\n"
                f"- Sitio P: La Peptidil Transferasa cataliza el enlace peptídico transfiriendo la cadena al nuevo aminoácido.\n"
                f"- Translocación: El ribosoma avanza 1 codón (3 nucleótidos) hacia 3'. El ARNt usado sale por el Sitio E."
            ),
            "visual": (
                f"ARNm leído     : ... [ {triplete} ] ...\n"
                f"Anticodón ARNt : ... [ 3'-{anticodon}-5' ] cargando {codigo_3}\n"
                f"Cadena naciente: H2N- {' - '.join(aminoacidos_3)} -COOH"
            )
        }
        pasos.append(paso_elongacion)

        i += 3
        numero_ciclo += 1

    # --------------------------------------------------------------------------
    # PASO 3: Terminación
    # --------------------------------------------------------------------------
    pasos.append({
        "etapa": "Terminación de la Traducción",
        "enzima": "Factor de Liberación (Release Factor - RF)",
        "descripcion": (
            f"{motivo_parada}.\n"
            f"El Factor de Liberación reconoce el codón de parada, cataliza la hidrólisis "
            f"del polipéptido naciente y provoca la disociación completa de las dos subunidades ribosomales."
        ),
        "visual": (
            f"Proteína Sintetizada: H2N- {' - '.join(aminoacidos_3)} -COOH\n"
            f"Secuencia 1-letra   : {''.join(aminoacidos_1)}\n"
            f"Longitud            : {len(aminoacidos_3)} aminoácidos sintetizados."
        )
    })

    cadena_proteica = f"H2N- {' - '.join(aminoacidos_3)} -COOH" if aminoacidos_3 else "Cadena vacía"

    return {
        "arnm_5_3": arnm,
        "inicio_encontrado": True,
        "indice_inicio": indice_inicio,
        "codon_stop_encontrado": codon_stop_encontrado,
        "motivo_parada": motivo_parada,
        "codones_leidos": codones_leidos,
        "aminoacidos_3": aminoacidos_3,
        "aminoacidos_1": "".join(aminoacidos_1),
        "cadena_proteica": cadena_proteica,
        "pasos": pasos
    }


if __name__ == "__main__":
    arnm_demo = "AUGCGAUCGAUCGAUCGAUCGAUCGAUCGAUCUAG"
    res = simular_traduccion(arnm_demo)
    print("=== TEST TRADUCCIÓN ===")
    for paso in res["pasos"]:  # Mostrar los primeros
        print(f"\n[{paso['enzima']}] - {paso['etapa']}")
        print(paso['descripcion'])
        print(paso['visual'])
    print(f"\nProteína final: {res['cadena_proteica']}")
