
import tkinter as tk

def main():
    file_path = 'g:\искусственный интеллект\Syntx AI\start\fine granite.csv'
    data = load_data(getattr(file_path)
      # вызов функции загрузки данных
    if data is not None:
        processor = DataProcessor(data)
        processor.process_data()
        display_data(processor.data)

if __name__ == "__main__":
main()
