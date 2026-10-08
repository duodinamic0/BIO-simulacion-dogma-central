"""
================================================================================
MÓDULO DE TRANSCRIPCIÓN DEL ADN
================================================================================
Este módulo simula la transcripción de la información genética desde el ADN
hacia una molécula de ARN mensajero (ARNm).

Conceptos y enzimas clave:
  1. Cadena Codificante (sentido, 5'->3') vs Cadena Molde (antisentido, 3'->5').
  2. Región Promotora (ej. Caja TATA o señal de inicio): donde se une la ARN Polimerasa.
  3. ARN Polimerasa:
     - Desenrolla el ADN formando la "Burbuja de Transcripción".
     - Lee la hebra molde en sentido 3' -> 5'.
     - Sintetiza la molécula de ARNm en sentido 5' -> 3' utilizando ribonucleótidos.
     - Regla de complementariedad con Uracilo: Adenina (ADN) se aparea con Uracilo (ARN).
  4. Señal de Terminación y liberación del ARNm maduro.
================================================================================
"""

from typing import Dict, Any, List

# Complementariedad durante la transcripción: Cadena Molde ADN (3'->5') -> ARNm (5'->3')
# T (ADN) -> A (ARN)
# A (ADN) -> U (ARN)
# C (ADN) -> G (ARN)
# G (ADN) -> C (ARN)
TRANSCRIPCION_MAP = {
    'A': 'U',
    'T': 'A',
    'C': 'G',
    'G': 'C',
    'a': 'u',
    't': 'a',
    'c': 'g',
    'g': 'c'
}

COMPLEMENTO_ADN = {
    'A': 'T', 'T': 'A',
    'C': 'G', 'G': 'C'
}


def transcribir_cadena_molde(cadena_molde_3_5: str) -> str:
    """
    Transcribe una cadena molde de ADN (3' -> 5') a ARNm (5' -> 3').
    Aplica la regla biológica donde la Adenina del molde da lugar a Uracilo en el ARN.
    """
    return "".join(TRANSCRIPCION_MAP.get(b.upper(), 'N') for b in cadena_molde_3_5)


def simular_transcripcion(cadena_adn_5_3: str, usar_cadena_como_molde: bool = False) -> Dict[str, Any]:
    """
    Simula el proceso completo de transcripción.

    Parámetros:
      cadena_adn_5_3: Secuencia de ADN dada en sentido 5' -> 3'.
                      Por defecto se interpreta como Cadena Codificante (Coding Strand),
                      por lo que la cadena molde complementaria será 3' -> 5'.
      usar_cadena_como_molde: Si es True, interpreta directamente la cadena de entrada como molde.

    Retorna un diccionario con:
      - Cadena codificante (5'->3')
      - Cadena molde (3'->5')
      - Secuencia de ARNm sintetizada (5'->3')
      - Pasos pedagógicos y visuales
      - Representación gráfica de la burbuja de transcripción
      - Alineamiento nucleótido a nucleótido
    """
    adn_entrada = cadena_adn_5_3.upper().strip()

    if usar_cadena_como_molde:
        cadena_molde_3_5 = adn_entrada
        cadena_codificante_5_3 = "".join(COMPLEMENTO_ADN.get(b, 'N') for b in cadena_molde_3_5)
    else:
        cadena_codificante_5_3 = adn_entrada
        cadena_molde_3_5 = "".join(COMPLEMENTO_ADN.get(b, 'N') for b in cadena_codificante_5_3)

    arn_mensajero_5_3 = transcribir_cadena_molde(cadena_molde_3_5)

    pasos = []

    # --------------------------------------------------------------------------
    # PASO 1: Reconocimiento del Promotor e Iniciación
    # --------------------------------------------------------------------------
    pasos.append({
        "etapa": "Iniciación y Reconocimiento del Promotor",
        "enzima": "Factores de transcripción + ARN Polimerasa",
        "descripcion": (
            "La ARN Polimerasa reconoce la región promotora del gen (ej. secuencias tipo caja TATA) "
            "y se une fuertemente al ADN. Se determina cuál es la 'cadena molde' (3'->5') que será leída, "
            "y la 'cadena codificante' (5'->3') que quedará excluida de la lectura directa."
        ),
        "visual": (
            f"Cadena Codificante (sentido)    : 5'- {cadena_codificante_5_3} -3'\n"
            f"Cadena Molde (antisentido/leída): 3'- {cadena_molde_3_5} -5'\n"
            f"Sitio de unión ARN Polimerasa   : [=== PROMOTOR ===> Inicia síntesis hacia el extremo 3' del ARNm]"
        )
    })

    # --------------------------------------------------------------------------
    # PASO 2: Apertura de la Burbuja de Transcripción
    # --------------------------------------------------------------------------
    mitad = len(cadena_codificante_5_3) // 2
    inicio_burbuja = max(0, mitad - 5)
    fin_burbuja = min(len(cadena_codificante_5_3), mitad + 5)

    codif_pre = cadena_codificante_5_3[:inicio_burbuja]
    codif_bur = cadena_codificante_5_3[inicio_burbuja:fin_burbuja]
    codif_post = cadena_codificante_5_3[fin_burbuja:]

    molde_pre = cadena_molde_3_5[:inicio_burbuja]
    molde_bur = cadena_molde_3_5[inicio_burbuja:fin_burbuja]
    molde_post = cadena_molde_3_5[fin_burbuja:]

    arn_bur = arn_mensajero_5_3[inicio_burbuja:fin_burbuja]

    burbuja_ascii = (
        f"        Doble Hélice              Burbuja de Transcripción              Doble Hélice\n"
        f"5'- ... {codif_pre} ------/       {codif_bur}      \\---- {codif_post} ... -3' (Cadena Codificante)\n"
        f"                         /                         \\\n"
        f"         ARN Polimerasa [  ARNm: 5'- {arn_bur} --> ]\n"
        f"                         \\                         /\n"
        f"3'- ... {molde_pre} ------\\       {molde_bur}      /---- {molde_post} ... -5' (Cadena Molde leída)"
    )

    pasos.append({
        "etapa": "Elongación y Formación de la Burbuja",
        "enzima": "ARN Polimerasa",
        "descripcion": (
            "La ARN Polimerasa desenrolla localmente ~17 pares de bases formando la 'Burbuja de Transcripción'. "
            "Avanza leyendo la cadena molde en sentido 3'->5' e incorpora ribonucleótidos trifosfato (rNTPs) "
            "complementarios en sentido 5'->3'. ¡Atención!: frente a cada Adenina (A) del molde, "
            "la ARN Polimerasa incorpora Uracilo (U), nunca Timina."
        ),
        "visual": burbuja_ascii
    })

    # --------------------------------------------------------------------------
    # PASO 3: Terminación y Liberación del Transcrito
    # --------------------------------------------------------------------------
    pasos.append({
        "etapa": "Terminación y Liberación",
        "enzima": "ARN Polimerasa + Señal de Terminación",
        "descripcion": (
            "Al alcanzar una señal o secuencia de terminación, la ARN Polimerasa se detiene, "
            "se libera el híbrido ADN-ARN transitorio, la doble hélice de ADN se reasocia intacta "
            "y se libera la molécula madura de ARN mensajero (ARNm)."
        ),
        "visual": (
            f"ARNm Transcrito Sintetizado: 5'- {arn_mensajero_5_3} -3'\n"
            f"Alineamiento con ADN molde : 3'- {cadena_molde_3_5} -5'\n"
            f"Fíjate: El ARNm es idéntico a la cadena codificante (5'->3') cambiando 'T' por 'U'."
        )
    })

    # Tabla nucleótido a nucleótido para máxima claridad docente
    alineamiento = []
    for i in range(len(cadena_codificante_5_3)):
        c_cod = cadena_codificante_5_3[i]
        c_mol = cadena_molde_3_5[i]
        c_arn = arn_mensajero_5_3[i]
        alineamiento.append({
            "posicion": i + 1,
            "adn_codificante": c_cod,
            "adn_molde": c_mol,
            "arnm": c_arn
        })

    return {
        "cadena_codificante_5_3": cadena_codificante_5_3,
        "cadena_molde_3_5": cadena_molde_3_5,
        "arnm_5_3": arn_mensajero_5_3,
        "pasos": pasos,
        "alineamiento": alineamiento,
        "burbuja_ascii": burbuja_ascii
    }


if __name__ == "__main__":
    secuencia_demo = "ATGCGATCGATCGATCGATCGATCGATCGATCTAG"
    resultado = simular_transcripcion(secuencia_demo)
    print("=== TEST TRANSCRIPCIÓN ===")
    for paso in resultado["pasos"]:
        print(f"\n[{paso['enzima']}] - {paso['etapa']}")
        print(paso['descripcion'])
        print(paso['visual'])
