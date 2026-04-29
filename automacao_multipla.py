import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES ---
URL_APP = "http://localhost:8501"
PASTA_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")

def iniciar_docker():
    print("🚀 Iniciando Docker...")
    # Verifica se o container já está rodando para não dar erro de porta
    subprocess.Popen(["docker", "run", "-p", "8501:8501", "--rm", "conversor-ocr"], 
                     shell=True, stdout=subprocess.DEVNULL)
    print("⏳ Aguardando servidor Streamlit subir (15s)...")
    time.sleep(15)

def buscar_ultimos_arquivos(quantidade):
    # Lista apenas arquivos PDF na pasta Downloads ordenados por data de criação
    arquivos = [os.path.join(PASTA_DOWNLOADS, f) for f in os.listdir(PASTA_DOWNLOADS) if f.lower().endswith('.pdf')]
    arquivos.sort(key=os.path.getctime, reverse=True)
    return arquivos[:quantidade]

def processar_arquivos(lista_arquivos):
    options = webdriver.ChromeOptions()
    # Mantém a pasta de download padrão
    prefs = {"download.default_directory": PASTA_DOWNLOADS}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(URL_APP)
        time.sleep(5)

        for i, caminho_arquivo in enumerate(lista_arquivos):
            nome_arq = os.path.basename(caminho_arquivo)
            print(f"\n🔄 [{i+1}/{len(lista_arquivos)}] Processando: {nome_arq}")

            # 1. Upload do arquivo
            upload_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            upload_input.send_keys(caminho_arquivo)
            time.sleep(2)

            # 2. Clicar no botão de Iniciar
            botoes = driver.find_elements(By.TAG_NAME, "button")
            for btn in botoes:
                if "Iniciar Processamento" in btn.text:
                    btn.click()
                    break
            
            # 3. Aguardar conversão e botão de download
            print("⚙️ Executando OCR... Aguarde.")
            concluido = False
            timeout = 120 # 2 minutos por arquivo
            start_wait = time.time()
            
            while time.time() - start_wait < timeout:
                botoes_atuais = driver.find_elements(By.TAG_NAME, "button")
                download_btn = [b for b in botoes_atuais if "Baixar PDF" in b.text]
                
                if download_btn:
                    print(f"✅ Concluído! Baixando OCR_{nome_arq}")
                    download_btn[0].click()
                    time.sleep(5) # Tempo para o download completar
                    concluido = True
                    break
                time.sleep(3)
            
            if not concluido:
                print(f"⚠️ Aviso: O tempo limite para {nome_arq} esgotou.")

            # 4. Recarregar a página para o próximo arquivo (limpar o estado do Streamlit)
            driver.refresh()
            time.sleep(3)

    finally:
        print("\n🏁 Todas as tarefas concluídas.")
        driver.quit()

if __name__ == "__main__":
    # Pergunta ao usuário antes de tudo
    try:
        n = int(input("🔢 Quantos arquivos recentes da pasta Downloads você quer processar? "))
        arquivos_para_processar = buscar_ultimos_arquivos(n)
        
        if not arquivos_para_processar:
            print("❌ Nenhum arquivo PDF encontrado na pasta Downloads.")
        else:
            print(f"\n📂 Arquivos encontrados para processar:")
            for a in arquivos_para_processar: print(f" - {os.path.basename(a)}")
            
            confirmar = input("\nConfirma o início? (s/n): ")
            if confirmar.lower() == 's':
                iniciar_docker()
                processar_arquivos(arquivos_para_processar)
            else:
                print("Operação cancelada.")
    except ValueError:
        print("Por favor, digite um número válido.")