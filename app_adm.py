import streamlit as st

# 1. Configuração da página e Identidade Visual
# DEVE ser a primeira linha do código
st.set_page_config(page_title="Sistema de Gestão e Locação", layout="wide")

# Aplicando a identidade visual (Azul Marinho e Branco) na barra lateral
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

# 2. O Menu Único e Fixo na Barra Lateral
st.sidebar.title("Menu Principal")

opcoes_menu = [
    "Dashboard",
    "Gerar Intinerário", 
    "Despesa em Lote", 
    "Motos: Inadimplência e Bloqueio",
    "Motos: Validação de Vídeos",
    "Motos: Cadastros"
]

# O comando st.radio cria a lista fixa, eliminando o menu suspenso
escolha = st.sidebar.radio("Selecione o módulo:", opcoes_menu)

st.divider() # Linha visual para separar o topo

# 3. Roteamento das Telas (A lógica de cada menu)

if escolha == "Dashboard":
    st.title("Dashboard Principal")
    st.write("Aqui ficarão os gráficos e o resumo financeiro geral do seu negócio.")
    # Cole aqui a lógica original do seu Dashboard, se houver

elif escolha == "Gerar Intinerário":
    st.title("Gerar Intinerário")
    st.write("Módulo de organização de rotas e intinerários da equipe.")
    # Cole aqui a lógica original do seu Intinerário

elif escolha == "Despesa em Lote":
    st.title("Lançamento de Despesa em Lote")
    
    # Campo com digitação manual e autocompletar para não engessar a operação
    fornecedores_salvos = ["Fornecedor A", "Distribuidora Central", "Serviços Gerais Ltda"]
    
    col1, col2 = st.columns(2)
    busca_forn = col1.selectbox("Buscar fornecedor (Autocompletar)", [""] + fornecedores_salvos)
    novo_forn = col2.text_input("Ou digite manualmente um novo fornecedor")
    
    fornecedor_final = novo_forn if novo_forn else busca_forn
    
    valor = st.number_input("Valor Total (R$)", min_value=0.0)
    
    if st.button("Lançar Despesa"):
        st.success(f"Despesa de R$ {valor} para o fornecedor '{fornecedor_final}' registrada com sucesso!")
        # Cole aqui o restante da sua lógica original de Despesa em Lote

elif escolha == "Motos: Inadimplência e Bloqueio":
    st.title("Controle de Pagamentos Semanais")
    
    # Simulação de painel de alerta
    st.error("Atenção: Locatário João Silva (Placa ABC-1234) está com pagamento atrasado.")
    
    if st.button("Acionar Bloqueio da Moto (ABC-1234)"):
        st.success("Sinal de bloqueio de ignição enviado ao rastreador com sucesso!")

elif escolha == "Motos: Validação de Vídeos":
    st.title("Auditoria de Manutenção (Óleo e Filtro)")
    
    st.write("**Vídeo enviado por:** João Silva (Placa ABC-1234)")
    st.write("**Data do envio:** Hoje")
    
    # Exemplo visual de onde o vídeo do locatário aparecerá
    st.video("https://www.w3schools.com/html/mov_bbb.mp4") 
    
    col1, col2 = st.columns(2)
    if col1.button("✅ Aprovar Manutenção"):
        st.success("Manutenção aprovada. O relógio de quilometragem da peça foi zerado.")
    
    if col2.button("❌ Reprovar (Exigir novo vídeo)"):
        st.error("Notificação enviada ao locatário. Ele deverá enviar um novo vídeo demonstrando a troca.")

elif escolha == "Motos: Cadastros":
    st.title("Gestão de Frota e Clientes")
    
    # As abas organizam a tela sem precisar criar novos menus laterais
    aba_clientes, aba_motos, aba_fornecedores, aba_regras = st.tabs([
        "👤 Locatários", "🏍️ Frota", "🛠️ Oficinas", "⚙️ Regras"
    ])
    
    with aba_clientes:
        st.subheader("Cadastro de Locatário")
        with st.form("form_cliente"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo")
            cpf = col2.text_input("CPF")
            
            col3, col4 = st.columns(2)
            cnh = col3.text_input("Número da CNH")
            validade_cnh = col4.date_input("Validade da CNH")
            
            modalidade = st.selectbox("Modalidade", ["Com Repasse (Transferência)", "Sem Repasse (Devolução)"])
            
            if st.form_submit_button("Salvar Locatário"):
                st.success("Locatário cadastrado e pronto para assinatura do contrato.")

    with aba_motos:
        st.subheader("Cadastro de Motocicleta")
        with st.form("form_moto"):
            col1, col2 = st.columns(2)
            placa = col1.text_input("Placa")
            modelo = col2.text_input("Modelo e Ano")
            km_inicial = st.number_input("Quilometragem Inicial", min_value=0, step=1)
            
            if st.form_submit_button("Cadastrar Moto"):
                st.success("Moto adicionada à frota e disponível para locação.")

    with aba_fornecedores:
        st.subheader("Oficinas Parceiras")
        st.info("Utilize a busca ou cadastre digitando um novo nome no campo ao lado.")
        
        oficinas_existentes = ["Moto Peças Central", "Borracharia Express", "Speed Motos"]
        
        col1, col2 = st.columns(2)
        busca_oficina = col1.selectbox("Buscar Oficina (Autocompletar)", [""] + oficinas_existentes)
        nova_oficina = col2.text_input("Ou digite uma Nova Oficina")
        
        oficina_final = nova_oficina if nova_oficina else busca_oficina
        
        especialidade = st.multiselect("Serviços Realizados", ["Óleo", "Pneus", "Relação/Corrente", "Freios"])
        
        if st.button("Registrar Oficina"):
            st.success(f"Oficina '{oficina_final}' autorizada no sistema!")

    with aba_regras:
        st.subheader("Vida Útil das Peças (Em KM)")
        with st.form("form_regras"):
            st.write("Altere os valores padrão se necessário:")
            st.number_input("Troca de Óleo", value=1000)
            st.number_input("Filtro de Óleo", value=2000)
            st.number_input("Troca de Pneu", value=12000)
            st.number_input("Corrente/Relação", value=15000)
            st.number_input("Pastilha de Freio", value=5000)
            
            if st.form_submit_button("Salvar Regras da Frota"):
                st.success("As barras de progresso do aplicativo dos locatários foram atualizadas.")
