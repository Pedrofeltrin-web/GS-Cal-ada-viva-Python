from datetime import datetime

ADC_MAX = 4095
LIMITE_NORMAL_PCT = 40.0
LIMITE_CRITICO_PCT = 15.0

NOTA_ESTADO_LDR = {"Normal": 0, "Atenção": 3, "Crítico": 5}

CATEGORIAS = {
    "superficie": "Buracos e irregularidades",
    "obstaculo": "Obstáculos na passagem",
    "rampa": "Rampas inadequadas",
    "iluminacao": "Iluminação insuficiente",
}

DIVISOR_INDICE = 20
LIMITE_MODERADA = 0.25
LIMITE_ALTA = 0.50


def valor_adc_valido(valor_adc):
    return 0 <= valor_adc <= ADC_MAX


def percentual_luminosidade(valor_adc):
    return round(valor_adc / ADC_MAX * 100, 1)


def classificar_ldr(valor_adc):
    if not valor_adc_valido(valor_adc):
        return "Falha"
    pct = valor_adc / ADC_MAX * 100
    if pct >= LIMITE_NORMAL_PCT:
        return "Normal"
    if pct >= LIMITE_CRITICO_PCT:
        return "Atenção"
    return "Crítico"


def ultima_leitura_valida(dados, trecho_id):
    for leitura in reversed(dados["leituras"]):
        if leitura["trecho_id"] == trecho_id and leitura["estado"] != "Falha":
            return leitura
    return None


def componentes_trecho(dados, trecho_id):
    comp = {categoria: 0 for categoria in CATEGORIAS}
    for oc in dados["ocorrencias"]:
        if oc["trecho_id"] == trecho_id and oc["status"] == "validada":
            comp[oc["categoria"]] = max(comp[oc["categoria"]], oc["gravidade"])
    leitura = ultima_leitura_valida(dados, trecho_id)
    if leitura is not None:
        comp["iluminacao"] = max(comp["iluminacao"], NOTA_ESTADO_LDR[leitura["estado"]])
    return comp


def indice_barreira(comp):
    return sum(comp.values()) / DIVISOR_INDICE


def classificar_indice(b):
    if b < LIMITE_MODERADA:
        return "Baixa"
    if b < LIMITE_ALTA:
        return "Moderada"
    return "Alta"


def exposicao_trajeto(dados, trechos):
    comprimento = 0.0
    exposicao = 0.0
    detalhes = []
    for trecho in trechos:
        comp = componentes_trecho(dados, trecho["id"])
        b = indice_barreira(comp)
        parcial = b * trecho["extensao_m"]
        comprimento += trecho["extensao_m"]
        exposicao += parcial
        detalhes.append({"trecho": trecho, "b": b, "parcial": parcial})
    media = exposicao / comprimento if comprimento > 0 else 0.0
    return {
        "comprimento": comprimento,
        "exposicao": exposicao,
        "media": media,
        "detalhes": detalhes,
    }


def horas_entre(inicio_iso, fim_iso):
    inicio = datetime.fromisoformat(inicio_iso)
    fim = datetime.fromisoformat(fim_iso)
    return (fim - inicio).total_seconds() / 3600


def horas_ate_status(ocorrencia, status_alvo):
    for passo in ocorrencia["historico"]:
        if passo["para"] == status_alvo:
            return horas_entre(ocorrencia["registrada_em"], passo["data"])
    return None


def media_horas_ate_status(dados, status_alvo):
    tempos = []
    for oc in dados["ocorrencias"]:
        horas = horas_ate_status(oc, status_alvo)
        if horas is not None:
            tempos.append(horas)
    if not tempos:
        return None, 0
    return sum(tempos) / len(tempos), len(tempos)
