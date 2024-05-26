import streamlit as st
import pyodbc
from random import randrange, sample


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

        _self.conn = pyodbc.connect(_self.connection_string)
        _self.temp = None

    # Initialize connection.
    # Uses st.cache_resource to only run once.

    @st.cache_resource
    def init_connection(_self):
        return pyodbc.connect(_self.connection_string)


    # Perform query.
    # Uses st.cache_data to only rerun when the query changes or after 10 min.
    @st.cache_data(ttl=600)
    def run_query(_self, query):
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    @st.cache_data(ttl=600)
    def register_user(_self, username, pwd):
        with _self.conn.cursor() as cur:
            temp = _self.get_highest_ID('user')
            cur.execute("INSERT INTO riaoUsers (Username, UserPassword) VALUES (username, pwd)")
            if temp + 1 == self.get_highest_ID('user'):
                return 1
            else:
                return 0

    @st.cache_data(ttl=600)
    def get_highest_ID(_self, item):
        with _self.conn.cursor() as cur:
            if item.lower() == 'user':
                cur.execute("SELECT MAX(UserID) FROM riaoUsers")
                row = cur.fetchone()
                return row[0]
            elif item.lower() == 'question':
                cur.execute("SELECT MAX(QuestionID) FROM riaoQuestionsList")
                row = cur.fetchone()
                return row[0]

    @st.cache_data(ttl=600)
    def show_results(_self):
        with _self.conn.cursor() as cur:
            cur.execute("SELECT TOP 1 * FROM riaoAttempts ORDER BY ResultID ASC")
            cur.execute("SELECT * FROM riaoAttempts")
            return cur.fetchall()

    @st.cache_resource(ttl=1)
    def get_questions(_self, part):
        """Zwraca listę 5 tupli sformatowanych tak jak ostatnio trzeba było"""
        _max_value = _self.get_highest_ID('question')
        ids = sample(range(1, _max_value), 5)
        range_ = int(_self.get_highest_ID('question'))
        questions = []
        # for i in range(5):
        #     temp = ids[i]
        #     while temp in ids:
        #         ids[i] = randrange(range_-1)
        with _self.conn.cursor() as cur:
            for id_ in ids:
                cur.execute(f"SELECT * FROM riaoQuestionsList WHERE QuestionID = {id_}")
                questions.append(cur.fetchone())
        return questions

    @st.cache_data(ttl=600)
    def write_user(_self, username, pwd):
        with _self.conn.cursor() as cur:
            cur.execute("INSERT INTO riaoUsers (Username, UserPassword) VALUES (username, pwd)")

    @st.cache_data(ttl=600)
    def write_attempt(_self, questionIDs, questionsMarks):
        overall = questionsMarks[0] + questionsMarks[1] + questionsMarks[2] + questionsMarks[3] + questionsMarks[4]
        with _self.conn.cursor() as cur:
            cur.execute(f"INSERT INTO riaoAttempts (Question1, Question2, Question3, Question4, Question5,"
                        "Result1, Result2, Result3, Result4, Result5, OverallResult) "
                        "VALUES ({questionIDs[0]}, {questionIDs[1]}, {questionIDs[2]}, {questionIDs[3]}, "
                        "{questionIDs[4]}, {questionsMarks[0]}, {questionsMarks[1]}, {questionsMarks[2]},"
                        "{questionsMarks[3]}, {questionsMarks[4]}, {overall})")
    # _self.temp = run_query("SELECT * from riaoQuestionsList;")
