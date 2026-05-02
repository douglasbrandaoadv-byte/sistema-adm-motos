import streamlit as st
import datetime

# 1. Configuração Inicial e Identidade Visual (Azul Marinho e Branco)
st.set_page_config(page_title="Sistema de Locação de Motos", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #000080;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    div[data-baseweb="radio"] > div {
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialização da "Memória" do Sistema (Para conectar Motos e Clientes)
if 'motos_cadastradas' not in st.session_state:
    st.session_state.motos_cadastradas = ["CG 160 Titan - ABC-1234"] # Moto de exemplo
if 'clientes_cadastrados' not in st.session_state:
    st.session_state.clientes_cadastrados = ["Douglas Brandão"] # Cliente de exemplo

# 3. Menu Lateral Fixo
st.sidebar.title("Menu Principal")
opcoes_menu = [
    "Cadastro de Cliente", 
    "Cadastro de Moto", 
    "Relatório de Clientes", 
    "Manutenção de Motos"
]
escolha = st.sidebar.radio("Selecione o módulo:", opcoes_menu)

st.divider()

# --- MÓDULO 1: CADASTRO DE CLIENTE ---
if escolha == "Cadastro de Cliente":
    st.title("Cadastro de Novo Cliente")
    
    with st.form("form_novo_cliente"):
        st.subheader("Dados Pessoais")
        col1, col2, col3, col4 = st.columns(4)
        nome = col1.text_input("Nome Completo")
        cpf = col2.text_input("CPF")
        rg = col3.text_input("RG")
        data_nasc = col4.date_input("Data de Nascimento")
        
        st.subheader("Habilitação")
        col5, col6, col7 = st.columns(3)
        cnh = col5.text_input("Número da CNH")
        categoria_cnh = col6.selectbox("Categoria", ["A", "AB", "AC", "AD", "AE"])
        validade_cnh = col7.date_input("Validade da CNH")
        
        st.subheader("Contato")
        col8, col9, col10 = st.columns(3)
        telefone = col8.text_input("Telefone/WhatsApp")
        email = col9.text_input("E-mail")
        emergencia = col10.text_input("Contato de Emergência (Nome e Tel)")
        
        st.subheader("Endereço")
        col11, col12, col13, col14, col15 = st.columns([2, 1, 1, 1, 2])
        rua = col11.text_input("Rua")
        numero = col12.text_input("Número")
        bairro = col13.text_input("Bairro")
        cep = col14.text_input("CEP")
        cidade = col15.text_input("Cidade")
        
        st.subheader("Anexos")
        foto_cnh = st.file_uploader("Foto da CNH", type=['png', 'jpg', 'jpeg', 'pdf'])
        foto_residencia = st.file_uploader("Comprovante de Residência", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        st.subheader("Detalhes do Contrato")
        col16, col17 = st.columns(2)
        modalidade = col16.selectbox("Modalidade do Contrato", ["Com Repasse do Bem (Transferência)", "Sem Repasse (Devolução)"])
        
        # Aqui o sistema puxa automaticamente as motos cadastradas
        moto_escolhida = col17.selectbox("Modelo da Moto", st.session_state.motos_cadastradas)
        
        col18, col19, col20 = st.columns(3)
        valor_semanal = col18.number_input("Valor Financeiro (Semanal em R$)", min_value=0.0, step=10.0)
        prazo_meses = col19.number_input("Prazo do Contrato (Meses)", min_value=1, step=1)
        caucao = col20.number_input("Caução/Franquia de Retirada (R$)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Salvar Cadastro de Cliente"):
            if nome not in st.session_state.clientes_cadastrados:
                st.session_state.clientes_cadastrados.append(nome)
            st.success(f"Cliente {nome} cadastrado e vinculado à moto {moto_escolhida} com sucesso!")

# --- MÓDULO 2: CADASTRO DE MOTO ---
elif escolha == "Cadastro de Moto":
    st.title("Cadastro de Nova Motocicleta")
    
    with st.form("form_nova_moto"):
        st.subheader("Identificação")
        col1, col2, col3 = st.columns(3)
        placa = col1.text_input("Placa (ex: ABC-1234)")
        chassi = col2.text_input("Chassi")
        renavam = col3.text_input("Renavam")
        
        st.subheader("Características")
        col4, col5, col6, col7 = st.columns(4)
        marca = col4.text_input("Marca")
        modelo = col5.text_input("Modelo")
        ano = col6.text_input("Ano de Fabricação")
        cor = col7.text_input("Cor")
        
        st.subheader("Situação e Controle")
        col8, col9 = st.columns(2)
        km_inicial = col8.number_input("Quilometragem Inicial", min_value=0, step=1)
        status = col9.text_input("Status Atual", value="Disponível", disabled=True) 
        # O campo disabled=True torna o status automático e não editável aqui
        
        if st.form_submit_button("Cadastrar Moto"):
            nova_moto_str = f"{modelo} - {placa}"
            if nova_moto_str not in st.session_state.motos_cadastradas:
                st.session_state.motos_cadastradas.append(nova_moto_str)
            st.success(f"Moto {nova_moto_str} cadastrada com sucesso e já disponível para locação!")

# --- MÓDULO 3: RELATÓRIO DE CLIENTES ---
elif escolha == "Relatório de Clientes":
    st.title("Relatório Geral de Clientes")
    st.write("Selecione um cliente na lista abaixo para visualizar e editar suas informações.")
    
    # Campo de busca/seleção de clientes
    cliente_selecionado = st.selectbox("Buscar Cliente", [""] + st.session_state.clientes_cadastrados)
    
    if cliente_selecionado:
        st.subheader(f"Ficha Completa: {cliente_selecionado}")
        
        # Criação das duas abas exigidas
        aba_info_cliente, aba_info_moto = st.tabs(["👤 Informações do Cliente", "🏍️ Informações da Moto e Manutenções"])
        
        with aba_info_cliente:
            st.info("Para editar, altere os valores nos campos abaixo e clique em Salvar Alterações.")
            col1, col2, col3 = st.columns(3)
            # Para simular edição, os campos já vêm preenchidos com o valor atual (value=...)
            edit_nome = col1.text_input("Nome Completo", value=cliente_selecionado, key="edit_nome")
            edit_cpf = col2.text_input("CPF", value="000.000.000-00", key="edit_cpf")
            edit_telefone = col3.text_input("Telefone", value="(00) 00000-0000", key="edit_tel")
            
            if st.button("Salvar Alterações do Cliente"):
                st.success("Dados do cliente atualizados com sucesso!")
                
        with aba_info_moto:
            st.info("Para editar os dados do contrato/moto, altere os valores e salve.")
            col1, col2 = st.columns(2)
            edit_moto_vinculada = col1.selectbox("Moto Locada Atual", st.session_state.motos_cadastradas, key="edit_moto")
            edit_valor = col2.number_input("Valor Semanal (R$)", value=250.0, key="edit_valor")
            
            if st.button("Salvar Alterações da Moto"):
                st.success("Dados do contrato atualizados com sucesso!")
            
            st.divider()
            st.subheader("Histórico de Manutenções desta Moto")
            # Exibição estática para simular o histórico
            st.write("✅ **10/04/2026:** Troca de Óleo e Filtro (1.000 km)")
            st.write("✅ **25/03/2026:** Troca de Pastilha de Freio (5.000 km)")

# --- MÓDULO 4: MANUTENÇÃO DE MOTOS ---
elif escolha == "Manutenção de Motos":
    st.title("Gestão e Auditoria de Manutenções")
    
    # Abas para organizar a tela de manutenção
    aba_auditoria, aba_regras = st.tabs(["📹 Auditoria de Vídeos (Óleo/Filtro)", "⚙️ Configurar Vida Útil (Regras)"])
    
    with aba_auditoria:
        st.subheader("Histórico de Manutenções Realizadas")
        st.write("Abaixo estão os registros e comprovações enviadas pelos clientes.")
        
        # Simulação de um registro de manutenção enviado
        with st.expander("Manutenção Recente: Douglas Brandão (CG 160 - ABC-1234) - Data: Hoje"):
            st.write("**Tipo de Serviço:** Troca de Óleo e Filtro de Óleo")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Foto do Hodômetro (KM):**")
                # Simulando uma foto
                st.image("https://via.placeholder.com/300x200.png?text=Foto+do+Painel+(1000+km)", use_column_width=True)
            
            with col2:
                st.write("**Vídeo da Troca (Óleo e Filtro):**")
                # Simulando o vídeo
                st.video("https://www.w3schools.com/html/mov_bbb.mp4")
            
            st.button("Aprovar Manutenção", key="aprovar_douglas")

    with aba_regras:
        st.subheader("Configuração de Vida Útil Estimada")
        st.write("Defina a quilometragem padrão para a troca de cada item. Essa regra alimentará a barra de progresso no aplicativo do locatário.")
        
        with st.form("form_vida_util"):
            col1, col2 = st.columns(2)
            regra_oleo = col1.number_input("Troca de Óleo (KM)", value=1000)
            regra_filtro = col2.number_input("Filtro de Óleo (KM)", value=1000)
            
            col3, col4 = st.columns(2)
            regra_freio = col3.number_input("Pastilha de Freio (KM)", value=5000)
            regra_pneu = col4.number_input("Pneu (KM)", value=10000)
            
            col5, col6 = st.columns(2)
            regra_embreagem = col5.number_input("Cabo de Embreagem (KM)", value=12000)
            regra_corrente = col6.number_input("Corrente/Relação (KM)", value=15000)
            
            if st.form_submit_button("Salvar Regras de Quilometragem"):
                st.success("Regras atualizadas! O aplicativo dos locatários já refletirá as novas metas.")
