import streamlit as st
import pyodbc
from random import randrange, sample
import pandas as pd


class data_manager:

    def __init__(_self):
        _self.connection_string = """
        Driver={ODBC Driver 17 for SQL Server};
        Server=""" + st.secrets["db_server"] + """;
        Database=RiAO.recap;
        Uid=""" + st.secrets["db_uid"] + """;
        Pwd=""" + st.secrets["db_pwd"] + """;
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
        """
        _self.questions = []
        _self.conn = pyodbc.connect(_self.connection_string)
        _self.temp = None
        _self.IDS = []

    @st.cache_resource
    def init_connection(_self):
        """Connects to the database"""
        return pyodbc.connect(_self.connection_string)

    @st.cache_data(ttl=600)
    def run_query(_self, query):
        """Executes SQL Server query passed as a parameter"""
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    @st.cache_data(ttl=600)
    def register_user(_self, username, pwd):
        """Saves user's ID, login and password into the database"""
        with _self.conn.cursor() as cur:
            temp = _self.get_highest_ID('user')
            cur.execute("INSERT INTO riaoUsers (Username, UserPassword) VALUES (username, pwd)")
            if temp + 1 == self.get_highest_ID('user'):
                return 1
            else:
                return 0

    @st.cache_data(ttl=600)
    def get_highest_ID(_self, item, **kwargs):
        """Returns highest user or question ID"""
        with _self.conn.cursor() as cur:
            if item.lower() == 'user':
                cur.execute("SELECT MAX(UserID) FROM riaoUsers")
                row = cur.fetchone()
                return row[0]
            elif item.lower() == 'question':
                cur.execute(f"SELECT MAX(QuestionID) FROM riaoQuestionsList{kwargs['part']}")
                row = cur.fetchone()
                return row[0]

    @st.cache_data(ttl=0)
    def show_results(_self, part):
        """Returns a dataframe with results"""
        with _self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM riaoAttempts{part}")
            columns = [column[0] for column in cur.description]
            data = cur.fetchall()
            df = pd.DataFrame.from_records(data, columns=columns)
            print(df)
            return df

    @st.cache_data(ttl=600)
    def show_overall(_self, part):
        """Returns the best score in either part"""
        with _self.conn.cursor() as cur:
            cur.execute(f"SELECT TOP 1 * FROM riaoAttempts{part} ORDER BY ResultID ASC")
            return cur.fetchall()

    @st.cache_resource(ttl=60)
    def get_questions(_self, part):
        """Returns 5 question tuples in a format compatible with Quizy methods"""
        _max_value = _self.get_highest_ID('question', part=part)
        ids = sample(range(1, _max_value), 5)
        _self.IDS = ids
        with _self.conn.cursor() as cur:
            for id_ in ids:
                cur.execute(f"SELECT * FROM riaoQuestionsList{part} WHERE QuestionID = {id_}")
                _self.questions.append(cur.fetchone())
        return _self.questions

    @st.cache_data(ttl=2)
    def write_attempt(_self, q_ids, questionsMarks, part):
        """Saves user's attempt into the database"""
        overall = questionsMarks[0] + questionsMarks[1] + questionsMarks[2] + questionsMarks[3] + questionsMarks[4]
        with _self.conn.cursor() as cur:
            cur.execute(f"INSERT INTO riaoAttempts{part} (Question1, Question2, Question3, Question4, Question5, "
                        f"Result1, Result2, Result3, Result4, Result5, OverallResult, UserID)"
                        f"VALUES ({q_ids[0]}, {q_ids[1]}, {q_ids[2]}, {q_ids[3]}, {q_ids[4]}, {questionsMarks[0]}, "
                        f"{questionsMarks[1]}, {questionsMarks[2]}, {questionsMarks[3]}, {questionsMarks[4]}, {overall},"
                        f" 1)")
        # _self.temp = run_query("SELECT * from riaoQuestionsList;")
