# screens/noticias.py
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
import webbrowser
from kivy.clock import Clock

class NoticiasScreen(Screen):
    def on_enter(self, *args):
        Clock.schedule_once(self.mostrar_conteudo, 0)  # ✅ Força atualização da tela

    def mostrar_conteudo(self, dt):
        self.clear_widgets()
        self.add_widget(Label(
            text="Abrindo site do DEGEO...",
            font_size=20,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.5,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        ))
        webbrowser.open("https://geologia.ufc.br/pt/category/noticias/ ", autoraise=True)