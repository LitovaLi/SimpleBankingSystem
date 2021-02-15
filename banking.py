import random
import sqlite3
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

class Account():
    IIN = "400000"
    def __init__(self):
        self.card_number = self.new_card_number()
        self.card_pin = str(random.randint(1111, 9999))

    def new_card_number(self):
        customer_account_number = random.randint(111111111, 999999999)
        account = Account.IIN + str(customer_account_number)
        check_sum = 0
        for i in range(15):
            if i % 2 == 0:
                n = int(account[i]) * 2
                check_sum += n if n < 10 else (n - 9)
            else:
                check_sum += int(account[i])
        check_digit = (10 - (check_sum % 10))  if (check_sum % 10) != 0 else 0
        return account + str(check_digit)

def create_db():
    cur.execute("""CREATE TABLE IF NOT EXISTS card (
                id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
                )""")
    conn.commit()

def choose_log_action(card):
    while True:
        print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
        cur.execute("SELECT number, pin, balance FROM card WHERE number = :card", {'card': card[0]})
        conn.commit()
        card = cur.fetchone()
        choice = int(input())
        if choice == 1:
            print("\nBalance: ", card[2])
            print()
        elif choice == 2:
            add_income(card)
        elif choice == 3:
            do_transfer(card)
        elif choice == 4:
            close_account(card)
            break
        elif choice == 5:
            print("\nYou have successfully logged out!\n")
            break
        else:
            quit()

def add_income(card):
    print("\nEnter income:")
    income = int(input())
    cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?" , (income, card[0]))
    conn.commit()
    print("Income was added!\n")


def do_transfer(card):
    print("\nTransfer")
    enter_card = input(("Enter card number:\n"))
    check_sum = 0
    for i in range(15):
        if i % 2 == 0:
            n = int(enter_card[i]) * 2
            check_sum += n if n < 10 else (n - 9)
        else:
            check_sum += int(enter_card[i])
    check_digit = (10 - (check_sum % 10)) if (check_sum % 10) != 0 else 0

    cur.execute("SELECT number, balance FROM card WHERE number = :enter_card", {'enter_card': enter_card})
    exist_card = cur.fetchone()

    if enter_card == card[0]:
        print("You can't transfer money to the same account!\n")
    elif int(enter_card) % 10 != check_digit:
        print("Probably you made a mistake in the card number. Please try again!\n")
    elif exist_card is None:
        print("Such a card does not exist.\n")
    else:
        money = int(input("Enter how much money you want to transfer:\n"))
        if money > int(card[2]):
            print("Not enough money!\n")
        else:
            cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?" , (money, exist_card[0]))
            cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?" , (money, card[0]))
            conn.commit()
            print("Success!\n")

def close_account(card):
    cur.execute("DELETE FROM card WHERE number = :card", {'card': card[0]})
    conn.commit()
    print("\nThe account has been closed!\n")

def create_account():
    new_card = Account()
    add_card_to_db(new_card.card_number, new_card.card_pin)
    print("\nYour card number:\n" + new_card.card_number)
    print("Your card PIN:\n" + new_card.card_pin)
    print()

def add_card_to_db(card_number, card_pin):
    cur.execute("INSERT INTO card (number, pin) VALUES (:number, :pin)",
                {'number': card_number, 'pin': card_pin})
    conn.commit()

def log_into_account():
    card = input("\nEnter your card number:\n")
    pin = input("Enter your PIN:\n")
    cur.execute("SELECT number, pin, balance FROM card WHERE number = :card", {'card': card})
    card = cur.fetchone()
    conn.commit()
    if not card:
        print("Wrong card number or PIN!\n")
    elif card[1] == pin:
        print("You have successfully logged in!\n")
        choose_log_action(card)
    else:
        print("Wrong card number or PIN!\n")

cur.execute("DROP TABLE IF EXISTS card")
create_db()
while True:
    print('1. Create an account\n2. Log into account\n0. Exit')
    action = input()
    if action == "1":
        create_account()
    elif action == "2":
        log_into_account()
    elif action == "0":
        break

conn.close()
