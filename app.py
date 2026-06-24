from datetime import date

import pandas as pd
import streamlit as st

from bilitool_core import (
    consultar_bilitool_online,
    montar_html_impressao,
    montar_item,
    montar_linhas_tabela,
    montar_saida_texto,
    parse_btcs,
    parse_entrada,
    resolver_btc_paciente,
)

st.set_page_config(
    page_title="BiliTool Rotina Neonatal",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("BiliTool - Rotina Neonatal")
st.caption(
    "Extração de prontuário bruto ou entrada simplificada, HV, percentil "
    "INTERGROWTH-21st, perda ponderal e consulta ao BiliTool."
)
st.info(
    "BTC é opcional. Na folha impressa o campo BTC permanece sempre em branco para preenchimento manual. "
    "O leito é preenchido quando informado e fica tracejado quando ausente."
)


def inicializar_estado():
    padroes = {
        "dados_conferencia": [],
        "dados_resultado": [],
        "links_gerados": "",
    }
    for chave, valor in padroes.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


inicializar_estado()


def dados_atuais():
    return st.session_state.dados_resultado or st.session_state.dados_conferencia


def valor_inicial_opcoes(valor, opcoes):
    return opcoes.index(valor) if valor in opcoes else 0


def inteiro_ou_none(valor):
    texto = str(valor or "").strip()
    if not texto:
        return None
    return int(float(texto.replace(",", ".")))


def decimal_ou_none(valor):
    texto = str(valor or "").strip()
    if not texto:
        return None
    return float(texto.replace(",", "."))


@st.dialog("Editar dados do paciente", width="large")
def dialogo_edicao(indice):
    item = st.session_state.dados_conferencia[indice]
    p = dict(item.get("paciente_obj") or {})

    with st.form(f"form_edicao_{indice}"):
        c1, c2, c3 = st.columns(3)
        with c1:
            leito = st.text_input("Leito", value=str(p.get("leito") or ""))
            nome = st.text_input("Paciente", value=str(p.get("nome") or ""))
            sexo = st.text_input("Sexo", value=str(p.get("sexo") or ""))
            tipo_parto = st.text_input("Tipo de parto", value=str(p.get("tipo_parto") or ""))
            ci = st.text_input("CI/Coombs", value=str(p.get("ci") or ""))
        with c2:
            data_nasc = st.text_input("Data de nascimento", value=str(p.get("data_nasc") or ""))
            hora_nasc = st.text_input("Hora de nascimento", value=str(p.get("hora_nasc") or ""))
            ig_sem = st.text_input("IG - semanas", value=str(p.get("ig_sem") if p.get("ig_sem") is not None else ""))
            ig_dias = st.text_input("IG - dias", value=str(p.get("ig_dias") if p.get("ig_dias") is not None else ""))
            apgar1 = st.text_input("Apgar 1º minuto", value=str(p.get("apgar1") or ""))
            apgar5 = st.text_input("Apgar 5º minuto", value=str(p.get("apgar5") or ""))
        with c3:
            peso_g = st.text_input("Peso de nascimento (g)", value=str(p.get("peso_g") or ""))
            peso_atual_g = st.text_input("Peso atual mais recente (g)", value=str(p.get("peso_atual_g") or ""))
            data_peso_atual = st.text_input("Data do peso atual", value=str(p.get("data_peso_atual") or ""))
            hora_peso_atual = st.text_input("Hora do peso atual", value=str(p.get("hora_peso_atual") or ""))
            btc = st.text_input("BTC", value="" if item.get("btc") is None else str(item.get("btc")))

        c4, c5 = st.columns(2)
        with c4:
            abo_mae = st.selectbox(
                "ABO materno", ["", "O", "A", "B", "AB"],
                index=valor_inicial_opcoes(p.get("abo_mae") or "", ["", "O", "A", "B", "AB"]),
            )
            rh_mae = st.selectbox(
                "Rh materno", ["", "+", "-"],
                index=valor_inicial_opcoes(p.get("rh_mae") or "", ["", "+", "-"]),
            )
        with c5:
            abo_rn = st.selectbox(
                "ABO do RN", ["", "O", "A", "B", "AB"],
                index=valor_inicial_opcoes(p.get("abo_rn") or "", ["", "O", "A", "B", "AB"]),
            )
            rh_rn = st.selectbox(
                "Rh do RN", ["", "+", "-"],
                index=valor_inicial_opcoes(p.get("rh_rn") or "", ["", "+", "-"]),
            )

        observacao_manual = st.text_area(
            "Observação manual adicional",
            value=str(p.get("observacao_manual") or ""),
            height=80,
        )

        salvar = st.form_submit_button("Salvar alterações", type="primary")

    if salvar:
        try:
            p.update({
                "leito": leito.strip(),
                "nome": nome.strip(),
                "sexo": sexo.strip(),
                "tipo_parto": tipo_parto.strip(),
                "ci": ci.strip(),
                "data_nasc": data_nasc.strip(),
                "hora_nasc": hora_nasc.strip(),
                "ig_sem": inteiro_ou_none(ig_sem),
                "ig_dias": inteiro_ou_none(ig_dias),
                "apgar1": apgar1.strip() or None,
                "apgar5": apgar5.strip() or None,
                "peso_g": inteiro_ou_none(peso_g),
                "peso_atual_g": inteiro_ou_none(peso_atual_g),
                "data_peso_atual": data_peso_atual.strip() or None,
                "hora_peso_atual": hora_peso_atual.strip() or None,
                "abo_mae": abo_mae or None,
                "rh_mae": rh_mae or None,
                "abo_rn": abo_rn or None,
                "rh_rn": rh_rn or None,
                "observacao_manual": observacao_manual.strip(),
                "btc_entrada": decimal_ou_none(btc),
            })
            novo_item = montar_item(
                p=p,
                ordem=item["ordem"],
                btc=decimal_ou_none(btc),
                data_avaliacao_str=st.session_state.data_avaliacao_str,
                hora_avaliacao=st.session_state.hora_avaliacao_atual,
                modo_arredondamento_bilitool=st.session_state.modo_arredondamento_atual,
            )
            st.session_state.dados_conferencia[indice] = novo_item
            st.session_state.dados_resultado = []
            st.session_state.links_gerados = ""
            st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível salvar: {exc}")


col_data, col_hora = st.columns([1, 1])
with col_data:
    data_avaliacao = st.date_input("Data avaliação", value=date.today(), format="DD/MM/YYYY")
with col_hora:
    hora_avaliacao = st.text_input("Hora", value="08:00")

data_avaliacao_str = data_avaliacao.strftime("%d/%m/%Y")
st.session_state.data_avaliacao_str = data_avaliacao_str
st.session_state.hora_avaliacao_atual = hora_avaliacao

st.markdown("### Entrada e ajuste para o BiliTool")
col_formato, col_arred = st.columns([1, 2])
with col_formato:
    formato_label = st.radio(
        "Formato dos dados",
        options=["Detectar automaticamente", "Prontuário bruto", "Entrada simplificada"],
        index=0,
    )
with col_arred:
    modo_arredondamento_label = st.radio(
        "Arredondar idade gestacional apenas para o BiliTool",
        options=[
            "Não arredondar",
            "Arredondar apenas 6 dias para a semana seguinte (ex.: 37+6 → 38)",
            "Arredondar 5 ou 6 dias para a semana seguinte (ex.: 37+5/37+6 → 38)",
        ],
        index=0,
        help=(
            "Altera somente o parâmetro enviado ao BiliTool. A IG original, o percentil "
            "INTERGROWTH e a classificação gestacional permanecem inalterados."
        ),
    )

MAPA_FORMATO = {
    "Detectar automaticamente": "automatico",
    "Prontuário bruto": "bruto",
    "Entrada simplificada": "simplificado",
}
MAPA_MODO_ARREDONDAMENTO = {
    "Não arredondar": "nenhum",
    "Arredondar apenas 6 dias para a semana seguinte (ex.: 37+6 → 38)": "6_dias",
    "Arredondar 5 ou 6 dias para a semana seguinte (ex.: 37+5/37+6 → 38)": "5_dias",
}
modo_entrada = MAPA_FORMATO[formato_label]
modo_arredondamento_bilitool = MAPA_MODO_ARREDONDAMENTO[modo_arredondamento_label]
st.session_state.modo_arredondamento_atual = modo_arredondamento_bilitool

col1, col2 = st.columns([3, 1])
with col1:
    texto_prontuario = st.text_area(
        "Cole aqui os prontuários ou a entrada simplificada",
        height=280,
        placeholder=(
            "Exemplo simplificado:\nLEITO: 203\nNOME: RN de Maria Silva\n"
            "NASCIMENTO: 23/06/2026 08:42\nSEXO: F\nIG: 39+2\nPN: 3276\n"
            "PESO ATUAL: 3126\nDATA/HORA PESO ATUAL: 24/06/2026 20:14\nTSM: O+\nTSRN: A+\nAPGAR: 8/9"
        ),
    )
with col2:
    texto_btcs = st.text_area(
        "BTCs, um por linha, na mesma ordem. Opcional.",
        height=280,
        help="Quando o BTC também estiver na entrada simplificada, este campo externo tem prioridade.",
    )

b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
with b1:
    extrair = st.button("1) Extrair e conferir", type="primary")
with b2:
    gerar_links = st.button("2) Gerar links")
with b3:
    consultar = st.button("Consultar BiliTool online")
with b4:
    limpar = st.button("Limpar")

if limpar:
    st.session_state.dados_conferencia = []
    st.session_state.dados_resultado = []
    st.session_state.links_gerados = ""
    st.rerun()

if extrair:
    try:
        pacientes = parse_entrada(texto_prontuario, modo=modo_entrada)
        btcs = parse_btcs(texto_btcs)

        if not pacientes:
            st.error("Nenhum paciente identificado.")
        elif btcs and len(pacientes) != len(btcs):
            st.error(
                f"Foram identificados {len(pacientes)} pacientes, mas há {len(btcs)} BTCs. "
                "Deixe o campo de BTC vazio ou informe exatamente um valor por paciente."
            )
        else:
            dados = []
            for i, p in enumerate(pacientes, start=1):
                btc_externo = btcs[i - 1] if btcs else None
                btc = resolver_btc_paciente(p, btc_externo)
                dados.append(montar_item(
                    p=p,
                    ordem=i,
                    btc=btc,
                    data_avaliacao_str=data_avaliacao_str,
                    hora_avaliacao=hora_avaliacao,
                    modo_arredondamento_bilitool=modo_arredondamento_bilitool,
                ))
            st.session_state.dados_conferencia = dados
            st.session_state.dados_resultado = []
            st.session_state.links_gerados = ""
            st.success("Dados extraídos com sucesso.")
    except Exception as exc:
        st.error(f"Erro: {exc}")

if gerar_links:
    dados = st.session_state.dados_conferencia
    if not dados:
        st.warning("Primeiro clique em 'Extrair e conferir'.")
    else:
        st.session_state.links_gerados = "\n".join(
            f"{('Leito ' + item['leito']) if item.get('leito') else item['paciente']} | "
            f"{item['link'] or item.get('observacao_bilitool', 'sem link')}"
            for item in dados
        )
        st.success("Links gerados.")

if consultar:
    dados = st.session_state.dados_conferencia
    if not dados:
        st.warning("Primeiro clique em 'Extrair e conferir'.")
    else:
        resultados = []
        barra = st.progress(0)
        try:
            for idx, item in enumerate(dados, start=1):
                ig_bt = item.get("ig_sem_bilitool")
                if ig_bt is None:
                    resultados.append(dict(item))
                    barra.progress(idx / len(dados))
                    continue

                resposta = consultar_bilitool_online(
                    hv=item["hv"],
                    btc=item["btc"],
                    ig_sem_bilitool=ig_bt,
                    neuro=item["neuro"],
                )
                tem_btc_real = item.get("btc") is not None
                resultados.append({
                    **item,
                    "NC": resposta["NC"],
                    "NF": resposta["NF"],
                    "NE": resposta["NE"],
                    "EXT": resposta["EXT"],
                    "coletar": resposta["coletar"] if tem_btc_real else None,
                    "fototerapia": resposta["fototerapia"] if tem_btc_real else None,
                    "escalonar": resposta["escalonar"] if tem_btc_real else None,
                    "exsanguineo": resposta["exsanguineo"] if tem_btc_real else None,
                })
                barra.progress(idx / len(dados))
            st.session_state.dados_resultado = resultados
            st.success("Consulta ao BiliTool concluída.")
        except Exception as exc:
            st.error(f"Não foi possível consultar o BiliTool automaticamente. Detalhe técnico: {exc}")

atuais = dados_atuais()
st.subheader("Conferência / Resultado")
if atuais:
    df = pd.DataFrame(montar_linhas_tabela(atuais))
    st.dataframe(df.drop(columns=["Link"], errors="ignore"), width="stretch", hide_index=True)

    st.markdown("#### Edição manual")
    opcoes = list(range(len(st.session_state.dados_conferencia)))
    indice_edicao = st.selectbox(
        "Paciente",
        opcoes,
        format_func=lambda i: (
            f"Leito {st.session_state.dados_conferencia[i].get('leito')} - "
            if st.session_state.dados_conferencia[i].get("leito") else ""
        ) + st.session_state.dados_conferencia[i].get("paciente", ""),
    )
    if st.button("Editar paciente selecionado"):
        dialogo_edicao(indice_edicao)

    saida = montar_saida_texto(atuais)
    st.subheader("Saída final")
    st.code(saida, language="text")
    st.text_area("Saída final para copiar", value=saida, height=220)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "Baixar TXT",
            data=saida.encode("utf-8"),
            file_name="bilitool_saida.txt",
            mime="text/plain",
        )
    with c2:
        csv_data = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            "Baixar CSV",
            data=csv_data.encode("utf-8-sig"),
            file_name="bilitool_saida.csv",
            mime="text/csv",
        )
    with c3:
        html_doc = montar_html_impressao(atuais, data_avaliacao_str, hora_avaliacao)
        st.download_button(
            "Baixar HTML para imprimir",
            data=html_doc.encode("utf-8"),
            file_name="bilitool_impressao.html",
            mime="text/html",
        )
else:
    st.info("Cole os dados e clique em 'Extrair e conferir'.")

st.subheader("Links")
if st.session_state.links_gerados:
    st.text_area("Links gerados", value=st.session_state.links_gerados, height=160)
    st.download_button(
        "Baixar links TXT",
        data=st.session_state.links_gerados.encode("utf-8"),
        file_name="bilitool_links.txt",
        mime="text/plain",
    )
elif atuais:
    st.caption("Clique em 'Gerar links' para exibir os links do BiliTool.")
