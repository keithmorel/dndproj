# All the imports .....
from flask import Flask, render_template, request, session, abort, redirect, Response, url_for, g, flash
import random
import os
import sqlite3

app = Flask(__name__)
app.config.from_object(__name__)

# Configures the database name, secret key, and the admin username and password to be used to sign in.
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'dndusers.db'),
    SECRET_KEY='secret',
    USERNAME='admin',
    PASSWORD='pwd'
))
app.config.from_envvar('DNDROLLER_SETTINGS', silent=True)

# Connects to the sqlite database using the config settings above
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

# Creates a reference to the database
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# Clears out the database.
# If you change the .sql file, MAKE SURE TO CLICK ON THIS BUTTON OR IT WILL NOT WORK
@app.route('/init_db/')
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.execute('insert into user_list (username, password) values (?, ?)', [app.config['USERNAME'], app.config['PASSWORD']])
    db.commit()
    logout()
    return render_template('home.html')

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Route for basic homepage, subject to change
@app.route('/')
def index():
    return render_template('./home.html', **locals())

# Basic login page route that lets you login using the admin account info, locaed near the top of this file
@app.route("/login", methods=["GET", "POST"])
def login():
    # If the user is trying to log in
    if request.method == 'POST':
        user_name = request.form['username']
        pass_word = request.form['password']
        db = get_db()
        cur = db.execute('select * from user_list where username = ?', [user_name])
        db_user = cur.fetchone()
        # Check if the user exists
        if db_user == None:
            flash('That user does not exist. Try registering this username and password instead.')
            return redirect(url_for('login'))
        # Grab username and password from the database SELECT query
        for user in db_user:
            db_user_name = db_user[1]
            db_pass_word = db_user[2]
        # Check the username and password given against the username and password from the database
        if str(user_name) != str(db_user_name):
            flash('Invalid username')
        elif str(pass_word) != str(db_pass_word):
            flash('Invalid password')
        else:
            # If it all checks out, log them in
            flash('Successfully logged in')
            session['logged_in'] = True
            session['username'] = db_user_name
            return redirect('char_list')
    # If its a GET request, get all the users from the database that you can log in as
    db = get_db()
    cur = db.execute('select * from user_list')
    users = cur.fetchall()
    return render_template('login.html', **locals())

# Route for registering a new user to the database
@app.route("/register", methods=["GET", "POST"])
def register():
    # If clicking register button
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select * from user_list where username = ?', [request.form['username']])
        user = cur.fetchall()
        # Checking if user already exists
        if user != []:
            flash('User already exists. Try logging in with info instead')
            return redirect(url_for('login'))
        # If not, insert into database, login, and redirect to character list page
        cur = db.execute('insert into user_list (username, password) values (?, ?)', [request.form['username'], request.form['password']])
        db.commit()
        flash('Successfully registered')
        session['logged_in'] = True
        session['username'] = request.form['username']
        cur = db.execute('select * from char_sheets')
        entries = cur.fetchall()
        return redirect('char_list')
    return render_template('login.html', **locals())

# Logs out the current user
@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect("/")

# Route for the page that displays all of the current characters in the database
@app.route('/char_list')
def char_list():
    db = get_db()
    cur = db.execute('select * from char_sheets where author = ?', [session['username']])
    entries = cur.fetchall()
    return render_template('char_list.html', **locals())

# Route that adds all of the info from the form into the database
@app.route('/create', methods=['POST'])
def create():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    # Check if character already exists
    if cur.fetchall() != []:
        flash('Character with that name already exists. Try another one')
        return redirect('char_list')
    # If they don't exist, create them
    db.execute('insert into char_sheets (author, char_name, char_class, char_lvl, alignment, curr_health, max_health, char_armor, char_str, char_dex, char_const, char_intel, char_wisdom, char_charisma, char_perception, char_weapons, char_inv, char_skills, char_notes) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [session['username'], request.form['char_name'], request.form['char_class'], request.form['char_lvl'], request.form['alignment'], request.form['curr_health'], request.form['max_health'], request.form['char_armor'], request.form['char_str'], request.form['char_dex'], request.form['char_const'], request.form['char_intel'], request.form['char_wisdom'], request.form['char_charisma'], request.form['char_perception'], request.form['char_weapons'], request.form['char_inv'], request.form['char_skills'], request.form['char_notes']])
    db.commit()
    return redirect(url_for('char_list'))

# Route that deletes the character from the database, *** LOOK INTO MAKING A CONFIRM CHOICE POPUP BEFORE DELETING ***
@app.route('/delete_char/', methods=['POST'])
def delete_char():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from char_sheets where char_name = ? and author = ?', [request.form['to_delete'], session['username']])
    db.commit()
    return redirect(url_for('char_list'))

# Route to a page that brings up another character creation screen, but with all of the information filled out for the current character filled out for you
@app.route('/update_char', methods=['POST'])
def update_char():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['to_update'], session['username']])
    entry = cur.fetchall()
    return render_template('char_update.html', **locals())

# Route that actually does the "updating" of the character, it really just deletes and re-inserts character. Will not delete character if some information isn't filled out. 
# *** LOOK INTO GETTING THE UPDATE QUERY TO WORK SO IT DOESNT MOVE UPDATED CHARACTER TO BOTTOM OF LIST ***
@app.route('/char_update/', methods=['POST'])
def update():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('update char_sheets set char_class = ?, char_lvl = ?, alignment = ?, curr_health = ?, max_health = ?, char_armor = ?, char_str = ?, char_dex = ?, char_const = ?, char_intel = ?, char_wisdom = ?, char_charisma = ?, char_perception = ?, char_weapons = ?, char_inv = ?, char_skills = ?, char_notes = ? where char_name = ? and author = ?', [request.form['char_class'], request.form['char_lvl'], request.form['alignment'], request.form['curr_health'], request.form['max_health'], request.form['char_armor'], request.form['char_str'], request.form['char_dex'], request.form['char_const'], request.form['char_intel'], request.form['char_wisdom'], request.form['char_charisma'], request.form['char_perception'], request.form['char_weapons'], request.form['char_inv'], request.form['char_skills'], request.form['char_notes'], request.form['char_name'], session['username']])
    db.commit()
    return redirect(url_for('char_list'))

# Route to the page that just displays all of the character info and allows certain actions to take place
@app.route('/view_char', methods=['POST'])
def view_char():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['to_view'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Route to page that gives more information on all of the alignments
@app.route('/alignment_details')
def alignment_details():
    return render_template('./alignment_details.html')

# Default home page with all information filled in as blanks, showing you how the information is formatted.
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

@app.route("/level_up/", methods=['POST'])
def level_up():
    curr_lvl = int(request.form['char_lvl'])
    curr_lvl += 1
    db = get_db()
    db.execute('update char_sheets set char_lvl = ? where char_name = ? and author = ?', [curr_lvl, request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

@app.route("/update_weapons/", methods=['POST'])
def update_weapons():
    curr_weapons = request.form['char_weapons']
    db = get_db()
    db.execute('update char_sheets set char_weapons = ? where char_name = ? and author = ?', [curr_weapons, request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

@app.route("/update_inv/", methods=['POST'])
def update_inv():
    curr_inv = request.form['char_inv']
    db = get_db()
    db.execute('update char_sheets set char_inv = ? where char_name = ? and author = ?', [curr_inv, request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

@app.route("/update_notes/", methods=['POST'])
def update_notes():
    curr_notes = request.form['char_notes']
    db = get_db()
    db.execute('update char_sheets set char_notes = ? where char_name = ? and author = ?', [curr_notes, request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

@app.route("/update_hp/", methods=['POST'])
def update_hp():
    db = get_db()
    db.execute('update char_sheets set curr_health = ?, max_health = ? where char_name = ? and author = ?', [request.form['curr_health'], request.form['max_health'], request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

# Route that rolls strength based on current strength level, adding the modifier accordingly
@app.route("/roll_str/", methods=['POST'])
def roll_str():
    str_att = request.form['str_val']
    str_roll = random.randint(1,20)
    init_str_roll = str_roll
    if int(str_att) == 1:
        str_roll -= 5
        mod_str = "-5"
    elif int(str_att) == 2 or int(str_att) == 3:
        str_roll -= 4
        mod_str = "-4"
    elif int(str_att) == 4 or int(str_att) == 5:
        str_roll -= 3
        mod_str = "-3"
    elif int(str_att) == 6 or int(str_att) == 7:
        str_roll -= 2
        mod_str = "-2"
    elif int(str_att) == 8 or int(str_att) == 9:
        str_roll -= 1
        mod_str = "-1"
    elif int(str_att) == 10 or int(str_att) == 11:
        mod_str = "+0"
    elif int(str_att) == 12 or int(str_att) == 13:
        str_roll += 1
        mod_str = "+1"
    elif int(str_att) == 14 or int(str_att) == 15:
        str_roll += 2
        mod_str = "+2"
    elif int(str_att) == 16 or int(str_att) == 17:
        str_roll += 3
        mod_str = "+3"
    elif int(str_att) == 18 or int(str_att) == 19:
        str_roll += 4
        mod_str = "+4"
    elif int(str_att) == 20 or int(str_att) == 21:
        str_roll += 5
        mod_str = "+5"
    elif int(str_att) == 22 or int(str_att) == 23:
        str_roll += 6
        mod_str = "+6"
    elif int(str_att) == 24 or int(str_att) == 25:
        str_roll += 7
        mod_str = "+7"
    elif int(str_att) == 26 or int(str_att) == 27:
        str_roll += 8
        mod_str = "+8"
    elif int(str_att) == 28 or int(str_att) == 29:
        str_roll += 9
        mod_str = "+9"
    elif int(str_att) == 30:
        str_roll += 10
        mod_str = "+10"
    # Must grab the character from the database again or else the view character page won't be filled out.
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Route that rolls dexterity based on current strength level, adding the modifier accordingly
@app.route("/roll_dex/", methods=['POST'])
def roll_dex():
    dex_att = request.form['dex_val']
    dex_roll = random.randint(1,20)
    init_dex_roll = dex_roll
    if int(dex_att) == 1:
        dex_roll -= 5
        mod_dex = "-5"
    elif int(dex_att) == 2 or int(dex_att) == 3:
        dex_roll -= 4
        mod_dex = "-4"
    elif int(dex_att) == 4 or int(dex_att) == 5:
        dex_roll -= 3
        mod_dex = "-3"
    elif int(dex_att) == 6 or int(dex_att) == 7:
        dex_roll -= 2
        mod_dex = "-2"
    elif int(dex_att) == 8 or int(dex_att) == 9:
        dex_roll -= 1
        mod_dex = "-1"
    elif int(dex_att) == 10 or int(dex_att) == 11:
        mod_dex = "+0"
    elif int(dex_att) == 12 or int(dex_att) == 13:
        dex_roll += 1
        mod_dex = "+1"
    elif int(dex_att) == 14 or int(dex_att) == 15:
        dex_roll += 2
        mod_dex = "+2"
    elif int(dex_att) == 16 or int(dex_att) == 17:
        dex_roll += 3
        mod_dex = "+3"
    elif int(dex_att) == 18 or int(dex_att) == 19:
        dex_roll += 4
        mod_dex = "+4"
    elif int(dex_att) == 20 or int(dex_att) == 21:
        dex_roll += 5
        mod_dex = "+5"
    elif int(dex_att) == 22 or int(dex_att) == 23:
        dex_roll += 6
        mod_dex = "+6"
    elif int(dex_att) == 24 or int(dex_att) == 25:
        dex_roll += 7
        mod_dex = "+7"
    elif int(dex_att) == 26 or int(dex_att) == 27:
        dex_roll += 8
        mod_dex = "+8"
    elif int(dex_att) == 28 or int(dex_att) == 29:
        dex_roll += 9
        mod_dex = "+9"
    elif int(dex_att) == 30:
        dex_roll += 10
        mod_dex = "+10"
    # Must grab the character from the database again or else the view character page won't be filled out.
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Route that rolls constitution based on current strength level, adding the modifier accordingly
@app.route("/roll_const/", methods=['POST'])
def roll_const():
    const_att = request.form['const_val']
    const_roll = random.randint(1,20)
    init_const_roll = const_roll
    if int(const_att) == 1:
        const_roll -= 5
        mod_const = "-5"
    elif int(const_att) == 2 or int(const_att) == 3:
        const_roll -= 4
        mod_const = "-4"
    elif int(const_att) == 4 or int(const_att) == 5:
        const_roll -= 3
        mod_const = "-3"
    elif int(const_att) == 6 or int(const_att) == 7:
        const_roll -= 2
        mod_const = "-2"
    elif int(const_att) == 8 or int(const_att) == 9:
        const_roll -= 1
        mod_const = "-1"
    elif int(const_att) == 10 or int(const_att) == 11:
        mod_const = "+0"
    elif int(const_att) == 12 or int(const_att) == 13:
        const_roll += 1
        mod_const = "+1"
    elif int(const_att) == 14 or int(const_att) == 15:
        const_roll += 2
        mod_const = "+2"
    elif int(const_att) == 16 or int(const_att) == 17:
        const_roll += 3
        mod_const = "+3"
    elif int(const_att) == 18 or int(const_att) == 19:
        const_roll += 4
        mod_const = "+4"
    elif int(const_att) == 20 or int(const_att) == 21:
        const_roll += 5
        mod_const = "+5"
    elif int(const_att) == 22 or int(const_att) == 23:
        const_roll += 6
        mod_const = "+6"
    elif int(const_att) == 24 or int(const_att) == 25:
        const_roll += 7
        mod_const = "+7"
    elif int(const_att) == 26 or int(const_att) == 27:
        const_roll += 8
        mod_const = "+8"
    elif int(const_att) == 28 or int(const_att) == 29:
        const_roll += 9
        mod_const = "+9"
    elif int(const_att) == 30:
        const_roll += 10
        mod_const = "+10"
    # Must grab the character from the database again or else the view character page won't be filled out.
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Route that rolls intelligence based on current strength level, adding the modifier accordingly
@app.route("/roll_intel/", methods=['POST'])
def roll_intel():
    intel_att = request.form['intel_val']
    intel_roll = random.randint(1,20)
    init_intel_roll = intel_roll
    if int(intel_att) == 1:
        intel_roll -= 5
        mod_intel = "-5"
    elif int(intel_att) == 2 or int(intel_att) == 3:
        intel_roll -= 4
        mod_intel = "-4"
    elif int(intel_att) == 4 or int(intel_att) == 5:
        intel_roll -= 3
        mod_intel = "-3"
    elif int(intel_att) == 6 or int(intel_att) == 7:
        intel_roll -= 2
        mod_intel = "-2"
    elif int(intel_att) == 8 or int(intel_att) == 9:
        intel_roll -= 1
        mod_intel = "-1"
    elif int(intel_att) == 10 or int(intel_att) == 11:
        mod_intel = "+0"
    elif int(intel_att) == 12 or int(intel_att) == 13:
        intel_roll += 1
        mod_intel = "+1"
    elif int(intel_att) == 14 or int(intel_att) == 15:
        intel_roll += 2
        mod_intel = "+2"
    elif int(intel_att) == 16 or int(intel_att) == 17:
        intel_roll += 3
        mod_intel = "+3"
    elif int(intel_att) == 18 or int(intel_att) == 19:
        intel_roll += 4
        mod_intel = "+4"
    elif int(intel_att) == 20 or int(intel_att) == 21:
        intel_roll += 5
        mod_intel = "+5"
    elif int(intel_att) == 22 or int(intel_att) == 23:
        intel_roll += 6
        mod_intel = "+6"
    elif int(intel_att) == 24 or int(intel_att) == 25:
        intel_roll += 7
        mod_intel = "+7"
    elif int(intel_att) == 26 or int(intel_att) == 27:
        intel_roll += 8
        mod_intel = "+8"
    elif int(intel_att) == 28 or int(intel_att) == 29:
        intel_roll += 9
        mod_intel = "+9"
    elif int(intel_att) == 30:
        intel_roll += 10
        mod_intel = "+10"
    # Must grab the character from the database again or else the view character page won't be filled out.
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Route that rolls wisdom based on current strength level, adding the modifier accordingly
@app.route("/roll_wisdom/", methods=['POST'])
def roll_wisdom():
    wisdom_att = request.form['wisdom_val']
    wisdom_roll = random.randint(1,20)
    init_wisdom_roll = wisdom_roll
    if int(wisdom_att) == 1:
        wisdom_roll -= 5
        mod_wisdom = "-5"
    elif int(wisdom_att) == 2 or int(wisdom_att) == 3:
        wisdom_roll -= 4
        mod_wisdom = "-4"
    elif int(wisdom_att) == 4 or int(wisdom_att) == 5:
        wisdom_roll -= 3
        mod_wisdom = "-3"
    elif int(wisdom_att) == 6 or int(wisdom_att) == 7:
        wisdom_roll -= 2
        mod_wisdom = "-2"
    elif int(wisdom_att) == 8 or int(wisdom_att) == 9:
        wisdom_roll -= 1
        mod_wisdom = "-1"
    elif int(wisdom_att) == 10 or int(wisdom_att) == 11:
        mod_wisdom = "+0"
    elif int(wisdom_att) == 12 or int(wisdom_att) == 13:
        wisdom_roll += 1
        mod_wisdom = "+1"
    elif int(wisdom_att) == 14 or int(wisdom_att) == 15:
        wisdom_roll += 2
        mod_wisdom = "+2"
    elif int(wisdom_att) == 16 or int(wisdom_att) == 17:
        wisdom_roll += 3
        mod_wisdom = "+3"
    elif int(wisdom_att) == 18 or int(wisdom_att) == 19:
        wisdom_roll += 4
        mod_wisdom = "+4"
    elif int(wisdom_att) == 20 or int(wisdom_att) == 21:
        wisdom_roll += 5
        mod_wisdom = "+5"
    elif int(wisdom_att) == 22 or int(wisdom_att) == 23:
        wisdom_roll += 6
        mod_wisdom = "+6"
    elif int(wisdom_att) == 24 or int(wisdom_att) == 25:
        wisdom_roll += 7
        mod_wisdom = "+7"
    elif int(wisdom_att) == 26 or int(wisdom_att) == 27:
        wisdom_roll += 8
        mod_wisdom = "+8"
    elif int(wisdom_att) == 28 or int(wisdom_att) == 29:
        wisdom_roll += 9
        mod_wisdom = "+9"
    elif int(wisdom_att) == 30:
        wisdom_roll += 10
        mod_wisdom = "+10"
    # Must grab the character from the database again or else the view character page won't be filled out.
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Route that rolls charisma  based on current strength level, adding the modifier accordingly
@app.route("/roll_charisma/", methods=['POST'])
def roll_charisma():
    charisma_att = request.form['charisma_val']
    charisma_roll = random.randint(1,20)
    init_charisma_roll = charisma_roll
    if int(charisma_att) == 1:
        charisma_roll -= 5
        mod_charisma = "-5"
    elif int(charisma_att) == 2 or int(charisma_att) == 3:
        charisma_roll -= 4
        mod_charisma = "-4"
    elif int(charisma_att) == 4 or int(charisma_att) == 5:
        charisma_roll -= 3
        mod_charisma = "-3"
    elif int(charisma_att) == 6 or int(charisma_att) == 7:
        charisma_roll -= 2
        mod_charisma = "-2"
    elif int(charisma_att) == 8 or int(charisma_att) == 9:
        charisma_roll -= 1
        mod_charisma = "-1"
    elif int(charisma_att) == 10 or int(charisma_att) == 11:
        mod_charisma = "+0"
    elif int(charisma_att) == 12 or int(charisma_att) == 13:
        charisma_roll += 1
        mod_charisma = "+1"
    elif int(charisma_att) == 14 or int(charisma_att) == 15:
        charisma_roll += 2
        mod_charisma = "+2"
    elif int(charisma_att) == 16 or int(charisma_att) == 17:
        charisma_roll += 3
        mod_charisma = "+3"
    elif int(charisma_att) == 18 or int(charisma_att) == 19:
        charisma_roll += 4
        mod_charisma = "+4"
    elif int(charisma_att) == 20 or int(charisma_att) == 21:
        charisma_roll += 5
        mod_charisma = "+5"
    elif int(charisma_att) == 22 or int(charisma_att) == 23:
        charisma_roll += 6
        mod_charisma = "+6"
    elif int(charisma_att) == 24 or int(charisma_att) == 25:
        charisma_roll += 7
        mod_charisma = "+7"
    elif int(charisma_att) == 26 or int(charisma_att) == 27:
        charisma_roll += 8
        mod_charisma = "+8"
    elif int(charisma_att) == 28 or int(charisma_att) == 29:
        charisma_roll += 9
        mod_charisma = "+9"
    elif int(charisma_att) == 30:
        charisma_roll += 10
        mod_charisma = "+10"
    # Must grab the character from the database again or else the view character page won't be filled out.
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Runs the server in debug mode when file is run with "python3 main.py"
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
