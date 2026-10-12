"""
================================================================================
MÓDULO DE REPLICACIÓN DEL ADN
================================================================================
Este módulo simula de forma detallada y pedagógica el proceso biológico de la
replicación semiconservativa del ADN celular.

Enzimas y factores simulados:
  1. Helicasa: Desenrolla la doble hélice y rompe los puentes de hidrógeno.
  2. Topoisomerasa / Girasa: Alivia la tensión torsional por delante de la horquilla.
  3. Proteínas SSB: Estabilizan las cadenas sencillas para evitar que se reasocien.
  4. ARN Primasa: Sintetiza cebadores (primers) de ARN necesarios para iniciar la polimerización.
  5. ADN Polimerasa III: Sintetiza la cadena continua (líder) y discontinua (rezagada) en sentido 5'->3'.
  6. Fragmentos de Okazaki: Tramos discontinuos en la cadena rezagada (cebador ARN + ADN).
  7. ADN Polimerasa I: Elimina cebadores de ARN y los reemplaza por nucleótidos de ADN.
  8. ADN Ligasa: Sella las muescas (nicks) uniendo los fragmentos mediante enlaces fosfodiéster.
================================================================================
"""

from typing import List, Dict, Tuple, Any

# Reglas de complementariedad para ADN: A <-> T, C <-> G
COMPLEMENTO_ADN = {
    'A': 'T', 'T': 'A',
    'C': 'G', 'G': 'C',
    'a': 't', 't': 'a',
    'c': 'g', 'g': 'c'
}

# Complementariedad para síntesis de ARN primer: ADN -> ARN (A->U, T->A, C->G, G->C)
COMPLEMENTO_ARN = {
    'A': 'U', 'T': 'A',
    'C': 'G', 'G': 'C',
    'a': 'u', 't': 'a',
    'c': 'g', 'g': 'c'
}


def obtener_cadena_complementaria(cadena_adn: str) -> str:
    """Devuelve la cadena complementaria de ADN respetando A-T y C-G."""
    return "".join(COMPLEMENTO_ADN.get(base.upper(), 'N') for base in cadena_adn)


def simular_replicacion(cadena_adn: str, tam_okazaki: int = 10, tam_primer: int = 3, es_5a3: bool = True) -> Dict[str, Any]:
    """
    Simula paso a paso la replicación de una molécula de ADN bicatenario.

    Parámetros:
      cadena_adn: Secuencia de ADN introducida.
      tam_okazaki: Tamaño en nucleótidos de cada fragmento de Okazaki (por defecto 10).
      tam_primer: Tamaño en ribonucleótidos de cada cebador de ARN (por defecto 3).
      es_5a3: Indica si la secuencia suministrada está orientada en sentido 5' -> 3' (True)
              o en sentido 3' -> 5' (False).

    Retorna un diccionario completo con:
      - Hebras parentales
      - Pasos explicativos con la enzima actuando
      - Detalle de la cadena líder (continua)
      - Detalle de la cadena rezagada (fragmentos de Okazaki, cebadores, reemplazo y ligación)
      - Nuevas moléculas bicatenarias resultantes (demostrando semiconservatividad)
    """
    cadena_adn = cadena_adn.upper().strip()
    longitud = len(cadena_adn)

    if es_5a3:
        cadena_5_3 = cadena_adn
        cadena_3_5 = obtener_cadena_complementaria(cadena_5_3)
    else:
        cadena_3_5 = cadena_adn
        cadena_5_3 = obtener_cadena_complementaria(cadena_3_5)


    pasos = []

    # --------------------------------------------------------------------------
    # PASO 1: Apertura por Helicasa, Topoisomerasa y Proteínas SSB
    # --------------------------------------------------------------------------
    pasos.append({
        "etapa": "Iniciación de la horquilla",
        "enzima": "Helicasa + Topoisomerasa + SSB",
        "descripcion": (
            "La Helicasa rompe los puentes de hidrógeno entre las bases nitrogenadas, "
            "abriendo la doble hélice y creando la horquilla de replicación. "
            "La Topoisomerasa alivia la tensión superhelicoidal por delante de la horquilla "
            "y las proteínas SSB (Single-Stranded Binding) recubren las hebras sencillas para "
            "evitar que vuelvan a unirse o formen estructuras secundarias."
        ),
        "visual": (
            f"     5'- {cadena_5_3} -3'  (Hebra Molde para Cadena Rezagada)\n"
            f"Horquilla de replicación abierta por Helicasa --->\n"
            f"     3'- {cadena_3_5} -5'  (Hebra Molde para Cadena Líder)"
        )
    })

    # --------------------------------------------------------------------------
    # PASO 2: Síntesis de la Cadena Líder / Adelantada (Continuous Strand)
    # --------------------------------------------------------------------------
    # Molde: Hebra 3' -> 5' (cadena_3_5)
    # Síntesis: Se realiza de forma continua en sentido 5' -> 3' avanzando hacia la horquilla.
    primer_lider = "".join(COMPLEMENTO_ARN[b] for b in cadena_3_5[:tam_primer])
    adn_lider_restante = "".join(COMPLEMENTO_ADN[b] for b in cadena_3_5[tam_primer:])
    cadena_lider_completa = "".join(COMPLEMENTO_ADN[b] for b in cadena_3_5)

    pasos.append({
        "etapa": "Cadena Líder - Síntesis Continua",
        "enzima": "ARN Primasa + ADN Polimerasa III",
        "descripcion": (
            f"1. La ARN Primasa coloca un único cebador de ARN (5'-{primer_lider}-3') en el extremo 3' del molde.\n"
            f"2. La ADN Polimerasa III utiliza el 3'-OH libre del cebador y sintetiza ADN de forma continua "
            f"en dirección 5'->3', leyendo el molde directamente en sentido 3'->5' y avanzando hacia la horquilla."
        ),
        "visual": (
            f"Molde Líder: 3'- {cadena_3_5} -5'\n"
            f"Cebador ARN: 5'- [{primer_lider}] (ARN Primasa)\n"
            f"Elongación : 5'- [{primer_lider}]{adn_lider_restante} -3' (ADN Polimerasa III)"
        )
    })

    # --------------------------------------------------------------------------
    # PASO 3: Síntesis de la Cadena Rezagada / Retrasada (Lagging Strand)
    # --------------------------------------------------------------------------
    # Molde: Hebra 5' -> 3' (cadena_5_3).
    # Como la polimerasa SOLO lee en sentido 3'->5' y sintetiza en 5'->3', la síntesis
    # se realiza a contracorriente del avance de la horquilla, desde el extremo 3'
    # del molde hacia su extremo 5'.
    # Cada fragmento de Okazaki se sintetiza en sentido 5' -> 3' a partir de su molde leído 3' -> 5'.

    fragmentos_okazaki = []
    num_fragmento = 1

    # Recorremos el molde 5'->3' desde su extremo 3' (el final) hacia su extremo 5' (el principio)
    for inicio in range(0, longitud, tam_okazaki):
        fin = max(0, inicio + tam_okazaki)
        tramo_molde_5a3 = cadena_5_3[inicio:fin]
        # Invertimos el tramo para que la polimerasa lo lea en sentido 3' -> 5'
        tramo_molde_3a5 = tramo_molde_5a3[::-1]

        # Tamaño del cebador para este fragmento
        long_primer_frag = min(tam_primer, len(tramo_molde_3a5))
        # Cebador de ARN sintetizado en sentido 5' -> 3' sobre el molde 3' -> 5'
        sub_primer_arn = "".join(COMPLEMENTO_ARN[b] for b in tramo_molde_3a5[:long_primer_frag])
        # ADN elongado en sentido 5' -> 3' por ADN Polimerasa III
        sub_adn = "".join(COMPLEMENTO_ADN[b] for b in tramo_molde_3a5[long_primer_frag:])
        secuencia_total_okazaki = sub_primer_arn + sub_adn

        # ADN maduro correspondiente a este fragmento (tras reemplazar ARN por ADN)
        secuencia_dna_maduro = "".join(COMPLEMENTO_ADN[b] for b in tramo_molde_3a5)

        fragmentos_okazaki.append({
            "numero": num_fragmento,
            "rango": (inicio, fin),
            "molde": tramo_molde_5a3,
            "molde_3a5": tramo_molde_3a5,
            "cebador_arn": sub_primer_arn,
            "adn_sintetizado": sub_adn,
            "okazaki_con_arn": f"{sub_adn[::-1]}-[{sub_primer_arn[::-1]}]" if sub_adn else f"[{sub_primer_arn[::-1]}]",
            "dna_maduro": secuencia_dna_maduro[::-1]
        })
        num_fragmento += 1

    # Descripción visual de los fragmentos (todos sintetizados en sentido 5' -> 3')
    diagrama_okazaki = "  ".join(f"[Okz#{f['numero']}: 3'-{f['okazaki_con_arn']}-5']" for f in fragmentos_okazaki)
    pasos.append({
        "etapa": "Cadena Rezagada - Fragmentos de Okazaki",
        "enzima": "ARN Primasa + ADN Polimerasa III",
        "descripcion": (
            f"En la cadena rezagada (molde 5'->3'), la síntesis es discontinua y a contracorriente.\n"
            f"La polimerasa recorre el molde de 3' a 5', por lo que los fragmentos se generan "
            f"desde el extremo 3' hacia el 5' del molde.\n"
            f"Para cada fragmento, la ARN Primasa sintetiza un cebador y la ADN Polimerasa III "
            f"elonga en sentido 5'->3', produciendo {len(fragmentos_okazaki)} Fragmentos de Okazaki."
        ),
        "visual": (
            f"Molde Rezagada : 5'- {cadena_5_3} -3'\n"
            #f"Molde (3'->5') : 3'- {cadena_5_3[::-1]} -5'\n"
            f"Síntesis Okazaki (3'->5'):\n  {diagrama_okazaki}\n"
            f"  Nota: Cada fragmento contiene un cebador de ARN [...] y se sintetiza estrictamente en 5'->3'."
        )
    })

    # --------------------------------------------------------------------------
    # PASO 4: Maduración de Cebadores (Cadena Líder y Fragmentos de Okazaki)
    # --------------------------------------------------------------------------
    primer_lider_adn = primer_lider.replace('U', 'T')

    pasos.append({
        "etapa": "Reemplazo de Cebadores (Líder y Rezagada)",
        "enzima": "ADN Polimerasa I",
        "descripcion": (
            "La ADN Polimerasa I posee actividad exonucleasa 5'->3': degrada y elimina "
            "todos los cebadores de ARN celulares.\n"
            "1. En la CADENA LÍDER: retira el cebador inicial de ARN y lo reemplaza por ADN.\n"
            "2. En la CADENA REZAGADA: retira el cebador de cada fragmento de Okazaki "
            "sustituyendo los ribonucleótidos (U) por desoxirribonucleótidos (T)."
        ),
        "visual": (
            f"1. Cadena Líder madurada (Cebador ARN 5'-{primer_lider}-3' -> ADN 5'-{primer_lider_adn}-3'):\n"
            f"   5'- {cadena_lider_completa} -3'\n"
            f"2. Fragmentos de Okazaki madurados (reemplazo de U por T):\n  " +
            "  ".join(f"[Okz#{f['numero']}: 3'-{f['dna_maduro']}-5']" for f in fragmentos_okazaki) +
            "\n  (Persisten muescas/nicks en el esqueleto de fosfodiéster entre fragmentos)"
        )
    })

    # --------------------------------------------------------------------------
    # PASO 5: Sellado por ADN Ligasa y Conformación Final de las Dos Dobles Hélices
    # --------------------------------------------------------------------------
    cadena_rezagada_sellada_5a3 = "".join(f["dna_maduro"] for f in fragmentos_okazaki)

    pasos.append({
        "etapa": "Sellado de Muescas (Ligación) y Dúplex Finales",
        "enzima": "ADN Ligasa",
        "descripcion": (
            "La ADN Ligasa cataliza la formación de enlaces fosfodiéster covalentes "
            "entre el grupo 3'-OH de un fragmento madurado y el grupo 5'-fosfato del fragmento adyacente, "
            "sellando los fragmentos en una hebra de ADN continua en dirección 5' -> 3'.\n"
            "Con ello, se completan las dos moléculas hijas de ADN bicatenario con carácter semiconservativo."
        ),
        "visual": (
            f"DÚPLEX 1 (Molde Parental 1 + Nueva Cadena Rezagada Ligada):\n"
            f"  5'- {cadena_5_3} -3'  [Hebra Parental Original]\n"
            f"      {'|' * longitud}      (Puentes de hidrógeno)\n"
            f"  3'- {cadena_rezagada_sellada_5a3} -5'  [Nueva Cadena Rezagada (Fragmentos Okazaki)]\n\n"
            f"DÚPLEX 2 (Molde Parental 2 + Nueva Cadena Líder):\n"
            f"  3'- {cadena_3_5} -5'  [Hebra Parental Original]\n"
            f"      {'|' * longitud}      (Puentes de hidrógeno)\n"
            f"  5'- {cadena_lider_completa} -3'  [Nueva Cadena Líder (síntesis continua)]"
        )
    })

    # --------------------------------------------------------------------------
    # Resultado Final Semiconservativo: 2 moléculas bicatenarias idénticas
    # --------------------------------------------------------------------------
    # Molécula 1: Molde parental 1 (5'->3') + Cadena Rezagada Nueva (5'->3', antiparalela)
    # Molécula 2: Molde parental 2 (3'->5') + Cadena Líder Nueva (5'->3')
    resultado_final = {
        "molecula_1": {
            "hebra_antigua": f"5'- {cadena_5_3} -3'",
            "hebra_nueva":   f"5'- {cadena_rezagada_sellada_5a3} -3'",
            "tipo_sintesis": "Cadena Rezagada (fragmentos de Okazaki madurados y ligados)"
        },
        "molecula_2": {
            "hebra_antigua": f"3'- {cadena_3_5} -5'",
            "hebra_nueva":   f"5'- {cadena_lider_completa} -3'",
            "tipo_sintesis": "Cadena Líder (síntesis continua)"
        }
    }

    return {
        "hebra_original_5_3": cadena_5_3,
        "hebra_original_3_5": cadena_3_5,
        "fragmentos_okazaki": fragmentos_okazaki,
        "cadena_lider": cadena_lider_completa,
        "cadena_rezagada": cadena_rezagada_sellada_5a3,
        "pasos": pasos,
        "resultado_final": resultado_final,
        "es_5a3": es_5a3
    }


if __name__ == "__main__":
    # Prueba rápida unitaria del módulo
    secuencia_demo = "ATGCGATCGATCGATCGATCGATCGATCGATCTAG"
    datos = simular_replicacion(secuencia_demo)
    print("=== TEST REPLICACIÓN BIOLÓGICAMENTE CORREGIDA ===")
    for paso in datos["pasos"]:
        print(f"\n[{paso['enzima']}] - {paso['etapa']}")
        print(paso['descripcion'])
        print(paso['visual'])
