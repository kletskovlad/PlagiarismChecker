import json
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Логування (UTF-8 фікс)
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
        self.root.title(f"{self.config['app_name']} v{self.config['version']}")
        self.root.geometry("500x350")

        tk.Label(root, text="AI Перевірка Плагіату", font=("Arial", 14, "bold")).pack(pady=20)

        tk.Button(root, text="Обрати документ №1", command=lambda: self.load_file(1)).pack(pady=5)
        tk.Button(root, text="Обрати документ №2", command=lambda: self.load_file(2)).pack(pady=5)

        tk.Button(root, text="Порівняти", bg="blue", fg="white", command=self.compare).pack(pady=20)

        self.res_label = tk.Label(root, text="Схожість: - %", font=("Arial", 12))
        self.res_label.pack()

        self.doc1, self.doc2 = "", ""

    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error(f"Помилка конфігурації: {e}")
            self.config = {"app_name": "Checker", "version": "1.0"}

    # Читання файлів (.txt + .docx)
    def read_document(self, path):
        ext = os.path.splitext(path)[1]

        if ext == ".txt":
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == ".docx":
            from docx import Document
            doc = Document(path)
            return "\n".join([p.text for p in doc.paragraphs])

        else:
            raise ValueError("Непідтримуваний формат файлу")

    def load_file(self, num):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt *.docx")]
        )

        if path:
            try:
                content = self.read_document(path)

                if num == 1:
                    self.doc1 = content
                else:
                    self.doc2 = content

                logging.info(f"Завантажено файл {num}: {path}")

            except ValueError as e:
                messagebox.showerror("Помилка", str(e))

            except Exception as e:
                logging.error(f"Помилка читання: {e}")
                messagebox.showerror("Помилка", "Не вдалося прочитати файл")

    def compare(self):
        # Перевірка пустих даних
        if not self.doc1.strip() or not self.doc2.strip():
            messagebox.showwarning("Увага", "Один із файлів порожній!")
            return

        try:
            vectorizer = TfidfVectorizer()
            matrix = vectorizer.fit_transform([self.doc1, self.doc2])
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            score = round(similarity * 100, 2)

            self.res_label.config(text=f"Схожість: {score}%")
            logging.info(f"Розрахунок завершено: {score}%")

            with open("last_result.txt", "w", encoding='utf-8') as f:
                f.write(f"Result: {score}%")

        except Exception as e:
            logging.error(f"Помилка аналізу: {e}")
            messagebox.showerror("Помилка", "Сталася помилка при аналізі")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()