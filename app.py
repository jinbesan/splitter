from flask import Flask, render_template, request, redirect, url_for
import json, os
import split

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "split.json")

splitter = split.Split(DATA_FILE)

@app.route("/")
def index():
    people = splitter.get_people()
    transactions = splitter.get_transactions()
    settlements = splitter.settle_debts()

    return render_template("index.html", 
                           people=people,
                           transactions=transactions,
                           settlements=settlements
                           )

@app.route("/add-transaction", methods=["POST"])
def add_transaction():
    payer = request.form.get("payer")
    amount = request.form.get("amount")
    beneficiaries = request.form.getlist("beneficiaries")
    name = request.form.get("name")

    if payer and amount and beneficiaries:
        splitter.add_transaction(name, payer, float(amount), beneficiaries)
    

    return redirect(url_for("index"))

@app.route("/add-person", methods=["POST"])
def add_person():
    name = request.form.get("name")
    splitter.add_person(name)
    return redirect(url_for("index"))

@app.route("/settle/<debtor>2<creditor>", methods=["POST"])
def settle(debtor, creditor):
    settlements = splitter.settle_debts()
    settlement = [s for s in settlements if s['creditor'] == creditor and s['debtor'] == debtor][0]
    splitter.add_transaction("Debt Settlement", debtor, settlement['payment'], [creditor])
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)