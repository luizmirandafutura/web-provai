import streamlit as st
import json
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

# Definição dos modelos Pydantic para validação dos dados
class FileInfo(BaseModel):
    """Informações do arquivo processado"""
    file_name: str
    file_type: str
    total_pages: int

class SubThemes(BaseModel):
    """Subtemas do processo"""
    Contratos: List[str] = []
    Danos_Morais: List[str] = Field([], alias="Danos Morais")
    Responsabilidade_Civil: List[str] = Field([], alias="Responsabilidade Civil")
    Locacao: List[str] = Field([], alias="Locação")
    Arbitragem: List[str] = Field([], alias="Arbitragem")

class Metadata(BaseModel):
    """Metadados do processo judicial"""
    is_approved: Optional[bool] = None
    process_number: Optional[str] = None
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    distribution_date: Optional[str] = None
    response_deadline: Optional[str] = None
    responsible: Optional[str] = None
    judge_name: Optional[str] = None
    case_value: Optional[str] = None
    sentence_date: Optional[str] = None
    priority: Optional[str] = None
    theme: Optional[str] = None
    subthemes: SubThemes

class StructuredSummary(BaseModel):
    """Resumo estruturado do processo"""
    parties: str
    object: str
    decision: Optional[str] = None
    requests: str
    next_steps_deadlines: str
    legal_basis: str

class Summary(BaseModel):
    """Resumo completo do processo"""
    total_pages_processed: int
    pages_with_errors: int
    pages_with_images: int
    summary_all: str
    structured_summary: StructuredSummary
    controversial_points: List[str]

class PageResult(BaseModel):
    """Resultado da extração de uma página"""
    page_id: int
    file_name: str
    has_images: bool
    extracted_text: str
    extracted_image_text: Optional[str] = None
    summary: str

class ProcessoJudicial(BaseModel):
    """Modelo principal do processo judicial"""
    file: FileInfo
    results: List[PageResult]
    metadata: Metadata
    summary: Summary

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Exemplos da ProvAI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado para estilização
css = """
<style>
    /* Cores e Tema */
    :root {
        --main-color: #304080;
        --accent-color: #5060C0;
        --light-color: #E7ECFF;
        --dark-color: #21295C;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #E57373;
        --info-color: #64B5F6;
    }
    
    /* Estilo geral da página */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Cabeçalhos */
    h1 {
        color: var(--main-color);
        font-family: 'Georgia', serif;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
        margin-bottom: 1.5rem;
    }
    
    h2, h3, h4 {
        color: var(--dark-color);
        font-family: 'Georgia', serif;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Barra lateral */
    .sidebar .sidebar-content {
        background-color: var(--light-color);
    }
    
    /* Cards personalizados */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--main-color);
    }
    
    .card-header {
        color: var(--main-color);
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    
    /* Estilo para informações importantes */
    .destaque {
        background-color: var(--light-color);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Badges para status */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .badge-success {
        background-color: var(--success-color);
        color: white;
    }
    
    .badge-warning {
        background-color: var(--warning-color);
        color: white;
    }
    
    .badge-danger {
        background-color: var(--danger-color);
        color: white;
    }
    
    .badge-info {
        background-color: var(--info-color);
        color: white;
    }
    
    /* Estilização de tabelas */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden;
        border: none !important;
    }
    
    .dataframe thead th {
        background-color: var(--main-color) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: var(--light-color) !important;
    }
    
    /* Estilização de caixas de texto */
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px;
        border: 1px solid #DFE3E8;
    }
    
    /* Personalização de expandables */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--main-color);
    }
    
    /* Personalização dos botões principais */
    .stButton button {
        border-radius: 8px;
        background-color: var(--main-color);
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: var(--dark-color);
        box-shadow: 0 4px 8px rgba(33, 41, 92, 0.2);
    }
    
    /* Melhora seletores */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
    }
    
    /* Personaliza contadores e métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--main-color) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    
    /* Melhorias nos containers */
    div.stTabs [data-baseweb="tab-panel"] {
        padding: 1rem;
        border-radius: 0 0 10px 10px;
        border: 1px solid #E0E0E0;
        border-top: none;
    }
    
    div.stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    
    div.stTabs [role="tab"] {
        padding: 0.5rem 1rem;
        background-color: #F5F7FA;
        border-radius: 10px 10px 0 0;
        border: 1px solid #E0E0E0;
        border-bottom: none;
    }
    
    div.stTabs [aria-selected="true"] {
        background-color: white;
        border-bottom: 1px solid white;
        color: var(--main-color);
        font-weight: 600;
    }
    
    /* Estilo para ícones */
    .icon-text {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Personalização da barra de progresso */
    .stProgress .st-bo {
        background-color: var(--main-color);
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# HTML personalizado para criar cards elegantes
def card(title, content, icon=""):
    return f"""
    <div class="card">
        <div class="card-header">
            <div class="icon-text">
                {icon} {title}
            </div>
        </div>
        <div class="card-body">
            {content}
        </div>
    </div>
    """

# Função para criar badges de status
def badge(text, status):
    return f'<span class="badge badge-{status}">{text}</span>'

# Função para carregar o arquivo JSON
@st.cache_data
def carregar_json(caminho_arquivo):
    """Carrega e valida o arquivo JSON do processo"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        # Validar os dados usando o modelo Pydantic
        processo = ProcessoJudicial.model_validate(dados)
        return processo
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {str(e)}")
        return None

# Carregar os dados do processo
arquivo_json = "1016234-60.2025.8.26.0100_resultado.json"
processo = carregar_json(arquivo_json)

if processo:
    # Cabeçalho da aplicação com design aprimorado
    st.markdown('<h1>📊 Visualizador de Processos da ProvAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 2rem;">Ferramenta para análise e visualização de processos judiciais para avaliação</p>', unsafe_allow_html=True)
    
    # Menu lateral estilizado
    st.sidebar.markdown('<h2 style="color: #304080; border-bottom: 2px solid #5060C0; padding-bottom: 0.5rem;">Navegação</h2>', unsafe_allow_html=True)
    opcao = st.sidebar.radio(
        "Selecione uma seção:",
        ["Resumo do Processo", "Metadados", "Resultados por Página", "Pontos Controversos", "Análise Textual", "Conceitos dos Campos"],
    )
    
    # Exibição do número do processo
    if processo.metadata.process_number:
        numero_processo = processo.metadata.process_number
    else:
        nome_arquivo = processo.file.file_name
        numero_processo = nome_arquivo.split('.')[0]
    
    st.sidebar.markdown(f"""
    <div style="background-color: #E7ECFF; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <h3 style="color: #304080; margin: 0 0 0.5rem 0;">Processo</h3>
        <p style="font-size: 1.1rem; font-weight: 600; color: #21295C; margin: 0;">{numero_processo}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibição das informações conforme a opção selecionada
    if opcao == "Resumo do Processo":
        st.markdown('<h2>📝 Resumo do Processo</h2>', unsafe_allow_html=True)
        
        # Informações básicas com métricas estilizadas
        st.markdown('<div style="margin-bottom: 2rem;">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Total de Páginas", processo.file.total_pages)
        with col2:
            st.metric("🖼️ Páginas com Imagens", processo.summary.pages_with_images)
        with col3:
            st.metric("⚠️ Páginas com Erros", processo.summary.pages_with_errors)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Resumo estruturado em formato de cards
        st.markdown('<h3>Resumo Estruturado</h3>', unsafe_allow_html=True)
        
        # Criação de tabs para organizar o resumo estruturado
        tabs = st.tabs(["📋 Visão Geral", "📃 Detalhes", "⚖️ Aspectos Legais"])
        
        with tabs[0]:
            st.markdown(card(
                "Partes Envolvidas", 
                f'<div class="destaque">{processo.summary.structured_summary.parties}</div>',
                "👥"
            ), unsafe_allow_html=True)
            
            st.markdown(card(
                "Objeto do Processo", 
                f'<div class="destaque">{processo.summary.structured_summary.object}</div>',
                "🔎"
            ), unsafe_allow_html=True)
        
        with tabs[1]:
            if processo.summary.structured_summary.decision:
                st.markdown(card(
                    "Decisão", 
                    f'<div class="destaque">{processo.summary.structured_summary.decision}</div>',
                    "⚖️"
                ), unsafe_allow_html=True)
            
            st.markdown(card(
                "Pedidos", 
                f'<div class="destaque">{processo.summary.structured_summary.requests}</div>',
                "📝"
            ), unsafe_allow_html=True)
            
            st.markdown(card(
                "Próximos Passos/Prazos", 
                f'<div class="destaque">{processo.summary.structured_summary.next_steps_deadlines}</div>',
                "⏱️"
            ), unsafe_allow_html=True)
        
        with tabs[2]:
            st.markdown(card(
                "Base Legal", 
                f'<div class="destaque">{processo.summary.structured_summary.legal_basis}</div>',
                "📜"
            ), unsafe_allow_html=True)
        
        # Resumo completo
        st.markdown('<h3>Resumo Completo</h3>', unsafe_allow_html=True)
        with st.expander("Expandir para ver o resumo completo"):
            st.markdown(f'<div class="destaque" style="max-height: 400px; overflow-y: auto;">{processo.summary.summary_all}</div>', unsafe_allow_html=True)
    
    elif opcao == "Metadados":
        st.markdown('<h2>🔍 Metadados do Processo</h2>', unsafe_allow_html=True)
        
        # Seção de metadados gerais em formato de cards
        col1, col2 = st.columns(2)
        
        metadados_col1 = ""
        metadados_col2 = ""
        
        if processo.metadata.court:
            metadados_col1 += f'<p><strong>Tribunal:</strong> {processo.metadata.court}</p>'
        if processo.metadata.jurisdiction:
            metadados_col1 += f'<p><strong>Jurisdição:</strong> {processo.metadata.jurisdiction}</p>'
        if processo.metadata.distribution_date:
            metadados_col1 += f'<p><strong>Data de Distribuição:</strong> {processo.metadata.distribution_date}</p>'
        if processo.metadata.judge_name:
            metadados_col1 += f'<p><strong>Juiz(a):</strong> {processo.metadata.judge_name}</p>'
        if processo.metadata.response_deadline:
            metadados_col1 += f'<p><strong>Prazo de Resposta:</strong> {processo.metadata.response_deadline}</p>'
        if processo.metadata.priority:
            metadados_col1 += f'<p><strong>Prioridade:</strong> {processo.metadata.priority}</p>'
        
        if processo.metadata.responsible:
            metadados_col2 += f'<p><strong>Responsável:</strong> {processo.metadata.responsible}</p>'
        if processo.metadata.case_value:
            metadados_col2 += f'<p><strong>Valor da Causa:</strong> {processo.metadata.case_value}</p>'
        if processo.metadata.sentence_date:
            metadados_col2 += f'<p><strong>Data da Sentença:</strong> {processo.metadata.sentence_date}</p>'
        if processo.metadata.theme:
            metadados_col2 += f'<p><strong>Tema Principal:</strong> {processo.metadata.theme}</p>'
        if processo.metadata.is_approved is not None:
            status = "Aprovado" if processo.metadata.is_approved else "Não Aprovado"
            status_badge = badge(status, "success" if processo.metadata.is_approved else "danger")
            metadados_col2 += f'<p><strong>Status:</strong> {status_badge}</p>'
        
        with col1:
            st.markdown(card("Informações do Tribunal", metadados_col1, "🏛️"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(card("Informações do Caso", metadados_col2, "📋"), unsafe_allow_html=True)
        
        # Seção de subtemas com design aprimorado
        st.markdown('<h3>Subtemas</h3>', unsafe_allow_html=True)
        tabs = st.tabs(["📑 Contratos", "💰 Danos Morais", "⚖️ Responsabilidade Civil", "⏱️ Locação", "Arbitragem"])
        
        # Subtemas: Contratos
        with tabs[0]:
            if processo.metadata.subthemes.Contratos:
                items = "".join([f'<li>{item}</li>' for item in processo.metadata.subthemes.Contratos])
                st.markdown(f'<ul class="destaque">{items}</ul>', unsafe_allow_html=True)
            else:
                st.info("Nenhum subtema encontrado nesta categoria.")
        
        # Subtemas: Danos Morais
        with tabs[1]:
            if processo.metadata.subthemes.Danos_Morais:
                items = "".join([f'<li>{item}</li>' for item in processo.metadata.subthemes.Danos_Morais])
                st.markdown(f'<ul class="destaque">{items}</ul>', unsafe_allow_html=True)
            else:
                st.info("Nenhum subtema encontrado nesta categoria.")
        
        # Subtemas: Responsabilidade Civil
        with tabs[2]:
            if processo.metadata.subthemes.Responsabilidade_Civil:
                items = "".join([f'<li>{item}</li>' for item in processo.metadata.subthemes.Responsabilidade_Civil])
                st.markdown(f'<ul class="destaque">{items}</ul>', unsafe_allow_html=True)
            else:
                st.info("Nenhum subtema encontrado nesta categoria.")
        
        # Subtemas: Locação
        with tabs[3]:
            if processo.metadata.subthemes.Locacao:
                items = "".join([f'<li>{item}</li>' for item in processo.metadata.subthemes.Locacao])
                st.markdown(f'<ul class="destaque">{items}</ul>', unsafe_allow_html=True)
            else:
                st.info("Nenhum subtema encontrado nesta categoria.")
        
        # Subtemas: Arbitragem
        with tabs[4]:
            if processo.metadata.subthemes.Arbitragem:
                items = "".join([f'<li>{item}</li>' for item in processo.metadata.subthemes.Arbitragem])
                st.markdown(f'<ul class="destaque">{items}</ul>', unsafe_allow_html=True)
            else:
                st.info("Nenhum subtema encontrado nesta categoria.")
    
    elif opcao == "Resultados por Página":
        st.markdown('<h2>📄 Resultados por Página</h2>', unsafe_allow_html=True)
        
        # Seleção de página estilizada
        pagina_selecionada = st.selectbox(
            "Selecione uma página:",
            range(1, processo.file.total_pages + 1),
            format_func=lambda x: f"Página {x}"
        )
        
        # Buscar a página selecionada nos resultados
        pagina = None
        for result in processo.results:
            if result.page_id == pagina_selecionada:
                pagina = result
                break
        
        # Exibir os detalhes da página com estilo melhorado
        if pagina:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f'<h3>Conteúdo da Página {pagina.page_id}</h3>', unsafe_allow_html=True)
                
                # Tabs para texto extraído e texto de imagem
                tabs = st.tabs(["📝 Texto", "🖼️ Texto de Imagem (se houver)"])
                
                with tabs[0]:
                    st.text_area("Texto Extraído", pagina.extracted_text, height=400)
                
                with tabs[1]:
                    if pagina.has_images and pagina.extracted_image_text:
                        st.text_area("Texto Extraído de Imagens", pagina.extracted_image_text, height=400)
                    else:
                        st.info("Esta página não contém imagens ou texto extraído de imagens.")
            
            with col2:
                # Informações da página usando componentes nativos do Streamlit
                st.markdown("### ℹ️ Informações da Página")
                st.markdown(f"**Nome do Arquivo:** {pagina.file_name}")
                st.markdown(f"**Contém Imagens:** {'Sim' if pagina.has_images else 'Não'}")
                
                # Linha de separação
                st.markdown("---")
                
                # Resumo da página 
                st.markdown("### 📝 Resumo da Página")
                st.markdown(f"{pagina.summary}")
        else:
            st.error(f"Página {pagina_selecionada} não encontrada nos resultados.")
    
    elif opcao == "Pontos Controversos":
        st.markdown('<h2>⚠️ Pontos Controversos</h2>', unsafe_allow_html=True)
        
        # Estilização dos pontos controversos
        for i, ponto in enumerate(processo.summary.controversial_points, 1):
            st.markdown(card(
                f"Ponto {i}", 
                f'<div class="destaque">{ponto}</div>',
                "⚠️"
            ), unsafe_allow_html=True)
    
    elif opcao == "Análise Textual":
        st.markdown('<h2>📊 Análise Textual</h2>', unsafe_allow_html=True)
        
        # Análise de palavras-chave com estilização aprimorada
        st.markdown('<h3>Palavras-chave por categoria</h3>', unsafe_allow_html=True)
        
        # Coletar todas as palavras-chave de todos os subtemas
        palavras_chave = []
        categorias = []
        
        for item in processo.metadata.subthemes.Contratos:
            palavras_chave.append(item)
            categorias.append("Contratos")
        
        for item in processo.metadata.subthemes.Danos_Morais:
            palavras_chave.append(item)
            categorias.append("Danos Morais")
        
        for item in processo.metadata.subthemes.Responsabilidade_Civil:
            palavras_chave.append(item)
            categorias.append("Responsabilidade Civil")
        
        for item in processo.metadata.subthemes.Locacao:
            palavras_chave.append(item)
            categorias.append("Locação")
        
        for item in processo.metadata.subthemes.Arbitragem:
            palavras_chave.append(item)
            categorias.append("Arbitragem")
        
        # Criar um DataFrame com as palavras-chave
        if palavras_chave:
            df = pd.DataFrame({
                "Palavra-chave": palavras_chave,
                "Categoria": categorias
            })
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhuma palavra-chave encontrada nos subtemas.")
        
        # Análise da Base Legal com estilização
        st.markdown('<h3>Base Legal</h3>', unsafe_allow_html=True)
        base_legal = processo.summary.structured_summary.legal_basis
        
        if base_legal:
            leis = base_legal.split(", ")
            lei_html = ""
            for lei in leis:
                lei_html += f'<li>{lei.strip()}</li>'
            
            st.markdown(f'<ul class="destaque">{lei_html}</ul>', unsafe_allow_html=True)
        else:
            st.info("Nenhuma base legal especificada.")
    
    elif opcao == "Conceitos dos Campos":
        st.markdown('<h2>📘 Conceitos dos Campos</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 1.1rem; margin-bottom: 2rem;">Explicação detalhada sobre o significado e importância de cada campo do esquema JSON.</p>', unsafe_allow_html=True)
        
        # Seção File
        with st.expander("📁 Seção FILE", expanded=False):
            st.markdown("""
            ### Arquivo Original
            Esta seção contém informações básicas sobre o arquivo original processado.
            
            | Campo | Conceito |
            |-------|----------|
            | `file_name` | Nome do arquivo original submetido para análise. Geralmente contém o número do processo como identificador. |
            | `file_type` | Formato do arquivo original, como PDF, DOCX, JPG. Importante para determinar o método de extração adequado. |
            | `total_pages` | Quantidade total de páginas do documento, utilizado para controle de processamento e verificação de integridade. |
            """)
        
        # Seção Results
        with st.expander("📊 Seção RESULTS", expanded=False):
            st.markdown("""
            ### Resultados por Página
            Lista de resultados do processamento de cada página individual do documento.
            
            | Campo | Conceito |
            |-------|----------|
            | `page_id` | Identificador sequencial único para cada página, facilitando referências e organização dos dados. |
            | `file_name` | Nome específico do arquivo da página atual, geralmente o nome original acrescido do número da página. |
            | `has_images` | Indicador booleano que sinaliza a presença de elementos visuais como carimbos, assinaturas ou imagens na página. |
            | `extracted_text` | Conteúdo textual extraído diretamente da página usando tecnologias de OCR (Optical Character Recognition). Representa o texto principal do documento. |
            | `extracted_image_text` | Texto obtido especificamente de elementos visuais na página através de OCR especializado. Pode conter informações cruciais como assinaturas, carimbos oficiais ou anotações manuscritas. |
            | `summary` | Resumo conciso do conteúdo principal da página, facilitando a navegação rápida pelo documento sem necessidade de ler o texto completo. |
            """)
        
        # Seção Metadata
        with st.expander("🏷️ Seção METADATA", expanded=False):
            st.markdown("""
            ### Metadados do Processo
            Contém metadados estruturados e dados críticos extraídos do documento judicial.
            
            | Campo | Conceito |
            |-------|----------|
            | `is_approved` | Indicador de validação que confirma se os campos obrigatórios (número do processo, tribunal e jurisdição) foram extraídos com sucesso. |
            | `process_number` | Identificador oficial único do processo judicial no formato padronizado do CNJ (ex: NNNNNNN-DD.AAAA.J.TR.OOOO). Campo crítico para rastreamento e referência. |
            | `court` | Tribunal responsável pelo julgamento do processo. Determina a competência jurisdicional e as regras procedimentais aplicáveis. |
            | `jurisdiction` | Área geográfica ou especialidade jurídica sob a qual o caso está sendo julgado. Importante para determinar precedentes aplicáveis. |
            | `distribution_date` | Data em que o processo foi distribuído a um juiz ou vara específica. Marco inicial do prazo processual. |
            | `response_deadline` | Data limite para apresentação de resposta ou manifestação. Crucial para controle de prazos processuais e evitar preclusão. |
            | `responsible` | Advogado, procurador ou parte responsável pelo acompanhamento do processo. Essencial para atribuição interna de responsabilidades. |
            | `judge_name` | Nome do magistrado responsável pelo julgamento. Relevante para análise de tendências decisórias e possíveis impedimentos. |
            | `case_value` | Valor monetário atribuído à causa. Determina aspectos como custas processuais, competência de juizados e alçada recursal. |
            | `sentence_date` | Data em que foi proferida a sentença ou decisão principal. Marco importante para contagem de prazos recursais. |
            | `theme` | Categoria jurídica principal do processo (Civil, Criminal, Trabalhista, etc). Facilita a classificação e agrupamento temático. |
            | `subthemes` | Objeto contendo subcategorias temáticas com palavras-chave relacionadas. Permite classificação mais granular e específica do conteúdo. |
            | `priority` | Nível de prioridade de tramitação do processo. Identifica casos com tramitação prioritária por lei (idosos, doenças graves, etc). |
            | `related_cases` | Lista de processos relacionados ou conexos. Importante para análise contextual e estratégica do litígio. |
            """)
        
        # Seção Summary
        with st.expander("📝 Seção SUMMARY", expanded=False):
            st.markdown("""
            ### Resumo Consolidado
            Contém resumos e análises consolidadas do documento processado.
            
            | Campo | Conceito |
            |-------|----------|
            | `total_pages_processed` | Quantidade de páginas efetivamente processadas com sucesso. Utilizado para verificação de integridade do processamento. |
            | `pages_with_errors` | Número de páginas que apresentaram problemas durante o processamento. Útil para identificar necessidade de revisão manual. |
            | `pages_with_images` | Contagem de páginas que contêm elementos visuais. Indica complexidade do documento e potencial necessidade de análise especializada. |
            | `summary_all` | Resumo abrangente de todo o conteúdo do documento. Fornece visão geral e contextualização do caso em linguagem natural. |
            """)
        
        # Seção Structured Summary
        with st.expander("📋 Seção STRUCTURED_SUMMARY", expanded=False):
            st.markdown("""
            ### Resumo Estruturado
            Esta subseção organiza o resumo em categorias específicas para facilitar a compreensão rápida do caso.
            
            | Campo | Conceito |
            |-------|----------|
            | `parties` | Identificação completa das partes envolvidas no processo (autores, réus, terceiros interessados). Crucial para análise de conflitos de interesse. |
            | `object` | Descrição concisa do objeto da ação ou propósito principal do processo. Resume "sobre o que trata" o caso judicial. |
            | `decision` | Resumo das principais decisões ou eventos processuais ocorridos. Fornece histórico decisório resumido e atual status processual. |
            | `requests` | Compilação dos pedidos formulados pelas partes. Essencial para entender o que está sendo pleiteado e os riscos envolvidos. |
            | `next_steps_deadlines` | Indicação dos próximos atos processuais esperados e seus respectivos prazos. Fundamental para planejamento estratégico e controle de agenda. |
            | `legal_basis` | Resumo dos fundamentos legais e jurisprudência citados no documento. Identifica as bases normativas relevantes para o caso. |
            """)
        
        # Pontos Controversos
        with st.expander("⚠️ Campo CONTROVERSIAL_POINTS", expanded=False):
            st.markdown("""
            ### Pontos Controversos
            
            | Campo | Conceito |
            |-------|----------|
            | `controversial_points` | Lista de questões controversas ou pontos críticos identificados que podem impactar significativamente o resultado do caso. Orienta a análise de riscos e a estratégia processual. |
            """)
            
        # Temas e Subtemas Jurídicos
        with st.expander("📚 Temas e Subtemas Jurídicos", expanded=False):
            st.markdown("""
            ### Temas Jurídicos
            Os temas representam as principais áreas do direito às quais um processo pode pertencer:
            
            - Cível
            - Trabalhista
            - Criminal
            - Tributário
            - Administrativo
            - Previdenciário
            - Constitucional
            - Empresarial
            - Consumidor
            - Família
            - Ambiental
            - Eleitoral
            - Militar
            - Internacional
            - Saúde
            - Imobiliário
            - Propriedade Intelectual
            - Bancário
            - Digital
            - Agrário
            """)
            
            st.markdown("### Subtemas por Área Jurídica")
            
            # Usando tabs para mostrar subtemas em vez de expanders aninhados
            subtemas_tabs = st.tabs([
                "Cível", "Trabalhista", "Criminal", "Tributário", "Administrativo", 
                "Previdenciário", "Constitucional", "Empresarial", "Consumidor", "Família",
                "Ambiental", "Eleitoral", "Militar", "Internacional", "Saúde", "Imobiliário",
                "Propriedade Intelectual", "Bancário", "Digital", "Agrário"
            ])
            
            # Cível
            with subtemas_tabs[0]:
                st.markdown("""
                **Subtemas da área Cível:**
                - Contratos
                - Responsabilidade Civil
                - Posse e Propriedade
                - Obrigações
                - Danos Morais
                - Danos Materiais
                - Indenização
                - Locação
                - Usucapião
                - Condomínio
                - Servidão
                - Penhor
                - Hipoteca
                - Caução
                - Arbitragem
                - Mediação
                - Cumprimento de Sentença
                - Ação de Cobrança
                - Ação Monitória
                - Ação de Despejo
                - Reintegração de Posse
                - Interdito Proibitório
                - Ação de Nunciação de Obra Nova
                - Ação de Divisão de Terras
                - Ação de Demarcação
                """)
            
            # Trabalhista
            with subtemas_tabs[1]:
                st.markdown("""
                **Subtemas da área Trabalhista:**
                - Horas Extras
                - Rescisão Contratual
                - Acidente de Trabalho
                - Assédio Moral
                - Férias
                - Décimo Terceiro Salário
                - FGTS (Fundo de Garantia)
                - Insalubridade
                - Periculosidade
                - Estabilidade Provisória
                - Gestante
                - Aposentado
                - Dispensa Discriminatória
                - Jornada de Trabalho
                - Intervalo Intrajornada
                - Trabalho Infantil
                - Trabalho Escravo
                - Greve
                - Negociação Coletiva
                - Contrato de Experiência
                - Terceirização
                - Pejotização
                - Aviso Prévio
                - Reversão de Justa Causa
                - Dano Moral Coletivo
                """)
            
            # Criminal
            with subtemas_tabs[2]:
                st.markdown("""
                **Subtemas da área Criminal:**
                - Crimes contra a Pessoa
                - Crimes contra o Patrimônio
                - Crimes contra a Administração Pública
                - Tráfico de Drogas
                - Crimes Ambientais
                - Homicídio
                - Lesão Corporal
                - Estupro
                - Roubo
                - Furto
                - Extorsão
                - Apropriação Indébita
                - Estelionato
                - Receptação
                - Corrupção Ativa
                - Corrupção Passiva
                - Peculato
                - Prevaricação
                - Lavagem de Dinheiro
                - Organização Criminosa
                - Crimes Eleitorais
                - Crimes de Trânsito
                - Porte Ilegal de Arma
                - Falsidade Ideológica
                - Falsificação de Documento
                """)
            
            # Tributário
            with subtemas_tabs[3]:
                st.markdown("""
                **Subtemas da área Tributária:**
                - Impostos Federais
                - Impostos Estaduais
                - Impostos Municipais
                - Planejamento Tributário
                - Execução Fiscal
                - ICMS
                - IPI
                - ISS
                - IPTU
                - IPVA
                - IRPF (Imposto de Renda Pessoa Física)
                - IRPJ (Imposto de Renda Pessoa Jurídica)
                - Contribuições Previdenciárias
                - PIS/COFINS
                - Taxas Públicas
                - Multas Tributárias
                - Sonegação Fiscal
                - Auto de Infração
                - Compensação Tributária
                - Restituição de Tributos
                - Isenção Fiscal
                - Imunidade Tributária
                - Parcelamento de Débitos
                - Contencioso Administrativo
                - Contencioso Judicial
                """)
            
            # Administrativo
            with subtemas_tabs[4]:
                st.markdown("""
                **Subtemas da área Administrativa:**
                - Licitações
                - Atos Administrativos
                - Processo Administrativo
                - Improbidade Administrativa
                - Concessões Públicas
                - Permissões Públicas
                - Parcerias Público-Privadas (PPP)
                - Contratos Administrativos
                - Expropriação
                - Desapropriação
                - Serviços Públicos
                - Responsabilidade do Estado
                - Sanções Administrativas
                - Controle Interno
                - Controle Externo
                - Tribunal de Contas
                - Ato Normativo
                - Regulamentação
                - Consulta Pública
                - Audiência Pública
                - Intervenção Estatal
                - Revogação de Ato
                - Anulação de Ato
                - Concurso Público
                - Nomeação e Posse
                """)
            
            # Previdenciário
            with subtemas_tabs[5]:
                st.markdown("""
                **Subtemas da área Previdenciária:**
                - Aposentadoria por Idade
                - Aposentadoria por Tempo de Contribuição
                - Aposentadoria por Invalidez
                - Pensão por Morte
                - Auxílio-Doença
                - Benefício Assistencial (LOAS)
                - Revisão de Benefícios
                - Salário-Maternidade
                - Auxílio-Reclusão
                - Aposentadoria Especial
                - Contagem de Tempo de Serviço
                - Contribuições em Atraso
                - Desaposentação
                - Reforma da Previdência
                - Averbação de Tempo
                - Certidão de Tempo de Contribuição
                - Invalidez Permanente
                - Doença Ocupacional
                - Acidente de Trabalho
                - Revisão de Cálculo
                - Aposentadoria Rural
                - Benefício Negado
                - Processo Administrativo Previdenciário
                - Recurso ao INSS
                - Planejamento Previdenciário
                """)
            
            # Constitucional
            with subtemas_tabs[6]:
                st.markdown("""
                **Subtemas da área Constitucional:**
                - Direitos Fundamentais
                - Controle de Constitucionalidade
                - Ação Direta de Inconstitucionalidade (ADI)
                - Ação Declaratória de Constitucionalidade (ADC)
                - Habeas Data
                - Mandado de Injunção
                - Mandado de Segurança Individual
                - Mandado de Segurança Coletivo
                - Direito de Petição
                - Separação de Poderes
                - Estado de Defesa
                - Estado de Sítio
                - Intervenção Federal
                - Garantias Constitucionais
                - Princípios Constitucionais
                - Ação Popular
                - Direitos Sociais
                - Direitos Políticos
                - Direitos Individuais
                - Direitos Coletivos
                - Cláusulas Pétreas
                - Revisão Constitucional
                - Poder Constituinte
                - Tratados Internacionais
                - Supremacia Constitucional
                """)
            
            # Empresarial
            with subtemas_tabs[7]:
                st.markdown("""
                **Subtemas da área Empresarial:**
                - Falência
                - Recuperação Judicial
                - Recuperação Extrajudicial
                - Sociedades Anônimas
                - Sociedades Limitadas
                - Contratos Comerciais
                - Títulos de Crédito
                - Cheque
                - Nota Promissória
                - Duplicata
                - Propriedade Industrial
                - Concorrência Desleal
                - Dissolução de Sociedade
                - Fusão e Aquisição
                - Incorporação
                - Cisão Empresarial
                - Governança Corporativa
                - Responsabilidade dos Sócios
                - Contrato Social
                - Registro Empresarial
                - Planejamento Sucessório
                - Mediação Empresarial
                - Arbitragem Comercial
                - Dívidas Empresariais
                - Liquidação de Empresa
                """)
            
            # Consumidor
            with subtemas_tabs[8]:
                st.markdown("""
                **Subtemas da área do Consumidor:**
                - Garantia de Produto
                - Vício do Produto
                - Defeito do Produto
                - Propaganda Enganosa
                - Práticas Abusivas
                - Contrato de Adesão
                - Cláusulas Abusivas
                - Responsabilidade do Fornecedor
                - Dano Moral
                - Dano Material
                - Relações de Consumo
                - Recall
                - Serviços Públicos
                - Telefonia
                - Energia Elétrica
                - Planos de Saúde
                - Transporte
                - Compras Online
                - Atraso na Entrega
                - Cancelamento de Contrato
                - Cobrança Indevida
                - Inscrição indevida em Cadastro de Inadimplentes
                - Direito de Arrependimento
                - Oferta e Publicidade
                - Proteção Contratual
                """)
            
            # Família
            with subtemas_tabs[9]:
                st.markdown("""
                **Subtemas da área de Família:**
                - Divórcio
                - Guarda de Menores
                - Pensão Alimentícia
                - União Estável
                - Casamento
                - Inventário
                - Partilha de Bens
                - Regime de Bens
                - Adoção
                - Investigação de Paternidade
                - Alienação Parental
                - Interdição
                - Tutela
                - Curatela
                - Separação de Corpos
                - Mediação Familiar
                - Violência Doméstica
                - Planejamento Familiar
                - Reconhecimento de Filho
                - Alteração de Nome
                - Dissolução de União Estável
                - Testamento
                - Sucessão
                - Doação de Bens
                - Abandono Afetivo
                """)
            
            # Ambiental
            with subtemas_tabs[10]:
                st.markdown("""
                **Subtemas da área Ambiental:**
                - Desmatamento
                - Poluição
                - Licenciamento Ambiental
                - Áreas Protegidas
                - Crimes Ambientais
                - Dano Ambiental
                - Responsabilidade Ambiental
                - Recursos Hídricos
                - Gestão de Resíduos
                - Mudanças Climáticas
                - Zoneamento Ambiental
                - Unidades de Conservação
                - Multas Ambientais
                - Ação Civil Pública Ambiental
                - Recuperação de Área Degradada
                - Impacto Ambiental
                - Estudo de Impacto Ambiental (EIA)
                - Compensação Ambiental
                - Fauna e Flora
                - Pesca Ilegal
                - Mineração Ilegal
                - Sustentabilidade
                - Política Nacional do Meio Ambiente
                - Conflitos Fundiários
                - Direito das Águas
                """)
            
            # Eleitoral
            with subtemas_tabs[11]:
                st.markdown("""
                **Subtemas da área Eleitoral:**
                - Propaganda Eleitoral
                - Abuso de Poder Econômico
                - Abuso de Poder Político
                - Compra de Votos
                - Inelegibilidade
                - Registro de Candidatura
                - Impugnação de Mandato
                - Cassação de Mandato
                - Financiamento de Campanha
                - Prestação de Contas
                - Ficha Limpa
                - Crimes Eleitorais
                - Urna Eletrônica
                - Revisão de Eleitorado
                - Alistamento Eleitoral
                - Partidos Políticos
                - Coligações
                - Fidelidade Partidária
                - Horário Eleitoral
                - Pesquisas Eleitorais
                - Ação de Investigação Judicial Eleitoral
                - Recurso contra Diplomação
                - Sistema Eleitoral
                - Cotas de Gênero
                - Justiça Eleitoral
                """)
            
            # Militar
            with subtemas_tabs[12]:
                st.markdown("""
                **Subtemas da área Militar:**
                - Crimes Militares
                - Deserção
                - Insubordinação
                - Peculato Militar
                - Abuso de Autoridade
                - Processo Disciplinar
                - Reforma Militar
                - Pensão Militar
                - Promoção
                - Transferência
                - Licenciamento
                - Serviço Militar Obrigatório
                - Habeas Corpus Militar
                - Conselho de Justificação
                - Conselho de Disciplina
                - Aposentadoria Militar
                - Reserva Remunerada
                - Invalidez Militar
                - Hierarquia e Disciplina
                - Justiça Militar
                - Missões de Paz
                - Operações Militares
                - Regulamentos Disciplinares
                - Uniformes e Insígnias
                - Patrimônio Militar
                """)
            
            # Internacional
            with subtemas_tabs[13]:
                st.markdown("""
                **Subtemas da área Internacional:**
                - Tratados Internacionais
                - Direitos Humanos Internacionais
                - Comércio Internacional
                - Extradition
                - Asilo Político
                - Refugiados
                - Nacionalidade
                - Conflitos Armados
                - Direito do Mar
                - Tribunais Internacionais
                - Arbitragem Internacional
                - Investimento Estrangeiro
                - Cooperação Jurídica
                - Reconhecimento de Sentenças Estrangeiras
                - Imunidade Diplomática
                - Relações Diplomáticas
                - Organizações Internacionais
                - Sanções Internacionais
                - Direito Humanitário
                - Crimes Transnacionais
                - Contratos Internacionais
                - Conflitos de Jurisdição
                - Protocolos Internacionais
                - Mediação Internacional
                - Direito Aéreo Internacional
                """)
            
            # Saúde
            with subtemas_tabs[14]:
                st.markdown("""
                **Subtemas da área da Saúde:**
                - Plano de Saúde
                - Negativa de Cobertura
                - Tratamento Médico
                - Fornecimento de Medicamentos
                - Erro Médico
                - Responsabilidade Médica
                - Internação
                - Cirurgia
                - Saúde Pública
                - SUS (Sistema Único de Saúde)
                - Vigilância Sanitária
                - Regulação de Medicamentos
                - Vacinação
                - Doação de Órgãos
                - Transplante
                - Pesquisa Clínica
                - Direito à Vida
                - Direito à Saúde
                - Bioética
                - Saúde Mental
                - Epidemiologia
                - Controle de Doenças
                - Ações contra Hospitais
                - Ações contra Clínicas
                - Reajuste de Planos
                """)
            
            # Imobiliário
            with subtemas_tabs[15]:
                st.markdown("""
                **Subtemas da área de Imobiliário:**
                - Compra e Venda
                - Locação Residencial
                - Locação Comercial
                - Usucapião
                - Despejo
                - Reintegração de Posse
                - Condomínio
                - Incorporação Imobiliária
                - Loteamento
                - Regularização Fundiária
                - Hipoteca
                - Penhor Imobiliário
                - Distrato Imobiliário
                - Atraso na Entrega de Imóvel
                - Vícios de Construção
                - Imissão na Posse
                - Ação de Divisão
                - Ação de Demarcação
                - Servidão de Passagem
                - Direito de Vizinhança
                - Registro de Imóveis
                - Escritura Pública
                - Contrato de Promessa
                - Financiamento Imobiliário
                - Leilão de Imóveis
                """)

            with subtemas_tabs[16]:
                st.markdown("""
                **Subtemas da área de Propriedade Intelectual:**
                - Patentes
                - Marcas
                - Direitos Autorais
                - Desenhos Industriais
                - Software
                - Plágio
                - Contrafação
                - Licenciamento
                - Transferência de Tecnologia
                - Segredo Industrial
                - Registro de Marca
                - Registro de Patente
                - Inovação
                - Propriedade Industrial
                - Concorrência Desleal
                - Proteção de Dados Criativos
                - Domínio na Internet
                - Publicação de Obras
                - Direitos Morais
                - Direitos Patrimoniais
                - Exploração Comercial
                - Ações de Nulidade
                - Ações de Infrações
                - Mediação em PI
                - Arbitragem em PI
                """)

            with subtemas_tabs[17]:
                st.markdown("""
                **Subtemas da área de Bancário:**
                - Revisão de Contrato
                - Juros Abusivos
                - Cobrança Indevida
                - Financiamento
                - Empréstimo
                - Consórcio
                - Cheque Especial
                - Cartão de Crédito
                - Tarifas Bancárias
                - Execução de Dívida
                - Alienação Fiduciária
                - Leasing
                - Câmbio
                - Investimentos
                - Fundos de Investimento
                - Ações contra Bancos
                - Fraudes Bancárias
                - Sustação de Protesto
                - Renegociação de Dívida
                - Busca e Apreensão
                - Liquidação Extrajudicial
                - Responsabilidade Bancária
                - Seguros Bancários
                - Ações de Indenização
                - Regulação Bancária
                """)

            with subtemas_tabs[18]:
                st.markdown("""
                **Subtemas da área de Digital:**
                - Crimes Cibernéticos
                - Proteção de Dados
                - LGPD (Lei Geral de Proteção de Dados)
                - Privacidade Online
                - Contratos Digitais
                - Assinatura Eletrônica
                - Comércio Eletrônico
                - Fraudes Online
                - Hacking
                - Phishing
                - Difamação Online
                - Cyberbullying
                - Pornografia Infantil
                - Propriedade Intelectual Digital
                - Registro de Domínio
                - Remoção de Conteúdo
                - Responsabilidade de Provedores
                - Acesso Não Autorizado
                - Segurança da Informação
                - Certificação Digital
                - Blockchain
                - Criptomoedas
                - Direito ao Esquecimento
                - Monitoramento Digital
                - Regulação de Plataformas
                """)

            with subtemas_tabs[19]:
                st.markdown("""
                **Subtemas da área de Agrário:**
                - Posse de Terra
                - Propriedade Rural
                - Reforma Agrária
                - Usucapião Rural
                - Arrendamento Rural
                - Parceria Agrícola
                - Conflitos Fundiários
                - Desapropriação Rural
                - Zoneamento Agrícola
                - Regularização de Terras
                - Registro Rural
                - Financiamento Agrícola
                - Seguro Agrícola
                - Produção Agropecuária
                - Cooperativas Agrícolas
                - Trabalho Rural
                - Aposentadoria Rural
                - Exploração Sustentável
                - Danos Ambientais Rurais
                - Irrigação
                - Assentamentos Rurais
                - Demarcação de Terras
                - Terras Indígenas
                - Quilombolas
                - Política Agrária
                """)

else:
    st.error("Não foi possível carregar o arquivo JSON do processo.") 