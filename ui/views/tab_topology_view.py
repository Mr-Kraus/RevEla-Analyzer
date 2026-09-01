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
            self.browser.setMinimumHeight(700)
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
            "<h2 style='font-family: Arial; color:#7F8C8D;'>Montando Rede Elétrica e Analisando Layout...</h2>"
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

        # 1. ESTILIZAÇÃO DOS NÓS (BARRAS E GERADORES)
        for node in nodes:
            node_id = str(node.get("id"))
            label = str(node.get("label", node_id))
            title = node.get("title", "")
            group = str(node.get("group", "load"))
            
            # Diferenciação Visual
            if group.lower() == "generation":
                color = "#F59E0B"   # Laranja para Geração
                shape = "hexagon"   # Formato Hexagonal
                size = 35           # Tamanho maior para destacar
            else:
                color = "#3498DB"   # Azul para Carga/Barra Comum
                shape = "dot"       # Formato circular padrão
                size = 20

            nx_graph.add_node(node_id, label=label, title=title, color=color, size=size, shape=shape)

        # 2. ESTILIZAÇÃO DAS ARESTAS (LINHAS E TRAFOS)
        for edge in edges:
            u = str(edge.get("from"))
            v = str(edge.get("to"))
            label = str(edge.get("label", ""))
            title = edge.get("title", "")
            
            # Verifica o tipo de conexão (assumindo que seu viewmodel repassa essa flag)
            edge_type = str(edge.get("type", "")) 

            if u and v and u != "None" and v != "None":
                if edge_type.lower() == "transformer" or "trafo" in title.lower() or "trafo" in label.lower():
                    # Transformadores: Linhas verdes e Tracejadas
                    nx_graph.add_edge(u, v, title=title, label=label, color="#10B981", width=2.5, dashes=True)
                else:
                    # Linhas de Transmissão: Linhas cinzas contínuas
                    nx_graph.add_edge(u, v, title=title, label=label, color="#94A3B8", width=1.5)

        net = Network(height="100%", width="100%", bgcolor="#F5F6FA", font_color="#2C3E50", cdn_resources="remote")
        net.from_nx(nx_graph)
        
        # 3. MOTOR DE FÍSICA OTIMIZADO PARA REDES GIGANTES (JSON ESTRITO)
        net.set_options("""
        {
            "physics": {
                "solver": "forceAtlas2Based",
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.005,
                    "springLength": 150,
                    "springConstant": 0.05
                },
                "stabilization": {
                    "enabled": true,
                    "iterations": 2000,
                    "updateInterval": 50,
                    "fit": true
                }
            }
        }
        """)

        html_path = os.path.abspath("temp_topology.html")
        net.save_graph(html_path)

        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()

            custom_css = """
            <style>
                html, body { height: 100vh !important; width: 100vw !important; margin: 0 !important; overflow: hidden !important; background-color: #F5F6FA !important; }
                #mynetwork { height: 100vh !important; width: 100vw !important; border: none !important; }
                
                /* Barra de Busca */
                #search-container {
                    position: absolute; top: 20px; left: 20px; z-index: 1000;
                    background: white; padding: 10px; border-radius: 8px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: flex; gap: 10px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                #search-input {
                    padding: 8px; border: 1px solid #BDC3C7; border-radius: 4px; width: 250px; font-size: 14px;
                }
                #search-btn {
                    padding: 8px 15px; background: #3498DB; color: white; border: none;
                    border-radius: 4px; cursor: pointer; font-weight: bold;
                }
                #search-btn:hover { background: #2980B9; }
                
                /* Modal de Info */
                #info-panel {
                    position: absolute; top: 20px; right: 20px; width: 320px; background: white; 
                    border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); 
                    padding: 20px; display: none; z-index: 1000; font-family: 'Segoe UI', Arial, sans-serif;
                    border-top: 4px solid #3498DB;
                }
                #info-panel h3 { margin-top: 0; color: #2C3E50; font-size: 18px; border-bottom: 1px solid #ECF0F1; padding-bottom: 10px;}
                #info-panel .content { color: #34495E; font-size: 14px; line-height: 1.6; }
                #close-btn { 
                    margin-top: 15px; width: 100%; padding: 8px; border: none; 
                    background: #ECF0F1; color: #7F8C8D; border-radius: 4px; cursor: pointer; font-weight: bold;
                }
                #close-btn:hover { background: #E74C3C; color: white; }
            </style>
            """
            
            custom_html = """
            <div id="search-container">
                <input type="text" id="search-input" list="node-datalist" placeholder="Buscar barra por nome ou ID...">
                <datalist id="node-datalist"></datalist>
                <button id="search-btn" onclick="searchNode()">Buscar</button>
            </div>
            
            <div id="info-panel">
                <h3 id="info-title">Detalhes do Elemento</h3>
                <div id="info-content" class="content"></div>
                <button id="close-btn" onclick="document.getElementById('info-panel').style.display='none'">Fechar</button>
            </div>
            """

            # 4. EVENTOS JS PARA DESLIGAR A FÍSICA
            custom_js = """
            <script type="text/javascript">
                
                // --- CONGELAMENTO DA REDE ---
                // Evento 1: Desliga a gravidade assim que a tela terminar de calcular (2000 iterações invisíveis)
                network.on("stabilizationIterationsDone", function () {
                    network.setOptions({ physics: false });
                });

                // Evento 2: Se o usuário clicar e arrastar qualquer nó durante ou após a animação, 
                // congela a física imediatamente para garantir fluidez total.
                network.on("dragStart", function (params) {
                    if (params.nodes.length > 0) {
                        network.setOptions({ physics: false });
                    }
                });

                // Popula as opções de autocompletar na barra de busca
                setTimeout(function() {
                    var datalist = document.getElementById('node-datalist');
                    var nodesArray = nodes.get();
                    nodesArray.forEach(function(n) {
                        var option = document.createElement('option');
                        option.value = n.label;
                        datalist.appendChild(option);
                    });
                }, 1000); 

                function searchNode() {
                    var searchTerm = document.getElementById('search-input').value.toLowerCase();
                    var foundNode = null;
                    var nodesArray = nodes.get();
                    
                    for (var i = 0; i < nodesArray.length; i++) {
                        if (nodesArray[i].label.toLowerCase().includes(searchTerm) || 
                            nodesArray[i].id.toLowerCase().includes(searchTerm)) {
                            foundNode = nodesArray[i].id;
                            break;
                        }
                    }

                    if (foundNode) {
                        network.focus(foundNode, {
                            scale: 1.5,
                            animation: { duration: 1000, easingFunction: "easeInOutQuad" }
                        });
                        network.selectNodes([foundNode]);
                        
                        var nodeObj = nodes.get(foundNode);
                        document.getElementById('info-title').innerHTML = "Barra: " + (nodeObj.label || foundNode);
                        document.getElementById('info-content').innerHTML = nodeObj.title || "Sem informações.";
                        document.getElementById('info-panel').style.display = 'block';
                    } else {
                        alert("Barra não encontrada!");
                    }
                }

                document.getElementById('search-input').addEventListener('keypress', function (e) {
                    if (e.key === 'Enter') {
                        searchNode();
                    }
                });

                network.on("click", function (params) {
                    var panel = document.getElementById("info-panel");
                    var titleEl = document.getElementById("info-title");
                    var contentEl = document.getElementById("info-content");

                    if (params.nodes.length > 0) {
                        var nodeId = params.nodes[0];
                        var node = nodes.get(nodeId);
                        titleEl.innerHTML = "Barra: " + (node.label || nodeId);
                        contentEl.innerHTML = node.title || "Sem informações registradas.";
                        panel.style.display = "block";
                    } else if (params.edges.length > 0) {
                        var edgeId = params.edges[0];
                        var edge = edges.get(edgeId);
                        titleEl.innerHTML = "Conexão: " + (edge.label || edgeId);
                        contentEl.innerHTML = edge.title || "Sem informações registradas.";
                        panel.style.display = "block";
                    } else {
                        panel.style.display = "none";
                    }
                });
            </script>
            </body>
            """

            content = content.replace("</head>", f"{custom_css}</head>")
            content = content.replace("<body>", f"<body>{custom_html}")
            content = content.replace("</body>", custom_js)

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)

        self.browser.setUrl(QUrl.fromLocalFile(html_path))

    def show_error(self, msg):
        QMessageBox.warning(self, "Aviso de Topologia", msg)