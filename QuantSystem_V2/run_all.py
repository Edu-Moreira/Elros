import subprocess
import sys
import os

def main():
    # Garante que estamos no diretório correto para o import config funcionar
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    # Criar pasta de output se não existir
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
    
    scripts = ["data_fetch.py", "markowitz_fund.py", "macro_tilt_fund.py"]
    
    for s in scripts:
        print(f"--- Executando {s} ---")
        # Usamos stdout=None para que o erro apareça direto no console do GitHub Actions
        result = subprocess.run([sys.executable, s], check=True)
        
    print("Sistema Quant V2 atualizado com sucesso.")

if __name__ == "__main__":
    main()
