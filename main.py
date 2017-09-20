from flask import Flask, render_template
app = Flask(__name__)
import random

@app.route('/')
def home():
    return 'Welcome to my DnD Dice Roller! Add a die to roll after a / to roll! Or to get many dice to roll on one page, add /roll.'

@app.route('/<sides>')
def arb_sides(sides):
    roll = random.randint(1, int(sides))
    return render_template('./dice.html', **locals())

@app.route('/roll')
def all_dice():
    d4 = 0
    d6 = 0
    d8 = 0
    d10 = 0
    d20 = 0
    return render_template('./mult_dice.html', **locals())

@app.route("/d4/", methods=['POST'])
def rolld4():
    d4 = random.randint(1,4)
    d6 = 0
    d8 = 0
    d10 = 0
    d20 = 0
    return render_template('./mult_dice.html', **locals())
@app.route("/d6/", methods=['POST'])
def rolld6():
    d4 = 0
    d6 = random.randint(1,6)
    d8 = 0
    d10 = 0
    d20 = 0
    
    return render_template('./mult_dice.html', **locals())
@app.route("/d8/", methods=['POST'])
def rolld8():
    d4 = 0
    d6 = 0
    d8 = random.randint(1,8)
    d10 = 0
    d20 = 0
    return render_template('./mult_dice.html', **locals())
@app.route("/d10/", methods=['POST'])
def rolld10():
    d4 = 0
    d6 = 0
    d8 = 0
    d10 = random.randint(1,10)
    d20 = 0
    return render_template('./mult_dice.html', **locals())
@app.route("/d20/", methods=['POST'])
def rolld20():
    d4 = 0
    d6 = 0
    d8 = 0
    d10 = 0
    d20 = random.randint(1,20)
    return render_template('./mult_dice.html', **locals())
