PROJETO = "Calçada Viva"
DESCRICAO = "Plataforma colaborativa de barreiras urbanas"
EVENTO = "FIAP Global Solution 2026.2 - CitizenTech"
DISCIPLINA = "Python"

INTEGRANTES = [
    {"nome": "Gustavo Basso", "rm": "572623"},
    {"nome": "Kaick Lima", "rm": "574060"},
    {"nome": "Guilherme Sales", "rm": "572933"},
    {"nome": "Pedro Feltrin", "rm": "569038"},
    {"nome": "Guilherme Failla", "rm": "571611"},
]


def texto_integrantes():
    return [f"{i['nome']} - RM {i['rm']}" for i in INTEGRANTES]


def exibir_banner():
    print("=" * 60)
    print(f"  {PROJETO.upper()} - {DESCRICAO}")
    print(f"  {EVENTO}")
    print(f"  Disciplina: {DISCIPLINA}")
    print("-" * 60)
    for linha in texto_integrantes():
        print(f"  {linha}")
    print("=" * 60)
