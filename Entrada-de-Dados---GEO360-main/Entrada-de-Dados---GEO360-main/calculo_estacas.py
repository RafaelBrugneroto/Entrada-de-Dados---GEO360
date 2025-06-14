"""Calculo da capacidade de carga de estacas por metodos semiempiricos.

O modulo implementa funcoes genericas para os metodos de Aoki & Velloso
(1975) e Decourt & Quaresma (1978/1996). Os valores de coeficientes (k, alpha,
C, etc.) devem ser fornecidos pelo usuario conforme o tipo de solo e o tipo da
estaca.

Cada camada de solo e representada por um dicionario contendo:
    - 'Prof_Inicial': profundidade inicial da camada (m)
    - 'Prof_Final'  : profundidade final da camada (m)
    - 'Tipo_Solo'   : descricao ou chave do tipo de solo
    - 'NSPT'        : valor do SPT representativo da camada

As funcoes retornam a carga de ruptura (qult) e, no caso de Decourt &
Quaresma, tambem a carga admissivel (qadm).
"""

from typing import List, Dict


def aoki_velloso(
    camadas: List[Dict],
    n_ponta: float,
    area_ponta: float,
    perimetro_fuste: float,
    k: Dict[str, float],
    alpha: Dict[str, float],
    f1: float = 1.0,
    f2: float = 2.0,
    tipo_solo_ponta: str | None = None,
) -> float:
    """Calcula a carga de ruptura pelo metodo de Aoki & Velloso.

    Parameters
    ----------
    camadas : lista de camadas de solo ao longo do fuste.
    n_ponta : valor de NSPT representativo junto a ponta da estaca.
    area_ponta : area da base da estaca (m^2).
    perimetro_fuste : perimetro do fuste (m).
    k : dicionario com coeficiente k por tipo de solo.
    alpha : dicionario com coeficiente alpha por tipo de solo.
    f1, f2 : coeficientes de correcao propostos por Aoki & Velloso.
    tipo_solo_ponta : opcional, tipo de solo na ponta. Se None, usa o das
        camadas fornecidas cuja profundidade final contem a ponta.
    """
    # Determina o tipo de solo na ponta se nao fornecido
    if tipo_solo_ponta is None:
        if not camadas:
            raise ValueError("Lista de camadas vazia")
        tipo_solo_ponta = camadas[-1]["Tipo_Solo"]

    n_ponta = min(n_ponta, 50)
    k_ponta = k.get(tipo_solo_ponta)
    if k_ponta is None:
        raise KeyError(f"Coeficiente k nao definido para {tipo_solo_ponta}")

    qult_ponta = f1 * area_ponta * k_ponta * n_ponta

    qult_lateral = 0.0
    for camada in camadas:
        solo = camada["Tipo_Solo"]
        n = min(float(camada.get("NSPT", 0)), 50)
        comp = float(camada["Prof_Final"]) - float(camada["Prof_Inicial"])
        k_c = k.get(solo)
        a_c = alpha.get(solo)
        if k_c is None or a_c is None:
            raise KeyError(f"Coeficientes k/alpha nao definidos para {solo}")
        tau = a_c * k_c * n
        qult_lateral += tau * comp

    qult_lateral *= perimetro_fuste * f2
    return qult_ponta + qult_lateral


def decourt_quaresma(
    camadas: List[Dict],
    n_ponta: float,
    area_ponta: float,
    perimetro_fuste: float,
    C: Dict[str, float],
    alpha_l: Dict[str, float],
    FSP: float = 2.0,
    FSL: float = 2.0,
    alpha_p: float = 1.0,
    tipo_solo_ponta: str | None = None,
) -> Dict[str, float]:
    """Calcula a carga de ruptura e admissivel pelo metodo de Decourt & Quaresma.

    Parameters
    ----------
    camadas : lista de camadas de solo ao longo do fuste.
    n_ponta : NSPT na ponta (media de tres valores, limitado a 50).
    area_ponta : area da base da estaca (m^2).
    perimetro_fuste : perimetro do fuste (m).
    C : coeficiente para resistencia de ponta por tipo de solo.
    alpha_l : coeficiente para adesao lateral (alpha') por tipo de solo.
    FSP, FSL : fatores de seguranca parciais para a ponta e o atrito lateral.
    alpha_p : coeficiente de majoração/minoração da ponta.
    tipo_solo_ponta : opcional, tipo de solo na ponta.
    """
    if tipo_solo_ponta is None:
        if not camadas:
            raise ValueError("Lista de camadas vazia")
        tipo_solo_ponta = camadas[-1]["Tipo_Solo"]

    n_ponta = min(n_ponta, 50)
    C_ponta = C.get(tipo_solo_ponta)
    if C_ponta is None:
        raise KeyError(f"Coeficiente C nao definido para {tipo_solo_ponta}")

    qp_ult = alpha_p * C_ponta * n_ponta
    qult_ponta = area_ponta * qp_ult

    qult_lateral = 0.0
    for camada in camadas:
        solo = camada["Tipo_Solo"]
        n = min(float(camada.get("NSPT", 0)), 50)
        comp = float(camada["Prof_Final"]) - float(camada["Prof_Inicial"])
        a_l = alpha_l.get(solo)
        if a_l is None:
            raise KeyError(f"Coeficiente alpha_l nao definido para {solo}")
        tau = a_l * n
        qult_lateral += tau * comp

    qult_lateral *= perimetro_fuste

    qult_total = qult_ponta + qult_lateral
    qadm = qult_ponta / FSP + qult_lateral / FSL
    return {"qult": qult_total, "qadm": qadm}


if __name__ == "__main__":
    # Exemplo simples de uso
    camadas_exemplo = [
        {"Prof_Inicial": 0.0, "Prof_Final": 2.0, "Tipo_Solo": "Areia", "NSPT": 15},
        {"Prof_Inicial": 2.0, "Prof_Final": 5.0, "Tipo_Solo": "Argila", "NSPT": 8},
    ]
    k = {"Areia": 0.1, "Argila": 0.05}
    alpha = {"Areia": 0.5, "Argila": 0.7}
    C = {"Areia": 0.5, "Argila": 0.3}
    alpha_l = {"Areia": 5.0, "Argila": 3.0}

    q_aoki = aoki_velloso(
        camadas_exemplo,
        n_ponta=20,
        area_ponta=0.2,
        perimetro_fuste=1.0,
        k=k,
        alpha=alpha,
        f1=1.0,
        f2=2.0,
        tipo_solo_ponta="Areia",
    )
    print(f"Aoki & Velloso - qult = {q_aoki:.2f} kN")

    res_dq = decourt_quaresma(
        camadas_exemplo,
        n_ponta=20,
        area_ponta=0.2,
        perimetro_fuste=1.0,
        C=C,
        alpha_l=alpha_l,
        FSP=2.0,
        FSL=2.0,
        alpha_p=1.0,
        tipo_solo_ponta="Areia",
    )
    print(
        f"Décourt & Quaresma - qult = {res_dq['qult']:.2f} kN, qadm = {res_dq['qadm']:.2f} kN"
    )
