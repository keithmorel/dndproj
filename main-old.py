from flask import Flask, render_template, request
app = Flask(__name__)
import random

@app.route('/')
def all_dice():
    d4 = 0
    d6 = 0
    d8 = 0
    d10 = 0
    d20 = 0
    return render_template('./mult_dice.html', **locals())

@app.route('/<sides>')
def arb_sides(sides):
    roll = random.randint(1, int(sides))
    return render_template('./dice.html', **locals())

@app.route("/d4/", methods=['POST'])
def rolld4():
    rolls = request.form.get('rolls')
    if rolls == '' or int(rolls) <= 0:
        d4 = random.randint(1,4)
    else:
        d4 = 0
        list_rolls = []
        for i in range(0,int(rolls)):
            curr_roll = random.randint(1,4)
            list_rolls += [curr_roll]
            d4 += curr_roll
    d6 = 0
    d8 = 0
    d10 = 0
    d20 = 0
    return render_template('./mult_dice.html', **locals())
@app.route("/d6/", methods=['POST'])
def rolld6():
    d4 = 0
    rolls = request.form.get('rolls')
    if rolls == '' or int(rolls) <= 0:
        d6 = random.randint(1,6)
    else:
        d6 = random.randint(1,6)*int(rolls)
    d8 = 0
    d10 = 0
    d20 = 0
    return render_template('./mult_dice.html', **locals())
@app.route("/d8/", methods=['POST'])
def rolld8():
    d4 = 0
    d6 = 0
    rolls = request.form.get('rolls')
    if rolls == '' or int(rolls) <= 0:
        d8 = random.randint(1,8)
    else:
        d8 = ramdom.randint(1,8)*int(rolls)
    d10 = 0
    d20 = 0
    return render_template('./mult_dice.html', **locals())
@app.route("/d10/", methods=['POST'])
def rolld10():
    d4 = 0
    d6 = 0
    d8 = 0
    rolls = request.form.get('rolls')
    if rolls == '' or int(rolls) <= 0:
        d10 = random.randint(1,10)
    else:
        d10 = random.randint(1,10)*int(rolls)
    d20 = 0
    return render_template('./mult_dice.html', **locals())
@app.route("/d20/", methods=['POST'])
def rolld20():
    d4 = 0
    d6 = 0
    d8 = 0
    d10 = 0
    rolls = request.form.get('rolls')
    if rolls == '' or int(rolls) <= 0:
        d20 = ranfom.randint(1,20)
    else:
        d20 = random.randint(1,20)*int(rolls)
    return render_template('./mult_dice.html', **locals())

@app.route("/mkchar")
def mkchar():
    return render_template('./mkchar.html', **locals())
