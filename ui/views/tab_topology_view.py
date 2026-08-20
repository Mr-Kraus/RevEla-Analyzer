import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        if not self.layout():
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            self.browser = QWebEngineView()
            self.browser.setMinimumHeight(700) # Expande a altura vertical do componente
            self.browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            
            layout.addWidget(self.browser)

    def setup_connections(self):
        self.viewmodel.topology_ready.connect(self.draw_graph)
        self.viewmodel.error_occurred.connect(self.show_error)

    def load_case(self, case_id: str):
        self.browser.setHtml(
            "<body style='background-color:#F5F6FA; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;'>"
            "<h2 style='font-family: Arial; color:#7F8C8D;'>Montando Rede Elétrica...</h2>"
            "</body>"
        )
        self.viewmodel.load_topology(case_id)

    def draw_graph(self, topology_data: dict):
        nodes = topology_data.get("nodes", [])
        edges = topology_data.get("edges", [])

        print(f"DEBUG TOPOLOGY VIEW: Desenhando {len(nodes)} nos e {len(edges)} arestas.")

        if not nodes:
            self.show_error("Nenhum dado de topologia encontrado.")
            return

        nx_graph = nx.Graph()

        for node in nodes:
            node_id = str(node.get("id"))
            label = str(node.get("label", node_id))
            group = str(node.get("group", "load"))
            
            color = "#27AE60" if group.lower() == "generation" else "#3498DB"
            nx_graph.add_node(node_id, label=label, color=color, size=22)

        for edge in edges:
            u = str(edge.get("from"))
            v = str(edge.get("to"))
            label = str(edge.get("label", ""))
            if u and v and u != "None" and v != "None":
                nx_graph.add_edge(u, v, title=label, color="#2C3E50", width=2)

        net = Network(height="100%", width="100%", bgcolor="#F5F6FA", font_color="#2C3E50", cdn_resources="remote")
        net.from_nx(nx_graph)
        
        # Estilização explícita de nós, arestas e física do Vis.js
        net.set_options("""
        var options = {
          "nodes": {
            "font": {"size": 13, "color": "#2C3E50"}
          },
          "edges": {
            "color": {"color": "#34495E", "highlight": "#E74C3C", "hover": "#E74C3C"},
            "width": 2,
            "smooth": {"enabled": true, "type": "continuous"}
          },
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -60,
              "centralGravity": 0.015,
              "springLength": 120,
              "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
          },
          "interaction": {
             "navigationButtons": true,
             "hover": true
          }
        }
        """)

        html_path = os.path.abspath("temp_topology.html")
        net.save_graph(html_path)

        # Injeta CSS para garantir que a tela ocupe 100% da altura da janela sem cortar no eixo Y
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()

            custom_css = """
            <style>
                html, body { height: 100vh !important; width: 100vw !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important; background-color: #F5F6FA !important; }
                #mynetwork { height: 100vh !important; width: 100vw !important; border: none !important; }
            </style>
            """
            content = content.replace("</head>", f"{custom_css}</head>")

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)

        self.browser.setUrl(QUrl.fromLocalFile(html_path))

    def show_error(self, msg):
        QMessageBox.warning(self, "Aviso de Topologia", msg)