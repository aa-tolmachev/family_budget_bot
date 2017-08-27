
#лист типов трат
def list_expense_types():
    list_expense_types = ['еда' , 'дом' , 'счета и услуги'
                        ,'транспорт' , 'долги' ,'личные расходы'
                        ,'сбережения' ,'другие'
                        ]

    keyboard_expense = []
    row_keyboard = []
    row_num = 0

    for i in list_expense_types:
        row_num += 1
        row_keyboard.append(i)
        if row_num > 2:
            keyboard_expense.append(row_keyboard)
            row_keyboard = []
            row_num = 0
        elif i == list_expense_types[-1]:
            keyboard_expense.append(row_keyboard)

    return keyboard_expense
