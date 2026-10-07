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


def simular_replicacion(cadena_5_3: str, tam_okazaki: int = 10, tam_primer: int = 3) -> Dict[str, Any]:
    """
    Simula paso a paso la replicación de una molécula de ADN bicatenario.

    Parámetros:
      cadena_5_3: Hebra original 1 en sentido 5' -> 3'.
      tam_okazaki: Tamaño en nucleótidos de cada fragmento de Okazaki (por defecto 10).
      tam_primer: Tamaño en ribonucleótidos de cada cebador de ARN (por defecto 3).

    Retorna un diccionario completo con:
      - Hebras parentales
      - Pasos explicativos con la enzima actuando
      - Detalle de la cadena líder (continua)
      - Detalle de la cadena rezagada (fragmentos de Okazaki, cebadores, reemplazo y ligación)
      - Nuevas moléculas bicatenarias resultantes (demostrando semiconservatividad)
    """
    cadena_5_3 = cadena_5_3.upper().strip()
    longitud = len(cadena_5_3)
    cadena_3_5 = obtener_cadena_complementaria(cadena_5_3)

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
            "La Topoisomerasa alivia la tensión superhelicoidal y las proteínas SSB "
            "(Single-Stranded Binding) recubren las hebras sencillas para evitar que vuelvan a unirse."
        ),
        "visual": (
            f"5'- {cadena_5_3} -3'  (Hebra Molde para Cadena Rezagada)\n"
            f"    {' ' * (longitud // 2)}<--- Horquilla de replicación abierta por Helicasa\n"
            f"3'- {cadena_3_5} -5'  (Hebra Molde para Cadena Líder)"
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
            f"1. La ARN Primasa coloca un único cebador de ARN ({primer_lider}) en el extremo 3' del molde.\n"
            f"2. La ADN Polimerasa III utiliza el 3'-OH libre del cebador y sintetiza ADN de forma continua "
            f"en dirección 5'->3', acompañando el avance de la horquilla."
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
    # Dado que la polimerasa SOLO puede sintetizar en sentido 5' -> 3', la síntesis
    # se realiza en sentido contrario al avance de la horquilla, requiriendo
    # múltiples cebadores de ARN y generando los fragmentos de Okazaki.

    fragmentos_okazaki = []
    inicio = 0
    num_fragmento = 1

    while inicio < longitud:
        fin = min(inicio + tam_okazaki, longitud)
        tramo_molde = cadena_5_3[inicio:fin]

        # Parte del cebador y parte de ADN en este fragmento
        long_primer_frag = min(tam_primer, len(tramo_molde))
        sub_primer_arn = "".join(COMPLEMENTO_ARN[b] for b in tramo_molde[:long_primer_frag])
        sub_adn = "".join(COMPLEMENTO_ADN[b] for b in tramo_molde[long_primer_frag:])
        secuencia_total_okazaki = sub_primer_arn + sub_adn
        secuencia_dna_final = "".join(COMPLEMENTO_ADN[b] for b in tramo_molde)

        fragmentos_okazaki.append({
            "numero": num_fragmento,
            "rango": (inicio, fin),
            "molde": tramo_molde,
            "cebador_arn": sub_primer_arn,
            "adn_sintetizado": sub_adn,
            "okazaki_con_arn": f"[{sub_primer_arn}]-{sub_adn}" if sub_adn else f"[{sub_primer_arn}]",
            "dna_maduro": secuencia_dna_final
        })

        inicio = fin
        num_fragmento += 1

    # Descripción visual de los fragmentos (síntesis de 5' a 3' sobre molde 5'->3')
    diagrama_okazaki = "  ".join(f"[Okz#{f['numero']}: 5'-{f['okazaki_con_arn']}-3']" for f in fragmentos_okazaki)

    pasos.append({
        "etapa": "Cadena Rezagada - Fragmentos de Okazaki",
        "enzima": "ARN Primasa + ADN Polimerasa III",
        "descripcion": (
            f"En la cadena rezagada (molde 5'->3'), la síntesis es discontinua.\n"
            f"La ARN Primasa sintetiza múltiples cebadores cortos de ARN.\n"
            f"La ADN Polimerasa III elonga cada cebador produciendo {len(fragmentos_okazaki)} Fragmentos de Okazaki."
        ),
        "visual": (
            f"Molde Rezagada : 5'- {cadena_5_3} -3'\n"
            f"Síntesis Okazaki: 3'- {diagrama_okazaki}\n"
            f"  Nota: Cada fragmento contiene un cebador de ARN entre corchetes [...] seguido de ADN."
        )
    })

    # --------------------------------------------------------------------------
    # PASO 4: Maduración de Fragmentos de Okazaki y Acción de la Ligasa
    # --------------------------------------------------------------------------
    pasos.append({
        "etapa": "Reemplazo de Cebadores",
        "enzima": "ADN Polimerasa I",
        "descripcion": (
            "La ADN Polimerasa I posee actividad exonucleasa 5'->3': degrada y elimina "
            "los cebadores de ARN de cada fragmento de Okazaki y de la cadena líder, "
            "rellenando los huecos con desoxirribonucleótidos (ADN)."
        ),
        "visual": (
            f"Fragmentos con ADN: 3'- " + " -|- ".join(f['dna_maduro'] for f in fragmentos_okazaki) + " -5'\n"
            f"  (Persisten muescas/nicks en el esqueleto de fosfodiéster entre fragmentos)"
        )
    })

    cadena_rezagada_sellada = "".join(COMPLEMENTO_ADN[b] for b in cadena_5_3)

    pasos.append({
        "etapa": "Sellado de Muescas (Ligation)",
        "enzima": "ADN Ligasa",
        "descripcion": (
            "La ADN Ligasa cataliza la formación de enlaces fosfodiéster covalentes "
            "entre el grupo 3'-OH de un fragmento y el grupo 5'-fosfato del fragmento adyacente, "
            "convirtiendo la cadena rezagada en una hebra de ADN continua y madura."
        ),
        "visual": (
            f"Cadena Rezagada Sellada: 3'- {cadena_rezagada_sellada} -5'\n"
            f"Molde Original         : 5'- {cadena_5_3} -3'\n"
            f"¡Cadena continua completada con éxito!"
        )
    })

    # --------------------------------------------------------------------------
    # Resultado Final Semiconservativo: 2 moléculas bicatenarias idénticas
    # --------------------------------------------------------------------------
    # Molécula 1: Hebra original 1 (5'->3') + Cadena Rezagada Nueva (3'->5')
    # Molécula 2: Hebra original 2 (3'->5') + Cadena Líder Nueva (5'->3')
    resultado_final = {
        "molecula_1": {
            "hebra_antigua": f"5'- {cadena_5_3} -3'",
            "hebra_nueva":   f"3'- {cadena_rezagada_sellada} -5'",
            "tipo_sintesis": "Cadena Rezagada (madurada y ligada)"
        },
        "molecula_2": {
            "hebra_antigua": f"3'- {cadena_3_5} -5'",
            "hebra_nueva":   f"5'- {cadena_lider_completa} -3'",
            "tipo_sintesis": "Cadena Líder (continua)"
        }
    }

    return {
        "hebra_original_5_3": cadena_5_3,
        "hebra_original_3_5": cadena_3_5,
        "fragmentos_okazaki": fragmentos_okazaki,
        "cadena_lider": cadena_lider_completa,
        "cadena_rezagada": cadena_rezagada_sellada,
        "pasos": pasos,
        "resultado_final": resultado_final
    }


if __name__ == "__main__":
    # Prueba rápida unitaria del módulo
    secuencia_demo = "ATGCGATCGATCGATCGATCGATCGATCGATCTAG"
    datos = simular_replicacion(secuencia_demo)
    print("=== TEST REPLICACIÓN ===")
    for paso in datos["pasos"]:
        print(f"\n[{paso['enzima']}] - {paso['etapa']}")
        print(paso['descripcion'])
        print(paso['visual'])
