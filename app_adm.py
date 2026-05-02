import streamlit as st

st.set_page_config(page_title="Painel ADM - Locadora", layout="wide")
st.title("Painel Administrativo da Locadora")

menu = ["Dashboard", "Inadimplência e Bloqueio", "Galeria de Validação (Vídeos)", "Cadastro"]
escolha = st.sidebar.selectbox("Menu de Navegação", menu)

if escolha == "Inadimplência e Bloqueio":
    st.subheader("Controle de Pagamentos Semanais")
    st.warning("Atenção: João Silva (Placa ABC-1234) está com pagamento atrasado.")
    
    if st.button("Acionar Bloqueio da Moto (ABC-1234)"):
        st.error("Sinal de bloqueio enviado ao rastreador com sucesso!")

elif escolha == "Galeria de Validação (Vídeos)":
    st.subheader("Auditoria de Troca de Óleo e Filtro")
    st.write("Vídeo enviado por: João Silva (Placa ABC-1234)")
    st.video("https://www.w3schools.com/html/mov_bbb.mp4") # Exemplo visual
    
    col1, col2 = st.columns(2)
    col1.button("Aprovar Manutenção")
    col2.button("Reprovar (Exigir novo vídeo)")

import streamlit as st

st.set_page_config(page_title="Painel ADM - Locadora", layout="wide")
st.title("Administração - Gestão de Frota e Clientes")

# Menu Lateral
menu = ["Inadimplência", "Validação de Manutenção", "Cadastros do Sistema"]
escolha = st.sidebar.selectbox("Navegação", menu)

if escolha == "Cadastros do Sistema":
    st.header("Módulo de Cadastros")
    
    # Criando abas para organizar a tela
    aba_clientes, aba_motos, aba_fornecedores, aba_regras = st.tabs([
        "👤 Locatários", "🏍️ Frota", "🛠️ Oficinas Parceiras", "⚙️ Regras de Manutenção"
    ])
    
    # --- ABA 1: LOCATÁRIOS ---
    with aba_clientes:
        st.subheader("Novo Locatário")
        with st.form("form_cliente"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo")
            cpf = col2.text_input("CPF (Apenas números)")
            
            col3, col4 = st.columns(2)
            cnh = col3.text_input("Número da CNH")
            validade_cnh = col4.date_input("Validade da CNH")
            
            modalidade = st.selectbox("Modalidade do Contrato", ["Com Repasse (Transferência)", "Sem Repasse (Devolução)"])
            
            # Botão de salvar
            salvar_cliente = st.form_submit_button("Salvar Locatário")
            if salvar_cliente:
                st.success(f"Locatário {nome} cadastrado com sucesso!")
                # Aqui o sistema enviará os dados para o Supabase (Banco de Dados)

    # --- ABA 2: MOTOS ---
    with aba_motos:
        st.subheader("Nova Moto na Frota")
        with st.form("form_moto"):
            col1, col2 = st.columns(2)
            placa = col1.text_input("Placa (ex: ABC-1234)")
            modelo = col2.text_input("Modelo e Ano (ex: CG 160 Titan 2024)")
            
            km_inicial = st.number_input("Quilometragem Inicial", min_value=0, step=1)
            
            salvar_moto = st.form_submit_button("Cadastrar Moto")
            if salvar_moto:
                st.success(f"Moto placa {placa} cadastrada com sucesso!")

    # --- ABA 3: OFICINAS PARCEIRAS (Com Autocompletar) ---
    with aba_fornecedores:
        st.subheader("Gestão de Fornecedores e Oficinas")
        
        # Simulando uma lista de oficinas que já estão no banco de dados
        oficinas_existentes = ["Moto Peças Central", "Oficina do João", "Borracharia Express", "Speed Motos"]
        
        st.write("Digite o nome da oficina para buscar (autocompletar) ou cadastre uma nova.")
        
        # O text_input normal engessa, então usamos um selectbox que permite digitar e autocompletar,
        # ou deixamos o usuário digitar um nome totalmente novo.
        col1, col2 = st.columns(2)
        oficina_busca = col1.selectbox("Buscar Oficina Cadastrada", [""] + oficinas_existentes)
        novo_fornecedor = col2.text_input("Ou digite manualmente uma Nova Oficina")
        
        especialidade = st.multiselect("Tipos de Serviço", ["Troca de Óleo", "Pneus", "Relação/Corrente", "Freios"])
        
        if st.button("Registrar Oficina"):
            nome_final = novo_fornecedor if novo_fornecedor else oficina_busca
            st.success(f"Fornecedor '{nome_final}' salvo com as especialidades selecionadas!")

    # --- ABA 4: REGRAS DE MANUTENÇÃO ---
    with aba_regras:
        st.subheader("Configurar Vida Útil das Peças (Em KM)")
        st.info("Esses números alimentarão a barra de progresso no aplicativo do locatário.")
        with st.form("form_regras"):
            oleo = st.number_input("Troca de Óleo (km)", value=1000)
            filtro = st.number_input("Filtro de Óleo (km)", value=2000)
            pneu = st.number_input("Troca de Pneu (km)", value=12000)
            relacao = st.number_input("Troca de Corrente/Relação (km)", value=15000)
            
            salvar_regras = st.form_submit_button("Atualizar Regras")
            if salvar_regras:
                st.success("Regras de quilometragem atualizadas para toda a frota!")
