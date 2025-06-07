import sys
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
    QVBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt


class CitiesGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Города")
        self.setGeometry(100, 100, 400, 300)
        self.city_list = []
        self.used_cities = []
        self.records = []
        self.last_letter = ""
        self.player_score = 0
        self.computer_score = 0
        self.load_city_list()
        self.records = self.load_records()
        self.main_menu()

    def load_city_list(self):
        try:
            with open('cities.txt', 'r', encoding='utf-8') as f:
                self.city_list = [line.strip().lower() for line in f if line.strip()]
        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл городов не найден!")
            sys.exit(1)

    def load_records(self):
        if not os.path.exists("records.txt"):
            return []
        records = []
        with open("records.txt", "r", encoding="utf-8") as f:
            for line in f:
                try:
                    score = int(line.strip())
                    records.append(score)
                except ValueError:
                    continue
        return sorted(records, reverse=True)[:5]

    def save_score(self):
        self.records.append(self.player_score)
        self.records = sorted(self.records, reverse=True)[:5]
        with open("records.txt", "w", encoding="utf-8") as f:
            for score in self.records:
                f.write(f"{score}\n")

    def get_last_valid_letter(self, city):
        for c in reversed(city):
            if c not in 'ьъы':
                return c.lower()
        return city[-1].lower()

    def is_valid_city(self, city: str, last_letter: str) -> bool:
        return (city in self.city_list and
                city[0] == last_letter and
                city not in self.used_cities)

    def computer_move(self, last_letter: str) -> str:
        available = [c for c in self.city_list if c.startswith(last_letter) and c not in self.used_cities]
        return random.choice(available) if available else ""

    def has_available_moves(self):
        return any(c not in self.used_cities for c in self.city_list)

    def main_menu(self):
        self.clear_window()

        label = QLabel("Добро пожаловать в игру «Города»")
        label.setAlignment(Qt.AlignCenter)

        btn_start = QPushButton("Начать игру")
        btn_start.clicked.connect(self.start_game)

        btn_rules = QPushButton("Правила игры")
        btn_rules.clicked.connect(self.show_rules)

        btn_records = QPushButton("Таблица рекордов")
        btn_records.clicked.connect(self.show_records)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(btn_start)
        layout.addWidget(btn_rules)
        layout.addWidget(btn_records)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_game(self):
        self.clear_window()
        self.player_score = 0
        self.computer_score = 0
        self.used_cities = []
        self.last_letter = ""

        btn_exit = QPushButton("Выход")
        btn_exit.clicked.connect(self.main_menu)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите город")

        btn_submit = QPushButton("Отправить")
        btn_submit.clicked.connect(self.check_city)

        btn_hint = QPushButton("Подсказка")
        btn_hint.clicked.connect(self.show_hint)

        self.score_label = QLabel("Счёт: 0")
        self.score_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(btn_exit, alignment=Qt.AlignLeft)
        layout.addWidget(self.input)
        layout.addWidget(btn_submit)
        layout.addWidget(btn_hint)
        layout.addWidget(self.score_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.last_letter = random.choice(self.city_list)[-1].lower()
        self.show_message("Начало игры", f"Первый город должен начинаться на букву «{self.last_letter.upper()}».")

    def check_city(self):
        city = self.input.text().strip().lower()
        self.input.clear()

        if not city:
            return

        if city not in self.city_list:
            self.error("Такого города не существует.")
            return

        if city in self.used_cities:
            self.error("Город уже был использован.")
            return

        if self.last_letter and not city.startswith(self.last_letter):
            self.error(f"Город должен начинаться на букву «{self.last_letter.upper()}».")
            return

        self.used_cities.append(city)
        self.last_letter = self.get_last_valid_letter(city)
        self.player_score += 1
        self.score_label.setText(f"Счёт: {self.player_score}")

        if not self.has_available_moves():
            self.show_message("Конец игры", f"Больше нет возможных городов.\nВаш счёт: {self.player_score}")
            self.save_score()
            self.main_menu()
            return

        computer_city = self.computer_move(self.last_letter)
        if not computer_city:
            self.show_message("Победа!", f"Компьютер не смог назвать город.\nВы выиграли! Счёт: {self.player_score}")
            self.save_score()
            self.main_menu()
            return

        self.used_cities.append(computer_city)
        self.computer_score += 1
        self.last_letter = self.get_last_valid_letter(computer_city)
        self.show_message("Ход компьютера", f"Компьютер: {computer_city.capitalize()}")

    def show_hint(self):
        hint_cities = [city for city in self.city_list
                       if city.startswith(self.last_letter)
                       and city not in self.used_cities]

        if hint_cities:
            suggested = random.choice(hint_cities)
            self.show_message("Подсказка", f"Возможный город: {suggested.capitalize()}")
        else:
            self.show_message("Подсказка", "Нет возможных городов для этой буквы.")

    def show_rules(self):
        self.clear_window()

        btn_exit = QPushButton("Выход")
        btn_exit.clicked.connect(self.main_menu)

        label = QLabel("Правила игры:")
        label.setAlignment(Qt.AlignCenter)

        rules = QLabel("Называйте реальные города. Следующий город должен начинаться на последнюю букву предыдущего (исключая Ь, Ъ, Ы). Повторы запрещены.")
        rules.setWordWrap(True)
        rules.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(btn_exit, alignment=Qt.AlignLeft)
        layout.addWidget(label)
        layout.addWidget(rules)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_records(self):
        self.clear_window()

        btn_exit = QPushButton("Выход")
        btn_exit.clicked.connect(self.main_menu)

        title = QLabel("Таблица рекордов")
        title.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(btn_exit, alignment=Qt.AlignLeft)
        layout.addWidget(title)

        if self.records:
            for idx, score in enumerate(self.records, 1):
                layout.addWidget(QLabel(f"{idx}. Счёт: {score}"))
        else:
            layout.addWidget(QLabel("Нет рекордов."))

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_message(self, title, text):
        QMessageBox.information(self, title, text)

    def error(self, text):
        QMessageBox.warning(self, "Ошибка", text)

    def clear_window(self):
        widget = self.centralWidget()
        if widget:
            widget.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = CitiesGame()
    game.show()
    sys.exit(app.exec_())
