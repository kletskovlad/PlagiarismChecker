import json
import os
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
# Потрібні бібліотеки для математики (мають бути встановлені: pip install scikit-learn python-docx)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- КОНФІГУРАЦІЯ ЛОГУВАННЯ ---
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


class PlagiarismApp:
    def __init__(self, root):
        self.root = root
        self.load_config()

        # Налаштування головного вікна
        self.root.title(f"{self.config['app_name']} v{self.config['version']}")
        self.root.geometry("500x450")  # Трохи збільшили висоту для нової кнопки

        # --- ЕЛЕМЕНТИ ІНТЕРФЕЙСУ (GUI) ---
        tk.Label(root, text="AI Перевірка Плагіату", font=("Arial", 14, "bold")).pack(pady=20)

        tk.Button(root, text="Обрати документ №1", command=lambda: self.load_file(1), width=25).pack(pady=5)
        tk.Button(root, text="Обрати документ №2", command=lambda: self.load_file(2), width=25).pack(pady=5)

        tk.Button(root, text="Порівняти", bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                  command=self.compare, width=20).pack(pady=20)

        # НОВА КНОПКА (вимога Частини 4)
        tk.Button(root, text="Експорт звіту в JSON", bg="#4CAF50", fg="white",
                  command=self.run_export, width=20).pack(pady=5)

        self.res_label = tk.Label(root, text="Схожість: - %", font=("Arial", 12))
        self.res_label.pack(pady=10)

        # Сховище
        self.doc1, self.doc2 = "", ""
        self.file1_name, self.file2_name = "Не обрано", "Не обрано"
        self.last_score = None  # Тут зберігатимемо результат для експорту

    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error(f"Помилка конфігурації: {e}")
            self.config = {"app_name": "AI Checker", "version": "1.2.0"}

    def read_document(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".txt":
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == ".docx":
            from docx import Document
            doc = Document(path)
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            raise ValueError("Непідтримуваний формат файлу. Оберіть .txt або .docx")

    def load_file(self, num):
        path = filedialog.askopenfilename(filetypes=[("Текстові файли", "*.txt *.docx")])
        if path:
            try:
                content = self.read_document(path)
                if num == 1:
                    self.doc1 = content
                    self.file1_name = os.path.basename(path)
                else:
                    self.doc2 = content
                    self.file2_name = os.path.basename(path)
                logging.info(f"Успішно завантажено файл {num}: {path}")
                messagebox.showinfo("Успіх", f"Файл {num} готовий!")
            except Exception as e:
                logging.error(f"Помилка читання файлу: {e}")
                messagebox.showerror("Помилка", str(e))

    def compare(self):
        if not self.doc1.strip() or not self.doc2.strip():
            messagebox.showwarning("Увага", "Оберіть обидва файли!")
            return

        try:
            vectorizer = TfidfVectorizer()
            matrix = vectorizer.fit_transform([self.doc1, self.doc2])
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]

            self.last_score = round(similarity * 100, 2)
            self.res_label.config(text=f"Схожість: {self.last_score}%", fg="blue")

            logging.info(f"Результат: {self.last_score}%")
            with open("last_result.txt", "w", encoding='utf-8') as f:
                f.write(f"Останній результат: {self.last_score}%")
        except Exception as e:
            logging.error(f"Помилка аналізу: {e}")
            messagebox.showerror("Помилка", "Не вдалося порівняти тексти.")

    # --- НОВИЙ МОДУЛЬ ЕКСПОРТУ (Частина 4) ---
    def run_export(self):
        """Перевірка перед експортом"""
        if self.last_score is not None:
            self.export_to_json(self.file1_name, self.file2_name, self.last_score)
        else:
            messagebox.showwarning("Увага", "Спочатку натисніть 'Порівняти'!")

    def export_to_json(self, f1, f2, score):
        """Створення JSON файлу"""
        try:
            report = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "files": [f1, f2],
                "similarity_score": f"{score}%",
                "status": "Success"
            }
            with open("report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=4)

            logging.info("Звіт успішно експортовано в JSON")
            messagebox.showinfo("JSON Експорт", "Звіт збережено у файл report.json")
        except Exception as e:
            logging.error(f"Помилка експорту: {e}")
            messagebox.showerror("Помилка", "Не вдалося зберегти JSON.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()
