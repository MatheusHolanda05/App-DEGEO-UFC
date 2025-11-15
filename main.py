# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
import os
import sys

# Adiciona o diretório atual ao PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Telas do Aluno
from screens.login import LoginScreen
from screens.aluno import AlunoHomeScreen
from screens.aluno_aulas import AlunoAulasScreen
from screens.aluno_lista_professores import AlunoListaProfessoresScreen
from screens.aluno_visualizar_aula import AlunoVisualizarAulaScreen

# Telas do Professor
from screens.professor_login import ProfessorLoginScreen
from screens.professor_home import ProfessorHomeScreen
from screens.professor_cadastro import ProfessorCadastroScreen
from screens.professor_recuperar_senha import ProfessorRecuperarSenhaScreen
from screens.professor_codigo_recuperacao import ProfessorCodigoRecuperacaoScreen
from screens.professor_nova_senha import ProfessorNovaSenhaScreen
from screens.professor_criar_aula import ProfessorCriarAulaScreen
from screens.professor_visualizar_aula import ProfessorVisualizarAulasScreen


class DegeoApp(App):
    def build(self):
        sm = ScreenManager()

        # Telas do Aluno
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AlunoHomeScreen(name='aluno_home'))
        sm.add_widget(AlunoAulasScreen(name='aluno_aulas'))
        sm.add_widget(AlunoListaProfessoresScreen(name='aluno_lista_professores'))
        sm.add_widget(AlunoVisualizarAulaScreen(name='aluno_visualizar_aula'))

        # Telas do Professor
        sm.add_widget(ProfessorLoginScreen(name='professor_login'))
        sm.add_widget(ProfessorHomeScreen(name='professor_home'))
        sm.add_widget(ProfessorCadastroScreen(name='professor_cadastro'))
        sm.add_widget(ProfessorRecuperarSenhaScreen(name='professor_recuperar_senha'))
        sm.add_widget(ProfessorCodigoRecuperacaoScreen(name='professor_codigo_recuperacao'))
        sm.add_widget(ProfessorNovaSenhaScreen(name='professor_nova_senha'))
        sm.add_widget(ProfessorCriarAulaScreen(name='professor_criar_aula'))
        sm.add_widget(ProfessorVisualizarAulasScreen(name='professor_visualizar_aulas'))

        Window.size = (360, 640) 
        
        # ✅ ADICIONAR: Inicialização de serviços em background
        self._inicializar_servicos_background() 
        
        return sm

    # ✅ CORREÇÃO: Este método DEVE estar DENTRO da classe DegeoApp
    def _inicializar_servicos_background(self):
        """Inicializa serviços que rodam em background"""
        try:
            from utils.notificacoes_manager import NotificacoesManager
            notificacoes_manager = NotificacoesManager()
            notificacoes_manager.inicializar_servicos()
        except Exception as e:
            print(f"Erro ao inicializar serviços background: {e}")


if __name__ == '__main__':
    DegeoApp().run()