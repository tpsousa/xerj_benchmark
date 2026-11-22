#!/usr/bin/env python3
"""
Gera suite_pt/: a fase de testes em português do Brasil.

- Reaproveita os documentos e perguntas em português da suíte v1 (suite/), com o mesmo id,
  para que as rodadas continuem comparáveis (F09 foi trocada: a pergunta era ambígua).
- Cria 8 documentos novos (nota fiscal, boleto, holerite, extrato, edital, ata, aluguel, log).
- Todos os valores esperados que dependem de conta são CALCULADOS aqui em código,
  não digitados à mão.

Uso:  python3 tools/build_suite_pt.py
"""
import csv
import shutil
from datetime import date, datetime
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "suite_pt"
cases = []


def brl(v):
    s = f"{D(v):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def money(v):
    return f"R$ {brl(v)}"


def dd(d):
    return d.strftime("%d/%m/%Y")


def plain(v):
    return f"{D(v).quantize(D('0.01'), rounding=ROUND_HALF_UP):.2f}"


def add(cid, doc, question, kind, expected, status="ANSWER", category="extract", ref=""):
    cases.append([cid, doc, question, kind, expected, status, category, "pt", ref])


def write(name, text):
    (OUT / "docs" / name).write_text(text.strip("\n") + "\n", encoding="utf-8")


# ------------------------------------------------------------------ preparar pasta
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "docs").mkdir(parents=True)

# ------------------------------------------------------------------ v1 (pt) reaproveitado
with open(ROOT / "suite" / "cases.csv", encoding="utf-8", newline="") as f:
    v1 = [r for r in csv.DictReader(f) if r["lang"] == "pt"]
for r in v1:
    shutil.copy(ROOT / "suite" / "docs" / r["doc"], OUT / "docs" / r["doc"])
    if r["id"] == "F09":   # ambígua na v1: trocada por uma pergunta objetiva
        r.update(question="Qual é a forma de pagamento?", kind="text", expected="~boleto",
                 expected_status="ANSWER", category="extract")
    cases.append([r["id"], r["doc"], r["question"], r["kind"], r["expected"], r["expected_status"],
                  r["category"], r["lang"], r["ref_date"]])

# ------------------------------------------------------------------ A) nota fiscal
items = [("001", "Arroz tipo 1 5kg", "PCT", 40, D("21.90")), ("002", "Feijão carioca 1kg", "PCT", 60, D("8.50")),
         ("003", "Óleo de soja 900ml", "UN", 120, D("6.25")), ("004", "Açúcar cristal 1kg", "PCT", 80, D("4.80"))]
tot = {c: q * u for c, _, _, q, u in items}
produtos = sum(tot.values())
frete, desconto = D("150.00"), D("70.00")
total_nota = produtos + frete - desconto
icms = (produtos * D("0.12")).quantize(D("0.01"), rounding=ROUND_HALF_UP)
chave = "21" + "2611" + "45678901000123" + "55" + "001" + "000045318" + "1" + "12345678" + "9"
assert len(chave) == 44
chave_fmt = " ".join(chave[i:i + 4] for i in range(0, 44, 4))
linhas = "\n".join(f"{c}  {d:<22}{un:<4}{q:>4}  {brl(u):>8}  {brl(q * u):>9}" for c, d, un, q, u in items)
write("nota_fiscal_pt.txt", f"""
DANFE - DOCUMENTO AUXILIAR DA NOTA FISCAL ELETRÔNICA
NF-e Nº 000.045.318   Série 1
Chave de acesso: {chave_fmt}
Natureza da operação: Venda de mercadoria
Data de emissão: 12/11/2026   Hora: 14:32:10

EMITENTE
Razão social: Distribuidora Horizonte Ltda.
CNPJ: 45.678.901/0001-23   IE: 123456789
Cidade/UF: Imperatriz/MA

DESTINATÁRIO
Razão social: Mercadinho Bom Preço Eireli
CNPJ: 98.765.432/0001-10
Cidade/UF: São Luís/MA

ITENS
Cód  Descrição             Un   Qtd  Vl. Unit.  Vl. Total
{linhas}

Valor dos produtos: {money(produtos)}
Frete: {money(frete)}
Desconto: {money(desconto)}
Valor total da nota: {money(total_nota)}
ICMS (12%): {money(icms)}
Transportadora: Rápido Norte Transportes
Peso bruto: 410,5 kg
Informações adicionais: Entrega agendada para 16/11/2026. Mercadoria sujeita a conferência no ato do recebimento.
""")
N = "nota_fiscal_pt.txt"
add("NF01", N, "Qual é o número da NF-e?", "text", "000.045.318##45318##45.318##000045318")
add("NF02", N, "Qual é a data de emissão?", "date", "2026-11-12", category="date_format")
add("NF03", N, "Qual é o CNPJ do destinatário?", "text", "98.765.432/0001-10")
add("NF04", N, "Qual é o valor total da nota?", "money", plain(total_nota), category="ambiguity")
add("NF05", N, "Qual é o valor total dos produtos?", "money", plain(produtos))
add("NF06", N, "Quantas unidades de óleo de soja foram vendidas?", "number", "120", category="table")
add("NF07", N, "Qual item tem o maior valor total?", "text", "~Arroz", category="compute")
add("NF08", N, "Quanto custam juntos o feijão e o açúcar?", "money", plain(tot["002"] + tot["004"]), category="compute")
add("NF09", N, "Qual é a transportadora?", "text", "~Rápido Norte")
add("NF10", N, "Qual é a data de entrega agendada?", "date", "2026-11-16", category="date_format")
add("NF11", N, "Qual é o percentual de ICMS?", "pct", "12", category="percent")
add("NF12", N, "Quantos itens diferentes há na nota?", "number", str(len(items)), category="count")
add("NF13", N, "Qual é o valor do ICMS?", "money", plain(icms))
add("NF14", N, "Qual é o número do pedido de compra?", "text", "", "ABSENT", "absent")
add("NF15", N, "Qual é o CPF do motorista?", "text", "", "ABSENT", "absent")

# ------------------------------------------------------------------ B) boleto
valor_doc, desc_b = D("189.90"), D("10.00")
cobrado = valor_doc - desc_b
write("boleto_pt.txt", f"""
BOLETO DE COBRANÇA
Banco: Banco Meridional S.A. (código 237)
Beneficiário: Academia Corpo & Mente Ltda.
CNPJ do beneficiário: 22.333.444/0001-55
Pagador: Cliente Fictício da Silva
Nosso número: 123456789-0
Número do documento: MENS-2026-11
Data do documento: 01/11/2026
Vencimento: 10/11/2026
Valor do documento: {money(valor_doc)}
Desconto para pagamento até o vencimento: {money(desc_b)}
Valor cobrado até o vencimento: {money(cobrado)}
Multa após o vencimento: 2%
Juros de mora: 0,033% ao dia
Linha digitável: 23790.12345 60000.123456 78901.234567 8 98760000017990
Instruções: Pagável em qualquer banco até o vencimento. Não receber após 30 dias do vencimento.
""")
B = "boleto_pt.txt"
add("BO01", B, "Qual é a data de vencimento?", "date", "2026-11-10", category="date_format")
add("BO02", B, "Qual é o valor do documento?", "money", plain(valor_doc), category="ambiguity")
add("BO03", B, "Qual é o valor cobrado até o vencimento?", "money", plain(cobrado), category="ambiguity")
add("BO04", B, "Quem é o beneficiário?", "text", "~Academia Corpo")
add("BO05", B, "Qual é o CNPJ do beneficiário?", "text", "22.333.444/0001-55")
add("BO06", B, "Qual é o percentual da multa após o vencimento?", "pct", "2", category="percent")
add("BO07", B, "Qual é a taxa de juros de mora ao dia?", "pct", "0.033", category="percent")
add("BO08", B, "Até quantos dias após o vencimento o boleto pode ser recebido?", "number", "30")
add("BO09", B, "Qual é o nosso número?", "text", "123456789-0")
add("BO10", B, "Qual é a diferença entre o valor do documento e o valor cobrado até o vencimento?", "money",
    plain(valor_doc - cobrado), category="compute")
add("BO11", B, "Qual é a data do documento?", "date", "2026-11-01", category="date_format")
add("BO12", B, "Qual é o número do documento?", "text", "MENS-2026-11")
add("BO13", B, "Qual é o endereço do beneficiário?", "text", "", "ABSENT", "absent")
add("BO14", B, "Qual é o CPF do pagador?", "text", "", "ABSENT", "absent")

# ------------------------------------------------------------------ C) holerite
sal, he = D("6800.00"), D("425.00")
inss, irrf, vt, plano = D("828.38"), D("512.40"), (D("6800.00") * D("0.06")), D("180.00")
proventos = sal + he
descontos = inss + irrf + vt + plano
liquido = proventos - descontos
fgts = (proventos * D("0.08")).quantize(D("0.01"))
write("holerite_pt.txt", f"""
RECIBO DE PAGAMENTO DE SALÁRIO
Empresa: Tecnosul Soluções Ltda.   CNPJ: 11.222.333/0001-44
Funcionário: Colaborador Fictício   Matrícula: 004512
Cargo: Analista de Sistemas   Admissão: 03/02/2023
Competência: Outubro/2026

Código  Descrição              Referência  Proventos   Descontos
001     Salário base           30 dias     {brl(sal):>9}
015     Horas extras 50%       10 h        {brl(he):>9}
101     INSS                   -                       {brl(inss):>9}
102     IRRF                   -                       {brl(irrf):>9}
110     Vale-transporte (6%)   6%                      {brl(vt):>9}
120     Plano de saúde         -                       {brl(plano):>9}

Total de proventos: {money(proventos)}
Total de descontos: {money(descontos)}
Líquido a receber: {money(liquido)}
FGTS do mês (8%): {money(fgts)}
""")
H = "holerite_pt.txt"
add("HO01", H, "Qual é a competência deste recibo?", "text", "~Outubro/2026")
add("HO02", H, "Qual é o salário base?", "money", plain(sal))
add("HO03", H, "Qual é o total de proventos?", "money", plain(proventos))
add("HO04", H, "Qual é o total de descontos?", "money", plain(descontos))
add("HO05", H, "Qual é o valor líquido a receber?", "money", plain(liquido))
add("HO06", H, "Quantas horas extras foram pagas?", "number", "10", category="table")
add("HO07", H, "Qual é a data de admissão?", "date", "2023-02-03", category="date_format")
add("HO08", H, "Qual foi o maior desconto?", "text", "~INSS", category="compute")
add("HO09", H, "Quanto foi descontado de vale-transporte?", "money", plain(vt), category="table")
add("HO10", H, "Qual é o valor do FGTS do mês?", "money", plain(fgts))
add("HO11", H, "Qual é a matrícula do funcionário?", "text", "004512")
add("HO12", H, "Qual é o cargo do funcionário?", "text", "~Analista de Sistemas")
add("HO13", H, "Qual é a diferença entre o total de proventos e o valor líquido?", "money",
    plain(proventos - liquido), category="compute")
add("HO14", H, "Qual é o CPF do funcionário?", "text", "", "ABSENT", "absent")
add("HO15", H, "Quantos dependentes o funcionário tem?", "number", "", "ABSENT", "absent")

# ------------------------------------------------------------------ D) extrato
mov = [(date(2026, 10, 3), "PIX recebido - Cliente A", D("1200.00")),
       (date(2026, 10, 5), "Compra débito - Supermercado", D("-320.45")),
       (date(2026, 10, 8), "Pagamento boleto - Energia", D("-210.30")),
       (date(2026, 10, 12), "Transferência recebida", D("800.00")),
       (date(2026, 10, 15), "Compra débito - Farmácia", D("-89.90")),
       (date(2026, 10, 20), "Pagamento boleto - Internet", D("-119.90")),
       (date(2026, 10, 25), "PIX enviado - Aluguel", D("-1500.00")),
       (date(2026, 10, 28), "Tarifa mensal", D("-29.90"))]
saldo = D("2350.00")
saldo0 = saldo
lin = [f"{'01/10/2026':<12}{'Saldo anterior':<32}{'':>11}  {brl(saldo):>10}"]
saldos = {}
for d, desc, v in mov:
    saldo += v
    saldos[d] = saldo
    lin.append(f"{dd(d):<12}{desc:<32}{brl(v):>11}  {brl(saldo):>10}")
lin.append(f"{'31/10/2026':<12}{'Saldo final':<32}{'':>11}  {brl(saldo):>10}")
entradas = sum(v for _, _, v in mov if v > 0)
saidas = -sum(v for _, _, v in mov if v < 0)
n_deb = len([1 for _, _, v in mov if v < 0])
assert saldo0 + entradas - saidas == saldo
write("extrato_pt.txt", f"""
EXTRATO DE CONTA CORRENTE
Banco Meridional - Agência 1234 - Conta 56789-0
Período: 01/10/2026 a 31/10/2026

Data        Descrição                       Valor (R$)  Saldo (R$)
""" + "\n".join(lin))
X = "extrato_pt.txt"
add("EX01", X, "Qual foi o saldo final do período?", "money", plain(saldo))
add("EX02", X, "Qual era o saldo anterior?", "money", plain(saldo0))
add("EX03", X, "Quanto foi pago de aluguel?", "money", "1500.00")
add("EX04", X, "Qual é o total de entradas (créditos) no período?", "money", plain(entradas), category="compute")
add("EX05", X, "Qual é o total de saídas (débitos) no período?", "money", plain(saidas), category="compute")
add("EX06", X, "Quantas transações de débito há no período?", "number", str(n_deb), category="count")
add("EX07", X, "Qual foi o maior valor de saída?", "money", "1500.00", category="compute")
add("EX08", X, "Em que data foi recebida a transferência?", "date", "2026-10-12", category="date_format")
add("EX09", X, "Qual é o valor da tarifa mensal?", "money", "29.90##-29.90", category="negative_value")
add("EX10", X, "Qual era o saldo em 15/10/2026?", "money", plain(saldos[date(2026, 10, 15)]), category="table")
add("EX11", X, "Quanto foi gasto no supermercado?", "money", "320.45##-320.45", category="negative_value")
add("EX12", X, "Qual é o limite do cheque especial?", "money", "", "ABSENT", "absent")
add("EX13", X, "Qual é o nome do titular da conta?", "text", "", "ABSENT", "absent")

# ------------------------------------------------------------------ E) edital
cad_v, mesa_v = D("112500.00"), D("75000.00")
write("edital_pt.txt", f"""
PREFEITURA MUNICIPAL DE VILA NOVA
PREGÃO ELETRÔNICO Nº 014/2026
Processo administrativo nº 2026/0873

1. OBJETO
Contratação de empresa para fornecimento de 500 (quinhentas) cadeiras escolares e 250 (duzentas e cinquenta) mesas escolares.

2. VALOR ESTIMADO
O valor total estimado da contratação é de {money(cad_v + mesa_v)}, sendo {money(cad_v)} para as cadeiras e {money(mesa_v)} para as mesas.

3. DATAS
Recebimento das propostas: até 02 de dezembro de 2026, às 09h00.
Abertura da sessão pública: 02 de dezembro de 2026, às 10h00.
Impugnações ao edital: até 3 (três) dias úteis antes da abertura.

4. HABILITAÇÃO
As licitantes deverão apresentar certidão negativa de débitos federais, estaduais e municipais, e atestado de capacidade técnica.

5. PRAZO DE ENTREGA
A entrega deverá ser feita em até 30 (trinta) dias corridos após a assinatura do contrato.

6. PAGAMENTO
O pagamento será efetuado em até 15 dias após o recebimento definitivo dos itens.
""")
E = "edital_pt.txt"
add("ED01", E, "Qual é o número do pregão?", "text", "~014/2026")
add("ED02", E, "Qual é o valor total estimado da contratação?", "money", plain(cad_v + mesa_v))
add("ED03", E, "Quantas cadeiras serão contratadas?", "number", "500", category="word_number")
add("ED04", E, "Quantas mesas serão contratadas?", "number", "250", category="word_number")
add("ED05", E, "Qual é o valor unitário estimado de cada cadeira?", "money", plain(cad_v / 500), category="compute")
add("ED06", E, "Em que data será a abertura da sessão pública?", "date", "2026-12-02", category="month_name")
add("ED07", E, "A que horas será a abertura da sessão pública?", "time", "10:00##10h00##10:00:00", category="time")
add("ED08", E, "Qual é o prazo de entrega, em dias?", "duration", "~30")
add("ED09", E, "Qual é o prazo para o pagamento, em dias?", "duration", "~15")
add("ED10", E, "Até quantos dias úteis antes da abertura podem ser feitas impugnações?", "number", "3", category="word_number")
add("ED11", E, "Quanto o valor estimado das cadeiras supera o das mesas?", "money", plain(cad_v - mesa_v), category="compute")
add("ED12", E, "Qual é o órgão responsável pelo pregão?", "text", "~Prefeitura Municipal de Vila Nova")
add("ED13", E, "Qual é a garantia exigida dos itens?", "text", "", "ABSENT", "absent")
add("ED14", E, "Quem é o pregoeiro responsável?", "text", "", "ABSENT", "absent")

# ------------------------------------------------------------------ F) ata
ini, fim = datetime(2026, 11, 18, 9, 15), datetime(2026, 11, 18, 11, 40)
minutos = int((fim - ini).total_seconds() // 60)
d1, d2 = date(2026, 12, 16), date(2027, 1, 20)
write("ata_reuniao_pt.txt", f"""
ATA DA REUNIÃO ORDINÁRIA DO CONSELHO - 18/11/2026
Local: sala de reuniões 2. Início: 09h15. Término: 11h40.
Presentes: Ana Lima (presidente), Bruno Costa (secretário), Carla Dias, Diego Souza e Elisa Ramos. Ausente justificado: Fábio Alves.

Pauta e deliberações:
1. Orçamento 2027 - aprovado por 4 votos a favor e 1 abstenção. O valor aprovado é de R$ 950.000,00.
2. Contratação de auditoria externa - rejeitada por 3 votos contra 2.
3. Calendário de reuniões - as próximas reuniões serão realizadas em 16 de dezembro de 2026 e em 20 de janeiro de 2027.

Encaminhamentos:
- Bruno Costa enviará a minuta do orçamento até 25 de novembro.
- Carla Dias apresentará o relatório trimestral na próxima reunião.
- Diego Souza revisará o regimento interno em até 30 dias.
""")
A = "ata_reuniao_pt.txt"
R = "2026-11-18"
add("AT01", A, "Quem presidiu a reunião?", "text", "~Ana Lima", ref=R)
add("AT02", A, "Quantos minutos durou a reunião?", "number", str(minutos), category="compute", ref=R)
add("AT03", A, "Quantas pessoas estiveram presentes?", "number", "5", category="count", ref=R)
add("AT04", A, "Quem esteve ausente?", "text", "~Fábio Alves", ref=R)
add("AT05", A, "Qual foi o valor aprovado para o orçamento de 2027?", "money", "950000.00", ref=R)
add("AT06", A, "A contratação de auditoria externa foi aprovada?", "yesno", "no", category="yesno", ref=R)
add("AT07", A, "Quantos votos a favor teve o orçamento?", "number", "4", ref=R)
add("AT08", A, "Qual é a data da próxima reunião?", "date", d1.isoformat(), category="month_name", ref=R)
add("AT09", A, "Até que data Bruno Costa deve enviar a minuta do orçamento?", "date", "2026-11-25",
    category="ref_date", ref=R)
add("AT10", A, "Quem revisará o regimento interno?", "text", "~Diego Souza", ref=R)
add("AT11", A, "Quantos dias separam a próxima reunião da reunião seguinte?", "number", str((d2 - d1).days),
    category="compute", ref=R)
add("AT12", A, "Qual é o valor aprovado para a auditoria externa?", "money", "", "ABSENT", "absent", ref=R)
add("AT13", A, "Quem foi o relator do orçamento?", "text", "", "ABSENT", "absent", ref=R)

# ------------------------------------------------------------------ G) aluguel
alug, cond = D("2400.00"), D("650.00")
write("aluguel_pt.txt", f"""
CONTRATO DE LOCAÇÃO RESIDENCIAL

LOCADOR: Marcos Antônio Pereira. LOCATÁRIA: Juliana Ferreira Costa.
IMÓVEL: apartamento 302, Rua das Palmeiras, nº 150, bairro Centro, São Luís - MA.

Cláusula 1ª - O prazo da locação é de 30 meses, com início em 01/03/2026 e término em 31/08/2028.
Cláusula 2ª - O aluguel mensal é de {money(alug)}, com vencimento todo dia 5 de cada mês.
Cláusula 3ª - O aluguel será reajustado anualmente pela variação do IGP-M ou, na sua extinção, pelo IPCA.
Cláusula 4ª - O locatário pagará, além do aluguel, o condomínio (atualmente {money(cond)}) e o IPTU.
Cláusula 5ª - Em caso de atraso, incidirá multa de 10% sobre o valor do aluguel e juros de 1% ao mês.
Cláusula 6ª - Como garantia, o locatário depositou caução equivalente a 3 (três) aluguéis.
Cláusula 7ª - Se o locatário devolver o imóvel antes do término do prazo, pagará multa de 3 (três) aluguéis, proporcional ao tempo restante.
Cláusula 8ª - É vedada a sublocação, total ou parcial, sem autorização por escrito do locador.
""")
L = "aluguel_pt.txt"
add("AL01", L, "Qual é o valor do aluguel mensal?", "money", plain(alug))
add("AL02", L, "Em que dia do mês vence o aluguel?", "number", "5", category="word_number")
add("AL03", L, "Qual é o prazo da locação?", "duration", "~30")
add("AL04", L, "Qual é a data de término da locação?", "date", "2028-08-31", category="date_format")
add("AL05", L, "Qual é o valor da multa por atraso, em reais?", "money", plain(alug * D("0.10")), category="compute")
add("AL06", L, "Qual é o valor da caução depositada?", "money", plain(alug * 3), category="word_number")
add("AL07", L, "Qual é o valor mensal somando aluguel e condomínio?", "money", plain(alug + cond), category="compute")
add("AL08", L, "Qual índice reajusta o aluguel?", "text", "~IGP-M")
add("AL09", L, "É permitida a sublocação sem autorização por escrito?", "yesno", "no", category="yesno")
add("AL10", L, "Quem é a locatária?", "text", "~Juliana")
add("AL11", L, "Em que cidade fica o imóvel?", "text", "~São Luís")
add("AL12", L, "Qual é a data de nascimento do locador?", "date", "", "ABSENT", "absent")
add("AL13", L, "Qual é a área do imóvel em metros quadrados?", "number", "", "ABSENT", "absent")

# ------------------------------------------------------------------ H) log em português
write("log_pt.txt", """
[18/11/2026 10:02:11] INFO  Servidor iniciado na porta 9090
[18/11/2026 10:05:43] INFO  Requisição GET /clientes concluída em 120 ms
[18/11/2026 10:07:19] AVISO Uso de memória em 82%
[18/11/2026 10:09:55] ERRO  Falha ao conectar ao banco: timeout após 30 s
[18/11/2026 10:10:20] INFO  Reconexão ao banco bem-sucedida
[18/11/2026 10:14:02] INFO  Requisição POST /pedidos concluída em 480 ms
[18/11/2026 10:21:37] ERRO  Requisição POST /pagamentos falhou com status 500
[18/11/2026 10:22:05] AVISO Uso de memória em 91%
[18/11/2026 10:30:00] INFO  Requisição GET /produtos concluída em 95 ms
Resumo: 2 erros e 2 avisos registrados entre 10:00 e 10:30.
""")
G = "log_pt.txt"
add("LG01", G, "Em qual porta o servidor foi iniciado?", "number", "9090")
add("LG02", G, "Quantas linhas de ERRO há no log?", "number", "2", category="count")
add("LG03", G, "Qual foi o maior uso de memória registrado?", "pct", "91", category="percent")
add("LG04", G, "Quanto tempo levou a requisição POST /pedidos, em milissegundos?", "number", "480", category="units")
add("LG05", G, "Após quantos segundos ocorreu o timeout na conexão com o banco?", "number", "30", category="units")
add("LG06", G, "Qual é o horário do primeiro ERRO?", "time", "10:09:55", category="time")
add("LG07", G, "Quantos segundos se passaram entre a falha de conexão com o banco e a reconexão?", "number", "25",
    category="compute")
add("LG08", G, "Qual requisição falhou com status 500?", "text", "~/pagamentos")
add("LG09", G, "Qual foi a maior duração, em milissegundos, entre as requisições concluídas?", "number", "480",
    category="compute")
add("LG10", G, "Quantas requisições foram concluídas?", "number", "3", category="count")
add("LG11", G, "Quem corrigiu o erro de conexão com o banco?", "text", "", "ABSENT", "absent")
add("LG12", G, "Qual é a versão do servidor?", "text", "", "ABSENT", "absent")

# ------------------------------------------------------------------ gravar
with open(OUT / "cases.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "doc", "question", "kind", "expected", "expected_status", "category", "lang", "ref_date"])
    w.writerows(cases)

absent = len([c for c in cases if c[5] == "ABSENT"])
print(f"suite_pt: {len(cases)} perguntas ({absent} sem resposta no texto), "
      f"{len(set(c[1] for c in cases))} documentos")
