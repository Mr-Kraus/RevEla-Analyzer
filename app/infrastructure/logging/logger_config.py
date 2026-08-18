import logging
import sys

def configure_logging(log_level: str = "INFO"):
    """
    Configura o logger central da aplicação.
    Garante que os logs saiam no formato padrão e suportem o contexto das operações.
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING) # Evita poluição de SQL puro