# Verificação realizada

## Verificações estáticas

- `app.py` compilado com `python -m py_compile` sem erro de sintaxe.
- Removido `__pycache__` do pacote final.
- Projeto final contém apenas arquivos apropriados para GitHub/Streamlit:
  - `app.py`
  - `requirements.txt`
  - `README.md`
  - `.gitignore`
  - `VERIFICATION.md`

## Verificações funcionais offline

Foram testadas as funções centrais sem depender da interface:

- Separação de múltiplos prontuários por `Prontuário do RN`.
- Separação alternativa por `Mãe:` para o modelo mais simples.
- Extração de nome, data/hora, IG, peso, sexo, TSM e TSRN.
- Cálculo de horas de vida para 16/06/2026 às 08:00.
- Associação de BTCs na mesma ordem dos pacientes.
- Funcionamento com BTC ausente, mantendo `BTC __`.
- Geração de link BiliTool com BTC técnico 0.1 quando BTC real está ausente.
- Percentil por z-score INTERGROWTH-21st.
- Classificação PIG/AIG/GIG.
- Classificação por idade gestacional.

## Caso sentinela validado

Entrada validada previamente pelo usuário:

- Masculino
- IG 39+0
- Peso 2868 g
- TSM A+
- HV 17
- BTC 5.4

Resultado esperado/obtido na lógica local:

- Percentil: p17
- Classificação ponderal: AIG
- Classificação gestacional: Termo pleno
- Saída textual com `TSM`, `TSRN`, `IG`, `HV`, `BTC`, `NC` e `NF`.

## Observação

A consulta online ao BiliTool depende de internet no ambiente onde o Streamlit estiver rodando. Em redes com proxy/firewall, a geração de links continua funcional, mas a consulta automática pode depender da liberação de acesso ao domínio `emr.bilitool.org`.
