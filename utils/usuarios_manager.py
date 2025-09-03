# utils/usuarios_manager.py
import json
import os
import hashlib

class UsuariosManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.usuarios_file = os.path.join(data_dir, "usuarios.json")
        
        # Cria diretório de dados se não existir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Inicializa arquivo de usuários se não existir
        if not os.path.exists(self.usuarios_file):
            self._salvar_usuarios([])
    
    def _carregar_usuarios(self):
        try:
            with open(self.usuarios_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _salvar_usuarios(self, usuarios):
        with open(self.usuarios_file, "w") as f:
            json.dump(usuarios, f, indent=2)
    
    def cadastrar_usuario(self, nome, email, senha, tipo):
        """Cadastra um novo usuário (aluno ou professor)"""
        usuarios = self._carregar_usuarios()
        
        # Verifica se o email já está cadastrado
        if any(u["email"] == email for u in usuarios):
            return False, "Email já cadastrado"
        
        # Cria hash da senha
        senha_hash = self._hash_senha(senha)
        
        # Cria novo usuário
        novo_usuario = {
            "nome": nome,
            "email": email,
            "senha": senha_hash,
            "tipo": tipo  # 'aluno' ou 'professor'
        }
        
        usuarios.append(novo_usuario)
        self._salvar_usuarios(usuarios)
        
        return True, "Cadastro realizado com sucesso"
    
    def autenticar_usuario(self, email, senha):
        """Autentica um usuário"""
        usuarios = self._carregar_usuarios()
        
        senha_hash = self._hash_senha(senha)
        
        for usuario in usuarios:
            if usuario["email"] == email and usuario["senha"] == senha_hash:
                return True, usuario
        
        return False, "Email ou senha incorretos"
    
    def alterar_senha(self, email, nova_senha):
        """Altera a senha de um usuário"""
        usuarios = self._carregar_usuarios()
        
        # Procura o usuário
        usuario_idx = next((i for i, u in enumerate(usuarios) if u["email"] == email), None)
        
        if usuario_idx is None:
            return False, "Usuário não encontrado"
        
        # Atualiza a senha
        usuarios[usuario_idx]["senha"] = self._hash_senha(nova_senha)
        
        # Salva as alterações
        self._salvar_usuarios(usuarios)
        
        return True, "Senha alterada com sucesso"
    
    def _hash_senha(self, senha):
        """Gera um hash seguro para a senha"""
        return hashlib.sha256(senha.encode()).hexdigest()