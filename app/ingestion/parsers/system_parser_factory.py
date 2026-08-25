from app.ingestion.parsers.template_system_parser import TemplateSystemParser

class SystemParserFactory:
    @staticmethod
    def get_parser(software_version: str) -> TemplateSystemParser:
        """
        Retorna a instância configurada do parser dependendo da versão do software.
        """
        if software_version.upper() == "PSMORA":
            # Mapeia as Tags específicas do PSMora para o padrão do REVELA Clássico
            psmora_mapping = {
                "CLGERA": "CL_GERADORA",
                "LINHAS": "LT", # Exemplo: Ajuste para a tag real que o RELEVA usa
                # Adicione outras tags divergentes aqui conforme encontrar
            }
            return TemplateSystemParser(tag_mapping=psmora_mapping)
            
        else:
            # RELEVA (Padrão) - Não precisa de mapeamento, passa dicionário vazio
            return TemplateSystemParser(tag_mapping={})