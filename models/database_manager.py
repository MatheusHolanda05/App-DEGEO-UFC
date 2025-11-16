import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database_models import Base

logger = logging.getLogger('degeo_app')

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Caminho: projeto/data/degeo_app.db
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, "data", "degeo_app.db")
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Cria todas as tabelas do banco de dados"""
        try:
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            Base.metadata.create_all(self.engine)
            logger.info(f"Tabelas criadas em: {self.db_path}")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise
    
    def get_session(self):
        """Retorna uma nova sessão do banco de dados"""
        return self.Session()