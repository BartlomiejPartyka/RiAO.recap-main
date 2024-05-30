import streamlit as st
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(parent_dir, 'DataManager.py'))
from src.DataManager import data_manager


class Quizy:
    def __init__(self):
        self.page = None
        self.correct_answers = []
        self.answers = None
        self.answerCounter = 0
        self.cont = None
        self.radio_list = []
        self.check_list = []
        self.select_list = []
        self.data_manager = data_manager()
        self.q_ids = []

        if 'results' not in st.session_state:
            st.session_state['results'] = []

        if 'latest_result_index' not in st.session_state:
            st.session_state['latest_result_index'] = None

    def new_questions(self):
        self.correct_answers = []
        self.answers = None
        self.answerCounter = 0
        self.cont = None
        self.radio_list = []
        self.check_list = []
        self.select_list = []
        self.q_ids = []
        self.data_manager.get_questions.clear()

    def print_quiz(self):
        """This method adds radio buttons allowing the selection of parts of the material."""
        st.title("Quizy")
        st.subheader("Wybierz zakres materiału:")

        if "disabled" not in st.session_state:
            st.session_state.disabled = False
        if "submitted" not in st.session_state:
            st.session_state.submitted = False

        pages_names = ['Część 1', 'Część 2']
        self.page = st.radio(
            label="Część 1. zawiera zakres materiału dr inż. Węsierskiej. Część 2. zawiera zakres dr inż. Polińskiego.",
            options=pages_names, index=None)

        if self.page == 'Część 1':
            self.get_questions(1)
        elif self.page == 'Część 2':
            self.get_questions(2)

    def get_questions(self, part):
        """This method takes a part of the material, gets questions from the database and divides them by type"""

        # if self.get_new_questions:
        result = self.data_manager.get_questions(part)

        self.answers = list(0 for x in range(int(len(result))))
        self.cont = []
        self.q_ids = []
        counter = 0
        with st.form("my_form"):
            for index, r in enumerate(result):
                counter += 1
                st.write(str(counter) + ". Pytanie:")
                self.q_ids.append(r[0])
                self.correct_answers.append(r[4])
                self.cont.append(st.container(border=True))
                if r[1] == "radio":
                    self.radio_add(r, self.cont[index])
                elif r[1] == "select":
                    self.select_add(r, self.cont[index])
                elif r[1] == "check":
                    self.check_add(r, self.cont[index])

            submitted = st.form_submit_button("Zatwierdź", disabled=st.session_state.disabled)
            if submitted:
                st.session_state.disabled = True
                st.session_state.submitted = True
                st.experimental_rerun()
                self.show_results()
            if st.session_state.submitted:
                self.show_results()
        if st.button("Kolejna runda!"):
            self.new_questions()
            st.session_state.clear()
            st.rerun()

    def prettify(self, answers):
        """This method accepts a string of answers from database format and returns a list on answer Strings"""
        return answers.split("//")

    def radio_add(self, q_tuple, c):
        """This method add question with answers in case question type is radio"""
        options = list(x for x in range(int(q_tuple[3])))
        answers = self.prettify(q_tuple[5])
        for o in options:
            options[o] = str(answers[o])
        r_question = c.radio(
            str(q_tuple[2]),
            options, index=None, key=q_tuple[0]
        )

        for i in range(int(q_tuple[3])):
            if r_question == options[i]:
                self.answers[self.answerCounter] = 1 + i
                self.answerCounter += 1

    def select_add(self, q_tuple, c):
        """This method add question with answers in case question type is select"""
        options = list(x for x in range(int(q_tuple[3])))
        answers = self.prettify(q_tuple[5])
        for o in options:
            options[o] = str(answers[o])
        s_question = c.selectbox(
            str(q_tuple[2]),
            options, index=None, placeholder="Wybierz odpowiedź",
            key=q_tuple[0])
        # self.select_list.append(s_question)
        for i in range(int(q_tuple[3])):
            if s_question == options[i]:
                self.answers[int(self.answerCounter)] = 1 + i
                self.answerCounter += 1

    def check_add(self, q_tuple, c):
        """This method add question with answers in case question type is check"""
        c_answers = list(x for x in range(int(q_tuple[3])))
        answers = self.prettify(q_tuple[5])
        c.write(str(q_tuple[2]))
        options = list(x for x in range(int(q_tuple[3])))
        for o in options:
            options[o] = str(answers[o])
        for x in range(int(q_tuple[3])):
            key = int(f"{q_tuple[0]}{x}")
            check = c.checkbox(options[x], key=key)
            if check:
                c_answers[x] = "Checked"
            else:
                c_answers[x] = "N"

        compressed_answers = self.compress_check(c_answers)
        if compressed_answers > 0:
            self.answers[self.answerCounter] = int(compressed_answers)
            self.answerCounter += 1
        else:
            self.answers[self.answerCounter] = 0
            self.answerCounter += 1

    def compress_check(self, ans):
        """This method takes checkbox answers and returns number that symbolises answers"""
        number = 0
        for index, a in enumerate(ans):
            if a == "Checked":
                number = number * 10
                number += index + 1
        return number

    def show_results(self):
        """This method write the score on window and mark the answers as correct or wrong"""
        st.write(" ")
        st.subheader("Wynik:")
        score = 0
        marks = []
        for index, r in enumerate(self.cont):
            with self.cont[index]:
                if self.answers[index] == self.correct_answers[index]:
                    st.success('Poprawna odpowiedź!', icon="✅")
                    score += 1
                    marks.append(1)
                else:
                    st.error('Błędna lub tylko częściowo poprawna odpowiedź', icon="🚨")
                    marks.append(0)
        st.write(str(score) + "/" + str(len(self.cont)))
        if score == len(self.cont):
            st.balloons()
        self.data_manager.write_attempt(self.q_ids, marks)

        st.session_state['results'].append({
            'score': score,
            'total': len(self.cont),
            'correct_answers': self.correct_answers,
            'answers': self.answers,
        })

        st.session_state['latest_result_index'] = len(st.session_state['results']) - 1


quizy = Quizy()
quizy.print_quiz()
