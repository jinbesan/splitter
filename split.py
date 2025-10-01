import json, os
from collections import deque
from datetime import datetime

class Split:
    def __init__(self, data_path):
        self.path = data_path
        self.data = self.load_data()
        self.people = self.data["people"]
        self.transactions = deque(self.data["transactions"])

    def load_data(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        data = {
            "people": [],
            "transactions": []
        }

        return data
    
    def _savedata(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
        return
    
    def save(self):
        self._savedata({"people": self.people, "transactions": list(self.transactions)})
        return
    
    def add_person(self, name):
        newperson = {
            "name": name,
            "balance": 0
        }
        self.people.append(newperson)
        self.save()
        return
    
    def add_transaction(self, name, payer, amount, beneficiaries):
        name = name if name else "Unnamed Transaction"
        today = datetime.now()
        transaction = {
            "name": name,
            "payer": payer,
            "beneficiaries": beneficiaries,
            "amount": amount,
            "date": today.strftime("%d/%m/%y")
        }
        transaction["print"] = self.print_transaction(transaction)
        print(transaction)
        self.transactions.appendleft(transaction)
        self._update_balances(transaction)
        self.save()
        return
    
    def _update_balances(self, transaction):
        # Positive: Receive money, Negative: Owe money
        receive = transaction['amount']
        owe = receive / len(transaction['beneficiaries'])

        for i in range(len(self.people)):
            person = self.people[i]
            if (person['name'] == transaction['payer']):
                self.people[i]['balance'] += receive
            if (person['name'] in transaction['beneficiaries']):
                self.people[i]['balance'] -= owe
        return
    
    def get_people(self):
        return self.people

    
    def get_transactions(self):
        return self.transactions
    
    def settle_debts(self):
        creditors = [person.copy() for person in self.people if person['balance'] > 0]
        debtors = [person.copy() for person in self.people if person['balance'] < 0]

        creditors = sorted(creditors, key=lambda d: d['balance'], reverse=True)
        debtors = sorted(debtors, key=lambda d: d['balance'])

        settlements = []

        i, j = 0, 0
        while i < len(creditors) and j < len(debtors):


            payment = min(creditors[i]['balance'], -debtors[j]['balance'])
            creditors[i]['balance'] -= payment
            debtors[j]['balance'] += payment

            settlement = {
                "creditor": creditors[i]['name'],
                "debtor": debtors[j]['name'],
                "payment": payment
            }

            settlements.append(settlement)

            if creditors[i]['balance'] == 0:
                i += 1
            if debtors[j]['balance'] == 0:
                j += 1

        return settlements
    
    def print_transaction(self, transaction):
        beneficiaries = transaction['beneficiaries']

        if not beneficiaries:
            b = ""
        elif len(beneficiaries) == 1:
            b = beneficiaries[0]
        elif len(beneficiaries) == 2:
            b = f"{beneficiaries[0]} and {beneficiaries[1]}"
        else:
            b = ", ".join(beneficiaries[:-1]) + f" and {beneficiaries[-1]}"
        return f"{transaction['date']} | {transaction['name']}: {transaction['payer']} paid {transaction['amount']} for {b}"