import streamlit as st
import datetime
import json
import os

# --- 1. CONFIGURAÇÃO E IDENTIDADE VISUAL ---
st.set_page_config(page_title="Sistema de Locação de Motos", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #000080; }
    [data-testid="stSidebar"] * { color: white !important; }
    div[data-baseweb="radio"] > div { margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS E GESTÃO DE ARQUIVOS ---
ARQUIVO_DB = "banco_de_dados.json"
PASTA_ARQUIVOS = "arquivos_salvos"

# Cria a pasta para guardar as fotos/PDFs se ela não existir
if not os.path.exists(PASTA_ARQUIVOS):
    os.makedirs(PASTA_ARQUIVOS)

def carregar_dados():
    if os.path.exists(ARQUIVO_DB):
        with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"motos": {}, "clientes": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DB, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def salvar_arquivo_fisico(arquivo_upado, nome_cliente, tipo_doc):
    """Pega o arquivo do upload e salva permanentemente na pasta"""
    if arquivo_upado is not None:
        # Pega a extensão do arquivo (ex: .pdf, .jpg)
        extensao = os.path.splitext(arquivo_upado.name)[1]
        # Cria um nome único: ex "Douglas_CNH.pdf"
        nome_arquivo = f"{nome_cliente.replace(' ', '_')}_{tipo_doc}{extensao}"
        caminho_completo = os.path.join(PASTA_ARQUIVOS, nome_arquivo)
        
        # Grava o arquivo fisicamente na pasta
        with open(caminho_completo, "wb") as f:
            f.write(arquivo_upado.getbuffer())
        
        return caminho_completo
    return None

db = carregar_dados()

# --- 3. MENU FIXO LATERAL ---
st.sidebar.title("Menu Principal")
escolha = st.sidebar.radio("Selecione o módulo:", [
    "Cadastro de Cliente", 
    "Cadastro de Moto", 
    "Relatório de Motos", 
    "Relatório de Clientes", 
    "Manutenção de Motos"
])
st.divider()

# --- MÓDULO: CADASTRO DE CLIENTE ---
if escolha == "Cadastro de Cliente":
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
        
        st.subheader("Anexos (Upload Definitivo)")
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
        
        if st.form_submit_button("Salvar Cadastro Permanente"):
            if not nome:
                st.error("O nome do cliente é obrigatório.")
            elif moto_escolhida == "Nenhuma moto cadastrada":
                st.error("Cadastre uma moto primeiro.")
            else:
                # Salva os arquivos fisicamente e pega o caminho deles
                caminho_cnh = salvar_arquivo_fisico(foto_cnh, nome, "CNH")
                caminho_res = salvar_arquivo_fisico(foto_residencia, nome, "Residencia")

                db["clientes"][nome] = {
                    "cpf": cpf, "rg": rg, "data_nasc": str(data_nasc),
                    "cnh": cnh, "categoria": categoria_cnh, "validade_cnh": str(validade_cnh),
                    "telefone": telefone, "email": email, "emergencia": emergencia,
                    "rua": rua, "numero": numero, "bairro": bairro, "cep": cep, "cidade": cidade,
                    "modalidade": modalidade, "moto": moto_escolhida, "valor": valor_semanal,
                    "prazo": prazo_meses, "caucao": caucao,
                    # Agora guardamos o caminho exato do arquivo no disco
                    "caminho_cnh": caminho_cnh, 
                    "caminho_residencia": caminho_res,
                    "caminho_minuta": None # Inicia sem minuta
                }
                db["motos"][moto_escolhida]["status"] = f"Locada para {nome}"
                salvar_dados(db)
                st.success(f"Cliente {nome} e seus documentos foram salvos permanentemente!")

# --- MÓDULO: CADASTRO DE MOTO ---
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
        col8, col9, col10 = st.columns(3)
        km_inicial = col8.number_input("Quilometragem Inicial", min_value=0, step=1)
        licenciamento = col9.number_input("Ano do Último Licenciamento", min_value=2000, max_value=2100, value=2026, step=1)
        status = col10.text_input("Status Atual", value="Disponível", disabled=True) 
        
        if st.form_submit_button("Cadastrar Moto Permanente"):
            chave_moto = f"{modelo} - {placa}"
            db["motos"][chave_moto] = {
                "placa": placa, "chassi": chassi, "renavam": renavam,
                "marca": marca, "modelo": modelo, "ano": ano, "cor": cor,
                "km_inicial": km_inicial, "licenciamento": licenciamento, "status": status
            }
            salvar_dados(db)
            st.success(f"Moto {chave_moto} cadastrada permanentemente no banco de dados!")

# --- MÓDULO: RELATÓRIO DE MOTOS ---
elif escolha == "Relatório de Motos":
    st.title("Relatório Geral de Motocicletas")
    
    if len(db["motos"]) == 0:
        st.warning("Nenhuma moto cadastrada no banco de dados.")
    else:
        for chave, dados_moto in db["motos"].items():
            titulo_linha = f"🏍️ {dados_moto['marca']} {dados_moto['modelo']} | Placa: {dados_moto['placa']} | Ano: {dados_moto['ano']} | Cor: {dados_moto['cor']}"
            
            with st.expander(titulo_linha):
                st.subheader("Ficha Técnica Completa")
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.write(f"**Chassi:** {dados_moto['chassi']}")
                col_m1.write(f"**Renavam:** {dados_moto['renavam']}")
                col_m2.write(f"**KM Inicial:** {dados_moto['km_inicial']} km")
                col_m2.write(f"**Licenciamento (Ano):** {dados_moto['licenciamento']}")
                col_m3.write(f"**Status:** {dados_moto['status']}")

# --- MÓDULO: RELATÓRIO DE CLIENTES E GESTÃO DE ARQUIVOS ---
elif escolha == "Relatório de Clientes":
    st.title("Relatório Completo de Clientes")
    
    if len(db["clientes"]) == 0:
        st.warning("Nenhum cliente cadastrado no banco de dados.")
    else:
        cliente_selecionado = st.selectbox("Selecione um Cliente", [""] + list(db["clientes"].keys()))
        
        if cliente_selecionado != "":
            cli = db["clientes"][cliente_selecionado]
            st.subheader(f"Ficha do Cliente: {cliente_selecionado}")
            
            # EXIBIÇÃO DE TODOS OS DADOS CADASTRAIS
            st.markdown("### 📋 Dados Pessoais e Contato")
            c1, c2, c3, c4 = st.columns(4)
            c1.write(f"**CPF:** {cli['cpf']}")
            c2.write(f"**RG:** {cli['rg']}")
            c3.write(f"**Nascimento:** {cli['data_nasc']}")
            c4.write(f"**Telefone:** {cli['telefone']}")
            
            c5, c6, c7 = st.columns(3)
            c5.write(f"**E-mail:** {cli['email']}")
            c6.write(f"**Emergência:** {cli['emergencia']}")
            c7.write(f"**CNH:** {cli['cnh']} (Cat: {cli['categoria']}) - Validade: {cli['validade_cnh']}")
            
            st.markdown(f"**Endereço:** Rua {cli['rua']}, {cli['numero']}, {cli['bairro']} - {cli['cidade']} (CEP: {cli['cep']})")
            
            st.markdown("### 🏍️ Contrato e Moto")
            st.write(f"**Moto Vinculada:** {cli['moto']}")
            st.write(f"**Modalidade:** {cli['modalidade']}")
            st.write(f"**Financeiro:** R$ {cli['valor']}/semana | **Prazo:** {cli['prazo']} meses | **Caução:** R$ {cli['caucao']}")
            
            st.divider()
            
            # GESTÃO REAL DE DOCUMENTOS
            st.subheader("Gerenciador de Documentos do Cliente")
            col_doc1, col_doc2, col_doc3 = st.columns(3)
            
            # 1. CNH
            with col_doc1:
                st.markdown("**1. CNH do Cliente**")
                caminho_cnh = cli.get("caminho_cnh")
                if caminho_cnh and os.path.exists(caminho_cnh):
                    with open(caminho_cnh, "rb") as file:
                        st.download_button(label="📥 Baixar/Ver CNH", data=file, file_name=os.path.basename(caminho_cnh), key="dl_cnh")
                    
                    nova_cnh = st.file_uploader("🔄 Substituir CNH", type=['pdf', 'jpg', 'png'], key="sub_cnh")
                    if nova_cnh:
                        novo_caminho = salvar_arquivo_fisico(nova_cnh, cliente_selecionado, "CNH")
                        db["clientes"][cliente_selecionado]["caminho_cnh"] = novo_caminho
                        salvar_dados(db)
                        st.success("CNH substituída!")
                        st.rerun()
                else:
                    nova_cnh = st.file_uploader("📤 Inserir CNH Faltante", type=['pdf', 'jpg', 'png'], key="up_cnh")
                    if nova_cnh:
                        novo_caminho = salvar_arquivo_fisico(nova_cnh, cliente_selecionado, "CNH")
                        db["clientes"][cliente_selecionado]["caminho_cnh"] = novo_caminho
                        salvar_dados(db)
                        st.success("CNH salva!")
                        st.rerun()

            # 2. Comprovante de Residência
            with col_doc2:
                st.markdown("**2. Comprov. Residência**")
                caminho_res = cli.get("caminho_residencia")
                if caminho_res and os.path.exists(caminho_res):
                    with open(caminho_res, "rb") as file:
                        st.download_button(label="📥 Baixar/Ver Comprovante", data=file, file_name=os.path.basename(caminho_res), key="dl_res")
                    
                    novo_res = st.file_uploader("🔄 Substituir Comprovante", type=['pdf', 'jpg', 'png'], key="sub_res")
                    if novo_res:
                        novo_caminho = salvar_arquivo_fisico(novo_res, cliente_selecionado, "Residencia")
                        db["clientes"][cliente_selecionado]["caminho_residencia"] = novo_caminho
                        salvar_dados(db)
                        st.success("Comprovante substituído!")
                        st.rerun()
                else:
                    novo_res = st.file_uploader("📤 Inserir Comprovante Faltante", type=['pdf', 'jpg', 'png'], key="up_res")
                    if novo_res:
                        novo_caminho = salvar_arquivo_fisico(novo_res, cliente_selecionado, "Residencia")
                        db["clientes"][cliente_selecionado]["caminho_residencia"] = novo_caminho
                        salvar_dados(db)
                        st.success("Comprovante salvo!")
                        st.rerun()

            # 3. Minuta do Contrato
            with col_doc3:
                st.markdown("**3. Minuta do Contrato**")
                caminho_min = cli.get("caminho_minuta")
                if caminho_min and os.path.exists(caminho_min):
                    with open(caminho_min, "rb") as file:
                        st.download_button(label="📥 Baixar/Ver Minuta", data=file, file_name=os.path.basename(caminho_min), key="dl_min")
                    
                    nova_minuta = st.file_uploader("🔄 Substituir Minuta", type=['pdf', 'doc', 'docx'], key="sub_min")
                    if nova_minuta:
                        novo_caminho = salvar_arquivo_fisico(nova_minuta, cliente_selecionado, "Minuta")
                        db["clientes"][cliente_selecionado]["caminho_minuta"] = novo_caminho
                        salvar_dados(db)
                        st.success("Minuta substituída!")
                        st.rerun()
                else:
                    st.warning("Sem contrato no sistema.")
                    nova_minuta = st.file_uploader("📤 Inserir Minuta do Contrato", type=['pdf', 'doc', 'docx'], key="up_min")
                    if nova_minuta:
                        novo_caminho = salvar_arquivo_fisico(nova_minuta, cliente_selecionado, "Minuta")
                        db["clientes"][cliente_selecionado]["caminho_minuta"] = novo_caminho
                        salvar_dados(db)
                        st.success("Minuta salva!")
                        st.rerun()

# --- MÓDULO: MANUTENÇÃO DE MOTOS ---
elif escolha == "Manutenção de Motos":
    st.title("Gestão de Manutenções")
    st.write("Área para configurar quilometragens e validar os vídeos de troca de óleo (Em breve integrado aos arquivos físicos).")
