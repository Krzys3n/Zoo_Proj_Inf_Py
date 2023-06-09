import os
import sys
from functools import partial
import numpy as np
import seaborn as sns
from PyQt6 import uic, QtGui, QtWidgets, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QTableView, QFileDialog, QMessageBox, QDialog, QPushButton, QVBoxLayout, \
    QLineEdit, QHBoxLayout, QStyleFactory
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.uic import loadUiType

from reportlab.pdfgen import canvas
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextBrowser
from PyQt6.QtGui import QEnterEvent
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder


# przechowywanie dancyh
df = pd.read_csv('zoo.data', header=None)
df_with_labels = pd.DataFrame
df_with_labels = df.copy()
selected_indexes = set()
selected_columns = set()
selected_rows = set()
# Ustawianie nazw kolumn
labels = ["animal name", "hair", "feathers", "eggs", "milk", "airborne", "aquatic", "predator", "toothed", "backbone",
          "breathes", "venomous", "fins", "legs", "tail", "domestic", "catsize", "type"]
labels_no_zero_column = ["hair", "feathers", "eggs", "milk", "airborne", "aquatic", "predator", "toothed", "backbone",
                         "breathes", "venomous", "fins", "legs", "tail", "domestic", "catsize", "type"]
# model.setHorizontalHeaderLabels(labels)
df_with_labels.columns = labels

# Liczba kolumn minus 1
x = len(df.columns) - 1
#
# # Ustawienie nazw kolumn na liczby od 0 do x
df.columns = list(range(x + 1))
#

# Klasyfikacja danych:
def is_text_or_number(value):
    try:
        float(value)  # Spróbuj przekształcić wartość na liczbę zmiennoprzecinkową
        return False  # Jeśli się udało, oznacza to, że wartość jest liczbą
    except ValueError:
        return True  # Jeśli pojawił się ValueError, oznacza to, że wartość jest tekstem

def code_data(df):
    dane_tekstowe = df.select_dtypes(include=['object'])
    dane_numeryczne = df.select_dtypes(exclude=['object'])
    if dane_tekstowe.empty:
        return df
    else:
        dane_binarne = pd.get_dummies(dane_tekstowe)

    df_encoded = pd.concat([dane_numeryczne, dane_binarne], axis=1)
    return df_encoded

def classificate_selected_data(PyQtComboBox, PyQtTextBrowser):
    # Przygotowanie danych
    global delete_col
    isTextOrNumber = is_text_or_number(PyQtComboBox.currentText())
    if(isTextOrNumber == True):
        temp_column = df_with_labels[PyQtComboBox.currentText().strip()]
        delete_col = PyQtComboBox.currentText()
    if(isTextOrNumber == False):
        temp_column = df[int(PyQtComboBox.currentText())]
        delete_col = int(PyQtComboBox.currentText())

    if temp_column.dtype == 'object' or temp_column.dtype == 'int64'  or temp_column.dtype == 'float64' :
        czy_ma_kolumne = False
        df_class_init = pd.DataFrame()

        for column in selected_columns:
            nazwa_kolumny = df_with_labels.columns[column]
            df_class_init[nazwa_kolumny] = df_with_labels.iloc[:, column]


        for i in df_class_init.columns:
            if i == delete_col:
                czy_ma_kolumne = True

        if czy_ma_kolumne:
            if (isTextOrNumber == True):
                df_class_init = df_class_init.drop(delete_col, axis=1)
            else:
                df_class_init = df_class_init.drop(df_class_init.columns[delete_col], axis=1)
        df_class_init = code_data(df_class_init)
        predict_column = temp_column
        X_train, X_test, y_train, y_test = train_test_split(df_class_init, predict_column, test_size=0.1, random_state=42)

        # Inicjalizacja klasyfikatora
        classifier = DecisionTreeClassifier()

        # Trenowanie klasyfikatora na danych treningowych
        classifier.fit(X_train, y_train)

        # Wykonanie krzyżowej walidacji
        predicted_labels = cross_val_predict(classifier, df_class_init, predict_column, cv=5)

        # Tworzenie instancji LabelEncoder
        label_encoder = LabelEncoder()

        # Przekształcenie etykiet klas na liczby całkowite
        y_test_encoded = label_encoder.fit_transform(temp_column)
        predicted_labels_encoded = label_encoder.transform(predicted_labels)

        # Obliczenie dokładności klasyfikacji
        accuracy = accuracy_score(y_test_encoded, predicted_labels_encoded)

        # Utworzenie nowego DataFrame z przewidzianymi etykietami
        X_test = df_class_init.copy()
        X_test[f'Predicted {PyQtComboBox.currentText()}'] = predicted_labels

        # Wyświetlenie wyników klasyfikacji
        PyQtTextBrowser.append(X_test.to_string())
        # Wyświetlenie wyników klasyfikacji
        PyQtTextBrowser.append(f"\nDokładność klasyfikacji: {accuracy}")
    else:
        PyQtTextBrowser.append("Błąd: Wybrany atrybut do przewidywania jest numeryczny.")

# Funkcje statystyczne:

def calculate_minimum(QtTextBrowser, QtTableView): #git
    try:
        for column in selected_columns:
            # Oblicz minimum z wybranej kolumny
            minimum = df[column].min()

            # Konwertuj wartość na string
            minimum_str = str(minimum)

            # Pobierz tekst nagłówka kolumny z QTableView
            header_text = QtTableView.model().headerData(column, Qt.Orientation.Horizontal)

            # Wyświetl wartość w QTextBrowser
            QtTextBrowser.append(f"Minimum from column {header_text} is: {minimum_str}")
    except Exception as e:
        QtTextBrowser.append(f"Error occurred: {str(e)}")

def calculate_maximum(QtTextBrowser, QtTableView): #git
    try:
        for column in selected_columns:
            # Oblicz maksimum z wybranej kolumny
            maximum = df[column].max()

            # Konwertuj wartość na string
            maximum_str = str(maximum)

            # Pobierz tekst nagłówka kolumny z QTableView
            header_text = QtTableView.model().headerData(column, Qt.Orientation.Horizontal)

            # Wyświetl wartość w QTextBrowser
            QtTextBrowser.append(f"Maximum from column {header_text} is: {maximum_str}")
    except Exception as e:
        QtTextBrowser.append(f"Error occurred: {str(e)}")

def calculate_median(QtTextBrowser, QtTableView): #git
    try:
        for column in selected_columns:
            # Oblicz medianę z wybranej kolumny
            median = df[column].median()

            # Konwertuj wartość na string
            median_str = str(median)

            # Pobierz tekst nagłówka kolumny z QTableView
            header_text = QtTableView.model().headerData(column, Qt.Orientation.Horizontal)

            # Wyświetl wartość w QTextBrowser
            QtTextBrowser.append(f"Median from column {header_text} is: {median_str}")
    except Exception as e:
        QtTextBrowser.append(f"Error occurred: {str(e)}")

def calculate_std(QtTextBrowser, QtTableView): #git
    try:
        for column in selected_columns:
            # Oblicz odchylenie standardowe z wybranej kolumny
            std = df[column].std()

            # Konwertuj wartość na string
            std_str = str(std)

            # Pobierz tekst nagłówka kolumny z QTableView
            header_text = QtTableView.model().headerData(column, Qt.Orientation.Horizontal)

            # Wyświetl wartość w QTextBrowser
            QtTextBrowser.append(f"Standard deviation from column {header_text} is: {std_str}")
    except Exception as e:
        QtTextBrowser.append(f"Error occurred: {str(e)}")

def calculate_mean(QtTextBrowser, QtTableView): #git
    try:
        for column in selected_columns:
            # Oblicz średnią z wybranej kolumny
            mean = (df[column].mean())

            # Konwertuj wartość na string
            mean_str = str(mean)

            # Pobierz tekst nagłówka kolumny z QTableView
            header_text = QtTableView.model().headerData(column, Qt.Orientation.Horizontal)

            # Wyświetl wartość w QTextBrowser
            QtTextBrowser.append(f"Mean from column {header_text} is: {mean_str}")
    except Exception as e:
        QtTextBrowser.append(f"Error occurred: {str(e)}")

def calculate_coorelation(comboBoxAtrybut1, comboBoxAtrybut2,PyQtTextBrowser,tableView):
    model = tableView.model()
    # pobierz indeks wybranej kolumny z comboBoxAtrybut1
    column1_index = comboBoxAtrybut1.currentIndex() + 1
    # pobierz indeks wybranej kolumny z comboBoxAtrybut2
    column2_index = comboBoxAtrybut2.currentIndex() + 1
    # pobierz dane z wybranej kolumny 1
    column1_data = [model.data(model.index(row, column1_index)) for row in range(model.rowCount())]
    # pobierz dane z wybranej kolumny 2
    column2_data = [model.data(model.index(row, column2_index)) for row in range(model.rowCount())]
    # utwórz nowy obiekt DataFrame z pobranych danych
    data = pd.DataFrame(
        {comboBoxAtrybut1.currentText(): column1_data, comboBoxAtrybut2.currentText(): column2_data})
    data = data.apply(pd.to_numeric)
    correlation_matrix = data[[comboBoxAtrybut1.currentText(), comboBoxAtrybut2.currentText()]].corr()
    correlation_coefficient = correlation_matrix.iloc[0, 1]
    PyQtTextBrowser.append("Koorelacja między tymi atrybutami wynosi: " + str(correlation_coefficient))


def calculate_checked_stats(checkBoxMin,checkBoxMax,checkBoxStd,checkBoxMdn,checkBoxMean,textBrowser,tableView):
    if (checkBoxMin.isChecked() == True):
        calculate_minimum(textBrowser,tableView)
    if (checkBoxMax.isChecked() == True):
        calculate_maximum(textBrowser,tableView)
    if (checkBoxStd.isChecked() == True):
        calculate_std(textBrowser,tableView)
    if (checkBoxMdn.isChecked() == True):
        calculate_median(textBrowser,tableView)
    if (checkBoxMean.isChecked() == True):
        calculate_mean(textBrowser,tableView)

# funkcje generowania wykresów:

def generate_comparison_plot(tableView): #git
    model = tableView.model()

    data = pd.DataFrame()  # Utwórz pusty obiekt DataFrame

    for column_index in selected_columns:
        # Pobierz nazwę wybranej kolumny z QTableView
        column_name = model.headerData(column_index, Qt.Orientation.Horizontal)

        # Pobierz dane z wybranej kolumny
        column_data = [model.data(model.index(row, column_index)) for row in range(model.rowCount())]

        # Dodaj dane do obiektu DataFrame
        data[column_name] = column_data

    # Konwertuj dane na typ numeryczny
    data = data.apply(pd.to_numeric, errors='coerce')
    counts = data.apply(pd.Series.value_counts).fillna(0)
    counts.plot(kind='bar')

    plt.xlabel('Atrybut')
    plt.ylabel('Suma')

    # Skonstruuj tytuł wykresu na podstawie nazw zaznaczonych atrybutów
    title = "Zliczenia "
    for column_name in data.columns:
        title += str(column_name) + " + "

    title = title[:-3]  # Usuń ostatni znak "+" i spacje

    plt.title(title)

    plt.show()

def generate_correlation_heatmap(tableView): #git
    model = tableView.model()

    data = pd.DataFrame()  # Utwórz pusty obiekt DataFrame

    for column_index in selected_columns:
        # Pobierz nazwę wybranej kolumny z QTableView
        column_name = model.headerData(column_index, Qt.Orientation.Horizontal)

        # Pobierz dane z wybranej kolumny
        column_data = [model.data(model.index(row, column_index)) for row in range(model.rowCount())]

        # Dodaj dane do obiektu DataFrame
        data[column_name] = column_data

    # Konwertuj dane na typ numeryczny
    data = data.apply(pd.to_numeric, errors='coerce')

    # Oblicz macierz korelacji
    corr_matrix = data.corr()

    # Wygeneruj heatmapę korelacji
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
    plt.title('Heatmap - Korelacja')
    plt.show()



def generate_distribution_plot(tableView): #git
    model = tableView.model()

    data = pd.DataFrame()  # Utwórz pusty obiekt DataFrame

    for column_index in selected_columns:
        # Pobierz nazwę wybranej kolumny z QTableView
        column_name = model.headerData(column_index, Qt.Orientation.Horizontal)

        # Pobierz dane z wybranej kolumny
        column_data = [model.data(model.index(row, column_index)) for row in range(model.rowCount())]

        # Dodaj dane do obiektu DataFrame
        data[column_name] = column_data

    # Konwertuj dane na typ numeryczny
    data = data.apply(pd.to_numeric , errors='coerce')

    # Sumuj wartości dla każdej kolumny
    counts = data.sum()

    # Wygeneruj wykres kołowy
    plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
    plt.axis('equal')

    # Skonstruuj tytuł wykresu na podstawie nazw zaznaczonych atrybutów
    title = "Rozkład "
    for column_name in data.columns:
        title += str(column_name) + " + "

    title = title[:-3]  # Usuń ostatni znak "+" i spacje

    plt.title(title)

    plt.show()


##########################

## Obsługiwanie paska menu:
def load_CSV_file(comboBoxAtrybut1, comboBoxAtrybut2, comboBoxAtrybutClass, tableView):
    global df
    global df_with_labels
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Wczytywanie pliku CSV")
    msg_box.setText("Czy chcesz wczytać plik z nazwami kolumn?")

    yes_button = msg_box.addButton(QMessageBox.StandardButton.Yes)
    yes_button.setText("Tak, z nazwami")
    msg_box.addButton(QMessageBox.StandardButton.No).setText("Nie, bez nazw")
    cn_button = msg_box.addButton(QMessageBox.StandardButton.Cancel)
    cn_button.setVisible(False)

    msg_box.setDefaultButton(yes_button)

    reply = msg_box.exec()

    if reply == 16384:
        header = 0
    elif reply == 65536:
        header = None
    else:
        return

    current_dir = os.getcwd()
    filename, _ = QFileDialog.getOpenFileName(None, "Wybierz plik CSV lub DATA", current_dir,
                                              "All files (*);;Pliki CSV (*.csv);;Pliki DATA (*.data)")
    if not filename:
        # Wyjście z funkcji, jeśli nie został wybrany plik
        return

    # Wczytaj dane z pliku CSV do obiektu DataFrame z biblioteki Pandas
    df = pd.read_csv(filename, header=header)
    df_with_labels = df.copy()
    # Wyświetl dane za pomocą funkcji print

    model = QStandardItemModel(df.shape[0], df.shape[1])
    headers = list(df.columns)
    if reply == 16384:
        model.setHorizontalHeaderLabels(headers)

    for row in range(df.shape[0]):
        for column in range(df.shape[1]):
            item = QStandardItem(str(df.iloc[row, column]))
            model.setItem(row, column, item)

    tableView.setModel(model)

    # wczytywanie nazw kolumn do comboboxów
    column_names = df.columns.tolist()[1:]
    comboBoxAtrybut1.clear()
    comboBoxAtrybut2.clear()
    comboBoxAtrybutClass.clear()
    comboBoxAtrybut1.addItems([str(x) for x in column_names])
    comboBoxAtrybut2.addItems([str(x) for x in column_names])
    comboBoxAtrybutClass.addItems([str(x) for x in column_names])

    # Liczba kolumn minus 1
    x = len(df.columns) - 1

    # Ustawienie nazw kolumn na liczby od 0 do x
    df.columns = list(range(x + 1))

    tableView.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
    selection_model = tableView.selectionModel()
    selection_model.selectionChanged.connect(lambda:handle_selection_changed(tableView))


def save_to_CSV():

    # Okno dialogowe z pytaniem o zapisanie z nazwami kolumn lub bez
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Zapisywanie pliku CSV")
    msg_box.setText("Czy chcesz zapisać plik z nazwami kolumn?")

    yes_button = msg_box.addButton(QMessageBox.StandardButton.Yes)
    yes_button.setText("Tak")
    msg_box.addButton(QMessageBox.StandardButton.No).setText("Nie")
    cn_button = msg_box.addButton(QMessageBox.StandardButton.Cancel)
    cn_button.setVisible(False)

    msg_box.setDefaultButton(yes_button)

    reply = msg_box.exec()

    if reply == 16384:
        header = True
    elif reply == 65536:
        header = False
    else:
        return

    current_dir = os.getcwd()
    filename, _ = QFileDialog.getSaveFileName(None, "Zapisz plik CSV", current_dir, "Pliki CSV (*.csv)")

    if filename:
        df_with_labels.to_csv(filename, index=False, header=header)

import pandas as pd
from PyQt6 import QtCore

def retrieveData(tableView):
    global df, df_with_labels, labels
    model = tableView.model()
    rows = model.rowCount()
    cols = model.columnCount()

    data = []
    for row in range(rows):
        row_data = []
        for col in range(cols):
            index = model.index(row, col)
            value = model.data(index, QtCore.Qt.ItemDataRole.DisplayRole)
            if(is_text_or_number(value)==False):
                value = int(value)
            row_data.append(value)
        data.append(row_data)

    df = pd.DataFrame(data)
    df_with_labels = pd.DataFrame(data)
    df_with_labels.columns = labels

    # Przypisanie odpowiednich typów danych
    # df = df.astype(int, errors='ignore')  # Przypisanie typu int, pomijając błędy
    # df_with_labels['column_name'] = df_with_labels['column_name'].astype(str)  # Przypisanie typu str dla konkretnej kolumny

    print(df.dtypes)
    print(df_with_labels.dtypes)


def add_headers_manually(comboBoxAtrybut1, comboBoxAtrybut2, comboBoxAtrybutClass, tableView):
    global df
    global df_with_labels
    global labels
    for i in df.columns:
        dialog = QDialog()
        dialog.setWindowTitle("Nazwa nagłówka " + str(i))

        dialog.header_field = QLineEdit()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        anuluj_button = QPushButton("Anuluj")
        anuluj_button.clicked.connect(dialog.reject)  # Przerwanie dialogu po kliknięciu przycisku "Anuluj"
        anuluj_button.setVisible(False)
        layout = QVBoxLayout()
        layout.addWidget(dialog.header_field)
        layout.addWidget(ok_button)
        layout.addWidget(anuluj_button)
        dialog.setLayout(layout)

        if dialog.exec() == 1:
            label = dialog.header_field.text()
            labels.append(label)
        else:
            return 0
    model = QStandardItemModel(df.shape[0], df.shape[1])
    model.setHorizontalHeaderLabels(labels)

    for row in range(df.shape[0]):
        for column in range(df.shape[1]):
            item = QStandardItem(str(df.iloc[row, column]))
            model.setItem(row, column, item)

    tableView.setModel(model)

    df_with_labels.columns = labels

    # wczytywanie nazw kolumn do comboboxów
    comboBoxAtrybut1.clear()
    comboBoxAtrybut2.clear()
    comboBoxAtrybutClass.clear()
    comboBoxAtrybut1.addItems([str(x) for x in labels])
    comboBoxAtrybut2.addItems([str(x) for x in labels])
    comboBoxAtrybutClass.addItems([str(x)for x in labels])

def generate_pdf(QtTextBrowser):
    # Wyświetl okno dialogowe do wyboru miejsca zapisu pliku
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle("Save PDF")
    file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    file_dialog.setNameFilter("PDF Files (*.pdf)")
    file_dialog.setDefaultSuffix("pdf")

    if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
        file_path = file_dialog.selectedFiles()[0]
    else:
        return  # Użytkownik anulował wybór pliku

    if file_path:
        # Pobierz tekst z QTextBrowser
        text = QtTextBrowser.toPlainText()

        # Utwórz nowy obiekt Canvas
        c = canvas.Canvas(file_path)

        # Ustaw czcionkę i rozmiar tekstu
        c.setFont("Helvetica", 12)

        # Wypisz tekst w pliku PDF
        lines = text.split("\n")
        y = 800  # Wysokość początkowa
        for line in lines:
            c.drawString(50, y, line)
            y -= 20  # Zmniejsz wysokość dla kolejnej linii

        # Zamknij plik PDF
        c.save()


## Sekcja wyświetlania informacji:
# wyświetlanie informacji o przyciskach:
def switch_dictionary_buttons(button_name): #git
    switcher = {
        "pushButtonMinimum": "Calculates the minimum of selected columns data",
        "pushButtonMaximum": "Calculates the maximum of selected columns data",
        "pushButtonStd": "Calculates the standard deviation of selected columns data",
        "pushButtonMedian": "Calculates the median of selected columns data",
        "pushButtonMean": "Calculates the arithmetic average of selected columns data",
        "pushButtonClear": "Clears the result window",
        "pushButtonCalcChecked": "Designates selected descriptive statistics",
        "pushButtonKoorelacja": "Calculates the correlation of selected attributes and generates a correlation heatmap",
        "pushButtonPorownaj": "Generates a comparison plot of selected columns data",
        "pushButtonDystrybucja": "Generates a distribution plot of selected columns data",
        "pushButtonHeatmap": "Generates a coorelation Heatmap of selected columns data",
        "pushButtonClass": "Provides classification of selected attribute for selected data"

    }
    return switcher.get(button_name, "No information available for the button")


def on_button_enter(event: QEnterEvent, button_name: str, QtTextBrowser): #git
    info = switch_dictionary_buttons(button_name)
    QtTextBrowser.setText(info)
    QtTextBrowser.setAlignment(Qt.AlignmentFlag.AlignCenter)


# wyświetlanie informacji o danej kolumnie

def switch_dictionary(column_name): #git
    switcher = {
        "animal name": "The name of the animal",
        "hair": "Whether the animal has hair or not",
        "feathers": "Whether the animal has feathers or not",
        "eggs": "Whether the animal lays eggs or not",
        "milk": "Whether the animal produces milk or not",
        "airborne": "Whether the animal can fly or not",
        "aquatic": "Whether the animal lives in water or not",
        "predator": "Whether the animal is a predator or not",
        "toothed": "Whether the animal has teeth or not",
        "backbone": "Whether the animal has a backbone or not",
        "breathes": "Whether the animal breathes air or not",
        "venomous": "Whether the animal is venomous or not",
        "fins": "Whether the animal has fins or not",
        "legs": "Number of legs that the animal has",
        "tail": "Whether the animal has a tail or not",
        "domestic": "Whether the animal is domesticated or not",
        "catsize": "Whether the animal is cat-sized or not",
        "type": "Type of animal (mammal, bird, reptile, etc.)"
    }
    return switcher.get(column_name, "No info about Column")


def display_column_info(index,table_view,textBrowserInfo): #git
    column_name = table_view.model().headerData(index.column(), Qt.Orientation.Horizontal)
    textBrowserInfo.setText(switch_dictionary(column_name))
    textBrowserInfo.setAlignment(Qt.AlignmentFlag.AlignCenter)


# obsługa zaznaczania rzeczy w tabeli
def handle_selection_changed(QtTableView):
    global selected_columns
    global selected_rows
    selected_indexes = QtTableView.selectionModel().selectedIndexes()
    selected_columns.clear()
    selected_rows.clear()

    # Sprawdź, czy liczba kolumn się zmieniła
    model = QtTableView.model()
    if model.columnCount() != len(selected_columns):
        # Zresetuj listę selected_columns
        selected_columns = set()

    for index in selected_indexes:
        selected_columns.add(index.column())
        selected_rows.add(index.row())

## Sekcja styli

#
def change_to_darkmode(window,table_view,textBrowserInfo):
    window.setStyleSheet("""
            background-color: #262626;
            color: white;
            font-family: Titillium;
            font-size: 14px;

        }
            """)
    table_view.setStyleSheet("""
            background-color: #262626;
            color: white;
            font-family: Titillium;
            font-size: 18px;

        }
            """)
    table_view.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #262626; color: white; }")
    table_view.verticalHeader().setStyleSheet("QHeaderView::section { background-color: #262626; color: white; }")


def change_to_lightmode(window,table_view):
    window.setStyleSheet("")
    # hor_header = CustomHeaderView3(QtCore.Qt.Orientation.Horizontal)
    # ver_header = CustomHeaderView4(QtCore.Qt.Orientation.Vertical)
    # table_view.setHorizontalHeader(hor_header)
    # table_view.setVerticalHeader(ver_header)
    table_view.horizontalHeader().setVisible(True)
    table_view.verticalHeader().setVisible(True)
    table_view.setStyleSheet("""
            background-color: #fffff;
            color: black;
            font-family: Titillium;
            font-size: 18px;

        }
            """)

    table_view.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #fffff; color: black; }")
    table_view.verticalHeader().setStyleSheet("QHeaderView::section { background-color: #fffff; color: black; }")

