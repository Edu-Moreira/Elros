# 📘 Guia de Implementação: Elros Quant System

Este guia detalha como configurar a automação via **GitHub Actions** e o deploy no **Vercel** para que seu dashboard de fundos quantitativos funcione de forma autônoma.

---

## 1. Preparação do Repositório (GitHub)

1. **Crie um repositório** no GitHub (pode ser privado).
2. **Suba os arquivos** das pastas `QuantSystem_V2` e `quant-vercel` para a raiz do repositório.
3. **Configure as Secrets**:
   - Vá em `Settings > Secrets and variables > Actions`.
   - Clique em `New repository secret`.
   - Nome: `FRED_API_KEY`.
   - Valor: Sua chave da API do FRED (Federal Reserve).

---

## 2. Automação (GitHub Actions)

O arquivo `.github/workflows/update_v2.yml` já está configurado. Ele realizará as seguintes ações todos os dias úteis:
1. Ativa um ambiente Python.
2. Instala as dependências do `requirements.txt`.
3. Executa o simulador (`run_all.py`), que baixa dados e recalcula o Markowitz e o Macro Tilt.
4. Salva os novos CSVs na pasta `QuantSystem_V2/output/`.
5. Faz um `commit` e `push` automático dos novos dados para o repositório.

---

## 3. Deploy do Dashboard Web (Vercel)

Para colocar o dashboard Next.js no ar:

1. Vá para [vercel.com](https://vercel.com) e conecte sua conta do GitHub.
2. Importe o repositório do projeto.
3. **Configuração Importante**:
   - No campo **Root Directory**, selecione a pasta `quant-vercel`.
   - Clique em **Deploy**.
4. **Sincronização de Dados**:
   - Sempre que o GitHub Actions atualizar os CSVs, o Vercel detectará a mudança no repositório e fará um novo "Build" automático, atualizando o gráfico no ar com os dados do dia.

---

## 4. Uso Local (Streamlit)

Caso queira rodar o dashboard localmente para testes rápidos:

1. Ative seu ambiente: `micromamba activate quant`.
2. Rode o simulador para garantir dados novos: `python QuantSystem_V2/run_all.py`.
3. Inicie o dashboard: `streamlit run QuantSystem_V2/dashboard.py`.

---

## 5. Estrutura de Arquivos Críticos

- `QuantSystem_V2/config.py`: Altere aqui o universo de ETFs ou os pesos da carteira neutra. Tudo o restante se ajustará sozinho.
- `quant-vercel/src/app/page.tsx`: Edite este arquivo para mudar o design ou os textos do pitch na versão web.
- `QuantSystem_V2/output/`: Contém os dados brutos. **Não delete estes arquivos**, pois o dashboard depende deles.

---

## 🛠 Troubleshooting

- **Gráfico no Vercel não atualiza**: Verifique se o GitHub Action rodou com sucesso. Se ele falhar, os dados não mudam e o Vercel não trigga o build.
- **Erro de Moeda (BRL)**: Certifique-se de que o `data_fetch.py` está conseguindo baixar a PTAX com sucesso.
- **Performance Lenta**: O cálculo de Markowitz pode demorar alguns minutos no GitHub Actions devido à otimização matemática pesada; isso é normal.

---

*Desenvolvido por Antigravity para Eduardo | Rivendell Projetos*
