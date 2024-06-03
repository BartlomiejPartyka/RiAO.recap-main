import os, sys
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(parent_dir, 'DataManager.py'))
from DataManager import data_manager


class Results:
    def __init__(self):
        """
        Initialize the Results class.
        Create an instance of the data manager to handle database operations.
        Create an empty Streamlit placeholder for results.
        """
        self.db_manager = data_manager()
        self.results_placeholder = st.empty()

    def print_summary(self):
        """
        This method print the summary of results for both parts of the material.
        Fetch results from the database, calculate percentages, and display the results.
        """
        self.db_manager.init_connection()

        st.title("Wyniki")
        st.subheader("Część 1 materiału")

        results_df = self.db_manager.show_results(1)

        if not results_df.empty:
            results_df = self.calculate_percentage(results_df)

            last_5_results = results_df.tail(5)

            st.write("Ostatnie pięć podejść:")
            if not last_5_results.empty:
                last_5_results.reset_index(drop=True, inplace=True)
                last_5_results.index += 1
                last_5_results.rename(columns={'Percentage': 'Wynik procentowy'}, inplace=True)
                st.table(last_5_results[['Wynik procentowy']])
            else:
                st.write("Brak wyników do wyświetlenia.")

            self.display_session_results()
            self.print_histogram1()
        else:
            st.write("Brak wyników w bazie danych.")

        st.title("Wyniki")
        st.subheader("Część 2 materiału")

        # Fetch latest results from the second database table
        results_df2 = self.db_manager.show_results(2)

        if not results_df2.empty:
            results_df2 = self.calculate_percentage(results_df2)

            last_5_results2 = results_df2.tail(5)

            st.write("Ostatnie pięć podejść:")
            if not last_5_results2.empty:
                last_5_results2.reset_index(drop=True, inplace=True)
                last_5_results2.index += 1
                last_5_results2.rename(columns={'Percentage': 'Wynik procentowy'}, inplace=True)
                st.table(last_5_results2[['Wynik procentowy']])
            else:
                st.write("Brak wyników do wyświetlenia.")
            self.display_session_results()
            self.print_histogram2()
        else:
            st.write("Brak wyników w bazie danych.")

    def display_session_results(self):
        """This method display the results from the current session stored in Streamlit's session state."""
        if 'results' in st.session_state and st.session_state['results']:
            st.subheader("Wyniki z bieżącej sesji")
            for i, result in enumerate(st.session_state['results']):
                percentage = (result['score'] / result['total']) * 100
                st.write(f"Wynik ostatniego podejścia: {result['score']} / {result['total']} ({percentage:.2f}%)")
        else:
            st.write("Brak wyników w bieżącej sesji.")

    def calculate_percentage(self, df):
        """This method calculate the percentage score for each result row."""
        df['Percentage'] = (df[['Result1', 'Result2', 'Result3', 'Result4', 'Result5']].sum(axis=1) / 5) * 100
        return df

    def get_top_scores(self, results_df, n=10):
        """This method get the top n scores from the results DataFrame."""
        if not results_df.empty:
            top_scores_df = results_df.sort_values(by='Percentage', ascending=False).head(n)
            top_scores_df.reset_index(drop=True, inplace=True)
            return top_scores_df[['UserID', 'Percentage']]
        else:
            return pd.DataFrame()

    def print_histogram1(self):
        """Print a histogram of the results from the first part of the material."""
        results_df = self.db_manager.show_results(1)
        if not results_df.empty:
            results_df = self.calculate_percentage(results_df)
            scores = results_df['Percentage'].tolist()
            last_score = scores[-1] if scores else None

            sns.set(style="whitegrid")
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(scores, bins=10, kde=True, ax=ax)

            if last_score is not None:
                ax.axvline(last_score, color='r', linestyle='--', linewidth=2, label=f'Ostatni wynik: {last_score:.2f}%')

            plt.xlabel("Wynik")
            plt.ylabel("Liczba podejść z danym wynikiem")
            plt.title("Wyniki ze wszystkich podejść")
            plt.legend()
            st.pyplot(fig)
        else:
            st.write("Brak wyników do wyświetlenia.")

    def print_histogram2(self):
        """Print a histogram of the results from the second part of the material."""
        results_df = self.db_manager.show_results(2)
        if not results_df.empty:
            results_df = self.calculate_percentage(results_df)
            scores = results_df['Percentage'].tolist()
            last_score = scores[-1] if scores else None

            sns.set(style="whitegrid")
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(scores, bins=10, kde=True, ax=ax)

            if last_score is not None:
                ax.axvline(last_score, color='r', linestyle='--', linewidth=2, label=f'Ostatni wynik: {last_score:.2f}%')

            plt.xlabel("Wynik")
            plt.ylabel("Liczba podejść z danym wynikiem")
            plt.title("Wyniki ze wszystkich podejść")
            plt.legend()
            st.pyplot(fig)
        else:
            st.write("Brak wyników do wyświetlenia.")

results = Results()
results.print_summary()
