# All the imports .....
from flask import Flask, render_template, request, session, abort, redirect, Response, url_for, g, flash
import random
import os
import sqlite3

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'dndusers.db'),
    SECRET_KEY='secret',
    USERNAME='admin',
    PASSWORD='pwd'
))
app.config.from_envvar('DNDROLLER_SETTINGS', silent=True)

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database')

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Route for basic homepage, subject to change
@app.route('/')
def index():
    return render_template('./home.html', **locals())

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Logged in successfully')
            return redirect(url_for('user_list'))
    return render_template('login.html', **locals())

# Zzzzzzz
@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect("/")

@app.route('/user_list')
def user_list():
    db = get_db()
    cur = db.execute('select * from user_database')
    entries = cur.fetchall()
    return render_template('user_list.html', **locals())

@app.route('/register', methods=['POST'])
def register():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into user_database (username, password) values (?, ?)',
            [request.form['username'], request.form['password']])
    db.commit()
    flash('New user was successfully registered')
    return redirect(url_for('user_list'))

# Hey! Actual working code! Default home page with all information filled in as blanks, showing you how the information is formatted.
@app.route('/roll')
def all_dice():
    rolls_d4 = []    # Lists of accumulated rolls for all the different dice 
    rolls_d6 = []
    rolls_d8 = []
    rolls_d10 = []
    rolls_d20 = []
    rolls_dx = []
    mod_d4 = 0    # All the modifiers, + or -, that are added to the total of that dice's rolls, not each individual roll 
    mod_d6 = 0
    mod_d8 = 0
    mod_d10 = 0
    mod_d20 = 0
    mod_dx = 0
    d4_tot = 0    # Accumulated totals of each row from the lists above, mostly just for the result calculation 
    d6_tot = 0
    d8_tot = 0
    d10_tot = 0
    d20_tot = 0
    dx_tot = 0
    result = 0    # Final result that appears at the bottom right of the table 
    return render_template('./mult_dice.html', **locals())

# Main method that does the most amount of work on the site. Takes in all of the inputs and modifiers from all of the different dice available and calculates the total amount rolled for each row and total. 
@app.route("/roll_all/", methods=['POST'])
def roll_all():
    # Initializing a list to store the number of times to roll each individual die, using a GET request to pull this information from the inputs. 
    num_rolls = []
    num_rolls += [request.form.get('d4_rolls')]
    num_rolls += [request.form.get('d6_rolls')]
    num_rolls += [request.form.get('d8_rolls')]
    num_rolls += [request.form.get('d10_rolls')]
    num_rolls += [request.form.get('d20_rolls')]
    num_rolls += [request.form.get('dx_rolls')]
    # Initializing a list to store the modifiers that are added or subtracted to the totals of each row using a GET request, not to each individual roll. 
    mods = [] 
    mods += [request.form.get('d4_mod')]
    mods += [request.form.get('d6_mod')]
    mods += [request.form.get('d8_mod')]
    mods += [request.form.get('d10_mod')]
    mods += [request.form.get('d20_mod')]
    mods += [request.form.get('dx_mod')]
    for i in range(0,6):
        # Error checking of number of rolls:
        # If any of the rolls weren't filled out, don't roll them. This avoids TypeErrors with trying to add empty strings to integers. 
        if num_rolls[i] == '':
            num_rolls[i] = 0
    for j in range(0,6):
        # Error checking of modifiers:
        # If any modifiers weren't filled out, don't add anything. This avoids TypeErrors with trying to add empty strings to integers. 
        if mods[j] == '':
            mods[j] = 0
    result = 0    # Initialize final result as 0, just in case nothing is filled out. 
    row_tots = []   # Initialize list to hold the row totals, which will be added together at the end to the final result. 
    for x in range(0,6):
        # Since the dice chosen on this page are fixed and not in order, this is needed to be able to loop through the list of the number of rolls of each die and the modifiers for each die. e.g. [d4_rolls, d6_rolls, d8_rolls, d10_rolls, d20_rolls, dx_rolls], and [d4_mod, d6_mod, d8_mod, d10_mod, d20_mod, dx_mod] 
        if x == 0:
            # D4 
            rolls_d4 = []
            d4_tot = 0
            for y in range(0, int(num_rolls[x])):
                # Loop through rolling the die the amount of times specified by d4_rolls. 
                curr_roll = random.randint(1,4)    # Save current roll to variable so the number is the same when called multiple times. 
                rolls_d4 += [curr_roll]    # Add current roll to the list of rolls for this die. 
                d4_tot += curr_roll    # Add current roll to the row total. 
            d4_tot += int(mods[0])    # Once done with rolls for this die, add d4_mod to total. 
            row_tots += [d4_tot]    # Add the total for the row into the list of all row totals. 
        elif x == 1:
            # D6 
            rolls_d6 = []
            d6_tot = 0
            for z in range(0, int(num_rolls[x])):
                # Same as if case, but for d6. 
                curr_roll = random.randint(1,6)
                rolls_d6 += [curr_roll]
                d6_tot += curr_roll
            d6_tot += int(mods[1])
            row_tots += [d6_tot]
        elif x == 2:
            # D8 
            rolls_d8 = []
            d8_tot = 0
            for c in range(0, int(num_rolls[x])):
                # Same as if case, but for d8. 
                curr_roll = random.randint(1,8)
                rolls_d8 += [curr_roll]
                d8_tot += curr_roll
            d8_tot += int(mods[2])
            row_tots += [d8_tot]
        elif x == 3:
            # D10 
            rolls_d10 = []
            d10_tot = 0
            for n in range(0, int(num_rolls[x])):
                # Same as if case, but for d10. 
                curr_roll = random.randint(1,10)
                rolls_d10 += [curr_roll]
                d10_tot += curr_roll
            d10_tot += int(mods[3])
            row_tots += [d10_tot]
        elif x == 4:
            # D20 
            rolls_d20 = []
            d20_tot = 0
            for m in range(0, int(num_rolls[x])):
                # Same as if case, but for d20. 
                curr_roll = random.randint(1,20)
                rolls_d20 += [curr_roll]
                d20_tot += curr_roll
            d20_tot += int(mods[4])
            row_tots += [d20_tot]
        else:
            # DX
            rolls_dx = []
            dx_tot = 0
            to_roll = request.form.get('DX')
            for p in range(0, int(num_rolls[x])):
                # Same as if case, but for dx. 
                curr_roll = random.randint(1, int(to_roll))
                rolls_dx += [curr_roll]
                dx_tot += curr_roll
            dx_tot += int(mods[5])
            row_tots += [dx_tot]

    # Cumulative Total 
    for k in range(0, len(row_tots)):
        # Loop through the list of row totals, adding them all to the cumulative total. 
        result += row_tots[k]

    # Add a '+' to all positive modifiers, just for aesthetic purposes.
    if int(mods[0]) > 0:
        mod_d4 = '+' + str(mods[0])
    else:
        mod_d4 = str(mods[0])
    if int(mods[1]) > 0:
        mod_d6 = '+' + str(mods[1])
    else:
        mod_d6 = str(mods[1])
    if int(mods[2]) > 0:
        mod_d8 = '+' + str(mods[2])
    else:
        mod_d8 = str(mods[2])
    if int(mods[3]) > 0:
        mod_d10 = '+' + str(mods[3])
    else:
        mod_d10 = str(mods[3])
    if int(mods[4]) > 0:
        mod_d20 = '+' + str(mods[4])
    else:
        mod_d20 = str(mods[4])
    if int(mods[5]) > 0:
        mod_dx = '+' + str(mods[5])
    else:
        mod_dx = str(mods[5])

    # Add the last action done to the end of the list of rolls you had, For aesthetic purposes only
    # E.g. If you rolled 5 d6's, '5xd6' would be added to the list
    if int(num_rolls[0]) > 0:
        rolls_d4 += [str(num_rolls[0]) + 'xD4']
    if int(num_rolls[1]) > 0:
        rolls_d6 += [str(num_rolls[1]) + 'xD6']
    if int(num_rolls[2]) > 0:
        rolls_d8 += [str(num_rolls[2]) + 'xD8']
    if int(num_rolls[3]) > 0:
        rolls_d10 += [str(num_rolls[3]) + 'xD10']
    if int(num_rolls[4]) > 0:
        rolls_d20 += [str(num_rolls[4]) + 'xD20']
    if int(num_rolls[5]) > 0:
        rolls_dx += [str(num_rolls[5]) + 'xD' + str(to_roll)]

    return render_template('./mult_dice.html', **locals())

@app.route("/mkchar")
#@login_required
# Route to basic character design sheet creation, not fully implemented until user system up and running so users are able to save their characters to a database for future viewing/editing/deleting/etc. 
def mkchar():
    return render_template('./mkchar.html', **locals())

@app.route("/roll_str/", methods=['POST'])
def roll_str():
    str_att = request.form.get('char_str')
    str_roll = random.randint(1,20)
    if int(str_att) == 1:
        str_roll -= 5
    elif int(str_att) == 2 or int(str_att) == 3:
        str_roll -= 4
    elif int(str_att) == 4 or int(str_att) == 5:
        str_roll -= 3
    elif int(str_att) == 6 or int(str_att) == 7:
        str_roll -= 2
    elif int(str_att) == 8 or int(str_att) == 9:
        str_roll -= 1
    elif int(str_att) == 10 or int(str_att) == 11:
        str_roll = str_roll
    elif int(str_att) == 12 or int(str_att) == 13:
        str_roll += 1
    elif int(str_att) == 14 or int(str_att) == 15:
        str_roll += 2
    elif int(str_att) == 16 or int(str_att) == 17:
        str_roll += 3
    elif int(str_att) == 18 or int(str_att) == 19:
        str_roll += 4
    elif int(str_att) == 20 or int(str_att) == 21:
        str_roll += 5
    elif int(str_att) == 22 or int(str_att) == 23:
        str_roll += 6
    elif int(str_att) == 24 or int(str_att) == 25:
        str_roll += 7
    elif int(str_att) == 26 or int(str_att) == 27:
        str_roll += 8
    elif int(str_att) == 28 or int(str_att) == 29:
        str_roll += 9
    elif int(str_att) == 30:
        str_roll += 10
    return render_template("./mkchar.html", **locals())
