import subprocess
import sys
import os

def main():
    # Garante que estamos no diretório correto para o import config funcionar
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    scripts = ["data_fetch.py", "markowitz_fund.py", "macro_tilt_fund.py"]
    
    for s in scripts:
        print(f"Executando {s}...")
        subprocess.run([sys.executable, s], check=True)
        
    print("Sistema Quant V2 atualizado com sucesso.")

if __name__ == "__main__":
    main()
