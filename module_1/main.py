import json
import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import docx  # Бібліотека для Word
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Налаштування логування (Виправлено кодування для Windows)
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

        # Налаштування вікна
        self.root.title(f"{self.config.get('app_name', 'Plagiarism Checker')} v{self.config.get('version', '1.1.0')}")
        self.root.geometry("500x400")

        # Інтерфейс
        tk.Label(root, text="AI Plagiarism Detector", font=("Arial", 16, "bold")).pack(pady=20)

        self.btn1 = tk.Button(root, text="Завантажити документ №1", command=lambda: self.load_file(1), width=30)
        self.btn1.pack(pady=5)

        self.btn2 = tk.Button(root, text="Завантажити документ №2", command=lambda: self.load_file(2), width=30)
        self.btn2.pack(pady=5)

        self.check_btn = tk.Button(root, text="ПЕРЕВІРИТИ", bg="#27ae60", fg="white",
                                   font=("Arial", 10, "bold"), command=self.compare, width=20)
        self.check_btn.pack(pady=30)

        self.res_label = tk.Label(root, text="Результат: - %", font=("Arial", 14, "bold"))
        self.res_label.pack()

        self.text1 = ""
        self.text2 = ""

    def load_config(self):
        # Шукаємо конфігурацію в поточній папці або на рівень вище
        config_paths = ['config.json', '../config.json', 'module_1/config.json']
        self.config = {"app_name": "Plagiarism Detector", "version": "1.1.0"}  # Дефолт

        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                    logging.info(f"Конфігурацію завантажено з: {path}")
                    break
                except Exception:
                    continue

    def read_document(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.docx':
            doc = docx.Document(path)
            return " ".join([para.text for para in doc.paragraphs])
        return ""

    def load_file(self, num):
        path = filedialog.askopenfilename(filetypes=[("Documents", "*.txt *.docx")])
        if path:
            try:
                content = self.read_document(path)
                if not content.strip():
                    raise ValueError("Файл порожній!")

                if num == 1:
                    self.text1 = content
                else:
                    self.text2 = content

                logging.info(f"Файл {num} успішно завантажено: {path}")
                messagebox.showinfo("Успіх", f"Документ {num} готовий!")
            except Exception as e:
                logging.error(f"Помилка завантаження файлу {num}: {e}")
                messagebox.showerror("Помилка", f"Не вдалося прочитати файл: {e}")

    def compare(self):
        if not self.text1 or not self.text2:
            messagebox.showwarning("Увага", "Завантажте два файли!")
            return

        try:
            vectorizer = TfidfVectorizer()
            matrix = vectorizer.fit_transform([self.text1, self.text2])
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            result = round(similarity * 100, 2)

            self.res_label.config(text=f"Результат: {result}%")
            logging.info(f"Аналіз виконано. Схожість: {result}%")

            with open("analysis_report.txt", "w", encoding='utf-8') as f:
                f.write(f"Результат аналізу: {result}% подібності.")
        except Exception as e:
            logging.error(f"Помилка аналізу: {e}")
            messagebox.showerror("Помилка", "Сталася помилка при обробці")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()