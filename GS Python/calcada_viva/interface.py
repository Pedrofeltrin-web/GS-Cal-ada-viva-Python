from datetime import datetime

import calculos
import exemplos
import integrantes
import persistencia
import servicos
import validacoes as v

LARGURA = 66


def titulo(texto):
    print("\n" + "=" * LARGURA)
    print(f" {texto}")
    print("=" * LARGURA)


def formatar_data(iso):
    return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")


def formatar_horas(horas):
    if horas is None:
        return "-"
    if horas < 24:
        return f"{horas:.1f} h"
    return f"{horas / 24:.1f} dias"


def cortar(texto, tamanho):
    return texto if len(texto) <= tamanho else texto[: tamanho - 1] + "."


def marca(item):
    return "*" if item.get("simulado") else " "


def salvar(dados, caminho):
    try:
        persistencia.salvar(dados, caminho)
    except OSError as erro:
        print(f"  ! Não foi possível salvar os dados: {erro}")


def exibir_menu(nome, opcoes):
    titulo(nome)
    for chave, texto in opcoes:
        print(f"  {chave} - {texto}")
    return v.ler_opcao("Escolha uma opção: ", [chave for chave, _ in opcoes])


def pausar():
    input("\nPressione Enter para continuar...")


def mostrar_tabela_trechos(dados):
    if not dados["trechos"]:
        print("  Nenhum trecho cadastrado.")
        return False
    print(f"  {'ID':>3}   {'Trecho':<30} {'Bairro':<16} {'Ext.(m)':>8} {'b(x)':>6}  Faixa")
    for t in dados["trechos"]:
        b = calculos.indice_barreira(calculos.componentes_trecho(dados, t["id"]))
        print(f"  {t['id']:>3} {marca(t)} {cortar(t['nome'], 30):<30} {cortar(t['bairro'], 16):<16} "
              f"{t['extensao_m']:>8.1f} {b:>6.2f}  {calculos.classificar_indice(b)}")
    print("  (* = dado simulado)")
    return True


def escolher_trecho(dados, prompt="ID do trecho (0 para cancelar): "):
    if not mostrar_tabela_trechos(dados):
        return None
    while True:
        numero = v.ler_inteiro(prompt, minimo=0)
        if numero == 0:
            return None
        trecho = servicos.buscar_trecho(dados, numero)
        if trecho is not None:
            return trecho
        print("  Trecho não encontrado. Confira o ID na lista.")


def escolher_categoria():
    chaves = list(calculos.CATEGORIAS)
    for posicao, chave in enumerate(chaves, start=1):
        print(f"  {posicao} - {calculos.CATEGORIAS[chave]}")
    numero = v.ler_inteiro("Categoria: ", minimo=1, maximo=len(chaves))
    return chaves[numero - 1]


def mostrar_tabela_ocorrencias(lista, dados):
    if not lista:
        print("  Nenhuma ocorrência encontrada.")
        return False
    print(f"  {'ID':>3}   {'Trecho':<20} {'Categoria':<26} {'Grav':>4}  {'Status':<10} Data")
    for oc in lista:
        trecho = servicos.buscar_trecho(dados, oc["trecho_id"])
        nome = trecho["nome"] if trecho else f"#{oc['trecho_id']}"
        print(f"  {oc['id']:>3} {marca(oc)} {cortar(nome, 20):<20} "
              f"{cortar(calculos.CATEGORIAS[oc['categoria']], 26):<26} {oc['gravidade']:>4}  "
              f"{oc['status']:<10} {formatar_data(oc['registrada_em'])}")
    print("  (* = dado simulado)")
    return True


def mostrar_detalhe_ocorrencia(oc, dados):
    trecho = servicos.buscar_trecho(dados, oc["trecho_id"])
    print(f"\n  Ocorrência #{oc['id']}{' (simulada)' if oc.get('simulado') else ''}")
    print(f"  Trecho    : {trecho['nome'] if trecho else oc['trecho_id']}")
    print(f"  Categoria : {calculos.CATEGORIAS[oc['categoria']]}")
    print(f"  Gravidade : {oc['gravidade']} (1 a 5)")
    print(f"  Descrição : {oc['descricao']}")
    print(f"  Relator   : {oc['relator']}")
    print(f"  Status    : {oc['status']}")
    print("  Histórico :")
    for passo in oc["historico"]:
        origem = passo["de"] or "-"
        obs = f" - {passo['obs']}" if passo["obs"] else ""
        print(f"    {formatar_data(passo['data'])}  {origem} -> {passo['para']}{obs}")


def menu_trechos(dados, caminho):
    while True:
        escolha = exibir_menu("TRECHOS DE CALÇADA", [
            ("1", "Cadastrar trecho"),
            ("2", "Listar trechos"),
            ("3", "Editar trecho"),
            ("4", "Remover trecho"),
            ("0", "Voltar"),
        ])
        if escolha == "0":
            return
        if escolha == "1":
            nome = v.ler_texto("Nome do trecho (rua/avenida e referência): ", 3, 80)
            bairro = v.ler_texto("Bairro: ", 2, 40)
            extensao = v.ler_decimal("Extensão em metros: ", minimo=1, maximo=10000)
            trecho = servicos.criar_trecho(dados, nome, bairro, extensao)
            salvar(dados, caminho)
            print(f"  Trecho #{trecho['id']} cadastrado.")
        elif escolha == "2":
            titulo("TRECHOS CADASTRADOS")
            mostrar_tabela_trechos(dados)
        elif escolha == "3":
            trecho = escolher_trecho(dados)
            if trecho is None:
                continue
            print("  Deixe em branco para manter o valor atual.")
            nome = v.ler_texto(f"Nome [{trecho['nome']}]: ", 3, 80, obrigatorio=False)
            bairro = v.ler_texto(f"Bairro [{trecho['bairro']}]: ", 2, 40, obrigatorio=False)
            extensao = v.ler_decimal(f"Extensão em metros [{trecho['extensao_m']:.1f}]: ",
                                     minimo=1, maximo=10000, obrigatorio=False)
            servicos.atualizar_trecho(dados, trecho["id"], nome, bairro, extensao)
            salvar(dados, caminho)
            print("  Trecho atualizado.")
        elif escolha == "4":
            trecho = escolher_trecho(dados)
            if trecho is None:
                continue
            if v.confirmar(f"Remover o trecho '{trecho['nome']}'?"):
                try:
                    servicos.remover_trecho(dados, trecho["id"])
                    salvar(dados, caminho)
                    print("  Trecho removido.")
                except ValueError as erro:
                    print(f"  ! {erro}")


def registrar_ocorrencia_tela(dados, caminho):
    titulo("REGISTRAR OCORRÊNCIA")
    trecho = escolher_trecho(dados)
    if trecho is None:
        return
    print("\n  Tipo de barreira:")
    categoria = escolher_categoria()
    descricao = v.ler_texto("Descreva o problema: ", 5, 200)
    gravidade = v.ler_inteiro("Gravidade (1 = leve ... 5 = muito grave): ", 1, 5)
    relator = v.ler_texto("Seu nome: ", 2, 60)
    oc = servicos.registrar_ocorrencia(dados, trecho["id"], categoria, descricao, gravidade, relator)
    salvar(dados, caminho)
    print(f"  Relato #{oc['id']} registrado com status 'pendente'. "
          "Ele entra no índice depois que o administrador validar.")


def listar_ocorrencias_tela(dados):
    escolha = exibir_menu("CONSULTAR OCORRÊNCIAS", [
        ("1", "Todas"),
        ("2", "Por trecho"),
        ("3", "Por categoria"),
        ("4", "Por status"),
        ("5", "Ver detalhe de uma ocorrência"),
        ("0", "Voltar"),
    ])
    if escolha == "0":
        return
    if escolha == "5":
        numero = v.ler_inteiro("ID da ocorrência: ", minimo=1)
        oc = servicos.buscar_ocorrencia(dados, numero)
        if oc is None:
            print("  Ocorrência não encontrada.")
        else:
            mostrar_detalhe_ocorrencia(oc, dados)
        return
    trecho_id = categoria = status = None
    if escolha == "2":
        trecho = escolher_trecho(dados)
        if trecho is None:
            return
        trecho_id = trecho["id"]
    elif escolha == "3":
        categoria = escolher_categoria()
    elif escolha == "4":
        status = v.ler_opcao("Status (" + "/".join(servicos.STATUS_VALIDOS) + "): ",
                             servicos.STATUS_VALIDOS)
    lista = servicos.listar_ocorrencias(dados, trecho_id, categoria, status)
    print()
    mostrar_tabela_ocorrencias(lista, dados)


def menu_ocorrencias(dados, caminho):
    while True:
        escolha = exibir_menu("OCORRÊNCIAS (RELATOS DOS CIDADÃOS)", [
            ("1", "Registrar nova ocorrência"),
            ("2", "Consultar ocorrências"),
            ("0", "Voltar"),
        ])
        if escolha == "0":
            return
        if escolha == "1":
            registrar_ocorrencia_tela(dados, caminho)
        else:
            listar_ocorrencias_tela(dados)


def _escolher_ocorrencia_em(lista, dados, prompt):
    if not mostrar_tabela_ocorrencias(lista, dados):
        return None
    ids = {oc["id"]: oc for oc in lista}
    while True:
        numero = v.ler_inteiro(prompt, minimo=0)
        if numero == 0:
            return None
        if numero in ids:
            return ids[numero]
        print("  ID fora da lista. Escolha um dos IDs mostrados.")


def menu_admin(dados, caminho):
    while True:
        escolha = exibir_menu("ADMINISTRAÇÃO", [
            ("1", "Validar ou rejeitar relatos pendentes"),
            ("2", "Registrar resolução de ocorrência validada"),
            ("3", "Ver histórico de uma ocorrência"),
            ("0", "Voltar"),
        ])
        if escolha == "0":
            return
        if escolha == "1":
            lista = servicos.listar_ocorrencias(dados, status="pendente")
            oc = _escolher_ocorrencia_em(lista, dados, "ID do relato (0 para cancelar): ")
            if oc is None:
                continue
            mostrar_detalhe_ocorrencia(oc, dados)
            decisao = v.ler_opcao("Validar (v), rejeitar (r) ou cancelar (c)? ", ["v", "r", "c"])
            if decisao == "c":
                continue
            novo = "validada" if decisao == "v" else "rejeitada"
            obs = v.ler_texto("Observação (opcional): ", 1, 150, obrigatorio=False)
            servicos.alterar_status(dados, oc["id"], novo, obs)
            salvar(dados, caminho)
            print(f"  Relato #{oc['id']} marcado como '{novo}'.")
        elif escolha == "2":
            lista = servicos.listar_ocorrencias(dados, status="validada")
            oc = _escolher_ocorrencia_em(lista, dados, "ID da ocorrência resolvida (0 para cancelar): ")
            if oc is None:
                continue
            obs = v.ler_texto("Como foi resolvida (opcional): ", 1, 150, obrigatorio=False)
            servicos.alterar_status(dados, oc["id"], "resolvida", obs)
            salvar(dados, caminho)
            print(f"  Ocorrência #{oc['id']} marcada como 'resolvida'. Ela sai do cálculo do índice.")
        elif escolha == "3":
            numero = v.ler_inteiro("ID da ocorrência: ", minimo=1)
            oc = servicos.buscar_ocorrencia(dados, numero)
            if oc is None:
                print("  Ocorrência não encontrada.")
            else:
                mostrar_detalhe_ocorrencia(oc, dados)


def menu_leituras(dados, caminho):
    while True:
        escolha = exibir_menu("ILUMINAÇÃO - LEITURAS DO LDR (ESP32)", [
            ("1", "Registrar leitura"),
            ("2", "Histórico de leituras de um trecho"),
            ("0", "Voltar"),
        ])
        if escolha == "0":
            return
        trecho = escolher_trecho(dados)
        if trecho is None:
            continue
        if escolha == "1":
            print("  O LDR mede apenas a iluminação. Barreiras físicas vêm dos relatos.")
            print(f"  Escala do ADC: 0 a {calculos.ADC_MAX}. Use -1 para simular leitura inválida.")
            valor = v.ler_inteiro("Valor lido: ", minimo=-1, maximo=65535)
            fonte = "esp32" if v.confirmar("A leitura veio do ESP32/Wokwi?") else "manual"
            antes = calculos.indice_barreira(calculos.componentes_trecho(dados, trecho["id"]))
            leitura = servicos.registrar_leitura(dados, trecho["id"], valor, fonte)
            salvar(dados, caminho)
            depois = calculos.indice_barreira(calculos.componentes_trecho(dados, trecho["id"]))
            pct = f"{leitura['percentual']:.1f}%" if leitura["percentual"] is not None else "-"
            print(f"\n  Luminosidade: {pct}  ->  Estado: {leitura['estado']}")
            if leitura["estado"] == "Falha":
                print("  Leitura inválida: não entra no índice. Verifique o sensor.")
            else:
                print(f"  Decisão: nota de iluminação do trecho = {calculos.NOTA_ESTADO_LDR[leitura['estado']]}")
                print(f"  Índice b(x) do trecho: {antes:.2f} -> {depois:.2f}")
        else:
            leituras = servicos.leituras_do_trecho(dados, trecho["id"])
            if not leituras:
                print("  Nenhuma leitura registrada para este trecho.")
                continue
            print(f"\n  {'ID':>3}   {'Data':<16} {'ADC':>6} {'Lum.':>7}  {'Estado':<8} Fonte")
            for lt in leituras:
                pct = f"{lt['percentual']:.1f}%" if lt["percentual"] is not None else "-"
                print(f"  {lt['id']:>3} {marca(lt)} {formatar_data(lt['data']):<16} {lt['valor_adc']:>6} "
                      f"{pct:>7}  {lt['estado']:<8} {lt['fonte']}")
            print("  (* = dado simulado)")


def mostrar_modelo():
    titulo("COMO O ÍNDICE É CALCULADO")
    print("  b(x) = (s + o + r + l) / 20")
    print("    s = superfície | o = obstáculos | r = rampas | l = iluminação")
    print("    Cada componente vai de 0 a 5; logo b fica entre 0 e 1.")
    print("  Exposição acumulada: B(L) = integral de 0 a L de b(x) dx")
    print("    Em cada trecho b é constante, então B = soma de b * comprimento.")
    print("\n  Regras:")
    print("   - Só ocorrências VALIDADAS entram. Resolvidas saem do cálculo.")
    print("   - Cada categoria usa a maior gravidade entre as ocorrências validadas.")
    print("   - Iluminação = maior entre a gravidade dos relatos e a nota do LDR")
    print("     (Normal = 0, Atenção = 3, Crítico = 5; leitura com Falha é ignorada).")
    print(f"   - Faixas: Baixa < {calculos.LIMITE_MODERADA}, Moderada < {calculos.LIMITE_ALTA}, Alta >= {calculos.LIMITE_ALTA}.")
    print("\n  Limitações: pesos iguais, sem validação estatística. Não é um padrão")
    print("  oficial de acessibilidade. Serve para comparar trechos neste projeto.")


def detalhe_indice(dados):
    trecho = escolher_trecho(dados)
    if trecho is None:
        return
    comp = calculos.componentes_trecho(dados, trecho["id"])
    b = calculos.indice_barreira(comp)
    titulo(f"ÍNDICE DO TRECHO: {trecho['nome']}")
    print(f"  Superfície (s)  : {comp['superficie']}")
    print(f"  Obstáculos (o)  : {comp['obstaculo']}")
    print(f"  Rampas (r)      : {comp['rampa']}")
    print(f"  Iluminação (l)  : {comp['iluminacao']}")
    print(f"  b(x) = {sum(comp.values())}/{calculos.DIVISOR_INDICE} = {b:.2f}  "
          f"-> barreira {calculos.classificar_indice(b)}")
    print(f"  Exposição no trecho: {b * trecho['extensao_m']:.1f} (índice x metro) "
          f"em {trecho['extensao_m']:.0f} m")


def ranking_indice(dados):
    titulo("RANKING DE TRECHOS POR BARREIRA")
    if not dados["trechos"]:
        print("  Nenhum trecho cadastrado.")
        return
    linhas = []
    for t in dados["trechos"]:
        b = calculos.indice_barreira(calculos.componentes_trecho(dados, t["id"]))
        linhas.append((b, t))
    linhas.sort(key=lambda item: item[0], reverse=True)
    print(f"  {'#':>2}  {'Trecho':<32} {'b(x)':>6}  Faixa")
    for posicao, (b, t) in enumerate(linhas, start=1):
        print(f"  {posicao:>2} {marca(t)}{cortar(t['nome'], 32):<32} {b:>6.2f}  {calculos.classificar_indice(b)}")


def trajeto_indice(dados):
    titulo("EXPOSIÇÃO ACUMULADA EM UM TRAJETO")
    if not mostrar_tabela_trechos(dados):
        return
    print("  Informe os trechos na ordem do trajeto. Enter vazio termina.")
    escolhidos = []
    while True:
        numero = v.ler_inteiro(f"  Trecho {len(escolhidos) + 1} (Enter para terminar): ",
                               minimo=1, obrigatorio=False)
        if numero is None:
            break
        trecho = servicos.buscar_trecho(dados, numero)
        if trecho is None:
            print("  Trecho não encontrado.")
            continue
        escolhidos.append(trecho)
    if not escolhidos:
        print("  Nenhum trecho informado.")
        return
    resultado = calculos.exposicao_trajeto(dados, escolhidos)
    print(f"\n  {'Trecho':<32} {'Ext.(m)':>8} {'b(x)':>6} {'b*ext':>8}")
    for item in resultado["detalhes"]:
        t = item["trecho"]
        print(f"  {cortar(t['nome'], 32):<32} {t['extensao_m']:>8.1f} {item['b']:>6.2f} {item['parcial']:>8.1f}")
    print(f"\n  Comprimento total L : {resultado['comprimento']:.1f} m")
    print(f"  Exposição B(L)      : {resultado['exposicao']:.1f} (índice x metro)")
    print(f"  Barreira média B/L  : {resultado['media']:.2f} "
          f"-> {calculos.classificar_indice(resultado['media'])}")


def menu_indice(dados):
    while True:
        escolha = exibir_menu("ÍNDICE DE BARREIRAS", [
            ("1", "Índice de um trecho"),
            ("2", "Ranking de trechos"),
            ("3", "Exposição acumulada de um trajeto"),
            ("4", "Como o índice é calculado"),
            ("0", "Voltar"),
        ])
        if escolha == "0":
            return
        if escolha == "1":
            detalhe_indice(dados)
        elif escolha == "2":
            ranking_indice(dados)
        elif escolha == "3":
            trajeto_indice(dados)
        else:
            mostrar_modelo()


def _contar_por(lista, chave_func):
    contagem = {}
    for item in lista:
        chave = chave_func(item)
        contagem[chave] = contagem.get(chave, 0) + 1
    return contagem


def relatorio_geral(dados):
    titulo("PAINEL GERAL")
    ocs = dados["ocorrencias"]
    total = len(ocs)
    validadas_ou_mais = [o for o in ocs if o["status"] in ("validada", "resolvida")]
    resolvidas = [o for o in ocs if o["status"] == "resolvida"]
    print(f"  Trechos cadastrados   : {len(dados['trechos'])}")
    print(f"  Ocorrências           : {total}")
    for status in servicos.STATUS_VALIDOS:
        print(f"    - {status:<10}: {sum(1 for o in ocs if o['status'] == status)}")
    if validadas_ou_mais:
        taxa = len(resolvidas) / len(validadas_ou_mais) * 100
        print(f"  Taxa de resolução     : {taxa:.0f}% das ocorrências validadas")
    else:
        print("  Taxa de resolução     : -")
    print(f"  Leituras do LDR       : {len(dados['leituras'])}")
    falhas = sum(1 for lt in dados["leituras"] if lt["estado"] == "Falha")
    print(f"    - com falha         : {falhas}")


def relatorio_por_trecho(dados):
    titulo("OCORRÊNCIAS POR TRECHO")
    if not dados["trechos"]:
        print("  Nenhum trecho cadastrado.")
        return
    contagem = _contar_por(dados["ocorrencias"], lambda o: o["trecho_id"])
    print(f"  {'Trecho':<34} {'Total':>6} {'Abertas':>8}")
    for t in dados["trechos"]:
        total = contagem.get(t["id"], 0)
        abertas = sum(1 for o in dados["ocorrencias"]
                      if o["trecho_id"] == t["id"] and o["status"] in ("pendente", "validada"))
        print(f"  {marca(t)}{cortar(t['nome'], 33):<33} {total:>6} {abertas:>8}")


def relatorio_por_categoria(dados):
    titulo("OCORRÊNCIAS POR CATEGORIA")
    contagem = _contar_por(dados["ocorrencias"], lambda o: o["categoria"])
    for chave, nome in calculos.CATEGORIAS.items():
        print(f"  {nome:<28} {contagem.get(chave, 0):>4}")


def relatorio_por_status(dados):
    titulo("OCORRÊNCIAS POR STATUS")
    contagem = _contar_por(dados["ocorrencias"], lambda o: o["status"])
    for status in servicos.STATUS_VALIDOS:
        print(f"  {status:<12} {contagem.get(status, 0):>4}")


def relatorio_tempos(dados):
    titulo("TEMPOS MÉDIOS DE ATENDIMENTO")
    media_val, n_val = calculos.media_horas_ate_status(dados, "validada")
    media_res, n_res = calculos.media_horas_ate_status(dados, "resolvida")
    print(f"  Até a validação : {formatar_horas(media_val)}  ({n_val} ocorrência(s))")
    print(f"  Até a resolução : {formatar_horas(media_res)}  ({n_res} ocorrência(s))")
    print("  Contado a partir do registro do relato.")


def menu_relatorios(dados):
    while True:
        escolha = exibir_menu("RELATÓRIOS", [
            ("1", "Painel geral"),
            ("2", "Ocorrências por trecho"),
            ("3", "Ocorrências por categoria"),
            ("4", "Ocorrências por status"),
            ("5", "Tempos médios de validação e resolução"),
            ("0", "Voltar"),
        ])
        if escolha == "0":
            return
        {"1": relatorio_geral, "2": relatorio_por_trecho, "3": relatorio_por_categoria,
         "4": relatorio_por_status, "5": relatorio_tempos}[escolha](dados)


def menu_exemplos(dados, caminho):
    escolha = exibir_menu("DADOS DE EXEMPLO (SIMULADOS)", [
        ("1", "Carregar dados de exemplo"),
        ("2", "Remover dados de exemplo"),
        ("0", "Voltar"),
    ])
    if escolha == "1":
        if any(t.get("simulado") for t in dados["trechos"]):
            print("  Os dados de exemplo já foram carregados.")
        elif v.confirmar("Adicionar trechos, ocorrências e leituras simulados?"):
            criados = exemplos.carregar_exemplos(dados)
            salvar(dados, caminho)
            print(f"  Criados: {criados['trechos']} trechos, {criados['ocorrencias']} ocorrências, "
                  f"{criados['leituras']} leituras (todos marcados como simulados).")
    elif escolha == "2":
        if v.confirmar("Remover todos os registros simulados?"):
            removidos = servicos.remover_simulados(dados)
            salvar(dados, caminho)
            print(f"  Removidos: {removidos['trechos']} trechos, {removidos['ocorrencias']} ocorrências, "
                  f"{removidos['leituras']} leituras.")


def tela_sobre():
    titulo("SOBRE O PROJETO")
    print(f"  {integrantes.PROJETO} - {integrantes.DESCRICAO}")
    print(f"  {integrantes.EVENTO}")
    print(f"  Disciplina: {integrantes.DISCIPLINA}")
    print("\n  Integrantes:")
    for linha in integrantes.texto_integrantes():
        print(f"   - {linha}")
    print("\n  Observações honestas sobre o protótipo:")
    print("   - O LDR monitora apenas a iluminação. As barreiras físicas vêm dos relatos.")
    print("   - O índice de barreiras é experimental, não é padrão oficial.")
    print("   - Dados marcados com * são simulados.")


def menu_principal(dados, caminho):
    while True:
        escolha = exibir_menu("CALÇADA VIVA - MENU PRINCIPAL", [
            ("1", "Trechos de calçada"),
            ("2", "Ocorrências (relatos)"),
            ("3", "Administração (validar e resolver)"),
            ("4", "Iluminação - leituras do LDR"),
            ("5", "Índice de barreiras"),
            ("6", "Relatórios"),
            ("7", "Dados de exemplo (simulados)"),
            ("8", "Sobre o projeto / Integrantes"),
            ("0", "Sair"),
        ])
        if escolha == "0":
            print("\n  Dados salvos em", caminho)
            print("  Até logo!")
            return
        if escolha == "1":
            menu_trechos(dados, caminho)
        elif escolha == "2":
            menu_ocorrencias(dados, caminho)
        elif escolha == "3":
            menu_admin(dados, caminho)
        elif escolha == "4":
            menu_leituras(dados, caminho)
        elif escolha == "5":
            menu_indice(dados)
        elif escolha == "6":
            menu_relatorios(dados)
        elif escolha == "7":
            menu_exemplos(dados, caminho)
        elif escolha == "8":
            tela_sobre()
            pausar()
