import json
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- КОНФІГУРАЦІЯ ЛОГУВАННЯ ---
# Налаштування журналу подій для аудиту роботи програми
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'  # Підтримка кирилиці в логах
)


class PlagiarismApp:
    """
    Головний клас додатка, що описує логіку інтерфейсу 
    та обробку подій користувача.
    """

    def __init__(self, root):
        self.root = root
        self.load_config()  # Ініціалізація налаштувань

        # Налаштування головного вікна
        self.root.title(f"{self.config['app_name']} v{self.config['version']}")
        self.root.geometry("500x350")

        # --- ЕЛЕМЕНТИ ІНТЕРФЕЙСУ (GUI) ---
        tk.Label(root, text="AI Перевірка Плагіату", font=("Arial", 14, "bold")).pack(pady=20)

        # Кнопки вибору документів
        tk.Button(root, text="Обрати документ №1", command=lambda: self.load_file(1)).pack(pady=5)
        tk.Button(root, text="Обрати документ №2", command=lambda: self.load_file(2)).pack(pady=5)

        # Кнопка запуску аналізу
        tk.Button(root, text="Порівняти", bg="blue", fg="white", command=self.compare).pack(pady=20)

        # Мітка для відображення результату
        self.res_label = tk.Label(root, text="Схожість: - %", font=("Arial", 12))
        self.res_label.pack()

        # Тимчасове сховище для контенту документів
        self.doc1, self.doc2 = "", ""

    def load_config(self):
        """Зчитування метаданих проекту із зовнішнього JSON-файлу."""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error(f"Помилка конфігурації: {e}")
            # Значення за замовчуванням у разі відсутності файлу
            self.config = {"app_name": "Checker", "version": "1.0"}

    def read_document(self, path):
        """
        Універсальний метод для зчитування тексту.
        Підтримує формати .txt та .docx (через бібліотеку python-docx).
        """
        ext = os.path.splitext(path)[1].lower()

        if ext == ".txt":
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == ".docx":
            from docx import Document
            doc = Document(path)
            # Об'єднання всіх параграфів документа в один рядок
            return "\n".join([p.text for p in doc.paragraphs])

        else:
            raise ValueError("Непідтримуваний формат файлу. Оберіть .txt або .docx")

    def load_file(self, num):
        """Обробник події натискання кнопки вибору файлу."""
        path = filedialog.askopenfilename(
            filetypes=[("Текстові файли", "*.txt *.docx")]
        )

        if path:
            try:
                content = self.read_document(path)

                # Збереження контенту у відповідну змінну
                if num == 1:
                    self.doc1 = content
                else:
                    self.doc2 = content

                logging.info(f"Успішно завантажено файл {num}: {path}")

            except ValueError as e:
                messagebox.showerror("Формат файлу", str(e))
            except Exception as e:
                logging.error(f"Помилка читання файлу: {e}")
                messagebox.showerror("Помилка", "Не вдалося прочитати обраний файл")

    def compare(self):
        """
        Основний алгоритм порівняння.
        Реалізує векторизацію TF-IDF та косинусну схожість.
        """
        # --- ВАЛІДАЦІЯ ДАНИХ (Обробка порожніх файлів) ---
        if not self.doc1.strip() or not self.doc2.strip():
            messagebox.showwarning("Увага", "Один із файлів порожній або не обраний!")
            logging.warning("Спроба порівняння порожніх документів")
            return

        try:
            # Створення моделі TF-IDF (Term Frequency - Inverse Document Frequency)
            vectorizer = TfidfVectorizer()

            # Перетворення текстів у числові матриці (векторизація)
            matrix = vectorizer.fit_transform([self.doc1, self.doc2])

            # Обчислення косинусної схожості між векторами
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]

            # Форматування результату у відсотки
            score = round(similarity * 100, 2)

            # Оновлення інтерфейсу та логування результату
            self.res_label.config(text=f"Схожість: {score}%")
            logging.info(f"Аналіз завершено успішно. Результат: {score}%")

            # Збереження останнього результату у файл звіту
            with open("last_result.txt", "w", encoding='utf-8') as f:
                f.write(f"Останній результат перевірки: {score}%")

        except Exception as e:
            logging.error(f"Критична помилка під час аналізу: {e}")
            messagebox.showerror("Помилка аналізу", "Не вдалося провести математичне порівняння")


# --- ТОЧКА ВХОДУ ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()
