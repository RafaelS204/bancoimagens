import streamlit as st
from indexador import gerar_embeddings, limpar_e_gerar_tudo, pesquisar_por_imagem, pesquisar_por_texto
from PIL import Image
import os

st.set_page_config(page_title="Banco de imagens", layout="wide")
st.title("🗂️ Gerir índices")

col1, col2 = st.columns([1,4])
with col1:
    if st.button("🔄 Atualizar (add novos)"):
        with st.spinner("A atualizar índices com novas imagens..."):
            try:
                gerar_embeddings(resetar=False)
                st.success("Atualização concluída!")
            except Exception as e:
                st.error(f"Erro ao atualizar o índice: {e}")

with col2:
    if st.button("🧹 Limpar e recriar"):
        with st.spinner("A recriar todos os índices..."):
            try:
                limpar_e_gerar_tudo()
                st.success("Índice recriado do zero!")
            except Exception as e:
                st.error(f"Erro ao recriar o índice: {e}")

def mostrar_caminho_com_botao(caminho):
    st.write(f"`{caminho}`")

st.title("🔍 Pesquisa de Imagens (Local)")

col_text, col_aux = st.columns([3, 2])
    
with col_text:
    #st.markdown("### Pesquisa por texto")
    query = st.text_input("Descrição (ex: 'gato na praia')")
    if query:
        try:
            resultados = pesquisar_por_texto(query, k=25)
            if resultados:
                st.markdown("### Resultados:")
                cols_por_linha = 5
                for i, path in enumerate(resultados):
                    if i % cols_por_linha == 0:
                        cols = st.columns(cols_por_linha)
                    col = cols[i % cols_por_linha]  
                    with col:
                        if os.path.exists(path):
                            with Image.open(path) as img:
                                st.image(img, caption=os.path.basename(path), use_container_width=True)
                            mostrar_caminho_com_botao(path)
                        else:
                            st.warning(f"Imagem não encontrada: {path}")
            else:
                st.info("Nenhum resultado encontrado para essa pesquisa.")
        except Exception as e:
            st.error(f"Erro na pesquisa: {e}")

col_img, col_aux = st.columns([3, 2])

with col_img:
    #st.header("Pesquisa por imagem")
    uploaded_file = st.file_uploader("Carrega uma imagem para pesquisar", type=['png', 'jpg', 'jpeg'])
    st.markdown("---")
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert('RGB')
            st.image(image, caption="Imagem carregada", use_container_width=True)
            
            with st.spinner("A pesquisar imagens semelhantes..."):
                resultados_imagem = pesquisar_por_imagem(image, k=25)
            
            if resultados_imagem:
                st.markdown("### Resultados da pesquisa por imagem:")
                cols_por_linha = 5
                for i, path in enumerate(resultados_imagem):
                    if i % cols_por_linha == 0:
                        cols = st.columns(cols_por_linha)
                    col = cols[i % cols_por_linha]
                    with col:
                        if os.path.exists(path):
                            with Image.open(path) as img:
                                st.image(img, caption=os.path.basename(path), use_container_width=True)
                            mostrar_caminho_com_botao(path)
                        else:
                            st.warning(f"Imagem não encontrada: {path}")
            else:
                st.info("Nenhuma imagem semelhante encontrada.")
        except Exception as e:
            st.error(f"Erro na pesquisa por imagem: {e}")
