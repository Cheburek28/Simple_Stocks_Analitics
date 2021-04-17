import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime


# Класс компания, принимает значение тикера компании и страны регистрации
# Доступные методы:
#     Get_Multiplicators принимает массив имен необходимых мультипликаторов(Мультипликатор -
#         это коэффициент пропорциональности, который измеряет, насколько эндогенная переменная
#         изменяется в ответ на изменение некоторой экзогенной переменной.), исходя из определения не трудно понять, \
#         что мультипликатор - некое отношение => в его названии обязательно должен содержаться "/".
#         Возвращает словарь в котором ключи - значения мультипликаторов, а значения - значания
#     Get_Company_Stocks_Grafic принимает на вход дату - массив из двух дат в секундах от 1970 года
#         (значения стоит преобразовывать через библиотеку datetime)
#         Сохраниет график в текущую директорию с название тикер.png
#     Compare_Grafic_Of_To_Companies принимает на вход дату и другой объект класса company, строит график
#         цен обоих компаний на одном поле.
# Скрытые методы:
#     _Get_multiplicator_of_Russian_Comp
#     _Get_multiplicator_of_Abroad_Comp
#     Обе функции парсят мультипликторы, просто с различных сайтов
class Company:
    def __init__(self, tiker, country):
        self.__tiker = tiker
        self.__country = country


    def Get_Multiplicators(self, names):
        if self.__country == "Russia" or self.__country == "Rus" or self.__country == "Россия":
            return self._Get_multiplicator_of_Russian_Comp(names)
        else:
            return self._Get_multiplicator_of_Abroad_Comp(names)


    def _Get_multiplicator_of_Russian_Comp(self, names):
        Multiplicator_HTML = requests.get('https://smart-lab.ru/q/{0}/f/y/MSFO'.format(self.__tiker))
        Multiplicators_Dict = {}
        text = Multiplicator_HTML.text
        for i in range(len(names)):

            div = names[i].split("/")
            if text.find(div[0] + " / " + div[1]) > 0:
                Multiplicator_Value = text[text.find(div[0] + " / " + div[1]):]
            elif text.find(div[0] + "/" + div[1]) > 0:
                Multiplicator_Value = text[text.find(div[0] + "/" + div[1]):]
            else:
                Multiplicators_Dict.update({names[i]: "There is no such multiplicator"})
                continue
            Multiplicator_Value = Multiplicator_Value[str(Multiplicator_Value).find("ltm_spc"):]
            Multiplicator_Value = Multiplicator_Value[str(Multiplicator_Value).find("<td>") + 4:]
            Multiplicator_Value = str(Multiplicator_Value[:str(Multiplicator_Value).find("</td>")]).split()
            Value = ""
            for j in range(len(Multiplicator_Value)):
                Value = Value + Multiplicator_Value[j]
            Multiplicators_Dict.update({names[i]: Value})
        return Multiplicators_Dict



    def _Get_multiplicator_of_Abroad_Comp(self, names):
        Multiplicator_HTML = requests.get('https://finbull.ru/stock/{0}/'.format(self.__tiker))
        Multiplicators_Dict = {}
        text = Multiplicator_HTML.text
        for i in range(len(names)):
            div = names[i].split("/")
            if text.find(div[0] + " / " + div[1]) > 0:
                Multiplicator_Value = text[text.find(div[0] + " / " + div[1]):]
            elif text.find(div[0] + "/" + div[1]) > 0:
                Multiplicator_Value = text[text.find(div[0] + "/" + div[1]):]
            else:
                Multiplicators_Dict.update({names[i]: "There is no such multiplicator"})
                continue
            Multiplicator_Value = Multiplicator_Value[Multiplicator_Value.find("<td"):]
            Multiplicator_Value = Multiplicator_Value[Multiplicator_Value.find(">") + 1:Multiplicator_Value.find("</")].split()
            Value = ""
            for j in range(len(Multiplicator_Value)):
                Value = Value + Multiplicator_Value[j]
            Multiplicators_Dict.update({names[i]: Value})

        return Multiplicators_Dict

    def Get_Company_Stocks_Grafic(self, date, Grafic_or_Arrays):
        STOСKS_JSON = requests.get('https://api.bcs.ru/udfdatafeed/v1/history?symbol={0}&resolution=D&from={1}&to={2}'.format(self.__tiker, date[0],date[1]))
        Stoсks_Dict = json.loads(STOСKS_JSON.text)
        if Stoсks_Dict.get("errmsg") is None:
            Time_Array = Stoсks_Dict.get("t")
            Price_Array = Stoсks_Dict.get("c")
        else:
            print("There is no such tiker or date period")
            return [0], [0]
        if Grafic_or_Arrays == "Grafic":
            fig = plt.figure(figsize=(20, 9))
            # for i in range(len(Time_Array)):
            #     Time_Array[i] = datetime.utcfromtimestamp(Time_Array[i]).strftime('%Y-%m-%d %H:%M:%S')
            plt.plot(Time_Array, Price_Array, color="coral")
            plt.show()
            fig.savefig(self.__tiker)
        elif Grafic_or_Arrays == "Arrays":
            return Time_Array, Price_Array
        else:
            print("This function can take only two values of Grafic_or_Arrays: Grafic or Arrays")
            return

    def Compare_Grafic_Of_To_Companies(self, other, date):
        selfTime_Array, selfPrice_Array = self.Get_Company_Stocks_Grafic(date, "Arrays");
        otherTime_Array, otherPrice_Array = other.Get_Company_Stocks_Grafic(date, "Arrays");
        fig = plt.figure(figsize=(20, 9))
        # for i in range(len(self.Time_Array)):
        #     self.Time_Array[i] = datetime.utcfromtimestamp(self.Time_Array[i]).strftime('%Y-%m-%d %H:%M:%S')
        # for i in range(len(other.Time_Array)):
        #     other.Time_Array[i] = datetime.utcfromtimestamp(other.Time_Array[i]).strftime('%Y-%m-%d %H:%M:%S')
        plt.plot(selfTime_Array, selfPrice_Array, color="coral")
        plt.plot(otherTime_Array, otherPrice_Array, color="blue")
        plt.show()
        fig.savefig(self.__tiker + "_" + other.__tiker)



date = ["1600000000", "1618317179"]

tiker1 = "FIVE"
tiker2 = "T"

names = ["P/E","P/S","EV/EBITDA", "HUI/432"]

Comp1 = Company(tiker1, "Russia")
Comp2 = Company(tiker2, "USA")

Comp1.Get_Company_Stocks_Grafic(date, "Grafic")
Comp2.Get_Company_Stocks_Grafic(date, "Grafic")

# Пока что это песпонтово, тк хз, как сравнивать,
# если у одних график в баксах, а у другиз в рублях
Comp1.Compare_Grafic_Of_To_Companies(Comp2, date)
print(tiker1 + "   "  + str(Comp1.Get_Multiplicators(names)))
print(tiker2 + "   "  + str(Comp2.Get_Multiplicators(names)))


