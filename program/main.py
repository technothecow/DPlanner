import random
import sys
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import *
import datetime
import mysql.connector

LOGIN_DPLANNER_LOGO_FONT = "75 40pt \"Uroob\""
USING_ACCOUNT_LABEL_FONT = "75 14pt \"Uroob\""
BUTTON_FONT = "75 22pt \"Uroob\""

MODE_BUTTONS_FONT = "20pt \"Laksaman\""
MODE_BUTTONS_FONT_HOVER = "22pt \"Laksaman\""
DPLANNER_LOGO_FONT = "0 40pt \"Manjari Thin\""
SELECTED_MODE_LABEL_FONT = "40pt \"Laksaman\""

GENERAL_TODAY_LABEL_FONT = "30pt \"Laksaman\""

ADDTASK_DATETIMEEDIT_FONT = "18pt \"Samyak Malayalam\""
ADDTASK_LABELS_FONT = "18pt \"Noto Sans Mono CJK JP\""
ADDTASK_LINEEDIT_FONT = "18pt \"Manjari\""
ADDTASK_BUTTON_CONTINUE_FONT = "24pt \"Laksaman\""
ADDTASK_BUTTON_CONTINUE_FONT_HOVER = "26pt \"Laksaman\""

EDITTASK_SELECT_DATE_LABEL_FONT = "20pt \"Laksaman\""
EDITTASK_DATETIMEEDIT_FONT = "18pt \"Samyak Malayalam\""
EDITTASK_DATEEDIT_FONT = "18pt \"Samyak Malayalam\";"
EDITTASK_TASKNAME_INPUT = "18pt \"Manjari\""
EDITTASK_BUTTON_CONTINUE_FONT = "24pt \"Laksaman\""
EDITTASK_BUTTON_CONTINUE_FONT_HOVER = "26pt \"Laksaman\""
EDITTASK_LOAD_TASKS_BUTTON_FONT = "18pt \"Laksaman\""
EDITTASK_LOAD_TASKS_BUTTON_FONT_HOVER = "20pt \"Laksaman\""
EDITTASK_DELETE_BUTTON_FONT = "24pt \"Laksaman\""
EDITTASK_DELETE_BUTTON_FONT_HOVER = "26pt \"Laksaman\""

ACCOUNTSETTINGS_LOGGEDAS_LABEL_FONT = "18pt \"Noto Sans Mono CJK JP\""
ACCOUNTSETTINGS_CHANGEPASSWORD_LABEL_FONT = "18pt \"Noto Sans Mono CJK JP\""
ACCOUNTSETTINGS_PASSWORD_INPUT_FONT = "18pt \"Manjari\""
ACCOUNTSETTINGS_CONTINUE_BUTTON_FONT = "24pt \"Laksaman\""
ACCOUNTSETTINGS_CONTINUE_BUTTON_FONT_HOVER = "26pt \"Laksaman\""


class RegistrationError(Exception):
    pass


class Database:
    def __init__(self, host, user, passwd, database, main_table_name="Users", standard_dictionary=None):
        if standard_dictionary is None:
            standard_dictionary = DEFAULT_DICTIONARY
        self.database = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=database
        )
        self.cursor = self.database.cursor()
        self.tablename = main_table_name
        self.dictionary = standard_dictionary

    def initialize_users(self):
        if not self.is_users_initialized():
            self.cursor.execute(
                f"CREATE TABLE {self.tablename} (id int PRIMARY KEY NOT NULL AUTO_INCREMENT, username varchar(20),"
                f" password varchar(20), email varchar(50), time datetime)")
            self.database.commit()

    def is_users_initialized(self):
        self.cursor.execute(f"SHOW TABLES LIKE '{self.tablename}'")
        for i in self.cursor:
            return True
        return False

    def delete_users(self):
        if self.is_users_initialized():
            self.cursor.execute("DROP TABLE Users")
            self.database.commit()

    def get_table_name(self, username):
        return "".join([self.dictionary[i] for i in str(self.get_id(username))])

    def register_user(self, username, password, email):
        if not self.is_users_initialized():
            self.initialize_users()
        if self.get_id(username):
            raise RegistrationError("Username is already taken!")
        self.cursor.execute(
            "INSERT INTO Users (username, password, email, time) VALUES (%s,%s,%s,%s)",
            (username, password, email, datetime.datetime.now())
        )
        table_name = self.get_table_name(username)
        self.cursor.execute(
            f"CREATE TABLE {table_name} (id int PRIMARY KEY NOT NULL AUTO_INCREMENT, title varchar(70), "
            f"description varchar(700), date varchar(40))"
        )
        self.database.commit()

    def get_id(self, name):
        self.cursor.execute(f"SELECT id FROM Users WHERE username = '{name}'")
        for i in self.cursor:
            return int(i[0])
        return False

    def is_username_taken(self, name):
        return bool(self.get_id(name))

    def add_task(self, tablename, title, description, date):
        self.cursor.execute(f"INSERT INTO {tablename} (title, description, date) VALUES (%s,%s,%s)",
                            (title, description, date))
        self.database.commit()

    def view_tasks(self, tablename):
        output = list()
        self.cursor.execute(f"SELECT id, title, description, date FROM {tablename}")
        return [i for i in self.cursor]

    def change_password(self, id, old_password, new_password):
        self.cursor.execute(f"SELECT password FROM {self.tablename} WHERE id = {id}")
        password = [i for i in self.cursor][0][0]
        if old_password == password:
            self.cursor.execute(f"UPDATE {self.tablename} SET password = '{new_password}' WHERE id = {id}")
            self.database.commit()
        else:
            return False

    def edit_task(self, tablename, id, title, description, date):
        self.cursor.execute(f"UPDATE {tablename} SET title = %s, description = %s, date = %s WHERE id = {id}",
                            (title, description, date))
        self.database.commit()

    def delete_task(self, tablename, id):
        self.cursor.execute(f"DELETE FROM {tablename} WHERE id = %s", (id,))
        self.database.commit()

    def login(self, username, password):
        self.cursor.execute(f"SELECT id FROM Users WHERE username = '{username}' AND password = '{password}'")
        for i in self.cursor:
            return int(i[0])
        return False



KEYBOARD_RU = "ёйцукенгшщзхъфывапролджэячсмитьбю"
KEYBOARD_EN = "qwertyuiopasdfghjklzxcvbnm"
KEYBOARD = KEYBOARD_RU + KEYBOARD_EN


def check_letter_error(password):
    flag1, flag2 = False, False
    for letter in password:
        if letter in KEYBOARD:
            flag1 = True
        elif letter in KEYBOARD.upper():
            flag2 = True
    return flag1 and flag2


def check_digit_error(password):
    for letter in password:
        if letter.isdigit():
            return True
    return False


def check_password(password):
    if len(password) < 9:
        return "Password must contain at least 9 symbols"
    if not check_letter_error(password):
        return "Password must contain lower-case and upper-case letters from either russian or english alphabet"
    if not check_digit_error(password):
        return "Password must contain at least one digit!"
    return True


def check_username(username):
    if username == "":
        return "Username cant be empty"
    if len(username) > 20:
        return "Username is way too long! 20 symbols is the limit!"
    for i in username:
        if i not in KEYBOARD + "1234567890" + KEYBOARD.upper():
            return "You may use only letters from both Russian and English alphabet and numbers in your nickname!"
    return True


def check_email(email):
    if "@" not in email or email.count("@") > 1:
        return "Email is incorrect"
    mail, service = email.split("@")
    if "." not in service or ".." in service:
        return "Email is incorrect"
    for i in mail:
        if i not in KEYBOARD + "1234567890" + KEYBOARD.upper():
            return "Email is incorrect"
    return True


GENERAL, ADDTASK, EDITTASK, ACCOUNTSETTINGS = 1, 2, 3, 4

DEFAULT_DICTIONARY = {'0': 'o', '1': 'n', '2': 't', '3': 'h', '4': 'f', '5': 'i', '6': 's', '7': 'e', '8': 'i',
                      '9': 'j'}

# DATABASE = Database(host, user, password, database)

def to_formated_date(date):
    d, t = date.split(" ")
    d = d.split(".")
    d.reverse()
    d = "-".join(d)
    t = t.replace(":", "-")
    return "-".join([d, t])


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(640, 430)
        MainWindow.setStyleSheet("#MainWindow {\n"
                                 "    color: rgb(139, 139, 139);\n"
                                 "}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(-60, -40, 801, 591))
        self.frame.setStyleSheet(u"#frame {\n"
                                 "   background-color: rgb(136, 136, 136);\n"
                                 "        }\n"
                                 "\n"
                                 "#button_general {\n"
                                 f"  font: {MODE_BUTTONS_FONT};\n"
                                 "   background-color:transparent;\n"
                                 "   color:white;\n"
                                 "   border-radius: 0px;\n"
                                 "   border-bottom: 1px solid black;\n"
                                 "   border-right: 1px solid black;\n"
                                 "   border-top: 1px solid black;\n"
                                 "        }\n"
                                 "\n"
                                 "        #button_addtask {\n"
                                 f"  font: {MODE_BUTTONS_FONT};\n"
                                 "   background-color:transparent;\n"
                                 "   color:white;\n"
                                 "   border-radius: 0px;\n"
                                 "   border-bottom: 1px solid black;\n"
                                 "   border-right: 1px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#button_edittask {\n"
                                 f" font: {MODE_BUTTONS_FONT};\n"
                                 "	background-color:transparent;\n"
                                 "	color:white;\n"
                                 "	border-radius: 0px;\n"
                                 "	border-bottom: 1px solid black;\n"
                                 "	border-right: 1px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#button_accountsettings {\n"
                                 f" font: {MODE_BUTTONS_FONT};\n"
                                 "	background-color:transparent;\n"
                                 "	color:white;\n"
                                 "	border-radius: "
                                 "0px;\n"
                                 "	border-right: 1px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#label_DPlanner {\n"
                                 f"	font: {DPLANNER_LOGO_FONT};\n"
                                 "	border: 1px solid black;\n"
                                 "	border-left: 0px solid black;\n"
                                 "	border-top: 0px solid black;\n"
                                 "	color: white;\n"
                                 "}\n"
                                 "\n"
                                 "#button_general:hover {\n"
                                 f"	font: {MODE_BUTTONS_FONT_HOVER};\n"
                                 "	color:white;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#button_addtask:hover {\n"
                                 f"	font: {MODE_BUTTONS_FONT_HOVER};\n"
                                 "	color:white;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#button_edittask:hover {\n"
                                 f"	font: {MODE_BUTTONS_FONT_HOVER};\n"
                                 "	color:white;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#button_accountsettings:hover {\n"
                                 f"	font: {MODE_BUTTONS_FONT_HOVER};\n"
                                 "	color:white;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "#label_selected_mode {\n"
                                 "	border: 1px solid black;\n"
                                 "	border-left: 0px solid black;\n"
                                 "	border-top: 0px solid black;\n"
                                 "	border-right: 0px solid black;\n"
                                 f"	font: {SELECTED_MODE_LABEL_FONT};\n"
                                 "	color:white;\n"
                                 "}\n"
                                 "#addtask_plainTextEdit {\n"
                                 "	color: white;\n"
                                 "	background: transparent;\n"
                                 "	border: 1px solid black;\n"
                                 "}\n"
                                 "#addtask_listWidget {\n"
                                 "	background: transparent;\n"
                                 "	border: 1px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#addtask_plainTextEdit:hover {\n"
                                 "	background: transparent;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#addtask_listWidget:hover {\n"
                                 "	background: transparent;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "\n"
                                 "#addtask_dateTimeEdit {\n"
                                 f"	font: {ADDTASK_DATETIMEEDIT_FONT};\n"
                                 "	color: white;\n"
                                 "	border-radius: 1px;\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid gray;\n"
                                 "}\n"
                                 "#addtask_dateTimeEdit:focus {\n"
                                 f"	font: {ADDTASK_DATETIMEEDIT_FONT};\n"
                                 "	color: white;\n"
                                 "	border-radius: 1px;\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid white;\n"
                                 "}\n"
                                 "#addtask_label_1 {\n"
                                 "	color: white;\n"
                                 f"	font: {ADDTASK_LABELS_FONT};\n"
                                 "}\n"
                                 "#addtask_label_2 {\n"
                                 "	color: white;\n"
                                 f"	font: {ADDTASK_LABELS_FONT};\n"
                                 "}\n"
                                 "#addtask_label_3 {\n"
                                 "	color: white;\n"
                                 f"	font: {ADDTASK_LABELS_FONT};\n"
                                 "}\n"
                                 "#addtask_lineEdit {\n"
                                 "	color: white;\n"
                                 "	background: transparent;\n"
                                 f"	font: {ADDTASK_LINEEDIT_FONT};\n"
                                 "	border: none;\n"
                                 "	border-bottom: 1px solid gray;\n"
                                 "}\n"
                                 "#addtask_lineEdit:focus {\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid white;\n"
                                 "}\n"
                                 "#addtask_button_continue {\n"
                                 "	background: transparent;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 f"	font: {ADDTASK_BUTTON_CONTINUE_FONT};\n"
                                 "}\n"
                                 "#addtask_button_continue:hover {\n"
                                 "	border: 2px solid black;\n"
                                 f"	font: {ADDTASK_BUTTON_CONTINUE_FONT_HOVER};\n"
                                 "}\n"
                                 "#general_label_today {\n"
                                 "	color:white;\n"
                                 f"	font: {GENERAL_TODAY_LABEL_FONT};\n"
                                 "}\n"
                                 "#general_plainTextEdit {\n"
                                 "	background: transparent;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 "}\n"
                                 "#general_listWidget {\n"
                                 "	background: transparent;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 "}\n"
                                 "#general_plainTextEdit:hover {\n"
                                 "	background: transparent"
                                 ";\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "#general_listWidget:hover {\n"
                                 "	background: transparent;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "#edittask_label_select_date {\n"
                                 "	color:white;\n"
                                 f"	font: {EDITTASK_SELECT_DATE_LABEL_FONT};\n"
                                 "}\n"
                                 "#edittask_plainTextEdit {\n"
                                 "	color: white;\n"
                                 "	background: transparent;\n"
                                 "	border: 1px solid black;\n"
                                 "}\n"
                                 "#edittask_listWidget {\n"
                                 "	background: transparent;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 "}\n"
                                 "#edittask_dateTimeEdit {\n"
                                 f"	font: {EDITTASK_DATETIMEEDIT_FONT};\n"
                                 "	color: white;\n"
                                 "	border-radius: 1px;\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid gray;\n"
                                 "}\n"
                                 "#edittask_dateTimeEdit:focus {\n"
                                 f"	font: {EDITTASK_DATETIMEEDIT_FONT};\n"
                                 "	color: white;\n"
                                 "	border-radius: 1px;\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid white;\n"
                                 "}\n"
                                 "#edittask_plainTextEdit:hover {\n"
                                 "	background: transparent;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "#edittask_listWidget:hover {\n"
                                 "	background: transparent;\n"
                                 "	border: 2px solid black;\n"
                                 "}\n"
                                 "#edittask_dateEdit {\n"
                                 f"	font: {EDITTASK_DATEEDIT_FONT};\n"
                                 "	color: white;\n"
                                 "	border-radius: 1px;\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid gray;\n"
                                 "}\n"
                                 "#edittask_dateEdit:focus {\n"
                                 f"	font: {EDITTASK_DATEEDIT_FONT};\n"
                                 "	color: white;\n"
                                 "	border-radius: 1px;\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid white;\n"
                                 "}\n"
                                 "#edittask_lineEdit_task_name {\n"
                                 "	color: white;\n"
                                 "	background: transparent;\n"
                                 f"	font: {EDITTASK_TASKNAME_INPUT};\n"
                                 "	border: none;\n"
                                 "	border-bottom: 1px solid gray;\n"
                                 "}\n"
                                 "#edittask_lineEdit_task_name:focus {\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid white;\n"
                                 "}\n"
                                 "#edittask_button_continue {\n"
                                 "	background: transparent;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 f"	font: {EDITTASK_BUTTON_CONTINUE_FONT};\n"
                                 "}\n"
                                 "#edittask_button_continue:hover {\n"
                                 "	border: 2px solid black;\n"
                                 f"	font: {EDITTASK_BUTTON_CONTINUE_FONT_HOVER};\n"
                                 "}\n"
                                 "#edittask_button_load_tasks {\n"
                                 "	background: transparent;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 f"	font: {EDITTASK_LOAD_TASKS_BUTTON_FONT};\n"
                                 "}\n"
                                 "#edittask_button_load_tasks:hover {\n"
                                 "	border: 2px solid black;\n"
                                 f"	font: {EDITTASK_LOAD_TASKS_BUTTON_FONT_HOVER};\n"
                                 "}\n"
                                 "#edittask_button_delete {\n"
                                 "	background: transparent;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 f"	font: {EDITTASK_DELETE_BUTTON_FONT};\n"
                                 "}\n"
                                 "#edittask_button_delete:hover {\n"
                                 "	border: 2px solid black;\n"
                                 f"	font: {EDITTASK_DELETE_BUTTON_FONT_HOVER};\n"
                                 "}\n"
                                 "#accountsettings_label_logged_is_as {\n"
                                 "	color: white;\n"
                                 f"	font: {ACCOUNTSETTINGS_LOGGEDAS_LABEL_FONT};\n"
                                 "}\n"
                                 "#accountsettings_label_change_password {\n"
                                 "	color: white;\n"
                                 f"	font: {ACCOUNTSETTINGS_CHANGEPASSWORD_LABEL_FONT};\n"
                                 "}\n"
                                 "\n"
                                 "#accountsettings_lineEdit_old_password {\n"
                                 "	color: white;\n"
                                 "	background: transparent;\n"
                                 f"	font: {ACCOUNTSETTINGS_PASSWORD_INPUT_FONT};\n"
                                 "	border: none;\n"
                                 "	border-bottom: 1px solid gray;\n"
                                 "}\n"
                                 "\n"
                                 "#accountsettings_lineEdit_old_password:focus {\n"
                                 ""
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid white;\n"
                                 "}\n"
                                 "\n"
                                 "#accountsettings_lineEdit_new_password {\n"
                                 "	color: white;\n"
                                 "	background: transparent;\n"
                                 f"	font: {ACCOUNTSETTINGS_PASSWORD_INPUT_FONT};\n"
                                 "	border: none;\n"
                                 "	border-bottom: 1px solid gray;\n"
                                 "}\n"
                                 "\n"
                                 "#accountsettings_lineEdit_new_password:focus {\n"
                                 "	background: transparent;\n"
                                 "	border-bottom: 1px solid white;\n"
                                 "}\n"
                                 "\n"
                                 "#accountsettings_button_continue_change_pass{\n"
                                 "	background: transparent;\n"
                                 "	border-radius: 0px;\n"
                                 "	border: 1px solid black;\n"
                                 "	color: white;\n"
                                 f"	font: {ACCOUNTSETTINGS_CONTINUE_BUTTON_FONT};\n"
                                 "}\n"
                                 "\n"
                                 "#accountsettings_button_continue_change_pass:hover {\n"
                                 "	border: 2px solid black;\n"
                                 f"	font: {ACCOUNTSETTINGS_CONTINUE_BUTTON_FONT_HOVER};\n"
                                 "}")

        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.button_general = QtWidgets.QPushButton(self.frame)
        self.button_general.setGeometry(QtCore.QRect(60, 150, 200, 80))
        self.button_general.setObjectName("button_general")
        self.button_addtask = QtWidgets.QPushButton(self.frame)
        self.button_addtask.setGeometry(QtCore.QRect(60, 230, 200, 80))
        self.button_addtask.setObjectName("button_addtask")
        self.button_edittask = QtWidgets.QPushButton(self.frame)
        self.button_edittask.setGeometry(QtCore.QRect(60, 310, 200, 80))
        self.button_edittask.setObjectName("button_edittask")
        self.button_accountsettings = QtWidgets.QPushButton(self.frame)
        self.button_accountsettings.setGeometry(QtCore.QRect(60, 390, 200, 80))
        self.button_accountsettings.setObjectName("button_accountsettings")
        self.label_DPlanner = QtWidgets.QLabel(self.frame)
        self.label_DPlanner.setGeometry(QtCore.QRect(60, 40, 200, 111))
        self.label_DPlanner.setAlignment(QtCore.Qt.AlignCenter)
        self.label_DPlanner.setObjectName("label_DPlanner")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DPlanner"))
        self.button_general.setText(_translate("MainWindow", "General"))
        self.button_addtask.setText(_translate("MainWindow", "Add task"))
        self.button_edittask.setText(_translate("MainWindow", "Edit task"))
        self.button_accountsettings.setText(_translate("MainWindow", "Account settings"))
        self.label_DPlanner.setText(_translate("MainWindow", "DPlanner"))


class Ui_Login(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(640, 420)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("#frame {\n"
                                 "	border-radius: 30px;\n"
                                 "	background-color: rgb(121, 121, 121);\n"
                                 "	border-width: 30px;\n"
                                 "}\n"
                                 "#label {\n"
                                 f"	font: {LOGIN_DPLANNER_LOGO_FONT};\n"
                                 "	color: white;\n"
                                 "}\n"
                                 "#label_2 {\n"
                                 "	color: white;\n"
                                 f"	font: {USING_ACCOUNT_LABEL_FONT};\n"
                                 "}\n"
                                 "QLineEdit {\n"
                                 "	background: transparent;\n"
                                 "	border: none;\n"
                                 "	color: #999;\n"
                                 "	border-bottom: 1px solid #717072\n"
                                 "}\n"
                                 "#pushButton {\n"
                                 "	background-color:transparent;\n"
                                 "	border:2px solid #dcdcdc;\n"
                                 "	color:#666666;\n"
                                 f"	font: {BUTTON_FONT};\n"
                                 "	border-radius: 25px;\n"
                                 "}\n"
                                 "#pushButton:hover {\n"
                                 "	background-color:white;\n"
                                 "}\n"
                                 "QLineEdit:focus {\n"
                                 "	background: transparent;\n"
                                 "	border: none;\n"
                                 "	color: #999;\n"
                                 "	border-bottom: 2px solid rgb(255, 255, 255)\n"
                                 "}\n"
                                 "#pushButton_2 {\n"
                                 "	background-color: rgb(121, 121, 121);\n"
                                 "	border:2px solid #dcdcdc;\n"
                                 "	color:#666666;\n"
                                 f"	font: {BUTTON_FONT};\n"
                                 "	border-radius: 25px;\n"
                                 "}\n"
                                 "#pushButton_2:hover {\n"
                                 "	background-color:rgb(255, 255, 255);\n"
                                 "	border:3px solid rgb(255, 255, 255);\n"
                                 "}")
        pictures = ["fox-1883658_640.png",
                    "peak-5645235_640.jpg",
                    "jusang-joint-4810725_640.jpg",
                    "guggenheim-museum-2707258_640.jpg",
                    "waterfall-3723422_640.jpg", "terraces-5568679_640.jpg"]
        self.pixmap = QPixmap(pictures[random.randrange(0, len(pictures))])
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(640, 427)
        self.image.setPixmap(self.pixmap)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(190, 30, 251, 331))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(80, 10, 111, 51))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(70, 60, 121, 20))
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(30, 240, 191, 51))
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setGeometry(QtCore.QRect(20, 110, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.lineEdit.setFont(font)
        self.lineEdit.setInputMask("")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_2.setGeometry(QtCore.QRect(20, 170, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setInputMask("")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QtCore.QRect(490, 365, 141, 51))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DPlanner"))
        self.label.setText(_translate("MainWindow", "Sign in"))
        self.label_2.setText(_translate("MainWindow", "Using DPlanner account"))
        self.pushButton.setText(_translate("MainWindow", "Continue"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Username"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "Password"))
        self.pushButton_2.setText(_translate("MainWindow", "Sign up"))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, window, name, id):
        self.username = name
        self.id = id
        self.tablename = DATABASE.get_table_name(self.username)
        super().__init__(window)
        super().setupUi(window)
        super().retranslateUi(window)
        self.current_mode = 1
        self.load()
        self.show_general()
        self.button_general.clicked.connect(self.open_general)
        self.button_addtask.clicked.connect(self.open_addtask)
        self.button_edittask.clicked.connect(self.open_edittask)
        self.button_accountsettings.clicked.connect(self.open_accountsettings)

    def get_tasks(self, date=None):
        raw_tasks = DATABASE.view_tasks(self.tablename)
        self.today_tasks = dict()
        if date is None:
            today = datetime.datetime.now()
            for task in raw_tasks:
                id, title, desc, time = task
                time = time.split("-")
                if today.year == int(time[0]) and today.month == int(time[1]) and today.day == int(time[2]):
                    time = f"{time[3]}:{time[4]}"
                    self.today_tasks[f"{time} - {title}"] = desc
            today_tasks_keys = list(self.today_tasks.keys())
            today_tasks_keys.sort(key=lambda x: int("".join(x.split("-")[0].split(":"))))
            return today_tasks_keys
        else:
            today = date.getDate()
            for task in raw_tasks:
                id, title, desc, time = task
                time = time.split("-")
                if today[0] == int(time[0]) and today[1] == int(time[1]) and today[2] == int(time[2]):
                    time = f"{time[3]}:{time[4]}"
                    self.today_tasks[f"{time} - {title} ({id})"] = desc
            today_tasks_keys = list(self.today_tasks.keys())
            today_tasks_keys.sort(key=lambda x: int("".join(x.split("-")[0].split(":"))))
            return today_tasks_keys

    def actions_general(self):
        self.general_listWidget.clear()
        for task in self.get_tasks():
            self.general_listWidget.addItem(task)

    def general_listWidget_clicked(self, item):
        self.general_plainTextEdit.setPlainText(self.today_tasks[item.text()])

    def addtask_button_continue_clicked(self):
        title = self.addtask_lineEdit.text()
        description = self.addtask_plainTextEdit.toPlainText()
        if title == "" or len(title) > 70:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Task title neither may be empty nor contain more than 70 symbols!")
            msg.setWindowTitle("Failure")
            x = msg.exec_()
            return
        if len(description) > 700:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Task description may not contain more than 700 symbols!")
            msg.setWindowTitle("Failure")
            x = msg.exec_()
            return
        if "\"" in description or "'" in description or "\"" in title or "'" in title:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Sorry, but you can't use neither ' nor \" symbol!")
            msg.setWindowTitle("Failure")
            x = msg.exec_()
            return
        date = to_formated_date(self.addtask_dateTimeEdit.text())
        DATABASE.add_task(self.tablename, title, description, date)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Task has been successfully added!")
        msg.setWindowTitle("Success")
        x = msg.exec_()

    def actions_edittask(self):
        self.edittask_dateEdit.setDate(datetime.datetime.now().date())
        self.edittask_button_load_tasks_clicked()

    def edittask_button_delete_clicked(self):
        try:
            if self.edittask_selected_id is None:
                raise AttributeError
            DATABASE.delete_task(self.tablename, self.edittask_selected_id)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Task successfully deleted!")
            msg.setWindowTitle("Success")
            x = msg.exec_()
            self.hide_edittask()
            self.show_edittask()
        except AttributeError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Select task by double-clicking on it first!")
            msg.setWindowTitle("Failure")
            x = msg.exec_()

    def edittask_button_continue_clicked(self):
        title = self.edittask_lineEdit_task_name.text()
        description = self.edittask_plainTextEdit.toPlainText()
        if title == "" or title > 70:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Task title neither may be empty nor contain more than 70 symbols!")
            msg.setWindowTitle("Failure")
            x = msg.exec_()
            return
        if description > 700:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Task description may not contain more than 700 symbols!")
            msg.setWindowTitle("Failure")
            x = msg.exec_()
            return
        if "\"" in description or "'" in description or "\"" in title or "'" in title:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Sorry, but you can't use neither ' nor \" symbol!")
            msg.setWindowTitle("Failure")
            x = msg.exec_()
            return
        DATABASE.edit_task(self.tablename, self.edittask_selected_id, title, description,
                           to_formated_date(self.edittask_dateTimeEdit.text()))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Task has been successfully edited!")
        msg.setWindowTitle("Success")
        x = msg.exec_()
        self.edittask_button_load_tasks_clicked()

    def edittask_listWidget_clicked(self, item):
        self.edittask_plainTextEdit.setPlainText(self.today_tasks[item.text()])
        self.edittask_selected_id = int(item.text().split()[-1].lstrip("(").rstrip(")"))
        self.edittask_lineEdit_task_name.setText(
            item.text().split(" - ")[1].rstrip(f" ({str(self.edittask_selected_id)})"))
        self.edittask_dateTimeEdit.setDate(self.edittask_dateEdit.date())
        time = datetime.time(*[int(i) for i in item.text().split(" - ")[0].split(":")])
        self.edittask_dateTimeEdit.setTime(time)

        self.edittask_button_continue.show()
        self.edittask_lineEdit_task_name.show()
        self.edittask_plainTextEdit.show()
        self.edittask_button_delete.show()
        self.edittask_dateTimeEdit.show()

    def edittask_button_load_tasks_clicked(self):
        self.edittask_listWidget.clear()
        for task in self.get_tasks(self.edittask_dateEdit.date()):
            self.edittask_listWidget.addItem(task)

    def accountsettings_button_continue_change_pass_clicked(self):
        response = check_password(self.accountsettings_lineEdit_new_password.text())
        if response is True:
            if DATABASE.change_password(self.id, self.accountsettings_lineEdit_old_password.text(),
                                        self.accountsettings_lineEdit_new_password.text()):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Password successfully changed!")
                msg.setWindowTitle("Success")
                x = msg.exec_()
                self.accountsettings_lineEdit_old_password.setText("")
                self.accountsettings_lineEdit_new_password.setText("")
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Old password is incorrect!")
                msg.setWindowTitle("Failure")
                x = msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(response)
            msg.setWindowTitle("Failure")
            x = msg.exec_()

    def close_current_mode(self):
        if self.current_mode == GENERAL:
            self.hide_general()
        elif self.current_mode == EDITTASK:
            self.hide_edittask()
        elif self.current_mode == ADDTASK:
            self.hide_addtask()
        elif self.current_mode == ACCOUNTSETTINGS:
            self.hide_accountsettings()

    def open_general(self):
        if self.current_mode != GENERAL:
            self.close_current_mode()
            self.show_general()
            self.current_mode = GENERAL

    def open_edittask(self):
        if self.current_mode != EDITTASK:
            self.close_current_mode()
            self.show_edittask()
            self.current_mode = EDITTASK

    def open_addtask(self):
        if self.current_mode != ADDTASK:
            self.close_current_mode()
            self.show_addtask()
            self.current_mode = ADDTASK

    def open_accountsettings(self):
        if self.current_mode != ACCOUNTSETTINGS:
            self.close_current_mode()
            self.show_accountsettings()
            self.current_mode = ACCOUNTSETTINGS

    def hide_general(self):
        self.general_plainTextEdit.hide()
        self.general_label_today.hide()
        self.general_listWidget.hide()

    def show_general(self):
        self.label_selected_mode.setText("General")
        self.general_plainTextEdit.show()
        self.general_label_today.show()
        self.general_listWidget.show()
        self.actions_general()

    def hide_edittask(self):
        self.edittask_dateEdit.hide()
        self.edittask_listWidget.hide()
        self.edittask_button_continue.hide()
        self.edittask_button_load_tasks.hide()
        self.edittask_label_select_date.hide()
        self.edittask_lineEdit_task_name.hide()
        self.edittask_plainTextEdit.hide()
        self.edittask_button_delete.hide()
        self.edittask_dateTimeEdit.hide()

    def show_edittask(self):
        self.actions_edittask()
        self.label_selected_mode.setText("Edit task")
        self.edittask_dateEdit.show()
        self.edittask_listWidget.show()
        self.edittask_button_load_tasks.show()
        self.edittask_label_select_date.show()
        self.edittask_selected_id = None
        self.edittask_plainTextEdit.clear()
        self.edittask_lineEdit_task_name.clear()

    def hide_addtask(self):
        self.addtask_lineEdit.hide()
        self.addtask_label_1.hide()
        self.addtask_label_2.hide()
        self.addtask_label_3.hide()
        self.addtask_dateTimeEdit.hide()
        self.addtask_button_continue.hide()
        self.addtask_plainTextEdit.hide()

    def show_addtask(self):
        self.label_selected_mode.setText("Add task")
        self.addtask_lineEdit.show()
        self.addtask_label_1.show()
        self.addtask_label_2.show()
        self.addtask_label_3.show()
        self.addtask_dateTimeEdit.show()
        self.addtask_button_continue.show()
        self.addtask_plainTextEdit.show()

    def hide_accountsettings(self):
        self.accountsettings_lineEdit_new_password.hide()
        self.accountsettings_button_continue_change_pass.hide()
        self.accountsettings_label_change_password.hide()
        self.accountsettings_label_logged_is_as.hide()
        self.accountsettings_lineEdit_old_password.hide()

    def show_accountsettings(self):
        self.label_selected_mode.setText("Account settings")
        self.accountsettings_lineEdit_new_password.show()
        self.accountsettings_button_continue_change_pass.show()
        self.accountsettings_label_change_password.show()
        self.accountsettings_label_logged_is_as.show()
        self.accountsettings_lineEdit_old_password.show()

    def load(self):
        self.label_selected_mode = QtWidgets.QLabel(self.frame)
        self.label_selected_mode.setGeometry(QtCore.QRect(260, 40, 441, 111))
        self.label_selected_mode.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing)
        self.label_selected_mode.setObjectName("label_selected_mode")

        # general
        self.general_label_today = QtWidgets.QLabel(self.frame)
        self.general_label_today.setGeometry(QtCore.QRect(267, 152, 421, 71))
        self.general_label_today.setObjectName("general_label_today")
        self.general_listWidget = QtWidgets.QListWidget(self.frame)
        self.general_listWidget.setGeometry(QtCore.QRect(270, 210, 181, 251))
        self.general_listWidget.setObjectName("general_listWidget")
        self.general_plainTextEdit = QtWidgets.QPlainTextEdit(self.frame)
        self.general_plainTextEdit.setGeometry(QtCore.QRect(470, 240, 221, 221))
        self.general_plainTextEdit.setObjectName("general_plainTextEdit")
        self.general_plainTextEdit.setReadOnly(True)

        self.label_selected_mode.setText("General")
        self.general_label_today.setText("Today")

        self.general_listWidget.itemDoubleClicked.connect(self.general_listWidget_clicked)

        # edittask
        self.edittask_button_continue = QtWidgets.QPushButton(self.frame)
        self.edittask_button_continue.setGeometry(QtCore.QRect(279, 409, 191, 41))
        self.edittask_button_continue.setObjectName("edittask_button_continue")
        self.edittask_button_delete = QtWidgets.QPushButton(self.frame)
        self.edittask_button_delete.setObjectName("edittask_button_delete")
        self.edittask_button_delete.setGeometry(QtCore.QRect(490, 409, 191, 41))
        self.edittask_dateEdit = QtWidgets.QDateEdit(self.frame)
        self.edittask_dateEdit.setGeometry(QtCore.QRect(410, 160, 141, 31))
        self.edittask_dateEdit.setObjectName("edittask_dateEdit")
        self.edittask_label_select_date = QtWidgets.QLabel(self.frame)
        self.edittask_label_select_date.setGeometry(QtCore.QRect(270, 150, 141, 41))
        self.edittask_label_select_date.setObjectName("edittask_label_select_date")
        self.edittask_listWidget = QtWidgets.QListWidget(self.frame)
        self.edittask_listWidget.setGeometry(QtCore.QRect(270, 200, 161, 192))
        self.edittask_listWidget.setObjectName("edittask_listWidget")
        self.edittask_lineEdit_task_name = QtWidgets.QLineEdit(self.frame)
        self.edittask_lineEdit_task_name.setGeometry(QtCore.QRect(460, 210, 221, 31))
        self.edittask_lineEdit_task_name.setObjectName("edittask_lineEdit_task_name")
        self.edittask_plainTextEdit = QtWidgets.QPlainTextEdit(self.frame)
        self.edittask_plainTextEdit.setGeometry(QtCore.QRect(460, 250, 221, 91))
        self.edittask_plainTextEdit.setObjectName("edittask_plainTextEdit")
        self.edittask_button_load_tasks = QtWidgets.QPushButton(self.frame)
        self.edittask_button_load_tasks.setGeometry(QtCore.QRect(560, 160, 131, 41))
        self.edittask_button_load_tasks.setObjectName("edittask_button_load_tasks")
        self.edittask_dateTimeEdit = QDateTimeEdit(self.frame)
        self.edittask_dateTimeEdit.setObjectName("edittask_dateTimeEdit")
        self.edittask_dateTimeEdit.setGeometry(QtCore.QRect(460, 350, 221, 41))

        self.edittask_label_select_date.setText("Select date: ")
        self.edittask_button_continue.setText("Continue")
        self.edittask_lineEdit_task_name.setPlaceholderText("Name of the task...")
        self.edittask_plainTextEdit.setPlaceholderText("Description of the task...")
        self.edittask_button_load_tasks.setText("Load tasks")
        self.edittask_button_delete.setText("Delete")

        self.edittask_button_load_tasks.clicked.connect(self.edittask_button_load_tasks_clicked)
        self.edittask_listWidget.itemDoubleClicked.connect(self.edittask_listWidget_clicked)
        self.edittask_button_delete.clicked.connect(self.edittask_button_delete_clicked)
        self.edittask_button_continue.clicked.connect(self.edittask_button_continue_clicked)

        self.hide_edittask()

        # addtask
        self.addtask_dateTimeEdit = QtWidgets.QDateTimeEdit(self.frame)
        self.addtask_dateTimeEdit.setGeometry(QtCore.QRect(410, 180, 231, 30))
        self.addtask_dateTimeEdit.setObjectName("addtask_dateTimeEdit")
        self.addtask_dateTimeEdit.setDateTime(datetime.datetime.now())
        self.addtask_label_1 = QtWidgets.QLabel(self.frame)
        self.addtask_label_1.setGeometry(QtCore.QRect(280, 160, 131, 60))
        self.addtask_label_1.setObjectName("addtask_label_1")
        self.addtask_label_2 = QtWidgets.QLabel(self.frame)
        self.addtask_label_2.setGeometry(QtCore.QRect(280, 210, 181, 60))
        self.addtask_label_2.setObjectName("addtask_label_2")
        self.addtask_lineEdit = QtWidgets.QLineEdit(self.frame)
        self.addtask_lineEdit.setGeometry(QtCore.QRect(460, 220, 211, 50))
        self.addtask_lineEdit.setObjectName("addtask_lineEdit")
        self.addtask_label_3 = QtWidgets.QLabel(self.frame)
        self.addtask_label_3.setGeometry(QtCore.QRect(280, 270, 181, 60))
        self.addtask_label_3.setObjectName("addtask_label_3")
        self.addtask_plainTextEdit = QtWidgets.QPlainTextEdit(self.frame)
        self.addtask_plainTextEdit.setGeometry(QtCore.QRect(470, 290, 201, 111))
        self.addtask_plainTextEdit.setObjectName("addtask_plainTextEdit")
        self.addtask_button_continue = QtWidgets.QPushButton(self.frame)
        self.addtask_button_continue.setGeometry(QtCore.QRect(279, 409, 401, 41))
        self.addtask_button_continue.setObjectName("addtask_button_continue")

        self.addtask_label_1.setText("Select time:")
        self.addtask_label_2.setText("Name of the task:")
        self.addtask_label_3.setText("Task description:")
        self.addtask_button_continue.setText("Continue")

        self.addtask_button_continue.clicked.connect(self.addtask_button_continue_clicked)

        self.hide_addtask()

        # accountsettings
        self.accountsettings_label_logged_is_as = QtWidgets.QLabel(self.frame)
        self.accountsettings_label_logged_is_as.setGeometry(QtCore.QRect(300, 160, 391, 41))
        self.accountsettings_label_logged_is_as.setObjectName("accountsettings_label_logged_is_as")
        self.accountsettings_lineEdit_old_password = QtWidgets.QLineEdit(self.frame)
        self.accountsettings_lineEdit_old_password.setGeometry(QtCore.QRect(272, 250, 220, 40))
        self.accountsettings_lineEdit_old_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.accountsettings_lineEdit_old_password.setObjectName("accountsettings_lineEdit_old_password")
        self.accountsettings_lineEdit_new_password = QtWidgets.QLineEdit(self.frame)
        self.accountsettings_lineEdit_new_password.setGeometry(QtCore.QRect(270, 300, 220, 41))
        font = QtGui.QFont()
        font.setFamily("Manjari")
        font.setPointSize(18)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.accountsettings_lineEdit_new_password.setFont(font)
        self.accountsettings_lineEdit_new_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.accountsettings_lineEdit_new_password.setObjectName("accountsettings_lineEdit_new_password")
        self.accountsettings_label_change_password = QtWidgets.QLabel(self.frame)
        self.accountsettings_label_change_password.setGeometry(QtCore.QRect(270, 200, 391, 41))
        self.accountsettings_label_change_password.setObjectName("accountsettings_label_change_password")
        self.accountsettings_button_continue_change_pass = QtWidgets.QPushButton(self.frame)
        self.accountsettings_button_continue_change_pass.setGeometry(QtCore.QRect(270, 350, 191, 51))
        self.accountsettings_button_continue_change_pass.setObjectName("accountsettings_button_continue_change_pass")

        self.accountsettings_label_logged_is_as.setText("Logged in as {}".format(self.username))
        self.accountsettings_lineEdit_old_password.setPlaceholderText("Old password")
        self.accountsettings_lineEdit_new_password.setPlaceholderText("New password")
        self.accountsettings_label_change_password.setText("Change password:")
        self.accountsettings_button_continue_change_pass.setText("Continue")

        self.accountsettings_button_continue_change_pass.clicked.connect(
            self.accountsettings_button_continue_change_pass_clicked)

        self.hide_accountsettings()


class LoginWindow(Ui_Login, QMainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        super().retranslateUi(self)
        self.current_mode = 0
        self.load_registration()
        self.pushButton.clicked.connect(self.con)
        self.pushButton_2.clicked.connect(self.button)

    def messagebox(self, message, icon, title):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setWindowTitle(title)
        x = msg.exec_()

    def load_registration(self):
        self.registration_lineEdit_login = QLineEdit(self.frame)
        self.registration_lineEdit_login.setObjectName("registration_lineEdit_login")
        self.registration_lineEdit_login.setGeometry(QRect(20, 110, 211, 31))
        font = QFont()
        font.setPointSize(16)
        self.registration_lineEdit_login.setFont(font)
        self.registration_lineEdit_password1 = QLineEdit(self.frame)
        self.registration_lineEdit_password1.setObjectName("registration_lineEdit_password1")
        self.registration_lineEdit_password1.setGeometry(QRect(20, 150, 211, 31))
        self.registration_lineEdit_password1.setFont(font)
        self.registration_lineEdit_password2 = QLineEdit(self.frame)
        self.registration_lineEdit_password2.setObjectName("registration_lineEdit_password2")
        self.registration_lineEdit_password2.setGeometry(QRect(20, 190, 211, 31))
        self.registration_lineEdit_password2.setFont(font)
        self.registration_lineEdit_email = QLineEdit(self.frame)
        self.registration_lineEdit_email.setObjectName("registration_lineEdit_email")
        self.registration_lineEdit_email.setGeometry(QRect(20, 70, 211, 31))
        self.registration_lineEdit_email.setFont(font)
        self.registration_lineEdit_email.setPlaceholderText("E-mail")
        self.registration_lineEdit_login.setPlaceholderText("Username")
        self.registration_lineEdit_password1.setPlaceholderText("Password")
        self.registration_lineEdit_password2.setPlaceholderText("Password again")
        self.registration_lineEdit_email.hide()
        self.registration_lineEdit_password1.hide()
        self.registration_lineEdit_password2.hide()
        self.registration_lineEdit_login.hide()

    def button(self):
        if self.current_mode == 0:
            self.open_signup()
        else:
            self.open_login()

    def open_login(self):
        if self.current_mode == 1:
            self.current_mode = 0

            self.pushButton_2.setText("Sign up")
            self.label_2.show()
            self.lineEdit.show()
            self.lineEdit_2.show()
            self.label.setText("Sign in")

            self.registration_lineEdit_email.hide()
            self.registration_lineEdit_password1.hide()
            self.registration_lineEdit_password2.hide()
            self.registration_lineEdit_login.hide()

            self.lineEdit.setText("")
            self.lineEdit_2.setText("")

    def open_signup(self):
        if self.current_mode == 0:
            self.current_mode = 1

            self.pushButton_2.setText("Sign in")
            self.label_2.hide()
            self.lineEdit.hide()
            self.lineEdit_2.hide()
            self.label.setText("Sign up")

            self.registration_lineEdit_email.show()
            self.registration_lineEdit_password1.show()
            self.registration_lineEdit_password2.show()
            self.registration_lineEdit_login.show()

            self.registration_lineEdit_email.setText("")
            self.registration_lineEdit_password1.setText("")
            self.registration_lineEdit_password2.setText("")
            self.registration_lineEdit_login.setText("")

    def con(self):
        if self.current_mode == 0:
            self.authorisation()
        else:
            self.registration()

    def registration(self):
        username, email, password1, password2 = self.registration_lineEdit_login.text(), self.registration_lineEdit_email.text(), self.registration_lineEdit_password1.text(), self.registration_lineEdit_password2.text()
        if password1 == password2:
            password_check = check_password(password1)
            username_check = check_username(username)
            email_check = check_email(email)
            if password_check is True and username_check is True and email_check is True:
                try:
                    DATABASE.register_user(username, password1, email)
                    self.messagebox("Account successfully created!", QMessageBox.Information, "Success")
                    self.open_login()
                    self.lineEdit.setText(username)
                except RegistrationError:
                    self.messagebox("Username has been taken!", QMessageBox.Warning, "Failure")
            else:
                errors = "\n".join([i for i in [password_check, username_check, email_check] if i is not True])
                self.messagebox(errors, QMessageBox.Warning, "Failure")

    def authorisation(self):
        username, password = self.lineEdit.text(), self.lineEdit_2.text()
        if "\"" in username or "'" in username or "\"" in password or "'" in password:
            self.messagebox("Sorry, but you cant use neither \" nor ' symbols!", QMessageBox.Critical, "Failure")
            return
        result = DATABASE.login(username, password)
        if result:
            mw = MainWindow(self, username, result)
        else:
            self.messagebox("Invalid login or password", QMessageBox.Warning, "Failure")

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            if self.current_mode == 0:
                self.authorisation()
            elif self.current_mode == 1:
                self.registration()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
