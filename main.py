import sys
import sqlite3
import json
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QDialog,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QCheckBox,
    QComboBox,
    QTabWidget,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Path to the logo icon
LOGO_ICON_PATH = "assets/images/logo.ico"


# Visualization Dialog
class VisualizationDialog(QDialog):
    """Dialog for displaying visualizations and data relations of the CP dataset."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(LOGO_ICON_PATH))
        self.setWindowTitle("Visualizations & Data Relations")
        self.resize(1200, 800)
        layout = QVBoxLayout()
        tabs = QTabWidget()
        # Data for visualizations
        self.problem_data = self.fetch_data()
        # Tab 1: Data Relationship Graph
        tabs.addTab(self.create_graph_tab(), "Data Relations Graph")
        # Tab 2: Problem Count by Difficulty
        tabs.addTab(self.create_difficulty_chart(), "Problems by Difficulty")
        # Tab 3: Tag Frequency
        tabs.addTab(self.create_tag_chart(), "Tag Frequency")
        # Tab 4: Language Usage
        tabs.addTab(self.create_language_chart(), "Language Usage")
        layout.addWidget(tabs)
        self.setLayout(layout)

    def fetch_data(self):
        """Fetch all problems and their solutions/implementations from the database."""
        # Fetch all problems and their solutions/implementations
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id, platform, title, difficulty, tags FROM problems")
            problems = c.fetchall()
            data = []
            for pid, platform, title, difficulty, tags in problems:
                c.execute(
                    "SELECT id, language FROM solutions WHERE problem_id=?", (pid,)
                )
                solutions = c.fetchall()
                sol_list = []
                for sid, language in solutions:
                    c.execute(
                        "SELECT method_name FROM implementations WHERE solution_id=?",
                        (sid,),
                    )
                    impls = [row[0] for row in c.fetchall()]
                    sol_list.append(
                        {"id": sid, "language": language, "implementations": impls}
                    )
                data.append(
                    {
                        "id": pid,
                        "platform": platform,
                        "title": title,
                        "difficulty": difficulty,
                        "tags": tags,
                        "solutions": sol_list,
                    }
                )
            conn.close()
            return data
        except Exception as e:
            show_error(self, f"Error fetching data: {e}")
            return []

    def create_graph_tab(self):
        # Draw a node/edge diagram using matplotlib (no networkx)
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.axis("off")
        node_positions = {}
        # Problems as root nodes
        for i, prob in enumerate(self.problem_data):
            px = 0
            py = -i * 3
            node_positions[f"P{prob['id']}"] = (px, py)
            ax.text(
                px,
                py,
                f"Problem: {prob['title']}",
                bbox=dict(facecolor="lightblue", alpha=0.7),
                ha="center",
            )
            # Draw solutions
            for j, sol in enumerate(prob["solutions"]):
                sx = px + 4
                sy = py - j * 1.5
                node_positions[f"S{sol['id']}"] = (sx, sy)
                ax.text(
                    sx,
                    sy,
                    f"Lang: {sol['language']}",
                    bbox=dict(facecolor="lightgreen", alpha=0.7),
                    ha="center",
                )
                # Edge: problem -> solution
                ax.plot([px, sx], [py, sy], "k-", lw=1)
                # Draw implementations
                for k, impl in enumerate(sol["implementations"]):
                    ix = sx + 4
                    iy = sy - k * 1.0
                    node_positions[f"I{sol['id']}_{k}"] = (ix, iy)
                    ax.text(
                        ix,
                        iy,
                        f"Impl: {impl}",
                        bbox=dict(facecolor="wheat", alpha=0.7),
                        ha="center",
                    )
                    # Edge: solution -> implementation
                    ax.plot([sx, ix], [sy, iy], "k--", lw=1)
        # Instead of tight_layout, use subplots_adjust to avoid margin issues
        fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)
        canvas = FigureCanvas(fig)
        scroll = QScrollArea()
        scroll.setWidget(canvas)
        scroll.setWidgetResizable(True)
        tab = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(scroll)
        tab.setLayout(vbox)
        return tab

    def create_difficulty_chart(self):
        # Bar chart: problem count by difficulty
        difficulties = {}
        for prob in self.problem_data:
            diff = prob["difficulty"] or "Unknown"
            difficulties[diff] = difficulties.get(diff, 0) + 1
        fig, ax = plt.subplots()
        ax.bar(list(difficulties.keys()), list(difficulties.values()), color="skyblue")
        ax.set_title("Problems by Difficulty")
        ax.set_xlabel("Difficulty")
        ax.set_ylabel("Count")
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        tab = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        return tab

    def create_tag_chart(self):
        # Bar chart: tag frequency
        tag_counts = {}
        for prob in self.problem_data:
            tags = prob["tags"]
            if tags:
                for tag in tags.split(","):
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        if not tag_counts:
            tag_counts = {"No Tags": 1}
        fig, ax = plt.subplots()
        tags, counts = zip(*sorted(tag_counts.items(), key=lambda x: -x[1]))
        ax.bar(tags, counts, color="orange")
        ax.set_title("Tag Frequency")
        ax.set_xlabel("Tag")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        tab = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        return tab

    def create_language_chart(self):
        # Bar chart: language usage
        lang_counts = {}
        for prob in self.problem_data:
            for sol in prob["solutions"]:
                lang = sol["language"] or "Unknown"
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        if not lang_counts:
            lang_counts = {"No Language": 1}
        fig, ax = plt.subplots()
        langs, counts = zip(*sorted(lang_counts.items(), key=lambda x: -x[1]))
        ax.bar(langs, counts, color="green")
        ax.set_title("Language Usage")
        ax.set_xlabel("Language")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        tab = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        return tab


DB_FILE = "cp_dataset.db"


def show_alert(parent, text, title="Alert"):
    """Show a warning alert message box."""
    try:
        QMessageBox.warning(parent, title, text)
    except Exception as e:
        print(f"Failed to show alert: {e}")


def show_error(parent, text, title="Error"):
    """Show an error message box."""
    try:
        QMessageBox.critical(parent, title, text)
    except Exception as e:
        print(f"Failed to show error: {e}")


def init_db():
    """Initialize the database and create tables if they do not exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                title TEXT,
                problem_description TEXT,
                url TEXT,
                difficulty TEXT,
                tags TEXT
            )
        """)
        # Add missing columns if needed
        columns = [row[1] for row in c.execute("PRAGMA table_info(problems)")]
        if "difficulty" not in columns:
            c.execute("ALTER TABLE problems ADD COLUMN difficulty TEXT")
        if "tags" not in columns:
            c.execute("ALTER TABLE problems ADD COLUMN tags TEXT")
        c.execute("""
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                language TEXT,
                FOREIGN KEY(problem_id) REFERENCES problems(id) ON DELETE CASCADE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS implementations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solution_id INTEGER,
                method_name TEXT,
                explanation TEXT,
                url TEXT,
                code TEXT,
                notes TEXT,
                FOREIGN KEY(solution_id) REFERENCES solutions(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        show_error(None, f"Database initialization failed: {e}")


class ImplementationDialog(QDialog):
    """Dialog for adding or editing an implementation for a solution."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(LOGO_ICON_PATH))
        self.setWindowTitle("Add/Edit Implementation")
        self.method_name_edit = QLineEdit()
        self.explanation_edit = QTextEdit()
        self.url_edit = QLineEdit()
        self.code_edit = QTextEdit()
        self.notes_edit = QTextEdit()
        if data:
            self.method_name_edit.setText(data.get("method_name", ""))
            self.explanation_edit.setPlainText(data.get("Explanation", ""))
            self.url_edit.setText(data.get("url", ""))
            self.code_edit.setPlainText(data.get("code", ""))
            self.notes_edit.setPlainText(data.get("notes", ""))
        layout = QFormLayout()
        layout.addRow("Method Name:", self.method_name_edit)
        layout.addRow("Explanation:", self.explanation_edit)
        layout.addRow("URL:", self.url_edit)
        layout.addRow("Code:", self.code_edit)
        layout.addRow("Notes:", self.notes_edit)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_data(self):
        """Return the data entered in the dialog as a dictionary."""
        return {
            "method_name": self.method_name_edit.text(),
            "Explanation": self.explanation_edit.toPlainText(),
            "url": self.url_edit.text(),
            "code": self.code_edit.toPlainText(),
            "notes": self.notes_edit.toPlainText(),
        }


class SolutionDialog(QDialog):
    """Dialog for adding or editing a solution (language) for a problem."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(LOGO_ICON_PATH))
        self.setWindowTitle("Add/Edit Language")
        self.language_edit = QLineEdit()
        self.impl_list = QListWidget()
        self.implementations = []
        if data:
            self.language_edit.setText(data.get("language", ""))
            for impl in data.get("implementations", []):
                item = QListWidgetItem(impl.get("method_name", ""))
                item.setData(Qt.ItemDataRole.UserRole, impl)
                self.impl_list.addItem(item)
                self.implementations.append(impl)
        add_btn = QPushButton("Add Implementation")
        add_btn.clicked.connect(self.add_impl)
        edit_btn = QPushButton("Edit Implementation")
        edit_btn.clicked.connect(self.edit_impl)
        del_btn = QPushButton("Delete Implementation")
        del_btn.clicked.connect(self.delete_impl)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Language:"))
        layout.addWidget(self.language_edit)
        layout.addWidget(QLabel("Implementations:"))
        layout.addWidget(self.impl_list)
        layout.addLayout(btn_layout)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def add_impl(self):
        dlg = ImplementationDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            if not data["method_name"].strip():
                show_alert(self, "Method Name cannot be empty.")
                return
            item = QListWidgetItem(data["method_name"])
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.impl_list.addItem(item)
            self.implementations.append(data)

    def edit_impl(self):
        row = self.impl_list.currentRow()
        if row == -1:
            show_alert(self, "Please select a method to edit.")
            return
        impl = self.impl_list.currentItem().data(Qt.ItemDataRole.UserRole)
        dlg = ImplementationDialog(self, impl)
        if dlg.exec():
            data = dlg.get_data()
            if not data["method_name"].strip():
                show_alert(self, "Method Name cannot be empty.")
                return
            self.impl_list.currentItem().setText(data["method_name"])
            self.impl_list.currentItem().setData(Qt.ItemDataRole.UserRole, data)
            self.implementations[row] = data

    def delete_impl(self):
        row = self.impl_list.currentRow()
        if row == -1:
            show_alert(self, "Please select a method to delete.")
            return
        self.impl_list.takeItem(row)
        del self.implementations[row]

    def get_data(self):
        """Return the data entered in the dialog as a dictionary."""
        return {
            "language": self.language_edit.text(),
            "implementations": [
                self.impl_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.impl_list.count())
            ],
        }


class ProblemDialog(QDialog):
    """Dialog for adding or editing a problem and its solutions."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(LOGO_ICON_PATH))
        self.setWindowTitle("Add/Edit Problem")
        self.platform_edit = QLineEdit()
        self.title_edit = QLineEdit()
        self.problem_description_edit = QTextEdit()
        self.url_edit = QLineEdit()
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["", "Easy", "Medium", "Hard"])
        self.tags_edit = QLineEdit()
        self.sol_list = QListWidget()
        self.solutions = []
        if data:
            self.platform_edit.setText(data.get("platform", ""))
            self.title_edit.setText(data.get("title", ""))
            self.problem_description_edit.setPlainText(
                data.get("problem_description", "")
            )
            self.url_edit.setText(data.get("url", ""))
            self.difficulty_combo.setCurrentText(data.get("difficulty", ""))
            self.tags_edit.setText(
                ", ".join(data.get("tags", []))
                if isinstance(data.get("tags"), list)
                else data.get("tags", "")
            )
            for sol in data.get("solutions", []):
                item = QListWidgetItem(sol.get("language", ""))
                item.setData(Qt.ItemDataRole.UserRole, sol)
                self.sol_list.addItem(item)
                self.solutions.append(sol)
        add_btn = QPushButton("Add Language")
        add_btn.clicked.connect(self.add_solution)
        edit_btn = QPushButton("Edit Language")
        edit_btn.clicked.connect(self.edit_solution)
        del_btn = QPushButton("Delete Language")
        del_btn.clicked.connect(self.delete_solution)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout = QVBoxLayout()
        info_group = QGroupBox("Problem Info")
        info_layout = QFormLayout()
        info_layout.addRow("Platform:", self.platform_edit)
        info_layout.addRow("Title:", self.title_edit)
        info_layout.addRow("Problem Description:", self.problem_description_edit)
        info_layout.addRow("URL:", self.url_edit)
        info_layout.addRow("Difficulty:", self.difficulty_combo)
        info_layout.addRow("Tags (comma separated):", self.tags_edit)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        layout.addWidget(QLabel("Languages:"))
        layout.addWidget(self.sol_list)
        layout.addLayout(btn_layout)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def add_solution(self):
        dlg = SolutionDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            if not data["language"].strip():
                show_alert(self, "Language cannot be empty.")
                return
            item = QListWidgetItem(data["language"])
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.sol_list.addItem(item)
            self.solutions.append(data)

    def edit_solution(self):
        row = self.sol_list.currentRow()
        if row == -1:
            show_alert(self, "Please select a language to edit.")
            return
        sol = self.sol_list.currentItem().data(Qt.ItemDataRole.UserRole)
        dlg = SolutionDialog(self, sol)
        if dlg.exec():
            data = dlg.get_data()
            if not data["language"].strip():
                show_alert(self, "Language cannot be empty.")
                return
            self.sol_list.currentItem().setText(data["language"])
            self.sol_list.currentItem().setData(Qt.ItemDataRole.UserRole, data)
            self.solutions[row] = data

    def delete_solution(self):
        row = self.sol_list.currentRow()
        if row == -1:
            show_alert(self, "Please select a language to delete.")
            return
        self.sol_list.takeItem(row)
        del self.solutions[row]

    def get_data(self):
        """Return the data entered in the dialog as a dictionary."""
        tags_str = self.tags_edit.text().strip()
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else []
        return {
            "platform": self.platform_edit.text(),
            "title": self.title_edit.text(),
            "problem_description": self.problem_description_edit.toPlainText(),
            "url": self.url_edit.text(),
            "difficulty": self.difficulty_combo.currentText(),
            "tags": tags,
            "solutions": [
                self.sol_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.sol_list.count())
            ],
        }


class MainWindow(QMainWindow):
    """Main application window for the CP Dataset GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(LOGO_ICON_PATH))
        self.setWindowTitle("CP Dataset GUI")
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "",
                "Platform",
                "Title",
                "Problem Description",
                "URL",
                "Difficulty",
                "Tags",
                "ID",
            ]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.cellDoubleClicked.connect(self.edit_problem)
        self.table.cellClicked.connect(self.handle_url_click)
        self.refresh_table()
        self.resize_table_headers()

        add_btn = QPushButton("Add Problem")
        add_btn.clicked.connect(self.add_problem)
        edit_btn = QPushButton("Edit Selected Problem")
        edit_btn.clicked.connect(self.edit_selected_problem)
        del_btn = QPushButton("Delete Selected Problem")
        del_btn.clicked.connect(self.delete_selected_problem)
        export_jsonl_btn = QPushButton("Export JSONL")
        export_jsonl_btn.clicked.connect(self.export_jsonl)
        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        import_btn = QPushButton("Import JSONL (add)")
        import_btn.clicked.connect(self.import_jsonl)
        visualize_btn = QPushButton("Visualization")
        visualize_btn.clicked.connect(self.open_visualization)
        hbox = QHBoxLayout()
        hbox.addWidget(add_btn)
        hbox.addWidget(edit_btn)
        hbox.addWidget(del_btn)
        hbox.addWidget(export_jsonl_btn)
        hbox.addWidget(export_csv_btn)
        hbox.addWidget(import_btn)
        hbox.addWidget(visualize_btn)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.table)
        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)

    def open_visualization(self):
        """Open the visualization dialog."""
        dlg = VisualizationDialog(self)
        dlg.exec()

    def resize_table_headers(self):
        """Resize the table headers for better display."""
        header = self.table.horizontalHeader()
        for col in range(1, self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 40)

    def refresh_table(self):
        """Refresh the table with the latest data from the database."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT id, platform, title, problem_description, url, difficulty, tags FROM problems"
        )
        try:
            rows = c.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                cb = QCheckBox()
                self.table.setCellWidget(i, 0, cb)
                for j in range(1, 7):
                    if j == 4:  # URL
                        url_item = QTableWidgetItem(str(row[j]))
                        url_item.setForeground(Qt.GlobalColor.blue)
                        url_item.setToolTip("Click to open in browser")
                        self.table.setItem(i, j, url_item)
                    else:
                        self.table.setItem(i, j, QTableWidgetItem(str(row[j])))
                self.table.setItem(i, 7, QTableWidgetItem(str(row[0])))
            conn.close()
            self.resize_table_headers()
        except Exception as e:
            show_error(self, f"Error refreshing table: {e}")

    def get_selected_rows(self):
        """Return a list of selected row indices."""
        selected = []
        for row in range(self.table.rowCount()):
            cb = self.table.cellWidget(row, 0)
            if cb and cb.isChecked():
                selected.append(row)
        return selected

    def get_problem_id(self, row):
        """Return the problem ID for a given row index."""
        item = self.table.item(row, 7)
        if item:
            return int(item.text())
        return None

    def get_problem_full(self, problem_id):
        """Return the full problem data for a given problem ID."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT platform, title, problem_description, url, difficulty, tags FROM problems WHERE id=?",
            (problem_id,),
        )
        try:
            result = c.fetchone()
            if not result:
                conn.close()
                return None
            platform, title, problem_description, url, difficulty, tags = result
            c.execute(
                "SELECT id, language FROM solutions WHERE problem_id=?", (problem_id,)
            )
            solutions = []
            for sol_id, language in c.fetchall():
                c.execute(
                    "SELECT method_name, explanation, url, code, notes FROM implementations WHERE solution_id=?",
                    (sol_id,),
                )
                impls = [
                    {
                        "method_name": m,
                        "Explanation": exp,
                        "url": u,
                        "code": code,
                        "notes": notes,
                    }
                    for m, exp, u, code, notes in c.fetchall()
                ]
                solutions.append({"language": language, "implementations": impls})
            conn.close()
            tags_list = [t.strip() for t in tags.split(",")] if tags else []
            return {
                "platform": platform,
                "title": title,
                "problem_description": problem_description,
                "url": url,
                "difficulty": difficulty,
                "tags": tags_list,
                "solutions": solutions,
            }
        except Exception as e:
            show_error(self, f"Error fetching problem data: {e}")
            return None

    def get_all_problem_ids(self):
        """Return a list of all problem IDs in the database."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id FROM problems")
        ids = [row[0] for row in c.fetchall()]
        conn.close()
        return ids

    def add_problem(self):
        """Add a new problem to the database."""
        try:
            dlg = ProblemDialog(self)
            if dlg.exec():
                data = dlg.get_data()
                if not data["title"].strip():
                    show_alert(self, "Title cannot be empty.")
                    return
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO problems (platform, title, problem_description, url, difficulty, tags) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        data["platform"],
                        data["title"],
                        data["problem_description"],
                        data["url"],
                        data["difficulty"],
                        ", ".join(data["tags"]),
                    ),
                )
                problem_id = c.lastrowid
                for sol in data["solutions"]:
                    c.execute(
                        "INSERT INTO solutions (problem_id, language) VALUES (?, ?)",
                        (problem_id, sol["language"]),
                    )
                    solution_id = c.lastrowid
                    for impl in sol["implementations"]:
                        c.execute(
                            "INSERT INTO implementations (solution_id, method_name, explanation, url, code, notes) VALUES (?, ?, ?, ?, ?, ?)",
                            (
                                solution_id,
                                impl["method_name"],
                                impl["Explanation"],
                                impl["url"],
                                impl["code"],
                                impl["notes"],
                            ),
                        )
                conn.commit()
                conn.close()
                self.refresh_table()
                QMessageBox.information(self, "Success", "Problem added successfully.")
        except Exception as e:
            show_error(self, f"Error adding problem: {e}")

    def edit_problem(self, row, column=None):
        """Edit the selected problem in the database."""
        try:
            checked_rows = self.get_selected_rows()
            if len(checked_rows) > 1:
                show_alert(self, "Please select only one row to edit.")
                return
            if not checked_rows and (self.table.rowCount() == 0):
                show_alert(self, "No problems available to edit.")
                return
            if not checked_rows:
                checked_rows = [row]
            problem_id = self.get_problem_id(checked_rows[0])
            if problem_id is None:
                show_alert(self, "No problem found for editing.")
                return
            row_data = self.get_problem_full(problem_id)
            if not row_data:
                show_alert(self, "No data found for editing.")
                return
            dlg = ProblemDialog(self, row_data)
            if dlg.exec():
                data = dlg.get_data()
                if not data["title"].strip():
                    show_alert(self, "Title cannot be empty.")
                    return
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute(
                    "UPDATE problems SET platform=?, title=?, problem_description=?, url=?, difficulty=?, tags=? WHERE id=?",
                    (
                        data["platform"],
                        data["title"],
                        data["problem_description"],
                        data["url"],
                        data["difficulty"],
                        ", ".join(data["tags"]),
                        problem_id,
                    ),
                )
                c.execute("SELECT id FROM solutions WHERE problem_id=?", (problem_id,))
                old_solution_ids = [row[0] for row in c.fetchall()]
                for sol_id in old_solution_ids:
                    c.execute(
                        "DELETE FROM implementations WHERE solution_id=?", (sol_id,)
                    )
                c.execute("DELETE FROM solutions WHERE problem_id=?", (problem_id,))
                for sol in data["solutions"]:
                    c.execute(
                        "INSERT INTO solutions (problem_id, language) VALUES (?, ?)",
                        (problem_id, sol["language"]),
                    )
                    solution_id = c.lastrowid
                    for impl in sol["implementations"]:
                        c.execute(
                            "INSERT INTO implementations (solution_id, method_name, explanation, url, code, notes) VALUES (?, ?, ?, ?, ?, ?)",
                            (
                                solution_id,
                                impl["method_name"],
                                impl["Explanation"],
                                impl["url"],
                                impl["code"],
                                impl["notes"],
                            ),
                        )
                conn.commit()
                conn.close()
                self.refresh_table()
                QMessageBox.information(
                    self, "Success", "Problem updated successfully."
                )
        except Exception as e:
            show_error(self, f"Error editing problem: {e}")

    def edit_selected_problem(self):
        """Edit the currently selected problem."""
        checked_rows = self.get_selected_rows()
        if not checked_rows and self.table.rowCount() == 0:
            show_alert(self, "No problems available to edit.")
            return
        if not checked_rows:
            show_alert(self, "Please select a problem to edit.")
            return
        if len(checked_rows) != 1:
            show_alert(self, "You can only edit one problem at a time.")
            return
        self.edit_problem(checked_rows[0])

    def delete_selected_problem(self):
        """Delete the selected problems from the database."""
        checked_rows = self.get_selected_rows()
        if not checked_rows:
            show_alert(self, "Please select problem(s) to delete.")
            return
        ret = QMessageBox.question(
            self,
            "Delete?",
            f"Are you sure you want to delete {len(checked_rows)} problem(s)?",
        )
        if ret != QMessageBox.StandardButton.Yes:
            return
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            for row in sorted(checked_rows, reverse=True):
                problem_id = self.get_problem_id(row)
                if problem_id is not None:
                    c.execute("DELETE FROM problems WHERE id=?", (problem_id,))
            conn.commit()
            conn.close()
            self.refresh_table()
            QMessageBox.information(self, "Success", "Problem(s) deleted successfully.")
        except Exception as e:
            show_error(self, f"Delete failed:\n{e}")

    def export_jsonl(self):
        """Export the dataset to a JSONL file."""
        if self.table.rowCount() == 0:
            show_alert(self, "No data to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export JSONL", filter="JSONL Files (*.jsonl);;All Files (*)"
        )
        if not file_path:
            show_alert(self, "No file selected for export.")
            return
        checked_rows = self.get_selected_rows()
        if checked_rows:
            ids = [self.get_problem_id(row) for row in checked_rows]
        else:
            ids = self.get_all_problem_ids()
        if not ids:
            show_alert(self, "No data to export.")
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for pid in ids:
                    obj = self.get_problem_full(pid)
                    if obj:
                        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
            QMessageBox.information(self, "Export", "Exported to JSONL.")
        except Exception as e:
            show_error(self, f"Export failed:\n{e}")

    def export_csv(self):
        """Export the dataset to a CSV file."""
        if self.table.rowCount() == 0:
            show_alert(self, "No data to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", filter="CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            show_alert(self, "No file selected for export.")
            return
        checked_rows = self.get_selected_rows()
        if checked_rows:
            ids = [self.get_problem_id(row) for row in checked_rows]
        else:
            ids = self.get_all_problem_ids()
        if not ids:
            show_alert(self, "No data to export.")
            return
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                # Header: include all top-level attributes and one row per implementation:
                writer.writerow(
                    [
                        "platform",
                        "title",
                        "problem_description",
                        "url",
                        "difficulty",
                        "tags",
                        "language",
                        "method_name",
                        "Explanation",
                        "impl_url",
                        "code",
                        "notes",
                    ]
                )
                for pid in ids:
                    obj = self.get_problem_full(pid)
                    if obj:
                        tags_field = ", ".join(obj.get("tags", []))
                        for sol in obj.get("solutions", []):
                            lang = sol.get("language", "")
                            for impl in sol.get("implementations", []):
                                writer.writerow(
                                    [
                                        obj.get("platform", ""),
                                        obj.get("title", ""),
                                        obj.get("problem_description", ""),
                                        obj.get("url", ""),
                                        obj.get("difficulty", ""),
                                        tags_field,
                                        lang,
                                        impl.get("method_name", ""),
                                        impl.get("Explanation", ""),
                                        impl.get("url", ""),
                                        impl.get("code", ""),
                                        impl.get("notes", ""),
                                    ]
                                )
            QMessageBox.information(self, "Export", "Exported to CSV.")
        except Exception as e:
            show_error(self, f"Export failed:\n{e}")

    def import_jsonl(self):
        """Import problems from a JSONL file into the database."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import JSONL", filter="JSONL Files (*.jsonl);;All Files (*)"
        )
        if not file_path:
            show_alert(self, "No file selected for import.")
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                count = 0
                for line in f:
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    tags = obj.get("tags", "")
                    if isinstance(tags, list):
                        tags = ", ".join(tags)
                    c.execute(
                        "INSERT INTO problems (platform, title, problem_description, url, difficulty, tags) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            obj.get("platform", ""),
                            obj.get("title", ""),
                            obj.get("problem_description", ""),
                            obj.get("url", ""),
                            obj.get("difficulty", ""),
                            tags,
                        ),
                    )
                    problem_id = c.lastrowid
                    for sol in obj.get("solutions", []):
                        c.execute(
                            "INSERT INTO solutions (problem_id, language) VALUES (?, ?)",
                            (problem_id, sol.get("language", "")),
                        )
                        solution_id = c.lastrowid
                        for impl in sol.get("implementations", []):
                            c.execute(
                                "INSERT INTO implementations (solution_id, method_name, explanation, url, code, notes) VALUES (?, ?, ?, ?, ?, ?)",
                                (
                                    solution_id,
                                    impl.get("method_name", ""),
                                    impl.get("Explanation", ""),
                                    impl.get("url", ""),
                                    impl.get("code", ""),
                                    impl.get("notes", ""),
                                ),
                            )
                    count += 1
                conn.commit()
                conn.close()
            self.refresh_table()
            QMessageBox.information(
                self, "Import", f"Import successful. {count} problems imported."
            )
        except Exception as e:
            show_error(self, f"Import failed:\n{e}")

    def handle_url_click(self, row, column):
        """Handle clicks on the URL column to open the link in a browser."""
        if column == 4:  # URL column
            url = self.table.item(row, 4).text()
            if url and (url.startswith("http://") or url.startswith("https://")):
                import webbrowser

                webbrowser.open(url)


def check_db_integrity():
    """Check if the database has the required tables and columns."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Check for required tables and columns
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems'"
        )
        if not c.fetchone():
            raise Exception("Missing 'problems' table")
        c.execute("PRAGMA table_info(problems)")
        problem_cols = [row[1] for row in c.fetchall()]
        for col in [
            "platform",
            "title",
            "problem_description",
            "url",
            "difficulty",
            "tags",
        ]:
            if col not in problem_cols:
                raise Exception(f"Missing column '{col}' in 'problems'")
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='solutions'"
        )
        if not c.fetchone():
            raise Exception("Missing 'solutions' table")
        c.execute("PRAGMA table_info(solutions)")
        solution_cols = [row[1] for row in c.fetchall()]
        for col in ["problem_id", "language"]:
            if col not in solution_cols:
                raise Exception(f"Missing column '{col}' in 'solutions'")
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='implementations'"
        )
        if not c.fetchone():
            raise Exception("Missing 'implementations' table")
        c.execute("PRAGMA table_info(implementations)")
        impl_cols = [row[1] for row in c.fetchall()]
        for col in [
            "solution_id",
            "method_name",
            "explanation",
            "url",
            "code",
            "notes",
        ]:
            if col not in impl_cols:
                raise Exception(f"Missing column '{col}' in 'implementations'")
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


def prompt_db_reset(parent, error_msg):
    """Prompt the user to reset the database if corruption or schema change is detected."""
    msg = (
        f"Warning: The dataset appears to be corrupted or its structure has changed.\n\n"
        f"Error: {error_msg}\n\n"
        "To get started, we need to delete the current database and create a new one.\n"
        "This action is NOT reversible.\n\n"
        "Please make sure to EXPORT your current data if possible before proceeding.\n\n"
        "Do you want to delete and reinitialize the database now?"
    )
    reply = QMessageBox.warning(
        parent,
        "Database Corrupted or Changed!",
        msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(LOGO_ICON_PATH))
    ok, err = check_db_integrity()
    if not ok:
        # Show warning and ask user if they want to reset
        proceed = prompt_db_reset(None, err)
        if proceed:
            import os

            try:
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to delete database: {e}")
                sys.exit(1)
            init_db()
            QMessageBox.information(
                None, "Database Reset", "Database has been reset and reinitialized."
            )
        else:
            sys.exit(0)
    else:
        init_db()
    win = MainWindow()
    win.resize(1500, 900)
    win.show()
    sys.exit(app.exec())
