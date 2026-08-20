import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings # <-- Importação de segurança adicionada
from PyQt6.QtCore import QUrl
import networkx as nx
from pyvis.network import Network

from ui.viewmodels.tab_topology_viewmodel import TabTopologyViewModel

class TabTopologyView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = TabTopologyViewModel()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        # 1. ERRO DO LAYOUT RESOLVIDO: Mudamos o nome da variável para não conflitar com o PyQt
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # O Navegador Embutido que vai renderizar o motor de física do Grafo
        self.browser = QWebEngineView()
        
        # 2. PERMISSÕES DE NAVEGADOR: Garantimos que ele pode executar JavaScript da internet
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        
        self.main_layout.addWidget(self.browser)

    def setup_connections(self):
        self.viewmodel.topology_ready.connect(self.draw_graph)
        self.viewmodel.error_occurred.connect(self.show_error)

    def load_case(self, case_id: str):
        # Carrega uma tela de carregamento temporária (com estilo)
        self.browser.setHtml(
            "<body style='background-color:#F5F6FA; display:flex; justify-content:center; align-items:center; height:100vh;'>"
            "<h2 style='font-family: Arial; color:#7F8C8D;'>Montando Rede Elétrica...</h2>"
            "</body>"
        )
        self.viewmodel.load_topology(case_id)

    def draw_graph(self, topology_data: dict):
        nodes = topology_data.get("nodes", [])
        edges = topology_data.get("edges", [])

        if not nodes:
            self.show_error("Nenhum dado de topologia encontrado.")
            return

        nx_graph = nx.Graph()

        for node in nodes:
            node_id = node.get("id")
            label = node.get("label", str(node_id))
            group = node.get("group", "load")
            
            # Cores: Geração (Verde), Carga (Azul)
            color = "#27AE60" if group == "generation" else "#3498DB"
            nx_graph.add_node(node_id, label=label, color=color, size=25)

        for edge in edges:
            u = edge.get("from")
            v = edge.get("to")
            label = edge.get("label", "")
            nx_graph.add_edge(u, v, title=label, color="#BDC3C7", width=3)

        # 3. ERRO DO VIS RESOLVIDO: O comando cdn_resources="remote" força a buscar o script online
        net = Network(height="100%", width="100%", bgcolor="#F5F6FA", font_color="#2C3E50", cdn_resources="remote")
        net.from_nx(nx_graph)
        
        # Opções da física do grafo
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
          },
          "interaction": {
             "navigationButtons": true
          }
        }
        """)

        # Salva o arquivo HTML temporário
        html_path = os.path.abspath("temp_topology.html")
        net.save_graph(html_path)

        # Renderiza no painel do PyQt6
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

    def show_error(self, msg):
        QMessageBox.warning(self, "Aviso de Topologia", msg)