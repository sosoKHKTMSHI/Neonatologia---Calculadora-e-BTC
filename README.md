# BiliTool Rotina Neonatal

Aplicação web em Streamlit para rotina neonatal de bilirrubina.

## Funcionalidades

- Extração automática dos dados do prontuário neonatal colado em texto.
- Cálculo de horas de vida na data/hora da avaliação.
- Identificação de TSM e TSRN, quando disponíveis.
- Definição operacional de fator de neurotoxicidade por incompatibilidade ABO/Rh presumida ou confirmada.
- Cálculo de percentil de peso ao nascer por z-score INTERGROWTH-21st, com cobertura de 24+0 a 42+6 semanas.
- Classificação PIG/AIG/GIG.
- Classificação por idade gestacional: pré-termo extremo, muito pré-termo, pré-termo moderado, pré-termo tardio, termo precoce, termo pleno, termo tardio e pós-termo.
- Geração de links do BiliTool.
- Consulta online do BiliTool para obter NC e NF.
- BTC opcional: sem BTC, o app obtém NC/NF usando BTC técnico apenas para consulta e mantém BTC em branco na saída.
- Exportação em TXT, CSV e HTML para impressão.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Streamlit Community Cloud

1. Crie um repositório no GitHub.
2. Envie `app.py`, `requirements.txt`, `README.md` e `.gitignore`.
3. Acesse Streamlit Community Cloud.
4. Clique em **New app**.
5. Selecione o repositório e a branch.
6. Em **Main file path**, use:

```text
app.py
```

7. Clique em **Deploy**.

## Observações de segurança e LGPD

O app processa o texto colado pelo usuário. Se utilizado com nomes reais e dados de prontuário em hospedagem externa, esses dados passam pelo servidor onde o app está hospedado. Para uso institucional com dados identificáveis, avalie hospedagem interna, acesso restrito ou anonimização.

## BiliTool

O app consulta o endpoint EMR do BiliTool por URL parametrizada. A consulta de NC/NF depende de acesso externo ao BiliTool a partir do servidor onde o app estiver rodando.
