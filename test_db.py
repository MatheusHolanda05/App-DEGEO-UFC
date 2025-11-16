# test_db.py
import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database_manager import DatabaseManager

def test_database():
    try:
        print("🧪 Testando criação do banco de dados...")
        
        db_manager = DatabaseManager()
        print("✅ Banco de dados criado com sucesso!")
        print(f"📍 Local: {db_manager.db_path}")
        
        # Testa uma sessão
        session = db_manager.get_session()
        session.close()
        print("✅ Sessão do banco testada com sucesso!")
        
        # Verifica se o arquivo foi criado
        if os.path.exists(db_manager.db_path):
            print("✅ Arquivo do banco criado fisicamente!")
            file_size = os.path.getsize(db_manager.db_path)
            print(f"📊 Tamanho do arquivo: {file_size} bytes")
        else:
            print("❌ Arquivo do banco NÃO foi criado!")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()