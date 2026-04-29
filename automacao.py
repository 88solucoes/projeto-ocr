import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES ---
CAMINHO_PROJETO = os.getcwd()
URL_APP = "http://localhost:8501"
PASTA_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")

def iniciar_docker():
    print("🚀 Iniciando Docker...")
    # Roda o comando em uma nova janela (shell)
    subprocess.Popen(["docker", "run", "-p", "8501:8501", "--rm", "conversor-ocr"], 
                     shell=True)
    print("⏳ Aguardando servidor Streamlit subir...")
    time.sleep(10) # Tempo para o container ligar

def automatizar_browser():
    # Encontrar o último arquivo baixado na pasta Downloads
    arquivos = [os.path.join(PASTA_DOWNLOADS, f) for f in os.listdir(PASTA_DOWNLOADS)]
    ultimo_download = max(arquivos, key=os.path.getctime)
    
    print(f"📄 Arquivo selecionado para OCR: {ultimo_download}")

    # Configurar o Chrome
    options = webdriver.ChromeOptions()
    # Opcional: configurar pasta de download padrão
    prefs = {"download.default_directory": PASTA_DOWNLOADS}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1. Abrir o navegador no servidor local
        driver.get(URL_APP)
        time.sleep(5)

        # 2. Localizar o input de upload (invisível no Streamlit, mas o Selenium acha)
        upload_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        upload_input.send_keys(ultimo_download)
        print("✅ Arquivo enviado para a página.")
        time.sleep(2)

        # 3. Clicar no botão de Iniciar Processamento
        # Buscamos pelo texto dentro do botão
        botoes = driver.find_elements(By.TAG_NAME, "button")
        for btn in botoes:
            if "Iniciar Processamento" in btn.text:
                btn.click()
                break
        
        print("⚙️ Processando OCR...")
        
        # 4. Aguardar o botão de Download aparecer (máximo 60 segundos)
        start_time = time.time()
        while time.time() - start_time < 60:
            botoes_atualizados = driver.find_elements(By.TAG_NAME, "button")
            download_btn = [b for b in botoes_atualizados if "Baixar PDF" in b.text]
            
            if download_btn:
                print("✅ OCR Concluído! Baixando...")
                download_btn[0].click()
                time.sleep(5) # Espera o download terminar
                break
            time.sleep(2)

    finally:
        print("🏁 Automação finalizada.")
        driver.quit()

if __name__ == "__main__":
    iniciar_docker()
    automatizar_browser()