import sys
import requests
import json
import webbrowser

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

SAVE_FILE = "place.json"

def load_place():
    try:
        with open(SAVE_FILE) as f:
            return json.load(f)["place"]
    except:
        return ""


def save_place(pid):
    with open(SAVE_FILE,"w") as f:
        json.dump({"place":pid},f)


class ServerCard(QFrame):

    def __init__(self, server, place_id):
        super().__init__()

        self.server = server
        self.place_id = place_id

        players = server["playing"]
        max_players = server["maxPlayers"]
        fps = server.get("fps",0)

        ping = players * 8

        self.setObjectName("card")

        layout = QVBoxLayout()

        title = QLabel(f"{players}/{max_players} Players")
        title.setObjectName("title")

        ping_layout = QHBoxLayout()

        ping_label = QLabel(f"Ping: {ping} ms")

        ping_dot = QLabel("●")
        ping_dot.setStyleSheet(f"color:{self.ping_color(ping)};font-size:16px")

        ping_layout.addWidget(ping_dot)
        ping_layout.addWidget(ping_label)
        ping_layout.addStretch()

        player_bar = QProgressBar()
        player_bar.setValue(int((players/max_players)*100))
        player_bar.setStyleSheet(self.progress_color(players/max_players))

        fps_bar = QProgressBar()
        fps_bar.setValue(int(min(float(fps),100)))
        fps_bar.setStyleSheet(self.fps_color(fps))

        join = QPushButton("JOIN")
        join.clicked.connect(self.join_server)

        layout.addWidget(title)
        layout.addLayout(ping_layout)

        layout.addWidget(QLabel(f"Players {players}/{max_players}"))
        layout.addWidget(player_bar)

        layout.addWidget(QLabel(f"FPS {fps}"))
        layout.addWidget(fps_bar)

        layout.addWidget(join)

        self.setLayout(layout)

    def join_server(self):
        url=f"roblox://placeId={self.place_id}&gameInstanceId={self.server['id']}"
        webbrowser.open(url)

    def ping_color(self,p):
        if p < 80:
            return "#00ff88"
        elif p < 150:
            return "#ffaa00"
        else:
            return "#ff4444"

    def progress_color(self,val):

        if val < 0.5:
            c="#00ff88"
        elif val < 0.8:
            c="#ffaa00"
        else:
            c="#ff4444"

        return f"""
        QProgressBar {{
            background:#1a1a1a;
            border:1px solid #333;
            height:8px;
        }}
        QProgressBar::chunk {{
            background:{c};
        }}
        """

    def fps_color(self,fps):

        if fps > 50:
            c="#00ff88"
        elif fps > 30:
            c="#ffaa00"
        else:
            c="#ff4444"

        return f"""
        QProgressBar {{
            background:#1a1a1a;
            border:1px solid #333;
            height:8px;
        }}
        QProgressBar::chunk {{
            background:{c};
        }}
        """


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Roblox Server Scanner")

        main = QVBoxLayout()

        header = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Masukkan Place ID")
        self.input.setText(load_place())

        scan_btn = QPushButton("Scan Server")
        scan_btn.clicked.connect(self.scan)

        header.addWidget(self.input)
        header.addWidget(scan_btn)

        main.addLayout(header)

        # SCROLL AREA
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()

        self.grid = QGridLayout(self.container)

        self.scroll.setWidget(self.container)

        main.addWidget(self.scroll)

        self.setLayout(main)

        self.setStyleSheet("""
        QWidget{
            background:#0b0b0b;
            color:white;
            font-family:Segoe UI;
        }

        QLineEdit{
            background:#111;
            border:1px solid #333;
            padding:6px;
        }

        QPushButton{
            background:#ffd400;
            border:none;
            padding:6px;
            color:black;
            font-weight:bold;
        }

        QPushButton:hover{
            background:#ffe34d;
        }

        #card{
            background:#101010;
            border:1px solid #333;
            border-radius:10px;
            padding:10px;
        }

        #title{
            font-size:14px;
            font-weight:bold;
        }

        QScrollBar:vertical {
            background:#0b0b0b;
            width:8px;
        }

        QScrollBar::handle:vertical {
            background:#ffd400;
            border-radius:4px;
        }
        """)

    def clear_grid(self):

        for i in reversed(range(self.grid.count())):
            widget=self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def scan(self):

        place_id = self.input.text().strip()

        if not place_id:
            return

        save_place(place_id)

        servers=[]
        cursor=None

        while True:

            url=f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit=100"

            if cursor:
                url+=f"&cursor={cursor}"

            res=requests.get(url).json()

            servers.extend(res["data"])

            cursor=res.get("nextPageCursor")

            if not cursor:
                break

        servers=sorted(servers,key=lambda s:s["playing"])

        self.clear_grid()

        row=0
        col=0

        for s in servers:

            card=ServerCard(s,place_id)

            self.grid.addWidget(card,row,col)

            col+=1

            if col==4:
                col=0
                row+=1


app = QApplication(sys.argv)

w = Window()
w.resize(950,600)
w.show()

sys.exit(app.exec())