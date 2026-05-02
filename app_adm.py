import streamlit as st
import datetime

# 1. Configuração e Identidade Visual
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

# 2. Inicialização do Banco de Dados Provisório (Memória do Sistema)
# Agora usamos dicionários para salvar TODOS os dados, não apenas os nomes.
if 'motos_db' not in st.session_state:
    st.session_state.motos_db = {}
if 'clientes_db' not in st.session_state:
    st.session_state.clientes_db = {}

# 3. Menu Fixo
st.sidebar.title("Menu Principal")
escolha = st.sidebar.radio("Selecione o módulo:", [
    "Cadastro de Cliente", 
    "Cadastro de Moto", 
    "Relatório de Clientes", 
    "Manutenção de Motos"
])
st.divider()

# --- MÓDULO 1: CADASTRO DE MOTO (Colocado antes para alimentar o cliente) ---
if escolha == "Cadastro de Moto":
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
        col8, col9, col10 = st.columns(3)
        km_inicial = col8.number_input("Quilometragem Inicial", min_value=0, step=1)
        # Campo de licenciamento adicionado (com limite amplo de data)
        licenciamento = col9.date_input("Último Licenciamento", min_value=datetime.date(2000, 1, 1), max_value=datetime.date(2100, 12, 31))
        status = col10.text_input("Status Atual", value="Disponível", disabled=True) 
        
        if st.form_submit_button("Cadastrar Moto"):
            chave_moto = f"{modelo} - {placa}"
            # Salvando todos os dados da moto na memória
            st.session_state.motos_db[chave_moto] = {
                "placa": placa, "chassi": chassi, "renavam": renavam,
                "marca": marca, "modelo": modelo, "ano": ano, "cor": cor,
                "km_inicial": km_inicial, "licenciamento": licenciamento, "status": status
            }
            st.success(f"Moto {chave_moto} cadastrada com sucesso e disponível para locação!")

# --- MÓDULO 2: CADASTRO DE CLIENTE ---
elif escolha == "Cadastro de Cliente":
    st.title("Cadastro de Novo Cliente")
    
    # Criando os limites de data exigidos
    data_minima_nasc = datetime.date(1920, 1, 1) # Permite clientes centenários
    data_maxima_cnh = datetime.date(2100, 12, 31) # Permite validade até o ano 2100
    
    with st.form("form_novo_cliente"):
        st.subheader("Dados Pessoais")
        col1, col2, col3, col4 = st.columns(4)
        nome = col1.text_input("Nome Completo")
        cpf = col2.text_input("CPF")
        rg = col3.text_input("RG")
        # Aplicando a data retroativa
        data_nasc = col4.date_input("Data de Nascimento", min_value=data_minima_nasc, max_value=datetime.date.today(), value=datetime.date(1990, 1, 1))
        
        st.subheader("Habilitação")
        col5, col6, col7 = st.columns(3)
        cnh = col5.text_input("Número da CNH")
        categoria_cnh = col6.selectbox("Categoria", ["A", "AB", "AC", "AD", "AE"])
        # Aplicando a data futura ampla
        validade_cnh = col7.date_input("Validade da CNH", min_value=datetime.date.today(), max_value=data_maxima_cnh)
        
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
        
        lista_motos = ["Nenhuma moto cadastrada"] if len(st.session_state.motos_db) == 0 else list(st.session_state.motos_db.keys())
        moto_escolhida = col17.selectbox("Modelo da Moto", lista_motos)
        
        col18, col19, col20 = st.columns(3)
        valor_semanal = col18.number_input("Valor Financeiro (Semanal em R$)", min_value=0.0, step=10.0)
        prazo_meses = col19.number_input("Prazo do Contrato (Meses)", min_value=1, step=1)
        caucao = col20.number_input("Caução/Franquia de Retirada (R$)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Salvar Cadastro de Cliente"):
            if moto_escolhida == "Nenhuma moto cadastrada":
                st.error("Cadastre uma moto primeiro antes de vincular a um cliente.")
            else:
                # Salvando todos os dados do cliente e vinculando à moto
                st.session_state.clientes_db[nome] = {
                    "cpf": cpf, "rg": rg, "data_nasc": data_nasc,
                    "cnh": cnh, "categoria": categoria_cnh, "validade_cnh": validade_cnh,
                    "telefone": telefone, "email": email, "emergencia": emergencia,
                    "rua": rua, "numero": numero, "bairro": bairro, "cep": cep, "cidade": cidade,
                    "modalidade": modalidade, "moto": moto_escolhida, "valor": valor_semanal,
                    "prazo": prazo_meses, "caucao": caucao
                }
                # Atualiza o status da moto para "Locada"
                st.session_state.motos_db[moto_escolhida]["status"] = f"Locada para {nome}"
                st.success(f"Cliente {nome} cadastrado com sucesso!")

# --- MÓDULO 3: RELATÓRIO DE CLIENTES ---
elif escolha == "Relatório de Clientes":
    st.title("Relatório Geral de Clientes")
    
    lista_clientes = list(st.session_state.clientes_db.keys())
    if len(lista_clientes) == 0:
        st.warning("Nenhum cliente cadastrado ainda. Vá em 'Cadastro de Cliente'.")
    else:
        cliente_selecionado = st.selectbox("Buscar Cliente", ["Selecione..."] + lista_clientes)
        
        if cliente_selecionado != "Selecione...":
            dados_cli = st.session_state.clientes_db[cliente_selecionado]
            st.subheader(f"Ficha Completa: {cliente_selecionado}")
            
            aba_info_cliente, aba_info_moto = st.tabs(["👤 Informações do Cliente", "🏍️ Moto e Manutenções"])
            
            with aba_info_cliente:
                st.info("Para editar, altere os valores nos campos abaixo e clique em Salvar Alterações.")
                col1, col2, col3 = st.columns(3)
                edit_nome = col1.text_input("Nome Completo", value=cliente_selecionado)
                edit_cpf = col2.text_input("CPF", value=dados_cli["cpf"])
                edit_rg = col3.text_input("RG", value=dados_cli["rg"])
                
                col4, col5, col6 = st.columns(3)
                edit_tel = col4.text_input("Telefone", value=dados_cli["telefone"])
                edit_email = col5.text_input("E-mail", value=dados_cli["email"])
                edit_emergencia = col6.text_input("Emergência", value=dados_cli["emergencia"])
                
                if st.button("Salvar Alterações do Cliente"):
                    st.success("Dados do cliente atualizados com sucesso! (Função visual no protótipo)")
                    
            with aba_info_moto:
                # 1. Trazendo todas as informações cadastradas da Moto
                moto_do_cliente = dados_cli["moto"]
                st.subheader("Dados da Motocicleta Locada")
                
                if moto_do_cliente in st.session_state.motos_db:
                    dados_moto = st.session_state.motos_db[moto_do_cliente]
                    col_m1, col_m2, col_m3 = st.columns(3)
                    edit_placa = col_m1.text_input("Placa", value=dados_moto["placa"])
                    edit_renavam = col_m2.text_input("Renavam", value=dados_moto["renavam"])
                    edit_chassi = col_m3.text_input("Chassi", value=dados_moto["chassi"])
                    
                    col_m4, col_m5, col_m6 = st.columns(3)
                    edit_marca = col_m4.text_input("Marca/Modelo", value=f"{dados_moto['marca']} - {dados_moto['modelo']}")
                    edit_licenca = col_m5.date_input("Último Licenciamento", value=dados_moto["licenciamento"], key="edit_licenca")
                    edit_km = col_m6.number_input("KM Inicial do Contrato", value=dados_moto["km_inicial"], key="edit_km")
                    
                    if st.button("Salvar Alterações da Moto"):
                        st.success("Dados da moto atualizados!")
                else:
                    st.error("Dados detalhados da moto não encontrados.")
                
                st.divider()
                
                # 2. Histórico e Visualização das Manutenções
                st.subheader("Histórico de Manutenções da Moto")
                st.write("Acompanhamento conforme envio do locatário:")
                
                # Exibição estruturada do histórico
                with st.expander("Manutenção: Troca de Óleo e Filtro (Realizada em 20/04/2026)"):
                    st.write("**Tipo:** Óleo e Filtro de Óleo")
                    st.write("**Status:** Aprovada")
                    
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        st.write("**Foto do Hodômetro (KM no momento da troca):**")
                        st.image("https://via.placeholder.com/300x200.png?text=Painel:+1.000+km", use_column_width=True)
                    with col_v2:
                        st.write("**Vídeo Comprobatório (Escoamento e Troca):**")
                        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                
                with st.expander("Manutenção: Pastilha de Freio (Realizada em 15/03/2026)"):
                    st.write("**Tipo:** Pastilha de Freio")
                    st.write("**Estabelecimento:** Oficina Credenciada da Locadora")
                    st.write("**Foto do Hodômetro:** 5.050 km")
                    st.info("Serviço validado pelo fornecedor indicado.")

# --- MÓDULO 4: MANUTENÇÃO DE MOTOS ---
elif escolha == "Manutenção de Motos":
    st.title("Gestão e Regras de Manutenções")
    
    st.subheader("Vida Útil Estimada e Regras do App")
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
