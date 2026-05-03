import logging
import math
import os
import random


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            os.path.join("logs", "vector_logs.log"),
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger("vector_logs")


class ArrayVector:
    def __init__(self, n=5, random_fill=False):
        if random_fill:
            self.arr = [random.randint(-10, 9) for _ in range(5)]
            logger.info("Random vector created with size 5")
        else:
            self.arr = [0 for _ in range(n)]
            logger.info(f"Vector created with size {n}")

    def set_element(self, index, value):
        if 0 <= index < len(self.arr):
            self.arr[index] = value
            logger.info(f"Element set: index={index}, value={value}")
        else:
            print("Invalid index")
            logger.warning(f"Invalid index while setting element: {index}")

    def get_element(self, index):
        if 0 <= index < len(self.arr):
            print(f"{index}-й элемент: {self.arr[index]}")
            logger.info(f"Element read: index={index}, value={self.arr[index]}")
        else:
            print("Invalid index")
            logger.warning(f"Invalid index while reading element: {index}")

    def get_norm(self):
        result = 0

        for value in self.arr:
            result += math.pow(value, 2)

        result = math.sqrt(result)
        print(f"Длинна вектора: {result}")
        logger.info(f"Vector norm calculated: {result}")

    def summ_positives_from_chet_index(self):
        result = 0

        for index in range(len(self.arr)):
            if index % 2 != 0 and self.arr[index] > 0:
                result += self.arr[index]

        if result == 0:
            print("Таких чисел нет")
            logger.info("Positive elements with required indexes were not found")
        else:
            print(f"Сумма: {result}")
            logger.info(f"Sum calculated: {result}")

    def summ_less_from_nechet_index(self):
        result = 0
        average = 0

        for value in self.arr:
            average += abs(value)

        average = average / len(self.arr)
        logger.debug(f"Average absolute value calculated: {average}")

        for index in range(len(self.arr)):
            if index % 2 == 0 and self.arr[index] < average:
                result += self.arr[index]

        if result == 0:
            print("Таких чисел нет")
            logger.info("Elements less than average were not found")
        else:
            print(f"Сумма: {result}")
            logger.info(f"Sum of elements less than average calculated: {result}")

    def mult_chet(self):
        result = 1
        count = 0

        for value in self.arr:
            if value % 2 == 0 and value > 0:
                result *= value
                count += 1

        if count == 0:
            print("Таких чисел нет")
            logger.info("Positive even elements were not found")
        else:
            print(f"Произведение: {result}")
            logger.info(f"Product of positive even elements calculated: {result}")

    def mult_nechet(self):
        result = 1
        count = 0

        for index in range(len(self.arr)):
            if index % 2 != 0 and self.arr[index] % 3 != 0:
                result *= self.arr[index]
                count += 1

        if count == 0:
            print("Таких чисел нет")
            logger.info("Elements for multiplication were not found")
        else:
            print(f"Произведение: {result}")
            logger.info(f"Product calculated: {result}")

    def sort_up(self):
        logger.info("Sorting vector in ascending order started")

        print("Вектор до:\n")
        self.info()

        self.arr.sort()

        print("\nВектор после:\n")
        self.info()

        logger.info("Vector sorted in ascending order")

    def sort_down(self):
        logger.info("Sorting vector in descending order started")

        print("Вектор до:\n")
        self.info()

        self.arr.sort(reverse=True)

        print("\nВектор после:\n")
        self.info()

        logger.info("Vector sorted in descending order")

    def info(self):
        print("(" + " ".join(str(value) for value in self.arr) + ")", end="")
        logger.debug(f"Vector displayed: {self.arr}")


class Vectors:
    @staticmethod
    def sum(vector_1, vector_2):
        vector_3 = ArrayVector(len(vector_1.arr))

        if len(vector_1.arr) != len(vector_2.arr):
            print("Размерности векторов разные")
            logger.warning(
                f"Different vector sizes for sum: "
                f"{len(vector_1.arr)} and {len(vector_2.arr)}"
            )
        else:
            for index in range(len(vector_1.arr)):
                vector_3.arr[index] = vector_1.arr[index] + vector_2.arr[index]

            logger.info("Vector sum calculated")

        return vector_3

    @staticmethod
    def scalar(vector_1, vector_2):
        result = 0

        if len(vector_1.arr) != len(vector_2.arr):
            print("Размерности векторов разные")
            logger.warning(
                f"Different vector sizes for scalar product: "
                f"{len(vector_1.arr)} and {len(vector_2.arr)}"
            )
        else:
            for index in range(len(vector_1.arr)):
                result += vector_1.arr[index] * vector_2.arr[index]

            logger.info(f"Scalar product calculated: {result}")

        return result

    @staticmethod
    def number_mult(vector, number):
        logger.info(f"Vector multiplication by number started: number={number}")

        for index in range(len(vector.arr)):
            vector.arr[index] *= number

        logger.info("Vector multiplication by number completed")
        return vector

    @staticmethod
    def get_norm(vector):
        result = 0

        for value in vector.arr:
            result += math.pow(value, 2)

        result = math.sqrt(result)
        logger.info(f"Static vector norm calculated: {result}")

        return result


def read_int(message):
    while True:
        try:
            print(message)
            value = int(input())
            logger.debug(f"User entered integer: {value}")
            return value
        except ValueError:
            print("Введите целое число")
            logger.warning("Invalid integer input")


def main():
    logger.info("Program started")

    print("Лабороторная работа №1(Повторение)")
    print("Выполнил Антоненков Антон 6102_020302D")

    key = False

    while key is False:
        print()
        print("Выберите пункт меню:")
        print("1 - обычные методы")
        print("2 - статические методы")
        print("3 - завершение работы\n")

        menu = input()
        logger.info(f"Main menu selected: {menu}")

        if menu == "1":
            logger.info("User selected common vector methods")

            print("Обычные методы")
            size_1 = read_int("Введите размерность: ")
            vector_1 = ArrayVector(size_1)

            key_1 = False

            while key_1 is False:
                print("\nКоординаты первого вектора: ")
                vector_1.info()
                print()
                print("Выберите пункт меню:")
                print("1 - установка")
                print("2 - чтение")
                print("3 - длина")
                print("4 - сумма_чет")
                print("5 - сумма_нечет")
                print("6 - произведение_чет")
                print("7 - произведение_нечет")
                print("8 - сорт_возр")
                print("9 - сорт_убыв")
                print("10 - завершение работы\n")

                menu_1 = input()
                logger.info(f"Common methods menu selected: {menu_1}")

                if menu_1 == "1":
                    print("Установка")
                    index = read_int("Введите индекс: ")
                    value = read_int("Введите значение: ")
                    vector_1.set_element(index, value)

                elif menu_1 == "2":
                    print("Чтение")
                    index = read_int("Введите индекс: ")
                    vector_1.get_element(index)

                elif menu_1 == "3":
                    print("Длина")
                    vector_1.get_norm()

                elif menu_1 == "4":
                    print("Сумма_чет")
                    vector_1.summ_positives_from_chet_index()

                elif menu_1 == "5":
                    print("Сумма_нечет")
                    vector_1.summ_less_from_nechet_index()

                elif menu_1 == "6":
                    print("Произведение_чет")
                    vector_1.mult_chet()

                elif menu_1 == "7":
                    print("Произведение_нечет")
                    vector_1.mult_nechet()

                elif menu_1 == "8":
                    print("Сорт_возр")
                    vector_1.sort_up()

                elif menu_1 == "9":
                    print("Сорт_убыв")
                    vector_1.sort_down()

                elif menu_1 == "10":
                    print("Завершение повтора меню\n")
                    logger.info("Common methods menu finished")
                    key_1 = True

                else:
                    print("Повторите ввод")
                    logger.warning(f"Unknown common methods menu option: {menu_1}")

        elif menu == "2":
            logger.info("User selected static vector methods")

            print("Статические методы")
            size_1 = read_int("Введите размерность 1ого вектора: ")
            vector_1 = ArrayVector(size_1)

            print("Введите элементы 1ого вектора: ")
            for index in range(len(vector_1.arr)):
                vector_1.arr[index] = int(input())

            logger.info(f"First vector filled: {vector_1.arr}")
            vector_1.info()

            size_2 = read_int("\nВведите размерность 2ого вектора: ")
            vector_2 = ArrayVector(size_2)

            print("Введите элементы 2ого вектора: ")
            for index in range(len(vector_2.arr)):
                vector_2.arr[index] = int(input())

            logger.info(f"Second vector filled: {vector_2.arr}")
            vector_2.info()

            key_2 = False

            while key_2 is False:
                print()
                print("Выберите пункт меню:")
                print("1 - сумма")
                print("2 - скалярное")
                print("3 - умножение на число")
                print("4 - длина")
                print("5 - завершение работы\n")

                menu_2 = input()
                logger.info(f"Static methods menu selected: {menu_2}")

                if menu_2 == "1":
                    print("Cумма")
                    vector_3 = Vectors.sum(vector_1, vector_2)
                    vector_3.info()

                elif menu_2 == "2":
                    print("Cкалярное")
                    print(f"Произведение: {Vectors.scalar(vector_1, vector_2)}")

                elif menu_2 == "3":
                    print("Умножение на число")
                    number = read_int("Введите число: ")
                    print("Выберете вектор:\n1 - первый")
                    print("Любое число - второй")
                    vector_number = int(input())
                    logger.info(
                        f"Vector selected for multiplication: {vector_number}"
                    )

                    if vector_number == 1:
                        vector_3 = Vectors.number_mult(vector_1, number)
                        vector_3.info()
                    else:
                        vector_3 = Vectors.number_mult(vector_2, number)
                        vector_3.info()

                elif menu_2 == "4":
                    print("Длина")
                    print("Выберете вектор:\n1 - первый")
                    print("Любое число - второй")
                    vector_number = int(input())
                    logger.info(f"Vector selected for norm: {vector_number}")

                    if vector_number == 1:
                        print(f"Длина: {Vectors.get_norm(vector_1)}")
                    else:
                        print(f"Длина: {Vectors.get_norm(vector_2)}")

                elif menu_2 == "5":
                    print("Завершение повтора меню\n")
                    logger.info("Static methods menu finished")
                    key_2 = True

                else:
                    print("Повторите ввод")
                    logger.warning(f"Unknown static methods menu option: {menu_2}")

        elif menu == "3":
            print("Завершение повтора меню\n")
            logger.info("Program finished by user")
            key = True

        else:
            print("Повторите ввод")
            logger.warning(f"Unknown main menu option: {menu}")


if __name__ == "__main__":
    main()