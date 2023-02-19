import sqlite3 as sq
import tkinter as tk
from tkinter import messagebox
from sys import exit as CritExit
from PIL import Image
from hashlib import md5

text_not_icon = \
"""Нет иконки приложения Minote! Ты куда ее дел???
Ну мы так не работаем... Скачивай заново minote.ico!
И не трогай файл .db если не хочешь потерять свои заметки."""

text_lie = \
"""Думаешь самый умный нашелся?
Мне нужно оригинальное изображение! Бери где хочешь!
Ну или не пользуйся..."""

text_unique = \
"""Заметка с таким именем уже существует.
Редактировать?"""

hash_minote_ico = "9c939174c8fba4860a6ffa5945e073d6"

def create_note(name, text):
    # Подключаемся к базе данных
    if name:
        position = ListNotes.curselection()
        with sq.connect("minote.db") as con:
            cur = con.cursor()

            # Создаем запись блокнота в базе
            try:
                cur.execute("INSERT INTO note VALUES (\
                    NULL,\
                    :name,\
                    :text\
                )\
                ", {
                    'name': name,
                    'text': text
                    })

                ListNotes.insert(tk.END, name)
                NameNote.delete(0, tk.END)
                textNote.delete("1.0", tk.END)
            except sq.Error as error:
                if "UNIQUE" in str(error):
                    request = messagebox.askquestion("Редактировать заметку?", text_unique)
                    if request == 'yes':
                        cur.execute("UPDATE note SET \
                            entry = :text\
                        WHERE name_note = :name\
                        ", {
                            'name': name,
                            'text': text
                            })
                else:
                    print(error)
                    messagebox.showerror("Ошибка заметки",f"{error}")
    else:
        messagebox.showerror("Ошибка записи", "Введите заголовок заметки")

def delete_note(position, name):
    name = ListNotes.get(position[0])
    request = messagebox.askquestion("Удаление записи!", f"Удалить запись {name}?")
    if request == 'yes':
        # Подключаемся к базе данных
        try:
            # Удаляем в БД
            with sq.connect("minote.db") as con:
                cur = con.cursor()

                # Создаем запись блокнота в базе
                cur.execute(f"DELETE FROM note WHERE name_note = :name", {'name': name})
            
            NameNote.delete(0, tk.END)
            textNote.delete("1.0", tk.END)
            
        except sq.Error as error:
            messagebox.showerror("Ошибка удаления",f"{error}")
        else:
            # Удаляем элемент из списка в графике
            ListNotes.delete(position[0])

def show_note(event):
    name = ListNotes.get(ListNotes.curselection()[0])
    textNote.delete("1.0", tk.END)
    NameNote.delete(0, tk.END)
    try:
        # Подключаемся к БД
        with sq.connect("minote.db") as con:
            cur = con.cursor()

            # Забираем текст заметки из БД
            cur.execute(f"SELECT entry, note_id FROM note WHERE name_note = :name", {'name': name})
            note = cur.fetchall()
            textNote.insert("1.0", note[0][0])
            NameNote.insert(0, name)
    except sq.Error as error:
        messagebox.showerror("Ошибка заметки",f"{error}")

def hide_note(event):        
    NameNote.delete(0, tk.END)
    textNote.delete("1.0", tk.END)
    
        
# Начальное подключение и создание таблицы в БД если та не существует
with sq.connect("minote.db") as con:
    cur = con.cursor()

    # Создаем таблицу для блокнотов
    cur.execute("""CREATE TABLE IF NOT EXISTS note (
        note_id INTEGER PRIMARY KEY,
        name_note TEXT NOT NULL UNIQUE,
        entry TEXT
        )""")

    # Получаем список блокнотов
    cur.execute("""SELECT name_note FROM note""")
    notes = []
    for row in cur:
        notes.append(row[0])

# Делаем графику

# Создаем главное окно программы
base = tk.Tk()
base.title("Minote")
try:
    with Image.open('minote.ico') as ico_file:
        ico_file_b = ico_file.tobytes()
        hash_object = md5(ico_file_b).hexdigest()
    
    if hash_object != hash_minote_ico:
        messagebox.showwarning("Предупреждение", text_lie)
        CritExit()
    base.iconbitmap("minote.ico")
except:
    messagebox.showwarning("Предупреждение", text_not_icon)
    CritExit()
base.geometry("550x250")
base.minsize(width=550, height=250)
base.columnconfigure(index=0, weight=1)
base.columnconfigure(index=1, weight=1)
base.columnconfigure(index=2, weight=4)
base.rowconfigure(index=0, weight=1)
base.rowconfigure(index=1, weight=1)
base.rowconfigure(index=2, weight=3)

base.bind("<Escape>", hide_note)

# Делаем поля в главном окне
NameNote = tk.Entry()
NameNote.grid(row=0, column=0, padx=6, pady=6,sticky=tk.EW)
CreateNote = tk.Button(text="Создать запись", command= lambda: create_note(NameNote.get(), textNote.get("1.0",tk.END)))
CreateNote.grid(row=0, column=1, padx=20, pady=5)
DeleteNote = tk.Button(text="Удалить запись", command= lambda: delete_note(ListNotes.curselection(), NameNote.get()))
DeleteNote.grid(row=1, column=1, padx=20, pady=5)

blocknotes_var = tk.StringVar(value=notes)
ListNotes = tk.Listbox(listvariable=blocknotes_var)
ListNotes.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
ListNotes.bind("<Double-1>", show_note)

textNote = tk.Text(base, width=30, bg = "light yellow", wrap="word")
textNote.grid(row=0, column=2, rowspan=3, sticky=tk.EW, padx=5, pady=5)

base.mainloop()