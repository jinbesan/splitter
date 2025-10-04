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
    
    def add_transaction(self, name, payer, amount, beneficiaries, type="equal", shares=None, exact=None):
        name = name if name else "Unnamed Transaction"
        today = datetime.now()
        transaction = {
            "name": name,
            "payer": payer,
            "beneficiaries": beneficiaries,
            "amount": amount,
            "type": type,
            "shares": shares,
            "exact": exact,
            "date": today.strftime("%d/%m/%y")
        }
        
        
        self._update_balances(transaction)
        transaction["print"] = self.print_transaction(transaction)
        self.transactions.appendleft(transaction)
        self.save()
        return
    
    def _update_balances(self, transaction):
        # Positive: Receive money, Negative: Owe money
        if (transaction['type'] == "equal"):
            receive = transaction['amount']
            owe = receive / len(transaction['beneficiaries'])

            for i in range(len(self.people)):
                person = self.people[i]
                if (person['name'] == transaction['payer']):
                    self.people[i]['balance'] += receive
                if (person['name'] in transaction['beneficiaries']):
                    self.people[i]['balance'] -= owe

        elif (transaction['type'] == "shares"):
            shares = transaction['shares']
            total_shares = sum(float(v) for v in shares.values())
            receive = transaction['amount']
            owe_pershare = receive / total_shares

            for i in range(len(self.people)):
                person = self.people[i]
                if (person['name'] == transaction['payer']):
                    self.people[i]['balance'] += receive
                if (person['name'] in transaction['beneficiaries']):
                    self.people[i]['balance'] -= owe_pershare * shares[person['name']]

        elif (transaction['type'] == "exact"):
            exacts = transaction['exact']
            receive = sum(float(v) for v in exacts.values())
            transaction['amount'] = receive

            for i in range(len(self.people)):
                person = self.people[i]
                if (person['name'] == transaction['payer']):
                    self.people[i]['balance'] += receive
                if (person['name'] in transaction['beneficiaries']):
                    self.people[i]['balance'] -= exacts[person['name']]
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
        print(beneficiaries)
        print(transaction)
        statement = f"{transaction['date']} | {transaction['name']}: {transaction['payer']} paid ${transaction['amount']:.2f} "
        if (transaction["type"] == "equal"):
            if not beneficiaries:
                b = ""
            elif len(beneficiaries) == 1:
                b = beneficiaries[0]
            elif len(beneficiaries) == 2:
                b = f"{beneficiaries[0]} and {beneficiaries[1]}"
            else:
                b = ", ".join(beneficiaries[:-1]) + f" and {beneficiaries[-1]}"
            statement = statement + f"for {b}"

        elif (transaction['type'] == "shares"):
            amount = transaction['amount']
            shares = transaction['shares']
            total_shares = sum(float(v) for v in shares.values())
            shares_statement = ", ".join(f"{beneficiary}: ${(amount/total_shares) * shares[beneficiary]:.2f}, {shares[beneficiary]:.1f} shares" for beneficiary in beneficiaries)
            statement = statement + shares_statement

        elif (transaction['type'] == "exact"):
            exact_statement = ", ".join(f"{beneficiary}: ${transaction['exact'][beneficiary]:.2f}" for beneficiary in beneficiaries)
            statement = statement + exact_statement

        return statement