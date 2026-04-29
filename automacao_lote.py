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
    subprocess.Popen(["docker", "run", "-p", "8501:8501", "--rm", "conversor-ocr"], shell=True)
    time.sleep(12)

def buscar_arquivos(n):
    arquivos = [os.path.join(PASTA_DOWNLOADS, f) for f in os.listdir(PASTA_DOWNLOADS) if f.lower().endswith('.pdf')]
    arquivos.sort(key=os.path.getctime, reverse=True)
    return arquivos[:n]

def executar_lote(lista_arquivos):
    options = webdriver.ChromeOptions()
    # Abre o Chrome e mantém os downloads na pasta correta
    prefs = {"download.default_directory": PASTA_DOWNLOADS}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    try:
        driver.get(URL_APP)
        time.sleep(5)

        # 1. Enviar todos os arquivos de uma vez (Upload múltiplo)
        # No Windows/Bash, separamos os caminhos por uma quebra de linha \n
        upload_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        caminhos_concatenados = "\n".join(lista_arquivos)
        
        print(f"📥 Fazendo upload de {len(lista_arquivos)} arquivos...")
        upload_input.send_keys(caminhos_concatenados)
        time.sleep(4)

        # 2. Clicar no botão de Processamento em Lote
        # Usamos XPATH para garantir que achamos o botão pelo texto exato
        btn_processar = driver.find_element(By.XPATH, "//button[contains(., 'Iniciar Processamento em Lote')]")
        btn_processar.click()
        
        print("⚙️ OCR em andamento... Acompanhe a barra de progresso no navegador.")

        # 3. Aguardar o surgimento de TODOS os botões de download
        # O Selenium vai esperar até que a quantidade de botões seja igual à de arquivos enviados
        timeout = 300 # 5 minutos para o lote todo
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Busca botões que começam com "Baixar OCR_"
            botoes_download = driver.find_elements(By.XPATH, "//button[contains(., 'Baixar OCR_')]")
            
            if len(botoes_download) == len(lista_arquivos):
                print(f"✅ Todos os {len(lista_arquivos)} arquivos processados!")
                
                # 4. Clicar em cada botão de download
                for btn in botoes_download:
                    # Rola até o botão para garantir que ele seja visível/clicável
                    driver.execute_script("arguments[0].scrollIntoView();", btn)
                    time.sleep(1)
                    btn.click()
                    print(f"📥 Baixando: {btn.text}")
                
                time.sleep(5) # Tempo final para os downloads terminarem
                break
            
            time.sleep(5) # Checa a cada 5 segundos

    finally:
        print("\n🏁 Processo finalizado.")
        driver.quit()

if __name__ == "__main__":
    n = int(input("Quantos arquivos recentes do Download deseja converter? "))
    arquivos = buscar_arquivos(n)
    if arquivos:
        iniciar_docker()
        executar_lote(arquivos)
    else:
        print("Nenhum PDF encontrado.")