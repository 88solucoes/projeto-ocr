import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from pypdf import PdfWriter, PdfReader
import io
import gc

# Configuração do Tesseract no Docker
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

st.set_page_config(page_title="OCR Conversor", page_icon="📄")

if 'resultados' not in st.session_state:
    st.session_state.resultados = []

st.title("📄 Conversor PDF para OCR (Lote)")

with st.sidebar:
    idioma = st.selectbox("Idioma", ["por", "eng"], format_func=lambda x: "Português" if x=="por" else "Inglês")

uploaded_files = st.file_uploader("Escolha até 10 arquivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 Iniciar Processamento em OCR", use_container_width=True):
        st.session_state.resultados = [] 
        
        try:
            barra_geral = st.progress(0)
            
            for idx, file in enumerate(uploaded_files):
                container_status = st.empty()
                container_status.write(f"⏳ Processando ({idx+1}/{len(uploaded_files)}): {file.name}")
                
                # 1. Redução de DPI para 150 (Essencial para o Render Free)
                images = convert_from_bytes(file.read(), 150)
                pdf_writer = PdfWriter()
                
                for img in images:
                    page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=idioma, extension='pdf')
                    pdf_writer.add_page(PdfReader(io.BytesIO(page_pdf_bytes)).pages[0])
                    # Limpa a memória da página imediatamente
                    del page_pdf_bytes
                
                out_stream = io.BytesIO()
                pdf_writer.write(out_stream)
                
                st.session_state.resultados.append({
                    "name": f"OCR_{file.name}",
                    "data": out_stream.getvalue()
                })
                
                # Atualiza progresso
                barra_geral.progress((idx + 1) / len(uploaded_files))
                container_status.empty()
                
                # 2. LIMPEZA CRÍTICA (Dentro do loop de arquivos)
                del images
                gc.collect() # Força o Python a liberar a RAM agora

            st.success("✅ Processamento de lote concluído!")
            
        except Exception as e:
            st.error(f"Erro no processamento: {e}")

# Exibe os botões de download
if st.session_state.resultados:
    st.divider()
    st.subheader("📥 Arquivos Prontos")
    for res in st.session_state.resultados:
        st.download_button(
            label=f"Baixar {res['name']}",
            data=res['data'],
            file_name=res['name'],
            key=res['name']
        )