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
    try:
        resposta = supabase.table("banco_json").select("dados").eq("id", 1).execute()
        if resposta.data:
            return resposta.data[0]["dados"]
    except Exception as e:
        pass
    return {"motos": {}, "clientes": {}}

def salvar_dados_nuvem(dados):
    supabase.table("banco_json").upsert({"id": 1, "dados": dados}).execute()

def salvar_arquivo_nuvem(arquivo_upado, nome_cliente, tipo_doc):
    if arquivo_upado is not None:
        extensao = os.path.splitext(arquivo_upado.name)[1]
        timestamp = int(datetime.datetime.now().timestamp())
        nome_arquivo = f"{nome_cliente.replace(' ', '_')}_{tipo_doc}_{timestamp}{extensao}"
        arquivo_bytes = arquivo_upado.getvalue()
        supabase.storage.from_("arquivos").upload(nome_arquivo, arquivo_bytes)
        return supabase.storage.from_("arquivos").get_public_url(nome_arquivo)
    return None

db = carregar_dados_nuvem()
if "motos" not in db: db["motos"] = {}
if "clientes" not in db: db["clientes"] = {}

# --- 3. MENU FIXO LATERAL ---
st.sidebar.title("Menu Principal")
escolha = st.sidebar.radio("Selecione o módulo:", [
    "Painel Inicial",
    "Cadastro de Cliente", 
    "Cadastro de Moto", 
    "Relatório de Clientes", 
    "Relatório de Motos"
])
st.divider()

# --- MÓDULO: PAINEL INICIAL (NOTIFICAÇÕES INTELIGENTES) ---
if escolha == "Painel Inicial":
    st.title("Painel Administrativo")
    
    st.subheader("🔔 Alertas de CNH")
    hoje = datetime.date.today()
    alerta_cnh = False
    
    for nome_cli, dados_cli in db["clientes"].items():
        if "validade_cnh" in dados_cli:
            try:
                validade = datetime.datetime.strptime(dados_cli["validade_cnh"], "%Y-%m-%d").date()
                dias = (validade - hoje).days
                if 0 <= dias <= 60:
                    st.warning(f"⚠️ A CNH de **{nome_cli}** vence em **{dias} dias** ({validade.strftime('%d/%m/%Y')}).")
                    alerta_cnh = True
                elif dias < 0:
                    st.error(f"🚨 A CNH de **{nome_cli}** está **VENCIDA** há {abs(dias)} dias!")
                    alerta_cnh = True
            except:
                pass
    if not alerta_cnh: st.success("✅ Nenhuma CNH vencendo nos próximos 60 dias.")
    
    st.divider()
    
    st.subheader("🔧 Alertas de Manutenção (Por Quilometragem)")
    alerta_manu = False
    
    for chave_moto, dados_moto in db["motos"].items():
        km_atual = dados_moto.get("km_atual", dados_moto.get("km_inicial", 0))
        regras = dados_moto.get("manutencao", {})
        
        for item, valores in regras.items():
            intervalo = valores.get("intervalo", 0)
            ultima_troca = valores.get("ultima_troca", 0)
            
            if intervalo > 0:
                km_proxima_troca = ultima_troca + intervalo
                if km_atual >= km_proxima_troca:
                    st.error(f"🚨 **{chave_moto}:** Troca de **{item.upper()}** atingida! (Passou de {intervalo}km desde a última). KM Atual: {km_atual}.")
                    alerta_manu = True
                elif (km_proxima_troca - km_atual) <= 200: 
                    st.warning(f"⚠️ **{chave_moto}:** Troca de **{item.upper()}** próxima. Faltam apenas {km_proxima_troca - km_atual}km.")
                    alerta_manu = True

    if not alerta_manu: st.success("✅ Nenhuma manutenção pendente na frota atual.")

# --- MÓDULO: CADASTRO DE CLIENTE ---
elif escolha == "Cadastro de Cliente":
    st.title("Cadastro de Novo Cliente")
    
    with st.form("form_novo_cliente", clear_on_submit=True):
        st.subheader("Dados Pessoais")
        col1, col2, col3, col4 = st.columns(4)
        nome = col1.text_input("Nome Completo")
        cpf = col2.text_input("CPF")
        rg = col3.text_input("RG")
        data_nasc = col4.date_input("Data Nascimento", min_value=datetime.date(1920, 1, 1), value=datetime.date(1990, 1, 1))
        
        st.subheader("Habilitação")
        col5, col6, col7 = st.columns(3)
        cnh = col5.text_input("Número da CNH")
        categoria_cnh = col6.selectbox("Categoria", ["A", "AB", "AC", "AD", "AE"])
        validade_cnh = col7.date_input("Validade CNH", min_value=datetime.date.today(), max_value=datetime.date(2100, 12, 31))
        
        st.subheader("Contato e Endereço")
        col8, col9 = st.columns(2)
        telefone = col8.text_input("Telefone/WhatsApp")
        emergencia = col9.text_input("Contato Emergência")
        rua = st.text_input("Endereço Completo (Rua, Nº, Bairro, CEP, Cidade)")
        
        st.subheader("Anexos (Upload)")
        foto_cnh = st.file_uploader("Foto CNH", type=['pdf', 'jpg', 'png'])
        foto_residencia = st.file_uploader("Comprovante Residência", type=['pdf', 'jpg', 'png'])
        
        st.subheader("Detalhes do Contrato")
        col10, col11 = st.columns(2)
        modalidade = col10.selectbox("Modalidade", ["Transferência", "Devolução"])
        
        # MOTOS DISPONÍVEIS
        motos_disponiveis = [m for m, d in db["motos"].items() if d.get("status", "") == "Disponível"]
        lista_motos = motos_disponiveis if len(motos_disponiveis) > 0 else ["Nenhuma moto disponível no momento"]
        moto_escolhida = col11.selectbox("Modelo da Moto", lista_motos)
        
        col12, col13, col14 = st.columns(3)
        valor_semanal = col12.number_input("Valor Semanal (R$)", min_value=0.0, step=10.0)
        prazo_meses = col13.number_input("Prazo (Meses)", min_value=1)
        caucao = col14.number_input("Caução (R$)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Salvar Cadastro"):
            if not nome:
                st.error("Nome é obrigatório.")
            elif moto_escolhida == "Nenhuma moto disponível no momento":
                st.error("Libere ou cadastre uma moto disponível primeiro.")
            else:
                with st.spinner("Salvando..."):
                    caminho_cnh = salvar_arquivo_nuvem(foto_cnh, nome, "CNH")
                    caminho_res = salvar_arquivo_nuvem(foto_residencia, nome, "Residencia")

                    db["clientes"][nome] = {
                        "cpf": cpf, "rg": rg, "data_nasc": str(data_nasc),
                        "cnh": cnh, "categoria": categoria_cnh, "validade_cnh": str(validade_cnh),
                        "telefone": telefone, "emergencia": emergencia, "rua": rua,
                        "modalidade": modalidade, "moto": moto_escolhida, "valor": valor_semanal,
                        "prazo": prazo_meses, "caucao": caucao,
                        "link_cnh": caminho_cnh, "link_residencia": caminho_res, "link_minuta": None
                    }
                    db["motos"][moto_escolhida]["status"] = f"Locada para {nome}"
                    salvar_dados_nuvem(db)
                st.success("Salvo com sucesso!")

# --- MÓDULO: CADASTRO DE MOTO ---
elif escolha == "Cadastro de Moto":
    st.title("Cadastro de Nova Motocicleta")
    
    with st.form("form_nova_moto", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        placa = col1.text_input("Placa")
        chassi = col2.text_input("Chassi")
        renavam = col3.text_input("Renavam")
        
        col4, col5, col6, col7 = st.columns(4)
        marca = col4.text_input("Marca")
        modelo = col5.text_input("Modelo")
        ano = col6.text_input("Ano")
        cor = col7.text_input("Cor")
        
        col8, col9 = st.columns(2)
        km_inicial = col8.number_input("Quilometragem Inicial", min_value=0, step=1)
        licenciamento = col9.number_input("Ano Licenciamento", min_value=2000, value=2026)
        
        if st.form_submit_button("Cadastrar Moto"):
            if placa and modelo:
                chave_moto = f"{modelo} - {placa}"
                db["motos"][chave_moto] = {
                    "placa": placa, "chassi": chassi, "renavam": renavam,
                    "marca": marca, "modelo": modelo, "ano": ano, "cor": cor,
                    "km_inicial": km_inicial, "km_atual": km_inicial,
                    "licenciamento": licenciamento, "status": "Disponível",
                    "manutencao": {
                        "Óleo": {"ultima_troca": km_inicial, "intervalo": 1000},
                        "Filtro": {"ultima_troca": km_inicial, "intervalo": 2000},
                        "Pastilha": {"ultima_troca": km_inicial, "intervalo": 5000},
                        "Pneu": {"ultima_troca": km_inicial, "intervalo": 10000},
                        "Embreagem": {"ultima_troca": km_inicial, "intervalo": 12000},
                        "Corrente": {"ultima_troca": km_inicial, "intervalo": 15000}
                    }
                }
                salvar_dados_nuvem(db)
                st.success("Moto salva como Disponível!")
            else:
                st.error("Placa e Modelo são obrigatórios.")

# --- MÓDULO: RELATÓRIO DE CLIENTES ---
elif escolha == "Relatório de Clientes":
    st.title("Relatório Completo de Clientes")
    
    if len(db["clientes"]) == 0:
        st.warning("Nenhum cliente cadastrado no banco de dados.")
    else:
        cliente_selecionado = st.selectbox("Selecione um Cliente", [""] + list(db["clientes"].keys()))
        
        if cliente_selecionado != "":
            cli = db["clientes"][cliente_selecionado]
            st.subheader(f"Ficha do Cliente: {cliente_selecionado}")
            
            # 1. VISUALIZAÇÃO DOS DADOS (RESTAURADA)
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
            
            st.markdown(f"**Endereço:** {cli.get('rua', '')}")
            
            st.markdown("### 🏍️ Contrato e Moto")
            st.write(f"**Moto Vinculada:** {cli.get('moto', '')}")
            st.write(f"**Modalidade:** {cli.get('modalidade', '')}")
            st.write(f"**Financeiro:** R$ {cli.get('valor', '')}/semana | **Prazo:** {cli.get('prazo', '')} meses | **Caução:** R$ {cli.get('caucao', '')}")
            
            st.divider()
            
            # 2. EDIÇÃO DOS DADOS DO CLIENTE
            with st.expander("✏️ Editar Informações do Cliente"):
                with st.form("form_editar_cliente"):
                    st.info("Altere os dados abaixo e clique em Salvar.")
                    e_cpf = st.text_input("CPF", value=cli.get('cpf', ''))
                    e_rg = st.text_input("RG", value=cli.get('rg', ''))
                    e_tel = st.text_input("Telefone", value=cli.get('telefone', ''))
                    e_rua = st.text_input("Endereço", value=cli.get('rua', ''))
                    e_cnh = st.text_input("CNH", value=cli.get('cnh', ''))
                    
                    moto_atual = cli.get('moto')
                    motos_disp = [m for m, d in db["motos"].items() if d.get("status", "") == "Disponível"]
                    if moto_atual in db["motos"] and moto_atual not in motos_disp:
                        opcoes_moto = [moto_atual] + motos_disp + ["Nenhuma"]
                    else:
                        opcoes_moto = motos_disp + ["Nenhuma"]
                        
                    e_moto = st.selectbox("Moto Vinculada (Mude para trocar/devolver)", opcoes_moto, index=0)
                    e_valor = st.number_input("Valor", value=float(cli.get('valor', 0.0)))
                    
                    if st.form_submit_button("Salvar Edição do Cliente"):
                        if e_moto != moto_atual:
                            if moto_atual in db["motos"]:
                                db["motos"][moto_atual]["status"] = "Disponível"
                            if e_moto != "Nenhuma" and e_moto in db["motos"]:
                                db["motos"][e_moto]["status"] = f"Locada para {cliente_selecionado}"
                        
                        db["clientes"][cliente_selecionado]["cpf"] = e_cpf
                        db["clientes"][cliente_selecionado]["rg"] = e_rg
                        db["clientes"][cliente_selecionado]["telefone"] = e_tel
                        db["clientes"][cliente_selecionado]["rua"] = e_rua
                        db["clientes"][cliente_selecionado]["cnh"] = e_cnh
                        db["clientes"][cliente_selecionado]["moto"] = e_moto
                        db["clientes"][cliente_selecionado]["valor"] = e_valor
                        salvar_dados_nuvem(db)
                        st.success("Dados atualizados!")
                        st.rerun()

            st.divider()

            # 3. GESTÃO DOS ARQUIVOS (RESTAURADA)
            st.subheader("Gerenciador de Documentos na Nuvem")
            col_doc1, col_doc2, col_doc3 = st.columns(3)
            
            with col_doc1:
                st.markdown("**1. CNH do Cliente**")
                link_cnh = cli.get("link_cnh")
                if link_cnh:
                    st.markdown(f"[📥 Baixar/Ver CNH]({link_cnh})", unsafe_allow_html=True)
                    nova_cnh = st.file_uploader("🔄 Substituir CNH", type=['pdf', 'jpg', 'png'], key="sub_cnh")
                    if nova_cnh:
                        with st.spinner("Substituindo..."):
                            db["clientes"][cliente_selecionado]["link_cnh"] = salvar_arquivo_nuvem(nova_cnh, cliente_selecionado, "CNH")
                            salvar_dados_nuvem(db)
                        st.success("Substituída! Atualize a página.")
                else:
                    nova_cnh = st.file_uploader("📤 Inserir CNH", type=['pdf', 'jpg', 'png'], key="up_cnh")
                    if nova_cnh:
                        db["clientes"][cliente_selecionado]["link_cnh"] = salvar_arquivo_nuvem(nova_cnh, cliente_selecionado, "CNH")
                        salvar_dados_nuvem(db)
                        st.success("Salva! Atualize a página.")

            with col_doc2:
                st.markdown("**2. Comprov. Residência**")
                link_res = cli.get("link_residencia")
                if link_res:
                    st.markdown(f"[📥 Baixar/Ver Comprovante]({link_res})", unsafe_allow_html=True)
                    novo_res = st.file_uploader("🔄 Substituir Comprovante", type=['pdf', 'jpg', 'png'], key="sub_res")
                    if novo_res:
                        with st.spinner("Substituindo..."):
                            db["clientes"][cliente_selecionado]["link_residencia"] = salvar_arquivo_nuvem(novo_res, cliente_selecionado, "Residencia")
                            salvar_dados_nuvem(db)
                        st.success("Substituído! Atualize a página.")
                else:
                    novo_res = st.file_uploader("📤 Inserir Comprovante", type=['pdf', 'jpg', 'png'], key="up_res")
                    if novo_res:
                        db["clientes"][cliente_selecionado]["link_residencia"] = salvar_arquivo_nuvem(novo_res, cliente_selecionado, "Residencia")
                        salvar_dados_nuvem(db)
                        st.success("Salvo! Atualize a página.")

            with col_doc3:
                st.markdown("**3. Minuta do Contrato**")
                link_min = cli.get("link_minuta")
                if link_min:
                    st.markdown(f"[📥 Baixar/Ver Minuta]({link_min})", unsafe_allow_html=True)
                    nova_minuta = st.file_uploader("🔄 Substituir Minuta", type=['pdf', 'doc', 'docx'], key="sub_min")
                    if nova_minuta:
                        with st.spinner("Substituindo..."):
                            db["clientes"][cliente_selecionado]["link_minuta"] = salvar_arquivo_nuvem(nova_minuta, cliente_selecionado, "Minuta")
                            salvar_dados_nuvem(db)
                        st.success("Substituída! Atualize a página.")
                else:
                    nova_minuta = st.file_uploader("📤 Inserir Minuta", type=['pdf', 'doc', 'docx'], key="up_min")
                    if nova_minuta:
                        db["clientes"][cliente_selecionado]["link_minuta"] = salvar_arquivo_nuvem(nova_minuta, cliente_selecionado, "Minuta")
                        salvar_dados_nuvem(db)
                        st.success("Salva! Atualize a página.")

# --- MÓDULO: RELATÓRIO DE MOTOS ---
elif escolha == "Relatório de Motos":
    st.title("Relatório Geral e Manutenção de Motos")
    
    if len(db["motos"]) == 0:
        st.warning("Nenhuma moto cadastrada no banco de dados.")
    else:
        moto_selecionada = st.selectbox("Selecione a Moto", [""] + list(db["motos"].keys()))
        
        if moto_selecionada != "":
            moto_dados = db["motos"][moto_selecionada]
            st.subheader(f"Ficha Técnica: {moto_selecionada}")
            
            # 1. VISUALIZAÇÃO DOS DADOS (RESTAURADA)
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.write(f"**Chassi:** {moto_dados.get('chassi', '')}")
            col_m1.write(f"**Renavam:** {moto_dados.get('renavam', '')}")
            col_m2.write(f"**Licenciamento (Ano):** {moto_dados.get('licenciamento', '')}")
            col_m2.write(f"**KM Inicial:** {moto_dados.get('km_inicial', '')} km")
            col_m3.write(f"**KM Atual:** {moto_dados.get('km_atual', moto_dados.get('km_inicial', 0))} km")
            col_m3.write(f"**Status:** {moto_dados.get('status', '')}")
            
            st.divider()
            
            # 2. EDIÇÃO DOS DADOS DA MOTO
            with st.expander("✏️ Editar Informações da Moto"):
                with st.form("form_editar_moto"):
                    em_chassi = st.text_input("Chassi", value=moto_dados.get('chassi', ''))
                    em_renavam = st.text_input("Renavam", value=moto_dados.get('renavam', ''))
                    em_cor = st.text_input("Cor", value=moto_dados.get('cor', ''))
                    em_licenca = st.number_input("Licenciamento", value=int(moto_dados.get('licenciamento', 2026)))
                    
                    if st.form_submit_button("Salvar Edição da Moto"):
                        db["motos"][moto_selecionada]["chassi"] = em_chassi
                        db["motos"][moto_selecionada]["renavam"] = em_renavam
                        db["motos"][moto_selecionada]["cor"] = em_cor
                        db["motos"][moto_selecionada]["licenciamento"] = em_licenca
                        salvar_dados_nuvem(db)
                        st.success("Dados atualizados!")
                        st.rerun()

            # 3. CONTROLE DE MANUTENÇÃO
            with st.expander("🔧 Cadastro de Quilometragem e Manutenções"):
                st.info("Atualize o KM da moto e ajuste os intervalos fixos para gerar alertas no Painel Inicial.")
                with st.form("form_manutencao"):
                    km_hoje = st.number_input("Atualizar KM ATUAL da Moto", value=int(moto_dados.get('km_atual', 0)), step=100)
                    st.divider()
                    
                    manutencao_db = moto_dados.get("manutencao", {})
                    pecas = ["Óleo", "Filtro", "Pastilha", "Pneu", "Embreagem", "Corrente"]
                    
                    novos_dados_manu = {}
                    for peca in pecas:
                        st.write(f"**{peca}**")
                        c1, c2 = st.columns(2)
                        val_ultima = manutencao_db.get(peca, {}).get("ultima_troca", 0)
                        val_intervalo = manutencao_db.get(peca, {}).get("intervalo", 0)
                        
                        nova_ultima = c1.number_input(f"KM Última Troca ({peca})", value=int(val_ultima), key=f"ult_{peca}")
                        novo_inter = c2.number_input(f"Intervalo Fixo ({peca})", value=int(val_intervalo), key=f"int_{peca}")
                        novos_dados_manu[peca] = {"ultima_troca": nova_ultima, "intervalo": novo_inter}
                        
                    if st.form_submit_button("Salvar Regras de Manutenção"):
                        db["motos"][moto_selecionada]["km_atual"] = km_hoje
                        db["motos"][moto_selecionada]["manutencao"] = novos_dados_manu
                        salvar_dados_nuvem(db)
                        st.success("KM e Regras salvas com sucesso!")
                        st.rerun()
