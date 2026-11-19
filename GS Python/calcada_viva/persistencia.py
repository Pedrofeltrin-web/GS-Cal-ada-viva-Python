import json
import os

ARQUIVO_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")
VERSAO_DADOS = 1


def dados_vazios():
    return {
        "versao": VERSAO_DADOS,
        "contadores": {"trechos": 0, "ocorrencias": 0, "leituras": 0},
        "trechos": [],
        "ocorrencias": [],
        "leituras": [],
    }


def _normalizar(dados):
    base = dados_vazios()
    for chave in ("trechos", "ocorrencias", "leituras"):
        lista = dados.get(chave)
        base[chave] = lista if isinstance(lista, list) else []
        maior = max([item.get("id", 0) for item in base[chave]] or [0])
        guardado = dados.get("contadores", {}).get(chave, 0)
        base["contadores"][chave] = max(maior, guardado if isinstance(guardado, int) else 0)
    return base


def carregar(caminho=ARQUIVO_PADRAO):
    if not os.path.exists(caminho):
        return dados_vazios(), None
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, dict):
            raise ValueError("estrutura inesperada")
    except (json.JSONDecodeError, ValueError, OSError):
        copia = caminho + ".corrompido"
        try:
            os.replace(caminho, copia)
            aviso = f"Arquivo de dados ilegível. Uma cópia foi guardada em '{copia}'."
        except OSError:
            aviso = "Arquivo de dados ilegível. Iniciando com dados vazios."
        return dados_vazios(), aviso
    return _normalizar(dados), None


def salvar(dados, caminho=ARQUIVO_PADRAO):
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    os.replace(temporario, caminho)


def proximo_id(dados, chave):
    dados["contadores"][chave] += 1
    return dados["contadores"][chave]
