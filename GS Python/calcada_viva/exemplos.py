from datetime import datetime, timedelta

import servicos


def _t(base, dias=0, horas=0):
    return (base + timedelta(days=dias, hours=horas)).isoformat(timespec="seconds")


def carregar_exemplos(dados):
    base = datetime.now().replace(microsecond=0) - timedelta(days=12)
    relator = "Exemplo (simulado)"

    t1 = servicos.criar_trecho(dados, "Rua das Acácias (fictícia)", "Bairro Modelo", 120, simulado=True)
    t2 = servicos.criar_trecho(dados, "Av. dos Ipês (fictícia)", "Bairro Modelo", 250, simulado=True)
    t3 = servicos.criar_trecho(dados, "Travessa do Cedro (fictícia)", "Bairro Exemplo", 80, simulado=True)

    oc = servicos.registrar_ocorrencia(dados, t1["id"], "superficie", "Buraco grande na calçada",
                                       4, relator, _t(base), True)
    servicos.alterar_status(dados, oc["id"], "validada", "Confirmado em vistoria", _t(base, horas=20))
    servicos.alterar_status(dados, oc["id"], "resolvida", "Calçada reparada", _t(base, dias=5))

    oc = servicos.registrar_ocorrencia(dados, t1["id"], "rampa", "Rampa sem inclinação adequada",
                                       3, relator, _t(base, dias=1), True)
    servicos.alterar_status(dados, oc["id"], "validada", "Confirmado", _t(base, dias=2))

    oc = servicos.registrar_ocorrencia(dados, t1["id"], "iluminacao", "Poste apagado",
                                       3, relator, _t(base, dias=2), True)
    servicos.alterar_status(dados, oc["id"], "validada", "Confirmado", _t(base, dias=3))

    oc = servicos.registrar_ocorrencia(dados, t2["id"], "obstaculo", "Poste e lixeira bloqueando a passagem",
                                       5, relator, _t(base, dias=3), True)
    servicos.alterar_status(dados, oc["id"], "validada", "Confirmado", _t(base, dias=3, horas=6))

    servicos.registrar_ocorrencia(dados, t2["id"], "superficie", "Piso solto em frente ao número 100",
                                  2, relator, _t(base, dias=9), True)

    oc = servicos.registrar_ocorrencia(dados, t2["id"], "obstaculo", "Relato duplicado",
                                       1, relator, _t(base, dias=4), True)
    servicos.alterar_status(dados, oc["id"], "rejeitada", "Duplicado da ocorrência anterior",
                            _t(base, dias=4, horas=3))

    servicos.registrar_ocorrencia(dados, t3["id"], "superficie", "Pequena rachadura",
                                  1, relator, _t(base, dias=10), True)

    servicos.registrar_leitura(dados, t1["id"], 2800, "simulada", _t(base, dias=10), True)
    servicos.registrar_leitura(dados, t1["id"], 420, "simulada", _t(base, dias=11), True)
    servicos.registrar_leitura(dados, t2["id"], 1200, "simulada", _t(base, dias=11), True)
    servicos.registrar_leitura(dados, t3["id"], 3500, "simulada", _t(base, dias=11), True)
    servicos.registrar_leitura(dados, t3["id"], -1, "simulada", _t(base, dias=11, horas=2), True)

    return {
        "trechos": 3,
        "ocorrencias": 7,
        "leituras": 5,
    }
