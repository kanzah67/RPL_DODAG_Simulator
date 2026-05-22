import sys
import random
import math

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QFormLayout,
    QStackedWidget, QMessageBox, QTableWidget,
    QTableWidgetItem, QTextEdit, QDialog, QComboBox,
    QFrame, QHeaderView, QMenu, QScrollArea
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class RPLSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPL DODAG Simulator")
        self.resize(1500, 850)

        self.current_theme = "Light"
        self.nodes = []
        self.sink = None
        self.area_size = 0
        self.node_count = 0
        self.communication_range = 0
        self.initial_energy = 0
        self.network_load = 0
        self.show_neighbors = False
        self.show_dodag = False
        self.show_packets = False
        self.highlight_path = []

        # ── Create all shared widgets FIRST before any page ──
        self.node_table = QTableWidget()
        self.node_table.setColumnCount(8)
        self.node_table.setHorizontalHeaderLabels([
            "ID", "X", "Y", "Energy\n(J)", "Load\n(pkts)", "Rank", "Parent", "Dist\n(m)"
        ])
        self.node_table.setMinimumHeight(300)
        self.node_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        hdr = self.node_table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.figure = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)

        self.info_label = QLabel("✅ Simulation Ready")
        self.info_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.path_label = QLabel("Highlighted Path: None")
        self.path_label.setStyleSheet(
            "font-size: 12px; color: #2563eb; font-weight: bold;"
        )

        self.node_selector = QComboBox()
        self.node_selector.addItem("Select Node")
        self.node_selector.setFixedWidth(170)
        self.node_selector.setFixedHeight(32)

        self.info_labels_widget = QLabel(
            "Area Size:\nNodes:\nRange:\nNetwork Load:\nInitial Energy:"
        )
        self.info_labels_widget.setStyleSheet("font-size: 14px;")

        self.info_data_widget = QLabel("\n\n\n\n")
        self.info_data_widget.setStyleSheet(
            "font-size: 14px; color: #2563eb; font-weight: bold;"
        )

        # ── Build pages ──
        self.stack = QStackedWidget()
        self.front_page = self.create_front_page()
        self.input_page = self.create_input_page()
        self.simulation_page = self.create_simulation_page()

        self.stack.addWidget(self.front_page)
        self.stack.addWidget(self.input_page)
        self.stack.addWidget(self.simulation_page)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.apply_theme("Light")

    # ─────────────────────────────────────────
    #  THEME
    # ─────────────────────────────────────────
    def apply_theme(self, theme):
        self.current_theme = theme
        if theme == "Dark":
            self.setStyleSheet("""
                QWidget { background-color: #0d1117; color: #c9d1d9; font-family: Arial; }
                QFrame#homeCard, QFrame#card {
                    background-color: #161b22; border-radius: 18px; border: 1px solid #30363d;
                }
                QLabel { color: #c9d1d9; }
                QPushButton {
                    background-color: #1f6feb; color: white; padding: 7px;
                    border-radius: 8px; font-size: 13px; font-weight: bold;
                }
                QPushButton:hover { background-color: #388bfd; }
                QLineEdit, QComboBox {
                    background-color: #21262d; color: #c9d1d9; padding: 6px;
                    border: 1px solid #30363d; border-radius: 8px; font-size: 13px;
                }
                QComboBox QAbstractItemView {
                    background-color: #21262d; color: #c9d1d9;
                    selection-background-color: #1f6feb; border: 1px solid #30363d;
                }
                QTextEdit {
                    background-color: #21262d; color: #c9d1d9;
                    border: 1px solid #30363d; border-radius: 8px; font-size: 12px;
                }
                QTableWidget {
                    background-color: #21262d; color: #c9d1d9;
                    gridline-color: #30363d; border-radius: 8px; font-size: 12px;
                }
                QTableWidget::item:selected { background-color: #1f6feb; color: white; }
                QHeaderView::section {
                    background-color: #161b22; color: #58a6ff;
                    font-weight: bold; padding: 5px; border: 1px solid #30363d;
                }
                QScrollArea { border: none; background: transparent; }
                QMenu {
                    background-color: #161b22; color: #c9d1d9;
                    border: 1px solid #30363d; padding: 8px;
                }
                QMenu::item { padding: 8px 28px; font-size: 14px; }
                QMenu::item:selected { background-color: #1f6feb; color: white; }
            """)
            try:
                self.figure.patch.set_facecolor("#161b22")
                ax = self.figure.gca()
                ax.set_facecolor("#21262d")
                ax.tick_params(colors="#c9d1d9")
                ax.xaxis.label.set_color("#c9d1d9")
                ax.yaxis.label.set_color("#c9d1d9")
                ax.title.set_color("#c9d1d9")
                self.canvas.draw()
            except Exception:
                pass
        else:
            self.setStyleSheet("""
                QWidget { background-color: #f4f7fb; color: #0f172a; font-family: Arial; }
                QFrame#homeCard, QFrame#card {
                    background-color: white; border-radius: 18px; border: 1px solid #dbeafe;
                }
                QLabel { color: #0f172a; }
                QPushButton {
                    background-color: #2563eb; color: white; padding: 7px;
                    border-radius: 8px; font-size: 13px; font-weight: bold;
                }
                QPushButton:hover { background-color: #1e40af; }
                QLineEdit, QComboBox {
                    background-color: white; color: black; padding: 6px;
                    border: 1px solid #cbd5e1; border-radius: 8px; font-size: 13px;
                }
                QComboBox QAbstractItemView {
                    background-color: white; color: black;
                    selection-background-color: #2563eb; border: 1px solid #cbd5e1;
                }
                QTextEdit {
                    background-color: white; color: black;
                    border: 1px solid #cbd5e1; border-radius: 8px; font-size: 12px;
                }
                QTableWidget {
                    background-color: white; color: black;
                    gridline-color: #cbd5e1; border-radius: 8px; font-size: 12px;
                }
                QTableWidget::item:selected { background-color: #2563eb; color: white; }
                QHeaderView::section {
                    background-color: #eff6ff; color: black;
                    font-weight: bold; padding: 5px; font-size: 12px;
                }
                QScrollArea { border: none; background: transparent; }
                QMenu {
                    background-color: white; color: #0f172a;
                    border: 1px solid #cbd5e1; padding: 8px;
                }
                QMenu::item { padding: 8px 28px; font-size: 14px; }
                QMenu::item:selected { background-color: #eff6ff; color: #2563eb; }
            """)
            try:
                self.figure.patch.set_facecolor("#ffffff")
                ax = self.figure.gca()
                ax.set_facecolor("#ffffff")
                ax.tick_params(colors="#0f172a")
                ax.xaxis.label.set_color("#0f172a")
                ax.yaxis.label.set_color("#0f172a")
                ax.title.set_color("#0f172a")
                self.canvas.draw()
            except Exception:
                pass

    # ─────────────────────────────────────────
    #  FRONT PAGE
    # ─────────────────────────────────────────
    def create_front_page(self):
        page = QWidget()
        outer = QVBoxLayout()
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("homeCard")
        card.setFixedWidth(650)

        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(45, 45, 45, 45)
        lay.setSpacing(18)

        logo = QLabel("RPL")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(110, 110)
        logo.setStyleSheet("""
            QLabel {
                background-color: #2563eb; color: white;
                border-radius: 55px; font-size: 30px; font-weight: bold;
            }
        """)

        title = QLabel("RPL DODAG Simulator")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 40px; font-weight: bold;")

        subtitle = QLabel("Desktop-Based IoT Routing Simulator")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 17px; color: #2563eb;")

        desc = QLabel(
            "A visual simulation tool for RPL-based DODAG formation in IoT networks.\n"
            "Create nodes, add a sink, discover neighbors, build routing paths,\n"
            "and analyze energy, distance, packet forwarding, and network performance."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 14px;")

        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Theme:")
        theme_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark"])
        self.theme_selector.currentTextChanged.connect(self.apply_theme)
        theme_row.addStretch()
        theme_row.addWidget(theme_lbl)
        theme_row.addWidget(self.theme_selector)
        theme_row.addStretch()

        start_btn = QPushButton("Start Simulation")
        start_btn.setFixedWidth(250)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-size: 16px;
                padding: 14px; border-radius: 10px; font-weight: bold;
            }
        """)
        start_btn.clicked.connect(self.show_input_page)

        lay.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addWidget(desc)
        lay.addLayout(theme_row)
        lay.addSpacing(10)
        lay.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        card.setLayout(lay)
        outer.addWidget(card)
        page.setLayout(outer)
        return page

    # ─────────────────────────────────────────
    #  INPUT PAGE
    # ─────────────────────────────────────────
    def create_input_page(self):
        page = QWidget()
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("homeCard")
        card.setFixedWidth(600)

        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(14)

        title = QLabel("Simulation Requirements")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold;")

        form_layout = QFormLayout()

        self.area_input = QLineEdit()
        self.node_input = QLineEdit()
        self.range_input = QLineEdit()
        self.energy_input = QLineEdit()
        self.load_input = QLineEdit()

        self.area_input.setPlaceholderText("Enter area size e.g. 100 (m²)")
        self.node_input.setPlaceholderText("Enter number of nodes e.g. 10")
        self.range_input.setPlaceholderText("Enter communication range e.g. 35 (m)")
        self.energy_input.setPlaceholderText("Enter initial energy e.g. 100 (J)")
        self.load_input.setPlaceholderText("Enter network load e.g. 5 (packets)")

        form_layout.addRow("Area Size (m²):",          self.area_input)
        form_layout.addRow("Number of Nodes:",          self.node_input)
        form_layout.addRow("Communication Range (m):",  self.range_input)
        form_layout.addRow("Initial Energy (J):",       self.energy_input)
        form_layout.addRow("Network Load (packets):",   self.load_input)

        create_button = QPushButton("Create Simulation Environment")
        create_button.clicked.connect(self.create_environment)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_front_page)

        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(create_button)
        layout.addWidget(back_button)

        card.setLayout(layout)
        outer_layout.addWidget(card)
        page.setLayout(outer_layout)
        return page

    # ─────────────────────────────────────────
    #  SIMULATION PAGE
    # ─────────────────────────────────────────
    def create_simulation_page(self):
        page = QWidget()
        main = QHBoxLayout(page)
        main.setContentsMargins(8, 6, 8, 6)
        main.setSpacing(8)

        # ── LEFT PANEL (scrollable) ──
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFixedWidth(420)
        left_scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")

        left_widget = QWidget()
        left_panel  = QVBoxLayout(left_widget)
        left_panel.setSpacing(8)
        left_panel.setContentsMargins(4, 4, 4, 4)
        left_scroll.setWidget(left_widget)

        # Info card
        info_card = QFrame()
        info_card.setObjectName("card")

        info_lay = QVBoxLayout()
        info_lay.setContentsMargins(16, 12, 16, 12)
        info_lay.setSpacing(6)

        info_title = QLabel("Simulation Info")
        info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb;")

        info_row = QHBoxLayout()
        info_row.setSpacing(20)
        info_row.addWidget(self.info_labels_widget)
        info_row.addWidget(self.info_data_widget)
        info_row.addStretch()

        info_lay.addWidget(info_title)
        info_lay.addLayout(info_row)
        info_card.setLayout(info_lay)

        # Table card
        table_card = QFrame()
        table_card.setObjectName("card")

        table_lay = QVBoxLayout()
        table_lay.setContentsMargins(12, 10, 12, 10)

        table_title = QLabel("Node Details")
        table_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb;")

        table_lay.addWidget(table_title)
        table_lay.addWidget(self.node_table)
        table_card.setLayout(table_lay)

        left_panel.addWidget(info_card)
        left_panel.addWidget(table_card, 1)

        # ── CENTER PANEL ──
        center = QVBoxLayout()
        center.setSpacing(6)

        # Top bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        t1 = QLabel("IoT Network Simulation")
        t1.setStyleSheet("font-size: 26px; font-weight: bold;")
        t2 = QLabel("RPL DODAG Routing Protocol Simulator")
        t2.setStyleSheet("font-size: 14px; color: #2563eb;")
        title_col.addWidget(t1)
        title_col.addWidget(t2)

        action_btn = QPushButton("☰ All Actions ▾")
        action_btn.setFixedWidth(130)
        action_btn.setFixedHeight(34)

        menu = QMenu(self)
        acts = [
            ("1. Generate Nodes",       self.generate_nodes),
            ("2. Add Sink",             self.add_sink),
            ("3. Discover Neighbors",   self.discover_neighbors),
            ("4. Run RPL / Form DODAG", self.run_rpl),
            ("5. Send Packets",         self.send_packets),
        ]
        for label, fn in acts:
            menu.addAction(label).triggered.connect(fn)
        menu.addSeparator()
        menu.addAction("Distance Matrix").triggered.connect(self.show_distance_matrix)
        menu.addAction("Performance Summary").triggered.connect(self.show_performance_summary)
        action_btn.setMenu(menu)

        reset_btn = QPushButton("Reset")
        reset_btn.setFixedWidth(72)
        reset_btn.setFixedHeight(34)
        reset_btn.setStyleSheet("""
            QPushButton{background-color:#64748b;color:white;border-radius:8px;
                        font-size:12px;font-weight:bold;}
            QPushButton:hover{background-color:#475569;}
        """)
        reset_btn.clicked.connect(self.reset_simulation)

        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(72)
        back_btn.setFixedHeight(34)
        back_btn.clicked.connect(self.show_input_page)

        top_bar.addLayout(title_col)
        top_bar.addStretch()
        top_bar.addWidget(action_btn)
        top_bar.addWidget(reset_btn)
        top_bar.addWidget(back_btn)

        # Status bar
        status_row = QHBoxLayout()
        status_row.setSpacing(10)

        status_card = QFrame()
        status_card.setObjectName("card")
        status_card.setMaximumHeight(42)
        s_lay = QHBoxLayout()
        s_lay.setContentsMargins(12, 4, 12, 4)
        s_lay.addWidget(self.info_label)
        s_lay.addStretch()
        s_lay.addWidget(self.path_label)
        status_card.setLayout(s_lay)

        path_row = QHBoxLayout()
        path_row.setSpacing(6)
        path_lbl = QLabel("Best Path:")
        path_lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        path_row.addWidget(path_lbl)
        path_row.addWidget(self.node_selector)

        show_path_btn = QPushButton("Show Path")
        show_path_btn.setFixedWidth(90)
        show_path_btn.setFixedHeight(32)
        show_path_btn.clicked.connect(self.show_selected_path)

        clear_path_btn = QPushButton("Clear")
        clear_path_btn.setFixedWidth(65)
        clear_path_btn.setFixedHeight(32)
        clear_path_btn.clicked.connect(self.clear_selected_path)

        path_row.addWidget(show_path_btn)
        path_row.addWidget(clear_path_btn)

        status_row.addWidget(status_card, 1)
        status_row.addLayout(path_row)

        # Graph card
        graph_card = QFrame()
        graph_card.setObjectName("card")

        graph_lay = QVBoxLayout()
        graph_lay.setContentsMargins(6, 6, 6, 6)
        graph_lay.addWidget(self.canvas, 1)
        graph_card.setLayout(graph_lay)

        # Log card BELOW graph
        log_card = QFrame()
        log_card.setObjectName("card")
        log_card.setMinimumHeight(220)
        log_card.setMaximumHeight(320)

        log_lay = QVBoxLayout()
        log_lay.setContentsMargins(12, 8, 12, 10)

        log_title = QLabel("Simulation Log")
        log_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563eb;")

        self.log_box.setMinimumHeight(160)
        self.log_box.setMaximumHeight(260)

        log_lay.addWidget(log_title)
        log_lay.addWidget(self.log_box)
        log_card.setLayout(log_lay)

        center.addLayout(top_bar)
        center.addLayout(status_row)
        center.addWidget(graph_card, 1)
        center.addWidget(log_card)

        main.addWidget(left_scroll)
        main.addLayout(center, 1)

        return page

    # ─────────────────────────────────────────
    #  NAVIGATION
    # ─────────────────────────────────────────
    def show_front_page(self):      self.stack.setCurrentWidget(self.front_page)
    def show_input_page(self):      self.stack.setCurrentWidget(self.input_page)
    def show_simulation_page(self): self.stack.setCurrentWidget(self.simulation_page)

    # ─────────────────────────────────────────
    #  LOG
    # ─────────────────────────────────────────
    def add_log(self, msg):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )

    def clear_log(self): self.log_box.clear()

    # ─────────────────────────────────────────
    #  CREATE ENVIRONMENT
    # ─────────────────────────────────────────
    def create_environment(self):
        try:
            self.area_size           = int(self.area_input.text())
            self.node_count          = int(self.node_input.text())
            self.communication_range = int(self.range_input.text())
            self.initial_energy      = int(self.energy_input.text())
            self.network_load        = int(self.load_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter all numeric values.")
            return

        checks = [
            (self.area_size < 50,          "Area size should be at least 50."),
            (self.node_count < 2,          "At least 2 nodes are required."),
            (self.communication_range < 1, "Communication range must be > 0."),
            (self.initial_energy < 10,     "Initial energy should be at least 10."),
            (self.network_load < 1,        "Network load should be at least 1."),
        ]
        for cond, msg in checks:
            if cond:
                QMessageBox.warning(self, "Input Error", msg)
                return

        self.nodes = []; self.sink = None
        self.show_neighbors = self.show_dodag = self.show_packets = False
        self.highlight_path = []

        self.figure.clear(); self.canvas.draw()
        self.node_table.setRowCount(0)
        self.node_selector.clear(); self.node_selector.addItem("Select Node")
        self.clear_log()

        self.info_labels_widget.setText(
            "Area Size:\nNodes:\nRange:\nNetwork Load:\nInitial Energy:"
        )
        self.info_data_widget.setText(
            f"{self.area_size} × {self.area_size} m²\n"
            f"{self.node_count}\n"
            f"{self.communication_range} m\n"
            f"{self.network_load} packets\n"
            f"{self.initial_energy} J"
        )

        self.add_log("Simulation environment created.")
        self.add_log(f"Area: {self.area_size}x{self.area_size} | "
                     f"Nodes: {self.node_count} | Range: {self.communication_range} | "
                     f"Energy: {self.initial_energy} | Load: {self.network_load}")

        self.info_label.setText("✅ Simulation Environment Created")
        self.path_label.setText("Highlighted Path: None")
        self.show_simulation_page()

    # ─────────────────────────────────────────
    #  STEP 1 — GENERATE NODES
    # ─────────────────────────────────────────
    def generate_nodes(self):
        self.nodes = []; self.sink = None
        self.show_neighbors = self.show_dodag = self.show_packets = False
        self.highlight_path = []
        self.node_selector.clear(); self.node_selector.addItem("Select Node")
        self.add_log("\nSTEP 1: Random node generation started.")

        for i in range(self.node_count):
            node = {
                "id": i + 1,
                "x":  random.randint(0, self.area_size),
                "y":  random.randint(0, self.area_size),
                "energy":    random.randint(1, self.initial_energy),
                "load":      self.network_load,
                "parent":    None,
                "rank":      math.inf,
                "neighbors": []
            }
            self.nodes.append(node)
            self.node_selector.addItem(f"Node {node['id']}")
            self.add_log(
                f"Node {node['id']} placed at ({node['x']}, {node['y']}) "
                f"with energy {node['energy']}."
            )

        self.info_label.setText("✅ Nodes Generated")
        self.update_table(); self.draw_network()

    # ─────────────────────────────────────────
    #  STEP 2 — ADD SINK
    # ─────────────────────────────────────────
    def add_sink(self):
        if not self.nodes:
            QMessageBox.warning(self, "Error", "Generate nodes first."); return

        self.sink = {
            "id": "SINK",
            "x":  self.area_size / 2, "y": self.area_size / 2,
            "energy": "∞", "load": "-",
            "parent": None, "rank": 0, "neighbors": []
        }
        self.add_log(f"\nSTEP 2: Sink added at ({self.sink['x']}, {self.sink['y']}). Rank=0.")
        self.info_label.setText("✅ Sink Added")
        self.update_table(); self.draw_network()

    # ─────────────────────────────────────────
    #  STEP 3 — DISCOVER NEIGHBORS
    # ─────────────────────────────────────────
    def discover_neighbors(self):
        if self.sink is None:
            QMessageBox.warning(self, "Error", "Add sink first."); return

        for n in [self.sink] + self.nodes:
            n["neighbors"] = []

        self.add_log("\nSTEP 3: Neighbor discovery started.")
        link_count = 0

        for node in self.nodes:
            d = self.calculate_distance(node, self.sink)
            if d <= self.communication_range:
                node["neighbors"].append(self.sink)
                self.sink["neighbors"].append(node)
                link_count += 1
                self.add_log(f"Node {node['id']} within sink range (d={d:.2f}).")
            else:
                self.add_log(
                    f"Node {node['id']} outside sink range (d={d:.2f}), "
                    f"cannot directly join DODAG."
                )

        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                d = self.calculate_distance(self.nodes[i], self.nodes[j])
                if d <= self.communication_range:
                    if self.nodes[j] not in self.nodes[i]["neighbors"]:
                        self.nodes[i]["neighbors"].append(self.nodes[j])
                    if self.nodes[i] not in self.nodes[j]["neighbors"]:
                        self.nodes[j]["neighbors"].append(self.nodes[i])
                    link_count += 1
                    self.add_log(
                        f"Node {self.nodes[i]['id']} ↔ Node {self.nodes[j]['id']} "
                        f"(d={d:.2f})."
                    )

        self._ensure_connections()
        self.show_neighbors = True
        self.show_dodag = self.show_packets = False
        self.highlight_path = []
        self.add_log(f"Discovery complete. Total links: {link_count}.")
        self.info_label.setText("✅ Neighbor Discovery Done")
        self.update_table(); self.draw_network()

    def _ensure_connections(self):
        for node in self.nodes:
            sensor_nb = [n for n in node["neighbors"] if n != self.sink]
            if not sensor_nb:
                nearest = min(
                    (o for o in self.nodes if o != node),
                    key=lambda o: self.calculate_distance(node, o),
                    default=None
                )
                if nearest:
                    if nearest not in node["neighbors"]:
                        node["neighbors"].append(nearest)
                    if node not in nearest["neighbors"]:
                        nearest["neighbors"].append(node)
                    d = self.calculate_distance(node, nearest)
                    self.add_log(
                        f"Node {node['id']} had no sensor neighbor, "
                        f"connected to nearest Node {nearest['id']} (d={d:.2f})."
                    )

    # ─────────────────────────────────────────
    #  STEP 4 — RUN RPL
    # ─────────────────────────────────────────
    def run_rpl(self):
        if self.sink is None:
            QMessageBox.warning(self, "Error", "Add sink first.")
            return

        if not self.show_neighbors:
            QMessageBox.warning(self, "Error", "Discover neighbors first.")
            return

        self.add_log("\nSTEP 4: RPL DODAG formation started.")
        self.add_log("Sink broadcasts DIO message with rank 0.")
        self.add_log("Multi-hop RPL enabled: nodes can join through any already-connected DODAG parent.")

        # Reset previous RPL state
        for node in self.nodes:
            node["rank"] = math.inf
            node["parent"] = None

        # Step 1: Direct sink neighbors receive DIO from sink first
        for node in self.nodes:
            d_sink = self.calculate_distance(node, self.sink)

            if self.sink in node["neighbors"] and d_sink <= self.communication_range:
                node["parent"] = self.sink
                node["rank"] = 1

                self.add_log(
                    f"Node {node['id']} received DIO from SINK, "
                    f"selected SINK as parent, rank = 1."
                )

        # Step 2: Multi-hop DIO propagation
        # A node can join if any neighbor is already in DODAG.
        changed = True

        while changed:
            changed = False

            for node in self.nodes:
                if node["parent"] is not None:
                    continue

                best_parent = None
                best_cost = math.inf
                best_distance = 0

                for neighbor in node["neighbors"]:
                    if neighbor == self.sink:
                        continue

                    if neighbor.get("rank", math.inf) == math.inf:
                        continue

                    distance = self.calculate_distance(node, neighbor)

                    # Important: forced visual nearest-neighbor links are not used
                    # for RPL if they are outside actual communication range.
                    if distance > self.communication_range:
                        continue

                    energy_factor = 0
                    if isinstance(neighbor.get("energy"), int):
                        energy_factor = (self.initial_energy - neighbor["energy"]) / self.initial_energy

                    cost = neighbor["rank"] + (distance / self.communication_range) + energy_factor

                    if cost < best_cost:
                        best_cost = cost
                        best_parent = neighbor
                        best_distance = distance

                if best_parent is not None:
                    node["parent"] = best_parent
                    node["rank"] = best_parent["rank"] + 1
                    changed = True

                    self.add_log(
                        f"Node {node['id']} received DIO from Node {best_parent['id']}, "
                        f"selected Node {best_parent['id']} as parent, "
                        f"rank = {node['rank']} (distance = {best_distance:.2f})."
                    )

        disconnected = [node["id"] for node in self.nodes if node["parent"] is None]

        if disconnected:
            self.add_log(
                f"Node {disconnected} has no valid multi-hop route to SINK due to communication range limitation."
            )
        else:
            self.add_log("All nodes successfully joined the DODAG through single-hop or multi-hop routing.")

        self.show_dodag = True
        self.show_packets = False
        self.highlight_path = []

        self.info_label.setText("✅ RPL DODAG Formed")
        self.update_table()
        self.draw_network()

    # ─────────────────────────────────────────
    #  STEP 5 — SEND PACKETS
    # ─────────────────────────────────────────
    def send_packets(self):
        if not self.show_dodag:
            QMessageBox.warning(self, "Error", "Run RPL/DODAG first."); return

        self.add_log("\nSTEP 5: Packet forwarding started.")
        for node in self.nodes:
            if node["parent"] is not None and node["energy"] > 0:
                old = node["energy"]
                node["energy"] = max(0, node["energy"] - node["load"])
                self.add_log(
                    f"Node {node['id']} forwarded packet to {node['parent']['id']}. "
                    f"Energy reduced from {old} to {node['energy']}."
                )
            elif node["parent"] is None:
                self.add_log(
                    f"Node {node['id']} has no valid parent/path to SINK, "
                    f"so packet cannot be forwarded."
                )
            else:
                self.add_log(f"Node {node['id']} has no energy left and cannot transmit.")

        self.show_packets = True
        self.info_label.setText("✅ Packets Forwarded Toward Sink")
        self.update_table(); self.draw_network()

    # ─────────────────────────────────────────
    #  SHOW / CLEAR PATH
    # ─────────────────────────────────────────
    def show_selected_path(self):
        if not self.show_dodag:
            QMessageBox.warning(self, "Error", "Run RPL/DODAG first."); return
        idx = self.node_selector.currentIndex()
        if idx <= 0:
            QMessageBox.warning(self, "Error", "Select a node."); return

        node = self.nodes[idx - 1]

        # Dead node check: a node with zero energy cannot transmit, forward,
        # or use an active best path.
        if node["energy"] <= 0:
            QMessageBox.information(
                self,
                "Dead Node",
                f"Node {node['id']} has no energy left, so it cannot send packets "
                f"or use a best path."
            )
            return

        if node["parent"] is None:
            QMessageBox.information(
                self, "No Path",
                f"Node {node['id']} has no valid multi-hop route to SINK "
                f"due to communication range limitation, so it cannot join DODAG."
            )
            return

        path, cur = [], node
        while cur is not None:
            # If any intermediate routing node is dead, the route is broken.
            if cur != self.sink and cur["energy"] <= 0:
                QMessageBox.information(
                    self,
                    "Broken Path",
                    f"Path is broken because Node {cur['id']} has no energy left."
                )
                return

            path.append(cur)
            if cur == self.sink:
                break
            cur = cur["parent"]

        self.highlight_path = path
        txt = " → ".join(str(n["id"]) for n in path)
        self.add_log(f"\nHighlighted best path: {txt}")
        self.path_label.setText(f"Highlighted Path: {txt}")
        self.info_label.setText("✅ Best Path Highlighted")
        self.draw_network()

    def clear_selected_path(self):
        self.highlight_path = []
        self.path_label.setText("Highlighted Path: None")
        self.info_label.setText("✅ Highlighted Path Cleared")
        self.draw_network()

    # ─────────────────────────────────────────
    #  DISTANCE
    # ─────────────────────────────────────────
    def calculate_distance(self, a, b):
        return math.sqrt((b["x"]-a["x"])**2 + (b["y"]-a["y"])**2)

    # ─────────────────────────────────────────
    #  DISTANCE MATRIX DIALOG
    # ─────────────────────────────────────────
    def show_distance_matrix(self):
        if not self.nodes:
            QMessageBox.warning(self, "Error", "Generate nodes first."); return
        if self.sink is None:
            QMessageBox.warning(self, "Error", "Add sink first."); return

        all_nodes = [self.sink] + self.nodes
        labels    = [str(n["id"]) for n in all_nodes]

        dlg = QDialog(self)
        dlg.setWindowTitle("Distance Matrix")
        dlg.setGeometry(80, 60, 1200, 620)
        dlg.setMinimumSize(800, 450)

        lay = QVBoxLayout()
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        lbl = QLabel("Distance Matrix Between Sink and Nodes")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        tbl = QTableWidget()
        tbl.setRowCount(len(all_nodes))
        tbl.setColumnCount(len(all_nodes))
        tbl.setHorizontalHeaderLabels(labels)
        tbl.setVerticalHeaderLabels(labels)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        tbl.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        for i in range(len(all_nodes)):
            for j in range(len(all_nodes)):
                val = "0" if i == j else \
                      f"{self.calculate_distance(all_nodes[i], all_nodes[j]):.2f}"
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tbl.setItem(i, j, item)

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setFixedHeight(36)
        close_btn.clicked.connect(dlg.close)

        btn_row = QHBoxLayout()
        btn_row.addStretch(); btn_row.addWidget(close_btn); btn_row.addStretch()

        lay.addWidget(lbl)
        lay.addWidget(tbl, 1)
        lay.addLayout(btn_row)
        dlg.setLayout(lay)
        dlg.exec()

    # ─────────────────────────────────────────
    #  PERFORMANCE SUMMARY
    # ─────────────────────────────────────────
    def show_performance_summary(self):
        if not self.nodes:
            QMessageBox.warning(self, "Error", "Generate nodes first."); return

        total     = len(self.nodes)
        connected = len([n for n in self.nodes if n["parent"] is not None])
        dead      = len([n for n in self.nodes if n["energy"] <= 0])
        avg_e     = sum(n["energy"] for n in self.nodes) / total
        pdr       = (connected / total) * 100

        all_n = ([self.sink] if self.sink else []) + self.nodes
        links = set()
        for n in all_n:
            for nb in n.get("neighbors", []):
                links.add(tuple(sorted([str(n["id"]), str(nb["id"])])))

        dlg = QDialog(self)
        dlg.setWindowTitle("Performance Summary")
        dlg.setGeometry(300, 100, 560, 480)
        dlg.setMinimumSize(500, 420)

        lay = QVBoxLayout()
        lay.setContentsMargins(20, 20, 20, 16)
        lay.setSpacing(12)

        lbl = QLabel("Performance Summary")
        lbl.setStyleSheet("font-size: 20px; font-weight: bold;")

        # Use a table for perfect alignment
        rows = [
            ("Total Nodes",                      str(total)),
            ("DODAG / Sink-Connected Nodes",      str(connected)),
            ("Neighbor-Only / Disconnected",      str(total - connected)),
            ("Total Neighbor Links",              str(len(links))),
            ("Dead Nodes (Energy Depleted)",      str(dead)),
            ("Average Remaining Energy",          f"{avg_e:.2f} J"),
            ("Packet Delivery Ratio",             f"{pdr:.2f}%"),
            ("Communication Range",               f"{self.communication_range} m"),
            ("Network Load",                      f"{self.network_load} packets"),
        ]

        summary_tbl = QTableWidget()
        summary_tbl.setRowCount(len(rows))
        summary_tbl.setColumnCount(2)
        summary_tbl.setHorizontalHeaderLabels(["Metric", "Value"])
        summary_tbl.verticalHeader().setVisible(False)
        summary_tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        summary_tbl.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        summary_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        summary_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        summary_tbl.setShowGrid(True)
        summary_tbl.setAlternatingRowColors(True)

        for r, (metric, value) in enumerate(rows):
            m_item = QTableWidgetItem(metric)
            m_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            v_item = QTableWidgetItem(value)
            v_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_tbl.setItem(r, 0, m_item)
            summary_tbl.setItem(r, 1, v_item)

        summary_tbl.resizeRowsToContents()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(38)
        close_btn.clicked.connect(dlg.close)

        lay.addWidget(lbl)
        lay.addWidget(summary_tbl, 1)
        lay.addWidget(close_btn)
        dlg.setLayout(lay)
        dlg.exec()

    # ─────────────────────────────────────────
    #  UPDATE TABLE
    # ─────────────────────────────────────────
    def update_table(self):
        self.node_table.setRowCount(len(self.nodes))
        for row, node in enumerate(self.nodes):
            parent_txt = "-"
            dist_txt   = "-"
            if node["parent"] is not None:
                parent_txt = str(node["parent"]["id"])
                dist_txt   = f"{self.calculate_distance(node, node['parent']):.2f}"
            rank_txt = "∞" if node["rank"] == math.inf else str(node["rank"])

            vals = [str(node["id"]), str(node["x"]), str(node["y"]),
                    str(node["energy"]), str(node["load"]),
                    rank_txt, parent_txt, dist_txt]
            for col, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.node_table.setItem(row, col, item)

    # ─────────────────────────────────────────
    #  DRAW NETWORK
    # ─────────────────────────────────────────
    def draw_network(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if self.current_theme == "Dark":
            fig_bg = "#161b22"; ax_bg = "#21262d"
            txt_c  = "#c9d1d9"; grid_c = "#30363d"
        else:
            fig_bg = "#ffffff"; ax_bg = "#ffffff"
            txt_c  = "#0f172a"; grid_c = "#e2e8f0"

        self.figure.patch.set_facecolor(fig_bg)
        ax.set_facecolor(ax_bg)
        ax.tick_params(colors=txt_c)
        ax.xaxis.label.set_color(txt_c)
        ax.yaxis.label.set_color(txt_c)
        ax.title.set_color(txt_c)
        for sp in ax.spines.values():
            sp.set_edgecolor(grid_c)

        self.figure.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.15)

        all_nodes = ([self.sink] if self.sink else []) + self.nodes

        if self.show_neighbors:
            for i in range(len(all_nodes)):
                for j in range(i + 1, len(all_nodes)):
                    if all_nodes[j] in all_nodes[i]["neighbors"]:
                        ax.plot(
                            [all_nodes[i]["x"], all_nodes[j]["x"]],
                            [all_nodes[i]["y"], all_nodes[j]["y"]],
                            color="gray", linestyle="--", linewidth=1, zorder=1
                        )

        if self.show_dodag:
            for node in self.nodes:
                if node["parent"] is not None:
                    ax.annotate("",
                        xy=(node["parent"]["x"], node["parent"]["y"]),
                        xytext=(node["x"], node["y"]),
                        arrowprops=dict(arrowstyle="->", color="green", lw=2), zorder=2
                    )

        if self.show_packets:
            for node in self.nodes:
                if node["parent"] is not None:
                    ax.annotate("",
                        xy=(node["parent"]["x"], node["parent"]["y"]),
                        xytext=(node["x"], node["y"]),
                        arrowprops=dict(arrowstyle="->", color="orange", lw=1.5), zorder=3
                    )

        if len(self.highlight_path) > 1:
            for i in range(len(self.highlight_path) - 1):
                a = self.highlight_path[i]; b = self.highlight_path[i+1]
                ax.annotate("",
                    xy=(b["x"], b["y"]), xytext=(a["x"], a["y"]),
                    arrowprops=dict(arrowstyle="->", color="purple", lw=4), zorder=4
                )

        for node in self.nodes:
            color = "blue"
            if node["parent"] is not None: color = "green"
            if not node["neighbors"]:      color = "yellow"
            if node in self.highlight_path: color = "purple"
            if node["energy"] <= 0:        color = "black"

            ax.scatter(node["x"], node["y"], color=color, s=120, zorder=5)
            ax.annotate(
                f"N{node['id']}  E:{node['energy']}J",
                xy=(node["x"], node["y"]),
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=7.5,
                color=txt_c,
                zorder=6,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", alpha=0.4, ec="none")
            )

        if self.sink:
            sc = "purple" if self.sink in self.highlight_path else "red"
            ax.scatter(self.sink["x"], self.sink["y"],
                       color=sc, s=250, marker="s", zorder=5)
            ax.text(self.sink["x"] + 1, self.sink["y"] + 1,
                    "SINK", fontsize=10, color="red", fontweight="bold", zorder=6)

        pad = self.area_size * 0.05
        ax.set_xlim(-pad, self.area_size + pad)
        ax.set_ylim(-pad, self.area_size + pad)
        ax.set_title("RPL DODAG Simulation", fontsize=11, fontweight="bold")
        ax.set_xlabel("X-axis"); ax.set_ylabel("Y-axis")
        ax.grid(True, color=grid_c, linewidth=0.8)

        self.canvas.draw()

    # ─────────────────────────────────────────
    #  RESET
    # ─────────────────────────────────────────
    def reset_simulation(self):
        self.nodes = []; self.sink = None
        self.show_neighbors = self.show_dodag = self.show_packets = False
        self.highlight_path = []

        self.node_table.setRowCount(0)
        self.node_selector.clear(); self.node_selector.addItem("Select Node")
        self.figure.clear(); self.canvas.draw()
        self.clear_log(); self.add_log("Simulation reset.")
        self.info_label.setText("✅ Reset")
        self.path_label.setText("Highlighted Path: None")


app = QApplication(sys.argv)
window = RPLSimulator()
window.showMaximized()
sys.exit(app.exec()) 