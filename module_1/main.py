import json
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Налаштування логування [cite: 6, 19]
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PlagiarismApp:
    def __init__(self, root):
        self.root = root
        self.load_config()
        self.root.title(f"{self.config['app_name']} v{self.config['version']}")
        self.root.geometry("500x350")

        # Графічний інтерфейс [cite: 4, 17]
        tk.Label(root, text="AI Перевірка Плагіату", font=("Arial", 14, "bold")).pack(pady=20)

        self.btn1 = tk.Button(root, text="Обрати документ №1", command=lambda: self.load_file(1))
        self.btn1.pack(pady=5)

        self.btn2 = tk.Button(root, text="Обрати документ №2", command=lambda: self.load_file(2))
        self.btn2.pack(pady=5)

        self.check_btn = tk.Button(root, text="Порівняти", bg="blue", fg="white", command=self.compare)
        self.check_btn.pack(pady=20)

        self.res_label = tk.Label(root, text="Схожість: - %", font=("Arial", 12))
        self.res_label.pack()

        self.doc1, self.doc2 = "", ""

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error(f"Помилка конфігурації: {e}")
            self.config = {"app_name": "Checker", "version": "1.0"}

    def load_file(self, num):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if num == 1:
                        self.doc1 = content
                    else:
                        self.doc2 = content
                logging.info(f"Завантажено файл {num}: {path}")
            except Exception as e:
                logging.error(f"Помилка читання: {e}")
                messagebox.showerror("Помилка", "Не вдалося прочитати файл")

    def compare(self):
        # Валідація [cite: 5, 17]
        if not self.doc1 or not self.doc2:
            messagebox.showwarning("Увага", "Завантажте обидва файли!")
            return

        try:
            # Алгоритм за Варіантом 5
            vectorizer = TfidfVectorizer()
            matrix = vectorizer.fit_transform([self.doc1, self.doc2])
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            score = round(similarity * 100, 2)

            self.res_label.config(text=f"Схожість: {score}%")
            logging.info(f"Розрахунок завершено: {score}%")

            # Збереження результату у файл [cite: 7, 20]
            with open("last_result.txt", "w") as f:
                f.write(f"Result: {score}%")
        except Exception as e:
            logging.error(f"Помилка аналізу: {e}")
            messagebox.showerror("Помилка", "Сталася помилка при аналізі")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()