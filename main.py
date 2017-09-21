from flask import Flask, render_template, request
app = Flask(__name__)
import random

@app.route('/')
def all_dice():
    rolls_d4 = []
    rolls_d6 = []
    rolls_d8 = []
    rolls_d10 = []
    rolls_d20 = []
    list_rolls = []
    result = 0
    return render_template('./mult_dice.html', **locals())

@app.route('/<sides>')
def arb_sides(sides):
    roll = random.randint(1, int(sides))
    return render_template('./dice.html', **locals())

@app.route("/roll_all/", methods=['POST'])
def roll_all():
    num_rolls = []
    num_rolls += [request.form.get('d4_rolls')]
    num_rolls += [request.form.get('d6_rolls')]
    num_rolls += [request.form.get('d8_rolls')]
    num_rolls += [request.form.get('d10_rolls')]
    num_rolls += [request.form.get('d20_rolls')]
    mods = []
    mods += [request.form.get('d4_mod')]
    mods += [request.form.get('d6_mod')]
    mods += [request.form.get('d8_mod')]
    mods += [request.form.get('d10_mod')]
    mods += [request.form.get('d20_mod')]
    for i in range(0,5):
        ''' Error checking of number of rolls:
        If any of the rolls weren't filled out, don't roll them.'''
        if num_rolls[i] == '':
            num_rolls[i] = 0
    for j in range(0,5):
        ''' Error checking of modifiers:
        If any weren't filled out, don't add anything. '''
        if mods[j] == '':
            mods[j] = 0
    result = 0
    row_tots = []
    for x in range(0,5):
        if x == 0:
            ''' D4 '''
            rolls_d4 = []
            d4_tot = 0
            for y in range(0, int(num_rolls[x])):
                curr_roll = random.randint(1,4)
                rolls_d4 += [curr_roll]
                d4_tot += curr_roll
            d4_tot += int(mods[0])
            row_tots += [d4_tot]
        elif x == 1:
            ''' D6 '''
            rolls_d6 = []
            d6_tot = 0
            for z in range(0, int(num_rolls[x])):
                curr_roll = random.randint(1,6)
                rolls_d6 += [curr_roll]
                d6_tot += curr_roll
            d6_tot += int(mods[1])
            row_tots += [d6_tot]
        elif x == 2:
            ''' D8 '''
            rolls_d8 = []
            d8_tot = 0
            for c in range(0, int(num_rolls[x])):
                curr_roll = random.randint(1,8)
                rolls_d8 += [curr_roll]
                d8_tot += curr_roll
            d8_tot += int(mods[2])
            row_tots += [d8_tot]
        elif x == 3:
            ''' D10 '''
            rolls_d10 = []
            d10_tot = 0
            for n in range(0, int(num_rolls[x])):
                curr_roll = random.randint(1,10)
                rolls_d10 += [curr_roll]
                d10_tot += curr_roll
            d10_tot += int(mods[3])
            row_tots += [d10_tot]
        else:
            ''' D20 '''
            rolls_d20 = []
            d20_tot = 0
            for m in range(0, int(num_rolls[x])):
                curr_roll = random.randint(1,20)
                rolls_d20 += [curr_roll]
                d20_tot += curr_roll
            d20_tot += int(mods[4])
            row_tots += [d20_tot]
    ''' Cumulative Total '''
    for k in range(0, len(row_tots)):
        result += row_tots[k]
    for l in range(0, len(mods)):
        if l == 0:
            if int(mods[0]) > 0:
                mod_d4 = str('+'+ str(mods[0]))
            else:
		mod_d4 = str(mods[0])
        elif l == 1:
            if int(mods[1]) > 0:
                mod_d6 = str('+'+ str(mods[1]))
            else:
		mod_d6 = str(mods[1])
        elif l == 2:
            if int(mods[2]) > 0:
                mod_d8 = str('+' + str(mods[2]))
            else:
		mod_d8 = str(mods[2])
        elif l == 3:
            if int(mods[3]) > 0:
                mod_d10 = str('+' + str(mods[3]))
            else:
		mod_d10 = str(mods[3])
        else:
            if int(mods[4]) > 0:
                mod_d20 = str('+' + str(mods[4]))
            else:
		mod_d20 = str(mods[4])

    return render_template('./mult_dice.html', **locals())

@app.route("/mkchar")
def mkchar():
    return render_template('./mkchar.html', **locals())
