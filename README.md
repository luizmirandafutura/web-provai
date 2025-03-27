# Visualizador de Processos Judiciais

Uma aplicação web desenvolvida com Streamlit para visualizar e analisar processos judiciais armazenados em formato JSON da ProvAI.

## Sobre o Projeto

Este aplicativo foi criado para facilitar a visualização e análise de processos judiciais. Ele permite aos usuários:

- Navegar pelo resumo e metadados do processo
- Ver informações detalhadas de cada página do documento
- Analisar pontos controversos
- Visualizar informações textuais e estatísticas

## Estrutura do Projeto

```
.
├── app.py                 # Aplicativo Streamlit principal
└── *.json                 # Arquivos JSON dos processos
```

## Requisitos

- Python 3.13+
- Streamlit 1.31.0+
- Pandas 2.2.0+
- Pydantic 2.5.3+

## Instalação

1. Instale o UV:

```bash
# Instale o UV (se ainda não tiver)
python -m pip install uv
```

2. Crie e ative o ambiente virtual:

```bash
1. uv venv
# ou
2. source .venv/bin/activate  # Linux/Mac
2. .venv\Scripts\activate  # Windows
```

3. Instale as dependências do uv:

```bash
# Instale as dependências usando UV
uv pip install .
```

## Execução

Para executar o aplicativo, use o seguinte comando:

```bash
streamlit run app.py
ou
uv run streamlit run app.py
```

Após executar o comando, o aplicativo será aberto automaticamente em seu navegador padrão no endereço `http://localhost:8501`.

## Estrutura do JSON

O aplicativo espera um arquivo JSON com a seguinte estrutura:

```json
{
  "file": {
    "file_name": "nome_do_arquivo.pdf",
    "file_type": "pdf",
    "total_pages": 94
  },
  "results": [
    {
      "page_id": 1,
      "file_name": "nome_da_pagina.pdf",
      "has_images": true,
      "extracted_text": "texto extraído",
      "extracted_image_text": "texto extraído de imagens",
      "summary": "resumo da página"
    }
  ],
  "metadata": {
    "is_approved": true/false,
    "process_number": "número do processo",
    "court": "tribunal",
    "jurisdiction": "jurisdição",
    "distribution_date": "data de distribuição",
    "response_deadline": "prazo de resposta",
    "responsible": "responsável",
    "judge_name": "nome do juiz",
    "case_value": "valor da causa",
    "sentence_date": "data da sentença",
    "priority": "prioridade",
    "theme": "tema",
    "subthemes": {
      "Contratos": ["subtema1", "subtema2"],
      "Danos Morais": ["subtema1", "subtema2"],
      "Responsabilidade Civil": ["subtema1", "subtema2"],
      "Tutela Antecipada": ["subtema1", "subtema2"],
      "Gratuidade de Justiça": ["subtema1", "subtema2"]
    }
  },
  "summary": {
    "total_pages_processed": 94,
    "pages_with_errors": 0,
    "pages_with_images": 22,
    "summary_all": "resumo completo",
    "structured_summary": {
      "parties": "partes envolvidas",
      "object": "objeto do processo",
      "decision": "decisão",
      "requests": "pedidos",
      "next_steps_deadlines": "próximos passos e prazos",
      "legal_basis": "base legal"
    },
    "controversial_points": [
      "ponto controverso 1",
      "ponto controverso 2"
    ]
  }
}
```
