import re
import csv
import time
import webbrowser
import urllib.parse
import urllib.request
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


BILITOOL_POST_URL = "https://bilitool.org/results.php"
BILITOOL_LINK_URL = "https://emr.bilitool.org/results.php"


# ============================================================
# FORMATAÇÃO
# ============================================================

def titulo_nome(nome):
    if not nome:
        return ""

    minusculas = {"de", "da", "do", "das", "dos", "e"}
    palavras = nome.strip().lower().split()
    final = []

    for p in palavras:
        if p in minusculas:
            final.append(p)
        else:
            final.append(p.capitalize())

    return " ".join(final)


def normalizar_rh(valor):
    if not valor:
        return None

    v = valor.strip().lower()

    if "positivo" in v or v == "+":
        return "+"

    if "negativo" in v or v == "-":
        return "-"

    return None


def formatar_tipo(abo, rh):
    if not abo:
        return "desconhecido"

    if not rh:
        return abo

    return f"{abo}{rh}"


def formatar_ig(semanas, dias):
    return f"{semanas}+{dias}"


def formatar_numero(valor):
    if valor is None:
        return ""

    try:
        return f"{float(valor):.1f}"
    except Exception:
        return str(valor)


# ============================================================
# EXTRAÇÃO DO PRONTUÁRIO
# ============================================================

def dividir_blocos(texto):
    texto = texto.strip()

    if re.search(r"Prontuário do RN", texto, flags=re.IGNORECASE):
        partes = re.split(r"(?=Prontuário do RN)", texto, flags=re.IGNORECASE)
        return [p.strip() for p in partes if p.strip().lower().startswith("prontuário do rn")]

    if re.search(r"\bMãe\s*:", texto, flags=re.IGNORECASE):
        partes = re.split(r"(?=\bMãe\s*:)", texto, flags=re.IGNORECASE)
        return [p.strip() for p in partes if p.strip().lower().startswith("mãe")]

    return []


def extrair_apos_rotulo(bloco, rotulo):
    linhas = bloco.splitlines()
    alvo = rotulo.lower().strip()

    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        linha_lower = linha_limpa.lower()

        if linha_lower.startswith(alvo + ":"):
            resto = linha_limpa.split(":", 1)[1].strip()

            if resto:
                return resto

            for j in range(i + 1, len(linhas)):
                prox = linhas[j].strip()
                if prox:
                    return prox

    return None


def extrair_campo_linha(bloco, rotulo):
    linhas = bloco.splitlines()
    alvo = rotulo.lower().strip()

    for linha in linhas:
        linha_limpa = linha.strip()
        linha_lower = linha_limpa.lower()

        if alvo in linha_lower:
            idx = linha_lower.find(alvo)
            resto = linha_limpa[idx + len(rotulo):].strip(" \t:-")

            if not resto:
                return None

            return resto.strip()

    return None


def extrair_nome_mae(bloco):
    nome_rn = extrair_apos_rotulo(bloco, "Nome RN")

    if nome_rn:
        nome = re.sub(r"^RN\s+de\s+", "", nome_rn, flags=re.IGNORECASE).strip()
        return titulo_nome(nome)

    m = re.search(r"\d+\s*-\s*RN DE\s+(.+?)\s+\(", bloco, flags=re.IGNORECASE)
    if m:
        return titulo_nome(m.group(1))

    mae = extrair_apos_rotulo(bloco, "Mãe")
    if mae:
        mae = re.sub(r"^\d+\s*-\s*", "", mae).strip()
        return titulo_nome(mae)

    return ""


def extrair_data_hora(bloco):
    data = extrair_apos_rotulo(bloco, "Data")
    hora = extrair_apos_rotulo(bloco, "Hora")

    if data and hora:
        return data, hora

    data_hora = extrair_apos_rotulo(bloco, "Data - Hora")
    if data_hora:
        m = re.search(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})", data_hora)
        if m:
            return m.group(1), m.group(2)

    return data, hora


def extrair_ig(bloco):
    valor = extrair_apos_rotulo(bloco, "Semanas gestacao")

    if not valor:
        return None, None

    m = re.search(r"(\d{2})(?:\s*e\s*(\d+)\s*dia)?", valor, flags=re.IGNORECASE)

    if not m:
        return None, None

    semanas = int(m.group(1))
    dias = int(m.group(2)) if m.group(2) else 0

    return semanas, dias


def extrair_peso_g(bloco):
    peso = extrair_apos_rotulo(bloco, "Peso")

    if not peso:
        return None

    m = re.search(r"([\d.,]+)", peso)

    if not m:
        return None

    valor = m.group(1).replace(",", ".")

    try:
        numero = float(valor)

        if numero < 20:
            return int(round(numero * 1000))

        return int(round(numero))
    except ValueError:
        return None


def extrair_abo_mae(bloco):
    valor = extrair_campo_linha(bloco, "ABO RH - Mãe")

    if not valor:
        return None

    m = re.search(r"\b(AB|A|B|O)\b", valor, flags=re.IGNORECASE)

    return m.group(1).upper() if m else None


def extrair_rh_mae(bloco):
    valor = extrair_campo_linha(bloco, "Fator RH - Mãe")

    if not valor:
        return None

    return normalizar_rh(valor)


def extrair_abo_rn(bloco):
    valor = extrair_campo_linha(bloco, "ABO RH - RN")

    if not valor:
        return None

    m = re.search(r"\b(AB|A|B|O)\b", valor, flags=re.IGNORECASE)

    return m.group(1).upper() if m else None


def extrair_rh_rn(bloco):
    valor = extrair_campo_linha(bloco, "Fator RH - RN")

    if not valor:
        return None

    return normalizar_rh(valor)


def parse_prontuarios(texto):
    blocos = dividir_blocos(texto)
    pacientes = []

    for bloco in blocos:
        data_nasc, hora_nasc = extrair_data_hora(bloco)
        semanas, dias = extrair_ig(bloco)

        paciente = {
            "nome": extrair_nome_mae(bloco),
            "data_nasc": data_nasc,
            "hora_nasc": hora_nasc,
            "tipo_parto": extrair_apos_rotulo(bloco, "Tipo obstetricia"),
            "sexo": extrair_apos_rotulo(bloco, "Sexo"),
            "ig_sem": semanas,
            "ig_dias": dias,
            "peso_g": extrair_peso_g(bloco),
            "apgar1": extrair_apos_rotulo(bloco, "Apgar 1º min"),
            "apgar5": extrair_apos_rotulo(bloco, "Apgar 5º min"),
            "abo_mae": extrair_abo_mae(bloco),
            "rh_mae": extrair_rh_mae(bloco),
            "abo_rn": extrair_abo_rn(bloco),
            "rh_rn": extrair_rh_rn(bloco),
            "bloco": bloco
        }

        pacientes.append(paciente)

    return pacientes


# ============================================================
# REGRAS OPERACIONAIS
# ============================================================

def calcular_hv(data_nasc, hora_nasc, data_avaliacao, hora_avaliacao):
    nascimento = datetime.strptime(f"{data_nasc} {hora_nasc}", "%d/%m/%Y %H:%M")
    avaliacao = datetime.strptime(f"{data_avaliacao} {hora_avaliacao}", "%d/%m/%Y %H:%M")

    horas = (avaliacao - nascimento).total_seconds() / 3600

    return round(horas)


def definir_neuro(abo_mae, rh_mae, abo_rn, rh_rn):
    abo_mae = abo_mae.upper() if abo_mae else None
    abo_rn = abo_rn.upper() if abo_rn else None

    risco_abo = False
    risco_rh = False

    if abo_mae == "O":
        if not abo_rn:
            risco_abo = True
        elif abo_rn != "O":
            risco_abo = True

    if rh_mae == "-":
        if not rh_rn:
            risco_rh = True
        elif rh_rn == "+":
            risco_rh = True

    return risco_abo or risco_rh


def semanas_bilitool(ig_sem):
    if ig_sem >= 40:
        return 40

    return ig_sem


def parse_btcs(texto):
    linhas = [x.strip().replace(",", ".") for x in texto.splitlines() if x.strip()]
    btcs = []

    for linha in linhas:
        try:
            btcs.append(float(linha))
        except ValueError:
            raise ValueError(f"BTC inválido: {linha}")

    return btcs


def resumo_rn(p):
    itens = []

    if p.get("sexo"):
        itens.append(p["sexo"][0].upper())

    if p.get("peso_g"):
        itens.append(f"PN {p['peso_g']}g")

    if p.get("tipo_parto"):
        itens.append(p["tipo_parto"])

    if p.get("apgar1") and p.get("apgar5"):
        itens.append(f"Apgar {p['apgar1']}/{p['apgar5']}")

    return " | ".join(itens)


# ============================================================
# LINKS E BILITOOL
# ============================================================

def gerar_link_bilitool(hv, btc, ig_sem_bilitool, neuro):
    params = {
        "ageHours": str(hv),
        "totalBilirubin": f"{btc:.1f}",
        "bilirubinUnits": "US",
        "gestationalWeeks": str(ig_sem_bilitool),
        "neuroRiskFactors": "Yes" if neuro else "No"
    }

    return BILITOOL_LINK_URL + "?" + urllib.parse.urlencode(params)


def extrair_threshold(texto, rotulo):
    padrao = rf"{rotulo}\?\s*(YES|NO)\s*\(([\d.]+)\s*mg/dL\)"
    m = re.search(padrao, texto, flags=re.IGNORECASE)

    if not m:
        return None, None

    return m.group(1).upper(), float(m.group(2))


def consultar_bilitool_online(hv, btc, ig_sem_bilitool, neuro):
    data = {
        "ageHours": str(hv),
        "totalBilirubin": f"{btc:.1f}",
        "bilirubinUnits": "US",
        "gestationalWeeks": str(ig_sem_bilitool),
        "etcoc": ""
    }

    if neuro:
        data["hemolytic"] = "1"

    encoded = urllib.parse.urlencode(data).encode("utf-8")

    req = urllib.request.Request(
        BILITOOL_POST_URL,
        data=encoded,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        html = response.read().decode("utf-8", errors="ignore")

    m = re.search(
        r'<textarea[^>]*id="bar"[^>]*>(.*?)</textarea>',
        html,
        flags=re.S | re.I
    )

    if not m:
        raise ValueError("Não foi possível localizar o resumo do BiliTool no HTML.")

    resumo = m.group(1)

    decisao_nc, nc = extrair_threshold(resumo, r"Check serum bilirubin if using TcB")
    decisao_nf, nf = extrair_threshold(resumo, r"Phototherapy")
    decisao_ne, ne = extrair_threshold(resumo, r"Escalation of care")
    decisao_ext, ext = extrair_threshold(resumo, r"Exchange transfusion")

    return {
        "NC": nc,
        "NF": nf,
        "NE": ne,
        "EXT": ext,
        "coletar": decisao_nc == "YES",
        "fototerapia": decisao_nf == "YES",
        "escalonar": decisao_ne == "YES",
        "exsanguineo": decisao_ext == "YES",
        "resumo": resumo
    }


def extrair_resultados_de_resumos(texto):
    padrao = (
        r"Check serum bilirubin if using TcB\?\s*(YES|NO)\s*\(([\d.]+)\s*mg/dL\)"
        r".*?"
        r"Phototherapy\?\s*(YES|NO)\s*\(([\d.]+)\s*mg/dL\)"
        r".*?"
        r"Escalation of care\?\s*(YES|NO)\s*\(([\d.]+)\s*mg/dL\)"
        r".*?"
        r"Exchange transfusion\?\s*(YES|NO)\s*\(([\d.]+)\s*mg/dL\)"
    )

    resultados = []

    for m in re.finditer(padrao, texto, flags=re.S | re.I):
        resultados.append({
            "NC": float(m.group(2)),
            "NF": float(m.group(4)),
            "NE": float(m.group(6)),
            "EXT": float(m.group(8)),
            "coletar": m.group(1).upper() == "YES",
            "fototerapia": m.group(3).upper() == "YES",
            "escalonar": m.group(5).upper() == "YES",
            "exsanguineo": m.group(7).upper() == "YES"
        })

    return resultados


# ============================================================
# INTERFACE
# ============================================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("BiliTool Rotina Neonatal")
        self.root.geometry("1400x850")

        self.dados_conferencia = []
        self.dados_resultado = []

        self.montar_tela()

    def montar_tela(self):
        topo = tk.Frame(self.root)
        topo.pack(fill="x", padx=10, pady=5)

        tk.Label(topo, text="Data avaliação:").pack(side="left")
        self.data_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        tk.Entry(topo, textvariable=self.data_var, width=12).pack(side="left", padx=5)

        tk.Label(topo, text="Hora:").pack(side="left")
        self.hora_var = tk.StringVar(value="08:00")
        tk.Entry(topo, textvariable=self.hora_var, width=8).pack(side="left", padx=5)

        botoes = tk.Frame(self.root)
        botoes.pack(fill="x", padx=10, pady=5)

        tk.Button(
            botoes,
            text="1) Extrair e conferir",
            command=self.extrair_conferir
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="2) Gerar links",
            command=self.gerar_links
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="Abrir links",
            command=self.abrir_links
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="Consultar BiliTool online",
            command=self.consultar_online
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="Extrair NC/NF dos resumos",
            command=self.extrair_dos_resumos
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="Copiar saída final",
            command=self.copiar_saida
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="Copiar links",
            command=self.copiar_links
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="Salvar CSV",
            command=self.salvar_csv
        ).pack(side="left", padx=4)

        tk.Button(
            botoes,
            text="Limpar",
            command=self.limpar
        ).pack(side="left", padx=4)

        painel_texto = tk.PanedWindow(self.root, orient="horizontal")
        painel_texto.pack(fill="both", expand=False, padx=10, pady=5)

        frame_pront = tk.Frame(painel_texto)
        tk.Label(frame_pront, text="Cole aqui os prontuários").pack(anchor="w")
        self.txt_pront = tk.Text(frame_pront, height=11)
        self.txt_pront.pack(fill="both", expand=True)

        frame_btc = tk.Frame(painel_texto)
        tk.Label(frame_btc, text="Cole aqui os BTCs, um por linha, na mesma ordem").pack(anchor="w")
        self.txt_btc = tk.Text(frame_btc, height=11, width=32)
        self.txt_btc.pack(fill="both", expand=True)

        painel_texto.add(frame_pront)
        painel_texto.add(frame_btc)

        tk.Label(self.root, text="Conferência / Resultado").pack(anchor="w", padx=10)

        colunas = (
            "ordem", "paciente", "tsm", "tsrn", "ig", "hv",
            "neuro", "btc", "nc", "nf", "coletar", "foto", "resumo"
        )

        self.tabela = ttk.Treeview(self.root, columns=colunas, show="headings", height=13)

        titulos = {
            "ordem": "#",
            "paciente": "Paciente",
            "tsm": "TSM",
            "tsrn": "TSRN",
            "ig": "IG",
            "hv": "HV",
            "neuro": "Neuro",
            "btc": "BTC",
            "nc": "NC",
            "nf": "NF",
            "coletar": "Coletar?",
            "foto": "Foto?",
            "resumo": "Resumo RN"
        }

        larguras = {
            "ordem": 40,
            "paciente": 260,
            "tsm": 70,
            "tsrn": 90,
            "ig": 70,
            "hv": 60,
            "neuro": 70,
            "btc": 70,
            "nc": 70,
            "nf": 70,
            "coletar": 80,
            "foto": 80,
            "resumo": 360
        }

        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, width=larguras[col], anchor="center")

        self.tabela.pack(fill="both", expand=True, padx=10, pady=5)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_saida = tk.Frame(self.tabs)
        self.tab_links = tk.Frame(self.tabs)
        self.tab_resumos = tk.Frame(self.tabs)

        self.tabs.add(self.tab_saida, text="Saída final")
        self.tabs.add(self.tab_links, text="Links")
        self.tabs.add(self.tab_resumos, text="Resumos copiados do BiliTool")

        self.txt_saida = tk.Text(self.tab_saida, height=9)
        self.txt_saida.pack(fill="both", expand=True)

        self.txt_links = tk.Text(self.tab_links, height=9)
        self.txt_links.pack(fill="both", expand=True)

        tk.Label(
            self.tab_resumos,
            text="Cole aqui os resumos copiados do BiliTool, na mesma ordem dos pacientes."
        ).pack(anchor="w")

        self.txt_resumos = tk.Text(self.tab_resumos, height=9)
        self.txt_resumos.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    # UTILITÁRIOS DE INTERFACE
    # ------------------------------------------------------------

    def limpar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

    def renderizar_tabela(self, dados):
        self.limpar_tabela()

        for item in dados:
            self.tabela.insert(
                "",
                "end",
                values=(
                    item.get("ordem", ""),
                    item.get("paciente", ""),
                    item.get("tsm", ""),
                    item.get("tsrn", ""),
                    item.get("ig", ""),
                    item.get("hv", ""),
                    "Sim" if item.get("neuro") else "Não",
                    formatar_numero(item.get("btc")),
                    formatar_numero(item.get("NC")),
                    formatar_numero(item.get("NF")),
                    "Sim" if item.get("coletar") else "Não" if item.get("coletar") is not None else "",
                    "Sim" if item.get("fototerapia") else "Não" if item.get("fototerapia") is not None else "",
                    item.get("resumo", "")
                )
            )

    def gerar_linha_final(self, item):
        nc = formatar_numero(item.get("NC"))
        nf = formatar_numero(item.get("NF"))

        return (
            f"{item['paciente']} | "
            f"{item['tsm']} | "
            f"{item['tsrn']} | "
            f"{item['ig']} | "
            f"{item['hv']}hv | "
            f"BTC {item['btc']:.1f} | "
            f"NC {nc} | "
            f"NF {nf}"
        )

    def atualizar_saida_final(self, dados):
        self.txt_saida.delete("1.0", "end")

        linhas = []

        for item in dados:
            linha = self.gerar_linha_final(item)
            linhas.append(linha)

            self.txt_saida.insert("end", linha + "\n")
            if item.get("resumo"):
                self.txt_saida.insert("end", f"Resumo: {item['resumo']}\n")
            self.txt_saida.insert("end", "\n")

        return "\n".join(linhas)

    def copiar_texto(self, texto):
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        self.root.update()

    # ------------------------------------------------------------
    # ETAPA 1: EXTRAIR
    # ------------------------------------------------------------

    def extrair_conferir(self):
        try:
            texto = self.txt_pront.get("1.0", "end")
            btc_texto = self.txt_btc.get("1.0", "end")

            pacientes = parse_prontuarios(texto)
            btcs = parse_btcs(btc_texto)

            if not pacientes:
                messagebox.showerror("Erro", "Nenhum paciente identificado.")
                return

            if len(pacientes) != len(btcs):
                messagebox.showerror(
                    "Erro",
                    f"Foram identificados {len(pacientes)} pacientes, mas há {len(btcs)} BTCs."
                )
                return

            self.dados_conferencia = []
            self.dados_resultado = []

            self.txt_saida.delete("1.0", "end")
            self.txt_links.delete("1.0", "end")

            for i, p in enumerate(pacientes, start=1):
                faltantes = []

                for campo in ["nome", "data_nasc", "hora_nasc", "ig_sem", "abo_mae", "rh_mae"]:
                    if p.get(campo) in [None, ""]:
                        faltantes.append(campo)

                if faltantes:
                    raise ValueError(f"Paciente {i} com campos faltantes: {', '.join(faltantes)}")

                hv = calcular_hv(
                    p["data_nasc"],
                    p["hora_nasc"],
                    self.data_var.get(),
                    self.hora_var.get()
                )

                if hv < 0:
                    raise ValueError(f"{p['nome']}: nascimento posterior à avaliação.")

                neuro = definir_neuro(
                    p["abo_mae"],
                    p["rh_mae"],
                    p["abo_rn"],
                    p["rh_rn"]
                )

                tsm = formatar_tipo(p["abo_mae"], p["rh_mae"])
                tsrn = formatar_tipo(p["abo_rn"], p["rh_rn"])
                ig = formatar_ig(p["ig_sem"], p["ig_dias"])
                btc = btcs[i - 1]

                link = gerar_link_bilitool(
                    hv=hv,
                    btc=btc,
                    ig_sem_bilitool=semanas_bilitool(p["ig_sem"]),
                    neuro=neuro
                )

                item = {
                    "ordem": i,
                    "paciente": p["nome"],
                    "tsm": tsm,
                    "tsrn": tsrn,
                    "ig": ig,
                    "ig_sem": p["ig_sem"],
                    "ig_dias": p["ig_dias"],
                    "hv": hv,
                    "neuro": neuro,
                    "btc": btc,
                    "resumo": resumo_rn(p),
                    "link": link,
                    "paciente_obj": p,
                    "NC": None,
                    "NF": None,
                    "NE": None,
                    "EXT": None,
                    "coletar": None,
                    "fototerapia": None,
                    "escalonar": None,
                    "exsanguineo": None
                }

                self.dados_conferencia.append(item)

            self.renderizar_tabela(self.dados_conferencia)
            self.atualizar_saida_final(self.dados_conferencia)

            messagebox.showinfo(
                "Conferência",
                "Dados extraídos com sucesso. Confira a tabela antes de consultar ou gerar links."
            )

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ------------------------------------------------------------
    # ETAPA 2: LINKS
    # ------------------------------------------------------------

    def gerar_links(self):
        if not self.dados_conferencia:
            messagebox.showwarning("Atenção", "Primeiro clique em 'Extrair e conferir'.")
            return

        self.txt_links.delete("1.0", "end")

        for item in self.dados_conferencia:
            linha = f"{item['ordem']} | {item['paciente']} | {item['link']}"
            self.txt_links.insert("end", linha + "\n")

        self.tabs.select(self.tab_links)

        messagebox.showinfo("Links", "Links gerados com sucesso.")

    def abrir_links(self):
        if not self.dados_conferencia:
            messagebox.showwarning("Atenção", "Primeiro clique em 'Extrair e conferir'.")
            return

        if not self.txt_links.get("1.0", "end").strip():
            self.gerar_links()

        for item in self.dados_conferencia:
            webbrowser.open_new_tab(item["link"])
            time.sleep(0.2)

        messagebox.showinfo("Links", "Links enviados ao navegador.")

    def copiar_links(self):
        texto = self.txt_links.get("1.0", "end").strip()

        if not texto:
            messagebox.showwarning("Atenção", "Não há links para copiar.")
            return

        self.copiar_texto(texto)
        messagebox.showinfo("Copiado", "Links copiados para a área de transferência.")

    # ------------------------------------------------------------
    # ETAPA 3A: CONSULTA ONLINE AUTOMÁTICA
    # ------------------------------------------------------------

    def consultar_online(self):
        if not self.dados_conferencia:
            messagebox.showwarning("Atenção", "Primeiro clique em 'Extrair e conferir'.")
            return

        try:
            resultados = []

            for item in self.dados_conferencia:
                r = consultar_bilitool_online(
                    hv=item["hv"],
                    btc=item["btc"],
                    ig_sem_bilitool=semanas_bilitool(item["ig_sem"]),
                    neuro=item["neuro"]
                )

                novo = {
                    **item,
                    "NC": r["NC"],
                    "NF": r["NF"],
                    "NE": r["NE"],
                    "EXT": r["EXT"],
                    "coletar": r["coletar"],
                    "fototerapia": r["fototerapia"],
                    "escalonar": r["escalonar"],
                    "exsanguineo": r["exsanguineo"]
                }

                resultados.append(novo)

            self.dados_resultado = resultados
            self.renderizar_tabela(self.dados_resultado)
            self.atualizar_saida_final(self.dados_resultado)
            self.tabs.select(self.tab_saida)

            messagebox.showinfo("Concluído", "Consulta online ao BiliTool concluída.")

        except Exception as e:
            messagebox.showerror(
                "Erro na consulta online",
                "Não foi possível consultar o BiliTool automaticamente.\n\n"
                "Use o modo navegador: gerar links, abrir links e colar os resumos.\n\n"
                f"Detalhe técnico:\n{e}"
            )

    # ------------------------------------------------------------
    # ETAPA 3B: EXTRAÇÃO MANUAL DOS RESUMOS COPIADOS
    # ------------------------------------------------------------

    def extrair_dos_resumos(self):
        if not self.dados_conferencia:
            messagebox.showwarning("Atenção", "Primeiro clique em 'Extrair e conferir'.")
            return

        texto = self.txt_resumos.get("1.0", "end")
        resultados_extraidos = extrair_resultados_de_resumos(texto)

        if not resultados_extraidos:
            messagebox.showerror(
                "Erro",
                "Nenhum resultado foi identificado nos resumos colados."
            )
            return

        if len(resultados_extraidos) != len(self.dados_conferencia):
            messagebox.showerror(
                "Erro",
                f"Foram extraídos {len(resultados_extraidos)} resultados, "
                f"mas há {len(self.dados_conferencia)} pacientes na conferência.\n\n"
                "Confira se você colou um resumo para cada paciente, na mesma ordem."
            )
            return

        self.dados_resultado = []

        for item, r in zip(self.dados_conferencia, resultados_extraidos):
            novo = {
                **item,
                "NC": r["NC"],
                "NF": r["NF"],
                "NE": r["NE"],
                "EXT": r["EXT"],
                "coletar": r["coletar"],
                "fototerapia": r["fototerapia"],
                "escalonar": r["escalonar"],
                "exsanguineo": r["exsanguineo"]
            }

            self.dados_resultado.append(novo)

        self.renderizar_tabela(self.dados_resultado)
        self.atualizar_saida_final(self.dados_resultado)
        self.tabs.select(self.tab_saida)

        messagebox.showinfo(
            "Concluído",
            "NC e NF extraídos dos resumos colados."
        )

    # ------------------------------------------------------------
    # COPIAR / SALVAR / LIMPAR
    # ------------------------------------------------------------

    def copiar_saida(self):
        texto = self.txt_saida.get("1.0", "end").strip()

        if not texto:
            messagebox.showwarning("Atenção", "Não há saída final para copiar.")
            return

        self.copiar_texto(texto)
        messagebox.showinfo("Copiado", "Saída final copiada para a área de transferência.")

    def salvar_csv(self):
        dados = self.dados_resultado if self.dados_resultado else self.dados_conferencia

        if not dados:
            messagebox.showwarning("Atenção", "Não há dados para salvar.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Salvar resultado"
        )

        if not caminho:
            return

        campos = [
            "ordem", "paciente", "tsm", "tsrn", "ig", "hv", "neuro", "btc",
            "NC", "NF", "NE", "EXT", "coletar", "fototerapia",
            "resumo", "link"
        ]

        with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=campos,
                extrasaction="ignore",
                delimiter=";"
            )
            writer.writeheader()
            writer.writerows(dados)

        messagebox.showinfo("Salvo", f"Arquivo salvo em:\n{caminho}")

    def limpar(self):
        self.txt_pront.delete("1.0", "end")
        self.txt_btc.delete("1.0", "end")
        self.txt_saida.delete("1.0", "end")
        self.txt_links.delete("1.0", "end")
        self.txt_resumos.delete("1.0", "end")

        self.limpar_tabela()

        self.dados_conferencia = []
        self.dados_resultado = []


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()