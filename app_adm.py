import streamlit as st
import datetime
import os
from supabase import create_client, Client

# --- 1. CONFIGURAÇÃO E IDENTIDADE VISUAL ---
st.set_page_config(page_title="Sistema de Locação de Motos", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #000080; }
    [data-testid="stSidebar"] * { color: white !important; }
    div[data-baseweb="radio"] > div { margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO COM A NUVEM (SUPABASE) ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def carregar_dados_nuvem():
    """Puxa os cadastros do banco de dados na nuvem"""
    try:
        resposta = supabase.table("banco_json").select("dados").eq("id", 1).execute()
        if resposta.data:
            return resposta.data[0]["dados"]
    except Exception as e:
        pass
    return {"motos": {}, "clientes": {}}

def salvar_dados_nuvem(dados):
    """Envia os cadastros usando UPSERT (Força a criação se não existir)"""
    supabase.table("banco_json").upsert({"id": 1, "dados": dados}).execute()

def salvar_arquivo_nuvem(arquivo_upado, nome_cliente, tipo_doc):
    """Envia arquivos para o bucket do Supabase"""
    if arquivo_upado is not None:
        extensao = os.path.splitext(arquivo_upado.name)[1]
        timestamp = int(datetime.datetime.now().timestamp())
        nome_arquivo = f"{nome_cliente.replace(' ', '_')}_{tipo_doc}_{timestamp}{extensao}"
        
        arquivo_bytes = arquivo_upado.getvalue()
        supabase.storage.from_("arquivos").upload(nome_arquivo, arquivo_bytes)
        
        link_publico = supabase.storage.from_("arquivos").get_public_url(nome_arquivo)
        return link_publico
    return None

# Carrega os dados sempre que a página atualiza
db = carregar_dados_nuvem()
# Garantir que a estrutura exista
if "motos" not in db: db["motos"] = {}
if "clientes" not in db: db["clientes"] = {}

# --- 3. MENU FIXO LATERAL (REORGANIZADO) ---
st.sidebar.title("Menu Principal")
escolha = st.sidebar.radio("Selecione o módulo:", [
    "Painel Inicial",
    "Cadastro de Cliente", 
    "Cadastro de Moto", 
    "Relatório de Clientes", 
    "Relatório de Motos", 
    "Manutenção de Motos"
])
st.divider()

# --- MÓDULO NOVO: PAINEL INICIAL (NOTIFICAÇÕES) ---
if escolha == "Painel Inicial":
    st.title("Painel Administrativo")
    st.subheader("🔔 Alertas do Sistema")
    
    hoje = datetime.date.today()
    alertas_gerados = False
    
    for nome_cliente, dados_cli in db["clientes"].items():
        if "validade_cnh" in dados_cli:
            try:
                # Converte a data salva (texto) de volta para formato de data real
                validade = datetime.datetime.strptime(dados_cli["validade_cnh"], "%Y-%m-%d").date()
                dias_restantes = (validade - hoje).days
                
                # Regra dos 60 dias
                if 0 <= dias_restantes <= 60:
                    st.warning(f"⚠️ **Atenção:** A CNH do cliente **{nome_cliente}** vence em **{dias_restantes} dias** (Data: {validade.strftime('%d/%m/%Y')}).")
                    alertas_gerados = True
                # Regra de vencida
                elif dias_restantes < 0:
                    st.error(f"🚨 **URGENTE:** A CNH do cliente **{nome_cliente}** está **VENCIDA** há {abs(dias_restantes)} dias (Data: {validade.strftime('%d/%m/%Y')}).")
                    alertas_gerados = True
            except:
                pass
                
    if not alertas_gerados:
        st.success("✅ Tudo certo! Nenhuma CNH vencendo nos próximos 60 dias.")
        
    st.divider()
    st.write(f"**Resumo da Frota:** {len(db['motos'])} moto(s) cadastrada(s).")
    st.write(f"**Resumo de Clientes:** {len(db['clientes'])} cliente(s) ativo(s).")

# --- MÓDULO: CADASTRO DE CLIENTE ---
elif escolha == "Cadastro de Cliente":
    st.title("Cadastro de Novo Cliente")
    
    with st.form("form_novo_cliente"):
        st.subheader("Dados Pessoais")
        col1, col2, col3, col4 = st.columns(4)
        nome = col1.text_input("Nome Completo")
        cpf = col2.text_input("CPF")
        rg = col3.text_input("RG")
        data_nasc = col4.date_input("Data de Nascimento", min_value=datetime.date(1920, 1, 1), value=datetime.date(1990, 1, 1))
        
        st.subheader("Habilitação")
        col5, col6, col7 = st.columns(3)
        cnh = col5.text_input("Número da CNH")
        categoria_cnh = col6.selectbox("Categoria", ["A", "AB", "AC", "AD", "AE"])
        validade_cnh = col7.date_input("Validade da CNH", min_value=datetime.date.today(), max_value=datetime.date(2100, 12, 31))
        
        st.subheader("Contato")
        col8, col9, col10 = st.columns(3)
        telefone = col8.text_input("Telefone/WhatsApp")
        email = col9.text_input("E-mail")
        emergencia = col10.text_input("Contato de Emergência")
        
        st.subheader("Endereço")
        col11, col12, col13, col14, col15 = st.columns([2, 1, 1, 1, 2])
        rua = col11.text_input("Rua")
        numero = col12.text_input("Número")
        bairro = col13.text_input("Bairro")
        cep = col14.text_input("CEP")
        cidade = col15.text_input("Cidade")
        
        st.subheader("Anexos (Upload para a Nuvem)")
        foto_cnh = st.file_uploader("Foto da CNH", type=['pdf', 'jpg', 'png', 'jpeg'])
        foto_residencia = st.file_uploader("Comprovante de Residência", type=['pdf', 'jpg', 'png', 'jpeg'])
        
        st.subheader("Detalhes do Contrato")
        col16, col17 = st.columns(2)
        modalidade = col16.selectbox("Modalidade", ["Com Repasse do Bem (Transferência)", "Sem Repasse (Devolução)"])
        
        lista_motos = ["Nenhuma moto cadastrada"] if len(db["motos"]) == 0 else list(db["motos"].keys())
        moto_escolhida = col17.selectbox("Modelo da Moto", lista_motos)
        
        col18, col19, col20 = st.columns(3)
        valor_semanal = col18.number_input("Valor Semanal (R$)", min_value=0.0, step=10.0)
        prazo_meses = col19.number_input("Prazo do Contrato (Meses)", min_value=1, step=1)
        caucao = col20.number_input("Caução/Franquia (R$)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Salvar Cadastro na Nuvem"):
            if not nome:
                st.error("O nome do cliente é obrigatório.")
            elif moto_escolhida == "Nenhuma moto cadastrada":
                st.error("Cadastre uma moto primeiro no menu 'Cadastro de Moto'.")
            else:
                with st.spinner("Enviando arquivos e salvando na nuvem..."):
                    caminho_cnh = salvar_arquivo_nuvem(foto_cnh, nome, "CNH")
                    caminho_res = salvar_arquivo_nuvem(foto_residencia, nome, "Residencia")

                    db["clientes"][nome] = {
                        "cpf": cpf, "rg": rg, "data_nasc": str(data_nasc),
                        "cnh": cnh, "categoria": categoria_cnh, "validade_cnh": str(validade_cnh),
                        "telefone": telefone, "email": email, "emergencia": emergencia,
                        "rua": rua, "numero": numero, "bairro": bairro, "cep": cep, "cidade": cidade,
                        "modalidade": modalidade, "moto": moto_escolhida, "valor": valor_semanal,
                        "prazo": prazo_meses, "caucao": caucao,
                        "link_cnh": caminho_cnh, 
                        "link_residencia": caminho_res,
                        "link_minuta": None
                    }
                    db["motos"][moto_escolhida]["status"] = f"Locada para {nome}"
                    salvar_dados_nuvem(db)
                st.success(f"Cliente {nome} salvo com sucesso! Atualize a página ou clique em outro menu para atualizar a tela.")

# --- MÓDULO: CADASTRO DE MOTO ---
elif escolha == "Cadastro de Moto":
    st.title("Cadastro de Nova Motocicleta")
    
    with st.form("form_nova_moto", clear_on_submit=True):
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
        licenciamento = col9.number_input("Ano do Último Licenciamento", min_value=2000, max_value=2100, value=2026, step=1)
        status = col10.text_input("Status Atual", value="Disponível", disabled=True) 
        
        if st.form_submit_button("Cadastrar Moto na Nuvem"):
            if not placa or not modelo:
                st.error("Placa e Modelo são obrigatórios.")
            else:
                chave_moto = f"{modelo} - {placa}"
                db["motos"][chave_moto] = {
                    "placa": placa, "chassi": chassi, "renavam": renavam,
                    "marca": marca, "modelo": modelo, "ano": ano, "cor": cor,
                    "km_inicial": km_inicial, "licenciamento": licenciamento, "status": status
                }
                salvar_dados_nuvem(db)
                st.success(f"Moto {chave_moto} salva na nuvem! Vá em 'Relatório de Motos' para confirmar.")

# --- MÓDULO: RELATÓRIO DE CLIENTES (AGORA ACIMA DO DE MOTOS) ---
elif escolha == "Relatório de Clientes":
    st.title("Relatório Completo de Clientes")
    
    if len(db["clientes"]) == 0:
        st.warning("Nenhum cliente cadastrado no banco de dados.")
    else:
        cliente_selecionado = st.selectbox("Selecione um Cliente", [""] + list(db["clientes"].keys()))
        
        if cliente_selecionado != "":
            cli = db["clientes"][cliente_selecionado]
            st.subheader(f"Ficha do Cliente: {cliente_selecionado}")
            
            st.markdown("### 📋 Dados Pessoais e Contato")
            c1, c2, c3, c4 = st.columns(4)
            c1.write(f"**CPF:** {cli.get('cpf', '')}")
            c2.write(f"**RG:** {cli.get('rg', '')}")
            c3.write(f"**Nascimento:** {cli.get('data_nasc', '')}")
            c4.write(f"**Telefone:** {cli.get('telefone', '')}")
            
            c5, c6, c7 = st.columns(3)
            c5.write(f"**E-mail:** {cli.get('email', '')}")
            c6.write(f"**Emergência:** {cli.get('emergencia', '')}")
            c7.write(f"**CNH:** {cli.get('cnh', '')} (Cat: {cli.get('categoria', '')}) - Validade: {cli.get('validade_cnh', '')}")
            
            st.markdown(f"**Endereço:** Rua {cli.get('rua', '')}, {cli.get('numero', '')}, {cli.get('bairro', '')} - {cli.get('cidade', '')} (CEP: {cli.get('cep', '')})")
            
            st.markdown("### 🏍️ Contrato e Moto")
            st.write(f"**Moto Vinculada:** {cli.get('moto', '')}")
            st.write(f"**Modalidade:** {cli.get('modalidade', '')}")
            st.write(f"**Financeiro:** R$ {cli.get('valor', '')}/semana | **Prazo:** {cli.get('prazo', '')} meses | **Caução:** R$ {cli.get('caucao', '')}")
            
            st.divider()
            
            st.subheader("Gerenciador de Documentos na Nuvem")
            col_doc1, col_doc2, col_doc3 = st.columns(3)
            
            # CNH
            with col_doc1:
                st.markdown("**1. CNH do Cliente**")
                link_cnh = cli.get("link_cnh")
                if link_cnh:
                    st.markdown(f"[📥 Baixar/Ver CNH]({link_cnh})", unsafe_allow_html=True)
                    nova_cnh = st.file_uploader("🔄 Substituir CNH", type=['pdf', 'jpg', 'png'], key="sub_cnh")
                    if nova_cnh:
                        with st.spinner("Substituindo..."):
                            novo_link = salvar_arquivo_nuvem(nova_cnh, cliente_selecionado, "CNH")
                            db["clientes"][cliente_selecionado]["link_cnh"] = novo_link
                            salvar_dados_nuvem(db)
                        st.success("Substituída! Atualize a página.")
                else:
                    nova_cnh = st.file_uploader("📤 Inserir CNH", type=['pdf', 'jpg', 'png'], key="up_cnh")
                    if nova_cnh:
                        novo_link = salvar_arquivo_nuvem(nova_cnh, cliente_selecionado, "CNH")
                        db["clientes"][cliente_selecionado]["link_cnh"] = novo_link
                        salvar_dados_nuvem(db)
                        st.success("Salva! Atualize a página.")

            # Comprovante
            with col_doc2:
                st.markdown("**2. Comprov. Residência**")
                link_res = cli.get("link_residencia")
                if link_res:
                    st.markdown(f"[📥 Baixar/Ver Comprovante]({link_res})", unsafe_allow_html=True)
                    novo_res = st.file_uploader("🔄 Substituir Comprovante", type=['pdf', 'jpg', 'png'], key="sub_res")
                    if novo_res:
                        with st.spinner("Substituindo..."):
                            novo_link = salvar_arquivo_nuvem(novo_res, cliente_selecionado, "Residencia")
                            db["clientes"][cliente_selecionado]["link_residencia"] = novo_link
                            salvar_dados_nuvem(db)
                        st.success("Substituído! Atualize a página.")
                else:
                    novo_res = st.file_uploader("📤 Inserir Comprovante", type=['pdf', 'jpg', 'png'], key="up_res")
                    if novo_res:
                        novo_link = salvar_arquivo_nuvem(novo_res, cliente_selecionado, "Residencia")
                        db["clientes"][cliente_selecionado]["link_residencia"] = novo_link
                        salvar_dados_nuvem(db)
                        st.success("Salvo! Atualize a página.")

            # Minuta
            with col_doc3:
                st.markdown("**3. Minuta do Contrato**")
                link_min = cli.get("link_minuta")
                if link_min:
                    st.markdown(f"[📥 Baixar/Ver Minuta]({link_min})", unsafe_allow_html=True)
                    nova_minuta = st.file_uploader("🔄 Substituir Minuta", type=['pdf', 'doc', 'docx'], key="sub_min")
                    if nova_minuta:
                        with st.spinner("Substituindo..."):
                            novo_link = salvar_arquivo_nuvem(nova_minuta, cliente_selecionado, "Minuta")
                            db["clientes"][cliente_selecionado]["link_minuta"] = novo_link
                            salvar_dados_nuvem(db)
                        st.success("Substituída! Atualize a página.")
                else:
                    nova_minuta = st.file_uploader("📤 Inserir Minuta", type=['pdf', 'doc', 'docx'], key="up_min")
                    if nova_minuta:
                        novo_link = salvar_arquivo_nuvem(nova_minuta, cliente_selecionado, "Minuta")
                        db["clientes"][cliente_selecionado]["link_minuta"] = novo_link
                        salvar_dados_nuvem(db)
                        st.success("Salva! Atualize a página.")

# --- MÓDULO: RELATÓRIO DE MOTOS ---
elif escolha == "Relatório de Motos":
    st.title("Relatório Geral de Motocicletas")
    
    if len(db["motos"]) == 0:
        st.warning("Nenhuma moto cadastrada no banco de dados.")
    else:
        for chave, dados_moto in db["motos"].items():
            titulo_linha = f"🏍️ {dados_moto.get('marca', '')} {dados_moto.get('modelo', '')} | Placa: {dados_moto.get('placa', '')} | Ano: {dados_moto.get('ano', '')} | Cor: {dados_moto.get('cor', '')}"
            with st.expander(titulo_linha):
                st.subheader("Ficha Técnica Completa")
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.write(f"**Chassi:** {dados_moto.get('chassi', '')}")
                col_m1.write(f"**Renavam:** {dados_moto.get('renavam', '')}")
                col_m2.write(f"**KM Inicial:** {dados_moto.get('km_inicial', '')} km")
                col_m2.write(f"**Licenciamento (Ano):** {dados_moto.get('licenciamento', '')}")
                col_m3.write(f"**Status:** {dados_moto.get('status', '')}")

# --- MÓDULO: MANUTENÇÃO DE MOTOS ---
elif escolha == "Manutenção de Motos":
    st.title("Gestão de Manutenções")
    st.write("Área estruturada para integração futura com o aplicativo dos locatários.")
