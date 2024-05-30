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
        self.db_manager.init_connection()

        st.title("Wyniki")
        st.subheader("Część 1 materiału")

        results_df = self.db_manager.show_results(1)

        if not results_df.empty:
            results_df = self.calculate_percentage(results_df)

            last_10_results = results_df.tail(10)

            if not last_10_results.empty:
                last_10_results.reset_index(drop=True, inplace=True)
                last_10_results.index += 1
                st.table(last_10_results[['UserID', 'Percentage']])
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

            last_10_results2 = results_df2.tail(10)

            if not last_10_results2.empty:
                last_10_results2.reset_index(drop=True, inplace=True)
                last_10_results2.index += 1
                st.table(last_10_results2[['UserID', 'Percentage']])
            else:
                st.write("Brak wyników do wyświetlenia.")

            self.display_session_results()
            self.print_histogram2()  # Moved this line here
        else:
            st.write("Brak wyników w bazie danych.")

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

    def print_histogram1(self):
        results_df = self.db_manager.show_results(1)
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

    def print_histogram2(self):
        results_df = self.db_manager.show_results(2)
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