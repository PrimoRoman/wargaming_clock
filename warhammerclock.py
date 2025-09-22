from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QFileDialog, QMessageBox, QFrame
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import sys
import csv
import time

PRIMARY_COLORS = ["red", "blue", "green", "yellow", "black", "white"]

class Player:
    def __init__(self, name):
        self.name = name
        self.time_elapsed = 0
        self.command_points = 0
        self.victory_points = 0
        self.turns = 0
        self.last_active = None
        self.color = "white"

class WarhammerClockApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warhammer 40k Clock")
        self.resize(900, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0dede;")
        self.players = [Player("Player 1"), Player("Player 2")]
        self.active_player = None
        self.running = False
        self.battle_round = 1
        self.log = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout()
        self.round_label = QLabel(f"Battle Round {self.battle_round} - Player 1's Turn")
        self.round_label.setFont(QFont("Times New Roman", 20, QFont.Weight.Bold))
        self.round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.round_label.setStyleSheet("color: #d4af37;")
        main_layout.addWidget(self.round_label)
        grid = QHBoxLayout()
        self.name_edits = []
        self.time_labels = []
        self.cp_labels = []
        self.vp_labels = []
        self.panels = []
        for i, player in enumerate(self.players):
            panel = QFrame()
            panel.setFrameShape(QFrame.Shape.StyledPanel)
            panel.setStyleSheet("QFrame { border: 2px solid #d4af37; border-radius: 10px; }")
            vbox = QVBoxLayout(panel)
            name_edit = QLineEdit(player.name)
            name_edit.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            name_edit.setStyleSheet("background-color: #2b2b2b; color: #e0dede;")
            vbox.addWidget(name_edit)
            self.name_edits.append((player, name_edit))
            time_lbl = QLabel("00:00")
            time_lbl.setFont(QFont("Arial", 42, QFont.Weight.Bold))
            time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(time_lbl, stretch=1)
            self.time_labels.append(time_lbl)
            cp_h = QHBoxLayout()
            cp_h.addWidget(QLabel("CP:"))
            cp_lbl = QLabel("0")
            cp_h.addWidget(cp_lbl)
            self.cp_labels.append(cp_lbl)
            btn_add_cp = QPushButton("+")
            btn_add_cp.clicked.connect(lambda _, p=player: self.add_cp(p))
            cp_h.addWidget(btn_add_cp)
            btn_sub_cp = QPushButton("-")
            btn_sub_cp.clicked.connect(lambda _, p=player: self.remove_cp(p))
            cp_h.addWidget(btn_sub_cp)
            vbox.addLayout(cp_h)
            vp_h = QHBoxLayout()
            vp_h.addWidget(QLabel("VP:"))
            vp_lbl = QLabel("0")
            vp_h.addWidget(vp_lbl)
            self.vp_labels.append(vp_lbl)
            btn_add_vp = QPushButton("+")
            btn_add_vp.clicked.connect(lambda _, p=player: self.add_vp(p))
            vp_h.addWidget(btn_add_vp)
            btn_sub_vp = QPushButton("-")
            btn_sub_vp.clicked.connect(lambda _, p=player: self.remove_vp(p))
            vp_h.addWidget(btn_sub_vp)
            vbox.addLayout(vp_h)
            btn_end = QPushButton("End Turn")
            btn_end.clicked.connect(lambda _, p=player: self.end_turn(p))
            vbox.addWidget(btn_end)
            color_combo = QComboBox()
            color_combo.addItems(PRIMARY_COLORS)
            color_combo.setStyleSheet("background-color: #2b2b2b; color: #e0dede;")
            color_combo.currentTextChanged.connect(lambda c, p=player, panel=panel: self.change_color(p, panel, c))
            vbox.addWidget(color_combo)
            grid.addWidget(panel)
            self.panels.append(panel)
        main_layout.addLayout(grid)
        control_h = QHBoxLayout()
        for text, handler in [
            ("Start Game", self.start_game),
            ("Pause Game", self.pause_game),
            ("Resume Game", self.resume_game),
            ("End Game", self.end_game),
            ("Export CSV", self.export_csv)
        ]:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            btn.setFont(QFont("Arial", 15))
            btn.setFixedHeight(60)
            control_h.addWidget(btn)
        main_layout.addLayout(control_h)
        self.setLayout(main_layout)

    def start_game(self):
        if not self.active_player:
            self.active_player = self.players[0]
        self.active_player.last_active = time.time()
        self.running = True
        for p in self.players:
            p.command_points += 1
            p.turns = self.battle_round
        if not self.timer.isActive():
            self.timer.start(500)
        self.update_ui()

    def pause_game(self):
        if self.active_player and self.active_player.last_active is not None:
            now = time.time()
            elapsed = now - self.active_player.last_active
            self.active_player.time_elapsed += elapsed
            self.active_player.last_active = None
        self.running = False
        if self.timer.isActive():
            self.timer.stop()
        self.update_ui()

    def resume_game(self):
        if self.active_player and not self.running:
            self.active_player.last_active = time.time()
            self.running = True
            if not self.timer.isActive():
                self.timer.start(500)

    def change_color(self, player, panel, color):
        player.color = color
        panel.setStyleSheet(f"QFrame {{ background-color: {color}; border: 2px solid #d4af37; border-radius: 10px; }}")

    def add_cp(self, player):
        player.command_points += 1
        self.update_ui()

    def remove_cp(self, player):
        if player.command_points > 0:
            player.command_points -= 1
        self.update_ui()

    def add_vp(self, player):
        player.victory_points += 1
        self.update_ui()

    def remove_vp(self, player):
        if player.victory_points > 0:
            player.victory_points -= 1
        self.update_ui()

    def end_turn(self, player):
        now = time.time()
        elapsed = 0
        if self.active_player and self.active_player.last_active is not None:
            elapsed = now - self.active_player.last_active
            self.active_player.time_elapsed += elapsed
        prev_total = 0
        for entry in reversed(self.log):
            if entry.get("Player") == player.name:
                prev_total = entry.get("VP total", 0)
                break
        vp_delta = player.victory_points - prev_total
        turn_time = round(elapsed)
        self.log.append({
            "Round": self.battle_round,
            "Player": player.name,
            "VP total": player.victory_points,
            "VP delta": vp_delta,
            "CP": player.command_points,
            "Turn": player.turns,
            "Turn Time(s)": turn_time,
            "Turn Time": time.strftime("%H:%M:%S", time.gmtime(turn_time))
        })
        self.active_player = self.players[1] if player == self.players[0] else self.players[0]
        for p in self.players:
            p.command_points += 1
        self.active_player.last_active = now
        if self.active_player == self.players[0]:
            self.battle_round += 1
        self.round_label.setText(f"Battle Round {self.battle_round} - {self.active_player.name}'s Turn")
        self.active_player.turns = self.battle_round
        for p, name_edit in self.name_edits:
            p.name = name_edit.text()
        self.update_ui()

    def update_clock(self):
        if self.active_player and self.active_player.last_active is not None and self.running:
            now = time.time()
            elapsed = now - self.active_player.last_active
            total = self.active_player.time_elapsed + elapsed
            self.set_time_label(self.active_player, total)

    def set_time_label(self, player, total_seconds):
        mins, secs = divmod(int(total_seconds), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        idx = self.players.index(player)
        self.time_labels[idx].setText(time_str)

    def update_ui(self):
        for i, player in enumerate(self.players):
            mins, secs = divmod(int(player.time_elapsed), 60)
            self.time_labels[i].setText(f"{mins:02d}:{secs:02d}")
            self.cp_labels[i].setText(str(player.command_points))
            self.vp_labels[i].setText(str(player.victory_points))
            for p, name_edit in self.name_edits:
                p.name = name_edit.text()

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if filename:
            with open(filename, "w", newline="") as f:
                fieldnames = ["Round", "Player", "VP total", "VP delta", "CP", "Turn", "Turn Time(s)", "Turn Time"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for entry in self.log:
                    writer.writerow(entry)
                f.write("\n")
                for player in self.players:
                    total_hms = time.strftime("%H:%M:%S", time.gmtime(player.time_elapsed))
                    writer.writerow({
                        "Round": "Summary",
                        "Player": player.name,
                        "VP total": player.victory_points,
                        "VP delta": "",
                        "CP": player.command_points,
                        "Turn": player.turns,
                        "Turn Time(s)": round(player.time_elapsed),
                        "Turn Time": total_hms
                    })

    def end_game(self):
        self.pause_game()
        p1, p2 = self.players
        if p1.victory_points > p2.victory_points:
            winner, loser = p1, p2
        elif p2.victory_points > p1.victory_points:
            winner, loser = p2, p1
        else:
            winner, loser = None, None
        if winner:
            msg = f"{winner.name} WINS! {winner.victory_points} VP to {loser.victory_points} VP"
        else:
            msg = f"Game is a TIE! {p1.victory_points} VP to {p2.victory_points} VP"
        total_game_time = sum(p.time_elapsed for p in self.players)
        total_hms = time.strftime("%H:%M:%S", time.gmtime(total_game_time))
        QMessageBox.information(self, "Game Over", msg + f"\nTotal Game Time: {total_hms}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WarhammerClockApp()
    window.show()
    sys.exit(app.exec())
