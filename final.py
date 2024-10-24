import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from yahooquery import search
from sentence_transformers import SentenceTransformer, util
import pandas as pd

def descriptions_from_csv():
    csv_file_path = 'good_companies.csv'
    data = pd.read_csv(csv_file_path, encoding='utf-8')
    descriptions = data['description'].tolist()
    return descriptions

def names_from_csv():
    csv_file_path = 'good_companies.csv'
    data = pd.read_csv(csv_file_path, encoding='utf-8')
    names = data['name'].tolist()
    return names

class Search:
    def __init__(self, docs=[]):
        self.model = SentenceTransformer('distilbert-base-nli-mean-tokens')
        self.documents = docs
        self.document_embeddings = self.model.encode([doc for doc in self.documents])

    def add_document(self, document):
        self.documents.append(document)
        self.document_embeddings = self.model.encode([doc for doc in self.documents])

    def search(self, query):
        query_embedding = self.model.encode([query])
        cosine_scores = util.pytorch_cos_sim(query_embedding, self.document_embeddings).flatten()
        relevant_docs = sorted(enumerate(cosine_scores), key=lambda x: x[1], reverse=True)
        names = names_from_csv()
        relevant_names = []
        total_results = 5
        for j in range(total_results):
            most_relevant_index = relevant_docs[j][0]
            name = names[most_relevant_index]
            relevant_names.append(name)
        return relevant_names

class Scrape:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.bind('<Escape>', self.end)
        
        self.name_companies_labels = []
        self.information_labels = []

        self.heading = tk.Label(self.root, text="Welcome To Stock Searcher!", font=('Arial', 60))
        self.heading.pack(padx=10, pady=10)

        self.entry_1 = tk.Entry(self.root, fg='gray', width=50, font=('Arial', 30))
        self.entry_1.insert(0, 'Enter A Company...')
        self.entry_1.bind('<FocusIn>', self.on_entry_click_1)
        self.entry_1.bind('<FocusOut>', self.on_focusout_1)
        self.entry_1.bind('<Return>', self.hide_company)
        self.entry_1.pack(pady=200)

        self.entry_2 = tk.Entry(self.root, fg='gray', width=50, font=('Arial', 30))
        self.entry_2.insert(0, 'Enter A Keyword...')
        self.entry_2.bind('<FocusIn>', self.on_entry_click_2)
        self.entry_2.bind('<FocusOut>', self.on_focusout_2)
        self.entry_2.bind('<Return>', self.ai)
        self.entry_2.pack(pady=20)

        self.button_1 = tk.Button(self.root, text="Find", font=('Arial', 20), command=self.hide_company)
        self.button_1.place(x=1550, y=315, height=50, width=100)

        self.button_2 = tk.Button(self.root, text="Find", font=('Arial', 20), command=self.ai)
        self.button_2.place(x=1550, y=583, height=50, width=100)

        print("Loading Model...")
        documents = descriptions_from_csv()
        self.searcher = Search(documents)
        print("Model Loaded")
        self.root.mainloop()

    def get_ticker_from_name(self, company_name):
        self.search_results = search(company_name)
        if self.search_results and 'quotes' in self.search_results:
            self.first_result = self.search_results['quotes'][0]
            return self.first_result['symbol']

    def on_entry_click_1(self, event):
        if self.entry_1.get() == 'Enter A Company...':
            self.entry_1.delete(0, "end")
            self.entry_1.config(fg='black')

    def on_focusout_1(self, event):
        if self.entry_1.get() == '':
            self.entry_1.insert(0, 'Enter A Company...')
            self.entry_1.config(fg='gray')

    def on_entry_click_2(self, event):
        if self.entry_2.get() == 'Enter A Keyword...':
            self.entry_2.delete(0, "end")
            self.entry_2.config(fg='black')

    def on_focusout_2(self, event):
        if self.entry_2.get() == '':
            self.entry_2.insert(0, 'Enter A Keyword...')
            self.entry_2.config(fg='gray')

    def hide_company(self, event=None):
        if event is None or event.keysym == "Return":
            self.entry_1.pack_forget()
            self.entry_2.pack_forget()
            self.button_1.place_forget()
            self.button_2.place_forget()
            self.heading.pack_forget()
            self.insert_formatted_text(self.entry_1.get())
    
    def ai(self, event=None):
        self.entry_1.pack_forget()
        self.entry_2.pack_forget()
        self.button_1.place_forget()
        self.button_2.place_forget()
        self.heading.pack_forget()
        query = self.entry_2.get()
        result = self.searcher.search(query)
        
        if result:
            for element in result:
                button = tk.Button(
                    self.root,
                    text=element,
                    font=('Arial', 60),
                    command=lambda e=element: self.show_companies(e),
                    bg=self.root.cget("bg"),
                    borderwidth=0,
                    highlightthickness=0,
                    activebackground=self.root.cget("bg")
                )
                button.pack(padx=10, pady=10 * (len(self.name_companies_labels) + 1))
                self.name_companies_labels.append(button)

        else:
            messagebox.showinfo("Search Result", "No relevant company found.")
            
        self.back_keyword = tk.Button(self.root, text="Go Back", font=('Arial', 20), command=self.go_back_keyword)
        self.back_keyword.place(x=1600, y=600, height=70, width=120)

    def end(self, event=None):
        self.root.destroy()

    def show_companies(self, comp):
        print(len(self.name_companies_labels))
        for btn in self.name_companies_labels[:]:
            print("Removing Button")
            btn.pack_forget()
            self.name_companies_labels.remove(btn)
        self.go_back_keyword()
        self.entry_1.pack_forget()
        self.entry_2.pack_forget()
        self.button_1.place_forget()
        self.button_2.place_forget()
        self.heading.pack_forget()
        self.insert_formatted_text(self.get_ticker_from_name(comp))

    def convert_to_number(self, risk_value):
        risk_value_1 = risk_value.replace(",", "")
        if '.' in risk_value_1:
            return float(risk_value_1)
        else:
            return int(risk_value_1)

    def add_commas(self, num):
        reverse_num = list(str(num)[::-1])
        copy = list(str(num)[::-1])
        c = 0
        for i in range(len(reverse_num)):
            if i % 3 == 2 and i != len(reverse_num) - 1:
                c += 1
                copy.insert(i + c, ",")
        return ''.join(copy[::-1])

    def insert_formatted_text(self, ticker):
        self.ticker = self.get_ticker_from_name(ticker)

        self.url = f'https://stockanalysis.com/stocks/{self.ticker}/'
        self.url_market_cap = f'https://stockanalysis.com/stocks/{self.ticker}/market-cap/'
        self.url_revenue = f'https://stockanalysis.com/stocks/{self.ticker}/revenue/'
        self.url_risk = f'https://stockanalysis.com/stocks/{self.ticker}/financials/balance-sheet/'
        self.url_income_state = f'https://stockanalysis.com/stocks/{self.ticker}/financials/'

        self.response_comp = requests.get(self.url)
        self.response_market_cap = requests.get(self.url_market_cap)
        self.response_revenue = requests.get(self.url_revenue)
        self.response_risk = requests.get(self.url_risk)
        self.response_income = requests.get(self.url_income_state)

        self.soup = BeautifulSoup(self.response_comp.text, 'html.parser')
        self.soup_market_cap = BeautifulSoup(self.response_market_cap.text, 'html.parser')
        self.soup_revenue = BeautifulSoup(self.response_revenue.text, 'html.parser')
        self.soup_risk = BeautifulSoup(self.response_risk.text, 'html.parser')
        self.soup_income = BeautifulSoup(self.response_income.text, 'html.parser')

        risk_rows = self.soup_risk.find_all('tr')
        self.total_current_assets = None
        self.total_current_liabilities = None
        for risk_row in risk_rows:
            risk_cells = risk_row.find_all('td')
            if len(risk_cells) > 1:
                risk_label = risk_cells[0].get_text(strip=True)
                risk_value = risk_cells[1].get_text(strip=True)
                if risk_label != None and risk_value != None:
                    if 'Total Current Assets' in risk_label:
                        self.total_current_assets = risk_value
                    elif 'Total Current Liabilities' in risk_label:
                        self.total_current_liabilities = risk_value
                else:
                    self.total_current_assets = "-"
                    self.total_current_liabilities = "-"

        margin_rows = self.soup_income.find_all('tr')
        self.profit_margin = "Could Not Find Net Profit Margin"
        for margin_row in margin_rows:
            margin_cells = margin_row.find_all('td')
            if len(margin_cells) > 1:
                margin_label = margin_cells[0].get_text(strip=True)
                margin_value = margin_cells[1].get_text(strip=True)

                if 'Profit Margin' in margin_label:
                    self.profit_margin = margin_value

        eps_rows = self.soup_income.find_all('tr')
        self.eps = None
        for eps_row in eps_rows:
            eps_cells = eps_row.find_all('td')
            if len(eps_cells) > 1:
                eps_label = eps_cells[0].get_text(strip=True)
                eps_value = eps_cells[1].get_text(strip=True)

                if 'EPS (Basic)' in eps_label:
                    self.eps = eps_value

        self.name = self.soup.find(class_='mb-0 text-2xl font-bold text-default sm:text-[26px]')
        self.price = self.soup.find(class_='text-4xl font-bold block sm:inline')
        if not self.price:
            self.price = self.soup.find(class_='text-4xl font-bold inline-block')
        self.market_cap = self.soup_market_cap.find(class_='mt-0.5 text-lg font-semibold bp:text-xl sm:mt-1.5 sm:text-2xl')
        self.revenue = self.soup_revenue.find(class_='mt-0.5 text-lg font-semibold bp:text-xl sm:mt-1.5 sm:text-2xl')
        self.pe_ratio = self.convert_to_number(self.price.text) / self.convert_to_number(self.eps)
        if self.pe_ratio > 25:
            self.pe_value = "High"
        elif self.pe_ratio < 15:
            self.pe_value = "Low"
        else:
            self.pe_value = "Average"
            
        self.data = [f"Stock Price: ${self.price.text}", f"Market Capital: ${self.market_cap.text}", f"Revenue(TTM): {self.revenue.text}", f"Estimated Total Current Assets: ${self.add_commas(int(self.convert_to_number(self.total_current_assets) * 1000000))}", f"Estimated Total Current Liabilities: ${self.add_commas(int(self.convert_to_number(self.total_current_liabilities) * 1000000))}", f"Safe Level (Assets/Liabilities): {self.convert_to_number(self.total_current_assets) / self.convert_to_number(self.total_current_liabilities) - 1}", f"Net Profit Margin: {self.profit_margin}", f"Value (P/E Ratio): {self.pe_ratio} ({self.pe_value})"]

        self.name_header = tk.Label(self.root, text=self.name.text, font=('Arial', 60))
        self.name_header.pack(padx=10, pady=5)
        for info in self.data:
            information = tk.Label(self.root, text=info, font=('Arial', 40))
            information.place(x=100, y=100 * (len(self.information_labels) + 1))
            self.information_labels.append(information)

        self.back_company = tk.Button(self.root, text="Go Back", font=('Arial', 20), command=self.go_back_company)
        self.back_company.place(x=1600, y=600, height=70, width=120)

    def go_back_keyword(self):
        self.name_companies_labels.clear()
        self.entry_1.pack(pady=200)
        self.entry_2.pack(pady=20)
        self.button_1.place(x=1550, y=315, height=50, width=100)
        self.button_2.place(x=1550, y=583, height=50, width=100)
        self.heading.pack(padx=10, pady=10)
        self.back_keyword.place_forget()
        self.entry_1.delete(0, "end")
        self.entry_2.delete(0, "end")

    def go_back_company(self):
        for label in self.information_labels[:]:
            print("Removing Label")
            label.place_forget()
            self.information_labels.remove(label)        
        self.name_header.pack_forget()
        self.heading.pack(padx=10, pady=10)
        self.entry_1.pack(pady=200)
        self.entry_2.pack(pady=20)
        self.button_1.place(x=1550, y=315, height=50, width=100)
        self.button_2.place(x=1550, y=583, height=50, width=100)
        self.back_company.place_forget()
        self.entry_1.delete(0, "end")
        self.entry_2.delete(0, "end")

Scrape()
