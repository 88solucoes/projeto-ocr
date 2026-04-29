import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from pypdf import PdfWriter, PdfReader
import io

# Configuração do Tesseract no Docker
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

st.set_page_config(page_title="OCR Lote Pro", page_icon="📄")

# Inicializa o estado da sessão para armazenar resultados
if 'resultados' not in st.session_state:
    st.session_state.resultados = []

st.title("📄 Conversor PDF para OCR (Lote)")

with st.sidebar:
    idioma = st.selectbox("Idioma", ["por", "eng"], format_func=lambda x: "Português" if x=="por" else "Inglês")

uploaded_files = st.file_uploader("Escolha até 10 arquivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 Iniciar Processamento em Lote", use_container_width=True):
        st.session_state.resultados = [] # Limpa resultados anteriores
        
        try:
            barra_geral = st.progress(0)
            
            for idx, file in enumerate(uploaded_files):
                container_status = st.empty()
                container_status.write(f"⏳ Processando ({idx+1}/{len(uploaded_files)}): {file.name}")
                
                # OCR das páginas
                images = convert_from_bytes(file.read(), 300)
                pdf_writer = PdfWriter()
                
                for img in images:
                    page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=idioma, extension='pdf')
                    pdf_writer.add_page(PdfReader(io.BytesIO(page_pdf_bytes)).pages[0])
                
                out_stream = io.BytesIO()
                pdf_writer.write(out_stream)
                
                # Salva no session_state para não perder ao clicar em download
                # Regra de nomeclatura
                st.session_state.resultados.append({
                    "name": f"OCR_{file.name}",
                    "data": out_stream.getvalue()
                })
                
                barra_geral.progress((idx + 1) / len(uploaded_files))
                container_status.empty()

            st.success("✅ Processamento de lote concluído!")
            
        except Exception as e:
            st.error(f"Erro no processamento: {e}")

# Exibe os botões de download se houver resultados no estado da sessão
if st.session_state.resultados:
    st.divider()
    st.subheader("📥 Arquivos Prontos")
    for res in st.session_state.resultados:
        st.download_button(
            label=f"Baixar {res['name']}",
            data=res['data'],
            file_name=res['name'],
            key=res['name'] # Chave única para o Streamlit não se perder
        )