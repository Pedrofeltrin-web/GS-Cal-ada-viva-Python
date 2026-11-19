from datetime import datetime

import calculos
import persistencia

STATUS_VALIDOS = ("pendente", "validada", "rejeitada", "resolvida")
TRANSICOES = {
    "pendente": ("validada", "rejeitada"),
    "validada": ("resolvida",),
}


def agora():
    return datetime.now().isoformat(timespec="seconds")


def buscar_trecho(dados, trecho_id):
    for trecho in dados["trechos"]:
        if trecho["id"] == trecho_id:
            return trecho
    return None


def criar_trecho(dados, nome, bairro, extensao_m, simulado=False):
    if extensao_m <= 0:
        raise ValueError("A extensão deve ser maior que zero.")
    trecho = {
        "id": persistencia.proximo_id(dados, "trechos"),
        "nome": nome,
        "bairro": bairro,
        "extensao_m": float(extensao_m),
        "criado_em": agora(),
        "simulado": simulado,
    }
    dados["trechos"].append(trecho)
    return trecho


def atualizar_trecho(dados, trecho_id, nome=None, bairro=None, extensao_m=None):
    trecho = buscar_trecho(dados, trecho_id)
    if trecho is None:
        raise ValueError("Trecho não encontrado.")
    if extensao_m is not None and extensao_m <= 0:
        raise ValueError("A extensão deve ser maior que zero.")
    if nome:
        trecho["nome"] = nome
    if bairro:
        trecho["bairro"] = bairro
    if extensao_m is not None:
        trecho["extensao_m"] = float(extensao_m)
    return trecho


def remover_trecho(dados, trecho_id):
    trecho = buscar_trecho(dados, trecho_id)
    if trecho is None:
        raise ValueError("Trecho não encontrado.")
    if any(oc["trecho_id"] == trecho_id for oc in dados["ocorrencias"]):
        raise ValueError("Há ocorrências neste trecho. Não é possível removê-lo.")
    if any(lt["trecho_id"] == trecho_id for lt in dados["leituras"]):
        raise ValueError("Há leituras de sensor neste trecho. Não é possível removê-lo.")
    dados["trechos"].remove(trecho)
    return trecho


def buscar_ocorrencia(dados, ocorrencia_id):
    for oc in dados["ocorrencias"]:
        if oc["id"] == ocorrencia_id:
            return oc
    return None


def registrar_ocorrencia(dados, trecho_id, categoria, descricao, gravidade,
                         relator, quando=None, simulado=False):
    if buscar_trecho(dados, trecho_id) is None:
        raise ValueError("Trecho não encontrado.")
    if categoria not in calculos.CATEGORIAS:
        raise ValueError("Categoria inválida.")
    if not 1 <= gravidade <= 5:
        raise ValueError("A gravidade deve estar entre 1 e 5.")
    instante = quando or agora()
    ocorrencia = {
        "id": persistencia.proximo_id(dados, "ocorrencias"),
        "trecho_id": trecho_id,
        "categoria": categoria,
        "descricao": descricao,
        "gravidade": gravidade,
        "relator": relator,
        "status": "pendente",
        "registrada_em": instante,
        "simulado": simulado,
        "historico": [
            {"data": instante, "de": None, "para": "pendente", "obs": "Relato registrado"}
        ],
    }
    dados["ocorrencias"].append(ocorrencia)
    return ocorrencia


def alterar_status(dados, ocorrencia_id, novo_status, observacao="", quando=None):
    ocorrencia = buscar_ocorrencia(dados, ocorrencia_id)
    if ocorrencia is None:
        raise ValueError("Ocorrência não encontrada.")
    permitidos = TRANSICOES.get(ocorrencia["status"], ())
    if novo_status not in permitidos:
        raise ValueError(
            f"Não é possível passar de '{ocorrencia['status']}' para '{novo_status}'."
        )
    ocorrencia["historico"].append({
        "data": quando or agora(),
        "de": ocorrencia["status"],
        "para": novo_status,
        "obs": observacao or "",
    })
    ocorrencia["status"] = novo_status
    return ocorrencia


def listar_ocorrencias(dados, trecho_id=None, categoria=None, status=None):
    resultado = []
    for oc in dados["ocorrencias"]:
        if trecho_id is not None and oc["trecho_id"] != trecho_id:
            continue
        if categoria is not None and oc["categoria"] != categoria:
            continue
        if status is not None and oc["status"] != status:
            continue
        resultado.append(oc)
    return resultado


def registrar_leitura(dados, trecho_id, valor_adc, fonte="manual", quando=None,
                      simulado=False):
    if buscar_trecho(dados, trecho_id) is None:
        raise ValueError("Trecho não encontrado.")
    leitura = {
        "id": persistencia.proximo_id(dados, "leituras"),
        "trecho_id": trecho_id,
        "valor_adc": valor_adc,
        "percentual": (calculos.percentual_luminosidade(valor_adc)
                       if calculos.valor_adc_valido(valor_adc) else None),
        "estado": calculos.classificar_ldr(valor_adc),
        "fonte": fonte,
        "data": quando or agora(),
        "simulado": simulado,
    }
    dados["leituras"].append(leitura)
    return leitura


def leituras_do_trecho(dados, trecho_id):
    return [lt for lt in dados["leituras"] if lt["trecho_id"] == trecho_id]


def remover_simulados(dados):
    removidos = {}
    for chave in ("ocorrencias", "leituras", "trechos"):
        antes = len(dados[chave])
        dados[chave] = [item for item in dados[chave] if not item.get("simulado")]
        removidos[chave] = antes - len(dados[chave])
    return removidos
