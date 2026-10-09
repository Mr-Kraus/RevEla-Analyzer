import os

def registrar_arquitetura(diretorio_raiz, arquivo_saida="arquitetura.txt"):
    """
    Escaneia o diretório informado e gera um arquivo .txt 
    com a estrutura de pastas, subpastas e arquivos identados.
    """
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        for raiz, diretorios, arquivos in os.walk(diretorio_raiz):
            # Ignora pastas ocultas, cache e ambientes virtuais comuns
            diretorios[:] = [d for d in diretorios if not d.startswith(('.', '__', 'venv', 'node_modules')) and d.lower() !='revela']
            
            # Calcula o nível de indentação atual
            nivel = raiz.replace(diretorio_raiz, '').count(os.sep)
            indentacao_pasta = '    ' * nivel
            
            # Define o nome da pasta atual
            nome_pasta = os.path.basename(raiz)
            if nome_pasta == '':
                nome_pasta = diretorio_raiz
                
            # Escreve a pasta/subpasta no arquivo
            f.write(f"{indentacao_pasta}[PASTA] {nome_pasta}\n")
            
            # Escreve os arquivos com um nível a mais de indentação
            indentacao_arquivo = '    ' * (nivel + 1)
            for arquivo in sorted(arquivos):
                if not arquivo.startswith('.'): # Ignora arquivos ocultos
                    f.write(f"{indentacao_arquivo}[ARQUIVO] {arquivo}\n")

if __name__ == "__main__":
    # Executa o mapeamento a partir da pasta atual do script
    registrar_arquitetura(".")
    print("Mapeamento concluído! O arquivo 'arquitetura.txt' foi criado.")