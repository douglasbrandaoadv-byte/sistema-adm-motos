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
