# test_usuario_repository.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repositories.usuario_repository import UsuarioRepository

def test_usuario_repository():
    print("🧪 Testando UsuarioRepository...")
    
    repo = UsuarioRepository()
    
    # Teste 1: Criar usuário
    print("1. Testando criação de usuário...")
    sucesso, mensagem = repo.criar_usuario(
        nome="Professor Teste",
        email="professor_teste@ufc.br", 
        senha="123456",
        tipo="professor",
        genero="Masculino",
        disciplina="Geologia"
    )
    print(f"   Resultado: {sucesso} - {mensagem}")
    
    # Teste 2: Autenticar usuário
    print("2. Testando autenticação...")
    sucesso, resultado = repo.autenticar_usuario("professor_teste@ufc.br", "123456")
    print(f"   Resultado: {sucesso} - {type(resultado)}")
    
    # Teste 3: Obter professores
    print("3. Testando obtenção de professores...")
    professores = repo.obter_professores()
    print(f"   Professores encontrados: {len(professores)}")
    
    print("✅ Teste do UsuarioRepository concluído!")

if __name__ == "__main__":
    test_usuario_repository()