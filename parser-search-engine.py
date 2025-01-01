import os
import pickle
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()  # If file doesn't exist

def load_settings():
    settings_file = os.path.join(get_script_dir(), 'settings.pkl')
    if os.path.exists(settings_file):
        with open(settings_file, 'rb') as f:
            return pickle.load(f)
    else:
        return {
            'user_agent': '',
            'language': 'en',
            'country': 'us',
            'query': ''
        }

def save_settings(settings):
    settings_file = os.path.join(get_script_dir(), 'settings.pkl')
    with open(settings_file, 'wb') as f:
        pickle.dump(settings, f)

def search_google(settings):
    headers = {'User-Agent': settings['user_agent']}
    query = settings['query']
    url = f"https://www.google.com/search?q={query}&hl={settings['language']}&gl={settings['country']}"
    response = requests.get(url, headers=headers)
    results = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('div', class_='tF2Cxc')
        for result in search_results:
            title = result.find('h3')
            link = result.find('a', href=True)
            snippet = result.find('span', class_='aCOpRe')
            entry = {
                'Title': title.text if title else 'No title found',
                'Link': link['href'] if link else 'No link found',
                'Snippet': snippet.text if snippet else 'No snippet found'
            }
            results.append(entry)
    df = pd.DataFrame(results)
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialdir=get_script_dir())
    if file_path:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Information", "Results have been saved successfully.")

def create_gui(settings):
    window = tk.Tk()
    window.title("Search Engine Parser Settings")

    tk.Label(window, text="User Agent:").grid(row=0, column=0)
    user_agent_entry = tk.Entry(window, width=50)
    user_agent_entry.insert(0, settings['user_agent'])
    user_agent_entry.grid(row=0, column=1)

    link_label = tk.Label(window, text="Find your user agent at https://www.whatsmyua.info", fg="white", cursor="hand2")
    link_label.grid(row=1, column=1)
    link_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.whatsmyua.info"))

    tk.Label(window, text="Language (hl):").grid(row=2, column=0)
    language_entry = tk.Entry(window)
    language_entry.insert(0, settings['language'])
    language_entry.grid(row=2, column=1)

    tk.Label(window, text="Country (gl):").grid(row=3, column=0)
    country_entry = tk.Entry(window)
    country_entry.insert(0, settings['country'])
    country_entry.grid(row=3, column=1)

    tk.Label(window, text="Query:").grid(row=4, column=0)
    query_entry = tk.Entry(window, width=50)
    query_entry.insert(0, settings['query'])
    query_entry.grid(row=4, column=1)

    def on_save():
        settings['user_agent'] = user_agent_entry.get()
        settings['language'] = language_entry.get()
        settings['country'] = country_entry.get()
        settings['query'] = query_entry.get()
        save_settings(settings)
        search_google(settings)

    tk.Button(window, text="Save Settings and Run Search", command=on_save).grid(row=5, columnspan=2)

    window.mainloop()

if __name__ == "__main__":
    settings = load_settings()
    create_gui(settings)
