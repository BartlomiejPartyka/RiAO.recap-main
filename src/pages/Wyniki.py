import os
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from src.DataManager import data_manager

class Results:
    def __init__(self):
        self.db_manager = data_manager()
        self.results_placeholder = st.empty()

    def print_summary(self):
        st.title("Wyniki")
        st.subheader("Część 1 materiału")

        results_df = self.db_manager.show_results()
        if not results_df.empty:
            results_df = self.calculate_percentage(results_df)

            # Display top 10 scores
            top_scores_df = self.get_top_scores(results_df, n=10)

            if not top_scores_df.empty:
                st.table(top_scores_df[['UserID', 'Percentage']])
            else:
                st.write("Brak najlepszych wyników do wyświetlenia.")

            if st.button("Wyczyść wyniki"):
                # self.clear_overall_results()
                st.success("Wyniki zostały wyczyszczone.")
        else:
            st.write("Brak wyników w bazie danych.")

        self.display_session_results()
    def display_session_results(self):
        if 'results' in st.session_state and st.session_state['results']:
            st.subheader("Wyniki z bieżącej sesji")
            for i, result in enumerate(st.session_state['results']):
                percentage = (result['score'] / result['total']) * 100
                st.write(f"Wynik ostatniego podejścia: {result['score']} / {result['total']} ({percentage:.2f}%)")
        else:
            st.write("Brak wyników w bieżącej sesji.")

    def calculate_percentage(self, df):
        df['Percentage'] = (df[['Result1', 'Result2', 'Result3', 'Result4', 'Result5']].sum(axis=1) / 5) * 100
        return df

    def get_top_scores(self, results_df, n=10):
        if not results_df.empty:
            top_scores_df = results_df.sort_values(by='Percentage', ascending=False).head(n)
            top_scores_df.reset_index(drop=True, inplace=True)
            return top_scores_df[['UserID', 'Percentage']]
        else:
            return pd.DataFrame()

    def print_histogram(self):
        results_df = self.db_manager.show_results()
        if not results_df.empty:
            results_df = self.calculate_percentage(results_df)
            scores = results_df['Percentage'].tolist()
            sns.set(style="whitegrid")
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(scores, bins=10, kde=True, ax=ax)
            plt.xlabel("Wynik")
            plt.ylabel("Liczba")
            plt.title("Wyniki z wszystkich podejść")
            st.pyplot(fig)
        else:
            st.write("Brak wyników do wyświetlenia.")

    # def clear_overall_results(self):
    #     # Perform database operation to clear overall_result data
    #     with self.db_manager.conn.cursor() as cur:
    #         cur.execute("DELETE FROM riaoAttempts")
    #         self.db_manager.conn.commit()

results = Results()
results.print_summary()
results.print_histogram()