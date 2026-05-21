import subprocess
import sys

def main():
    scripts = [
        "funds/data_fetch.py",
        "funds/markowitz_fund.py",
        "funds/macro_tilt_fund.py"
    ]
    
    for script in scripts:
        print(f"--- Executando {script} ---")
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"Erro ao executar {script}. Abortando.")
            sys.exit(1)
            
    print("--- Todos os fundos atualizados com sucesso! ---")

if __name__ == "__main__":
    main()
