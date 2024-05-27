import streamlit as st
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(parent_dir, 'DataManager.py'))
from DataManager import data_manager

class Results:
    def __init__(self):
        self.file_path = "scores.csv"
        self.score_float = None
        self.data_manager = data_manager()

        if 'scores' not in st.session_state:
            if os.path.exists(self.file_path):
                st.session_state.scores = self.load_scores()
            else:
                st.session_state.scores = []

    def load_scores(self):
        # scores = self.data_manager.show_results()
        scores_read = pd.read_csv(self.file_path)
        return scores_read

    def save_scores(self):
        scores_save = pd.DataFrame(st.session_state.scores, columns=["Wyniki"])
        scores_save.to_csv(self.file_path, index=False)

    def clear_scores(self):
        st.session_state.scores = []
        empty_scores = pd.DataFrame(columns=["Wyniki"])
        empty_scores.to_csv(self.file_path, index=False)

    def print(self):
        st.title("Wyniki")
        st.subheader("Część 1 materiału")

        # wprowadzanie i zatwierdzanie wyniku (kiedys czytanie z bazy)
        score = st.text_input("Podaj wynik (0-100):")
        if st.button("Dodaj wynik"):
            try:
                self.score_float = float(score)
                if  0 <= self.score_float <= 100:
                    st.session_state.scores.append(self.score_float)
                    st.session_state.scores = sorted(st.session_state.scores, reverse=True)[:10]

                    self.save_scores()

                else:
                    st.error("Wprowadź poprawny wynik od 0 do 100.")
            except ValueError:
                st.error("Wprowadź poprawny wynik.")

        # wyswietlanie 10 najlepszych wynikow w tabeli i na wykresie
        if st.session_state.scores:
            top_scores = sorted(st.session_state.scores, reverse=True)[:10]
            top_scores_df = pd.DataFrame(top_scores, columns=["Wynik [%]"])
            top_scores_df.index = top_scores_df.index + 1
            st.subheader("Najlepsze wyniki")
            st.table(top_scores_df)
        else:
            st.write("Tabela jest pusta.")

        self.plot_histogram(self.score_float)

        # czyszczenie tabeli, wykresu, csv
        if st.button("Wyczyść tabelę"):
            self.clear_scores()

        st.subheader("Część 2 materiału")

    def plot_histogram(self, highlight_score=None):
        sns.set(style="whitegrid")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.histplot(st.session_state.scores, bins=10, kde=True, ax=ax)
        plt.xlabel("Wynik")
        plt.ylabel("Liczba")
        plt.title("Wyniki")
        if highlight_score is not None:
            plt.axvline(highlight_score, color='r', linestyle='--', label=f'Nowy wynik: {highlight_score}')
            plt.legend()
        st.pyplot(fig)



results = Results()
results.print()
