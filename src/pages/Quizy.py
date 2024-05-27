import streamlit as st
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(parent_dir, 'DataManager.py'))
from DataManager import data_manager


class Quizy:
    def __init__(self):
        # if "btn" not in st.session_state:
        #     st.session_state.btn = False
        # self.next_round = st.button(label="Kolejna runda!",
        #                             disabled=st.session_state.btn,
        #                             on_click=self.new_questions)
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

    def new_questions(self):
        self.data_manager.get_questions.clear()
        st.rerun()
        self.print()

    def print(self):
        '''This method adds radio buttons allowing the selection of parts of the material.'''
        st.title("Quizy")
        st.subheader("Wybierz zakres materiału:")

        if "disabled" not in st.session_state:
            st.session_state.disabled = False

        pages_names = ['Część 1', 'Część 2']
        self.page = st.radio(
            label="Część 1. zawiera zakres materiału dr inż. Węsierskiej. Część 2. zawiera zakres dr inż. Polińskiego.",
            options=pages_names, index=None)

        if self.page == 'Część 1':
            self.get_questions(1)
        elif self.page == 'Część 2':
            self.get_questions(2)

    # @st.cache_resource
    def get_questions(self, part):
        '''This method takes a part of the material, get questions from the database and divide them by type'''

        # if self.get_new_questions:
        result = self.data_manager.get_questions(part)

        # st.write(result)

        self.answers = list(0 for x in range(int(len(result))))
        self.cont = []
        self.q_ids = []
        with st.form("my_form"):
            for index, r in enumerate(result):
                st.write(str(r[0]+1) + ". Pytanie:")
                self.q_ids.append(r[0])
                self.correct_answers.append(r[4])
                self.cont.append(st.container(border=True))
                if r[1] == "radio":
                    self.radio_add(r, self.cont[index])
                elif r[1] == "select":
                    self.select_add(r, self.cont[index])
                elif r[1] == "check":
                    self.check_add(r, self.cont[index])

            submitted = st.form_submit_button("Zatwierdź")
            if submitted:
                if not st.session_state.disabled:
                    self.show_results()
        st.button(label="Kolejna runda!", on_click=self.new_questions)


    def prettify(self, answers):
        """This method accepts a string of answers from databse format and returns a list on answer Strings"""
        return answers.split("//")

    def radio_add(self, q_tuple, c):
        '''This method add question with answers in case question type is radio'''
        options = list(x for x in range(int(q_tuple[3])))
        answers = self.prettify(q_tuple[5])
        for o in options:
            options[o] = str(answers[o])
        r_question = c.radio(
            str(q_tuple[2]),
            options, index=None, disabled=st.session_state.disabled, key=q_tuple[0]
        )

        for i in range(int(q_tuple[3])):
            if r_question == options[i]:
                self.answers[self.answerCounter] = 1+i
                self.answerCounter += 1

    def select_add(self, q_tuple, c):
        '''This method add question with answers in case question type is select'''
        options = list(x for x in range(int(q_tuple[3])))
        answers = self.prettify(q_tuple[5])
        for o in options:
            options[o] = str(answers[o])
        s_question = c.selectbox(
            str(q_tuple[2]),
            options, index=None, placeholder="Wybierz odpowiedź", disabled=st.session_state.disabled,
            key=q_tuple[0])
        #self.select_list.append(s_question)
        for i in range(int(q_tuple[3])):
            if s_question == options[i]:
                self.answers[int(self.answerCounter)] = 1+i
                self.answerCounter += 1

    def check_add(self, q_tuple, c):
        '''This method add question with answers in case question type is check'''
        c_answers = list(x for x in range(int(q_tuple[3])))
        answers = self.prettify(q_tuple[5])
        c.write(str(q_tuple[2]))
        options = list(x for x in range(int(q_tuple[3])))
        for o in options:
            options[o] = str(answers[o])
        for x in range(int(q_tuple[3])):
            key = int(f"{q_tuple[0]}{x}")
            check = c.checkbox(options[x], disabled=st.session_state.disabled, key=key)
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
        '''This method takes checkbox answers and returns number that symbolises answers'''
        number = 0
        for index, a in enumerate(ans):
            if a == "Checked":
                number = number*10
                number += index+1
        return number

    def show_results(self):
        '''This method write the score on window and mark the answers as correct or wrong'''
        # st.session_state.disabled = True
        # self.get_new_questions = False
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


quizy = Quizy()
quizy.print()
