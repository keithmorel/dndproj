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
    db.execute('insert into user_list (username, password, is_dm) values (?, ?, ?)', [app.config['USERNAME'], app.config['PASSWORD'], 'True'])
    db.commit()
    logout()
    flash('Reset database')
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
        if db_user is None:
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
            return redirect(url_for('index'))
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
            flash('User already exists')
            return redirect(url_for('login'))
        # If not, insert into database and login
        db.execute('insert into user_list (username, password, is_dm) values (?, ?, ?)', [request.form['username'], request.form['password'], request.form['is_dm']])
        db.commit()
        flash('Successfully registered ' + request.form['username'])
        session['logged_in'] = True
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html', **locals())

# Logs out the current user
@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Logged out')
    return redirect("/")

# Route to display the character creation page
@app.route('/create_char')
def create_char():
    if not session.get('logged_in'):
        flash('You must be logged in to create a character')
        return redirect(request.referrer)
    return render_template('char_create.html', **locals())

# Route for the page that displays all of the current characters in the database
@app.route('/char_list')
def char_list():
    if not session.get('logged_in'):
        flash('You must be logged in to view your characters')
        return redirect(request.referrer)
    db = get_db()
    cur = db.execute('select * from char_sheets where author = ?', [session['username']])
    entries = cur.fetchall()
    return render_template('char_list.html', **locals())

# Route that adds the new character to the database
@app.route('/submit_char/', methods=['POST'])
def submit_char():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    # Check if character already exists
    if cur.fetchall() != []:
        flash('Character with that name already exists. Try another one')
        return redirect('create_char')
    # If they don't exist, create them
    check = char_checker(request.form)
    if check != '':
        flash(check)
        return redirect(url_for('create_char'))
    db.execute('insert into char_sheets (author, char_name, char_race, char_class, char_lvl, char_speed, char_proficiency, alignment, curr_health, max_health, char_armor, char_str, char_dex, char_const, char_intel, char_wisdom, char_charisma, char_perception, char_weap_prim, char_weap_prim_num, char_weap_prim_die, char_weap_sec, char_weap_sec_num, char_weap_sec_die, char_inv, char_skills, char_notes) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [session['username'], request.form['char_name'], request.form['char_race'], request.form['char_class'], request.form['char_lvl'], request.form['char_speed'], request.form['char_proficiency'], request.form['alignment'], request.form['curr_health'], request.form['max_health'], request.form['char_armor'], request.form['char_str'], request.form['char_dex'], request.form['char_const'], request.form['char_intel'], request.form['char_wisdom'], request.form['char_charisma'], request.form['char_perception'], request.form['char_weap_prim'], request.form['char_weap_prim_num'], request.form['char_weap_prim_die'], request.form['char_weap_sec'], request.form['char_weap_sec_num'], request.form['char_weap_sec_die'], request.form['char_inv'], request.form['char_skills'], request.form['char_notes']])
    db.commit()
    flash('Successfully Created ' + str(request.form['char_name']))
    return redirect(url_for('char_list'))

# Route that deletes the character from the database, *** LOOK INTO MAKING A CONFIRM CHOICE POPUP BEFORE DELETING ***
@app.route('/delete_char/', methods=['POST'])
def delete_char():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from char_sheets where char_name = ? and author = ?', [request.form['to_delete'], session['username']])
    db.commit()
    flash('Successfully Deleted ' + str(request.form['to_delete']))
    return redirect('char_list')

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
    check = char_checker(request.form)
    if check != '':
        cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
        entry = cur.fetchall()
        flash(check)
        return render_template('char_update.html', **locals())
    db.execute('update char_sheets set char_race = ?, char_class = ?, char_lvl = ?, char_speed = ?, char_proficiency = ?, alignment = ?, curr_health = ?, max_health = ?, char_armor = ?, char_str = ?, char_dex = ?, char_const = ?, char_intel = ?, char_wisdom = ?, char_charisma = ?, char_perception = ?, char_weap_prim = ?, char_weap_prim_num = ?, char_weap_prim_die = ?, char_weap_sec = ?, char_weap_sec_num = ?, char_weap_sec_die = ?, char_inv = ?, char_skills = ?, char_notes = ? where char_name = ? and author = ?', [request.form['char_race'], request.form['char_class'], request.form['char_lvl'], request.form['char_speed'], request.form['char_proficiency'], request.form['alignment'], request.form['curr_health'], request.form['max_health'], request.form['char_armor'], request.form['char_str'], request.form['char_dex'], request.form['char_const'], request.form['char_intel'], request.form['char_wisdom'], request.form['char_charisma'], request.form['char_perception'], request.form['char_weap_prim'], request.form['char_weap_prim_num'], request.form['char_weap_prim_die'], request.form['char_weap_sec'], request.form['char_weap_sec_num'], request.form['char_weap_sec_die'], request.form['char_inv'], request.form['char_skills'], request.form['char_notes'], request.form['to_update'], session['username']])
    db.commit()
    flash('Successfully Updated ' + str(request.form['to_update']))
    return redirect(url_for('char_list'))

# Route to the page that just displays all of the character info and allows certain actions to take place
@app.route('/view_char', methods=['POST'])
def view_char():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['to_view'], request.form['user']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())

# Route to a page that displays basic info on the game currently being hosted by the user
@app.route('/game_list')
def game_list():
    if not session.get('logged_in'):
        flash('You must be logged in to view your game')
        return redirect(request.referrer)
    db = get_db()
    is_dm = db.execute('select is_dm from user_list where username = ?', [session['username']])
    if is_dm.fetchone()[0] == 'False':
        flash('You must be logged into a DM account to access this page.')
        return redirect(request.referrer)
    cur = db.execute('select * from games where dm_name = ?', [session['username']])
    games = cur.fetchall()
    if games == []:
        no_games = True
    else:
        no_games = False
    cur = db.execute('select * from char_sheets where dm = ?', [session['username']])
    players = cur.fetchall()
    if players == []:
        no_players = True
    else:
        no_players = False
    return render_template('dm_game.html', **locals())

# Allows you to create a game with whatevre name you like
@app.route('/submit_game', methods=['POST'])
def submit_game():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if request.form['game_name'] == '':
        flash('You must give your game a name')
        return redirect('game_list')
    check = db.execute('select * from games where dm_name = ?', [session['username']])
    if check.fetchall() != []:
        flash('You are already hosting a game with this account.')
        return redirect(url_for('game_list'))
    db.execute('insert into games (dm_name, game_name, game_notes) values (?, ?, ?)', [session['username'], request.form['game_name'], request.form['game_notes']])
    db.commit()
    flash('Successfully created ' + request.form['game_name'])
    return redirect(url_for('game_list'))

# Updates the notes of the user's game
@app.route('/update_game/', methods=['POST'])
def update_game():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('update games set game_notes = ? where dm_name = ? and game_name = ?', [request.form['game_notes'], session['username'], request.form['game_name']])
    db.commit()
    flash('Successfully Updated ' + request.form['game_name'])
    return redirect(url_for('game_list'))

# Deletes just the game currently *** REMOVE ALL MONSTERS AS WELL ***
@app.route('/delete_game/', methods=['POST'])
def delete_game():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('update char_sheets set dm = ?, game = ? where dm = ? and game = ?', [None, None, session['username'], request.form['game_name']])
    db.execute('delete from npcs where dm = ?', [session['username']])
    db.execute('delete from games where dm_name = ? and game_name = ?', [session['username'], request.form['game_name']])
    db.commit()
    flash('Successfully deleted ' + request.form['game_name'])
    return redirect(url_for('game_list'))

# Adds a player to the game by adding a reference to the DM in the character sheet
@app.route('/add_player_to_game/', methods=['POST'])
def add_to_game():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    to_add = request.form['char_name']
    player = db.execute('select * from char_sheets where char_name = ? and author = ?', [to_add, request.form['author']])
    if player.fetchall() == []:
        flash('That player does not exist for that user. Try a different user or character name.')
        return redirect(url_for('game_list'))
    db.execute('update char_sheets set dm = ?, game = ? where char_name = ? and author = ?', [session['username'], request.form['game'], to_add, request.form['author']])
    db.commit()
    flash('Successfully added ' + to_add + ' to ' + request.form['game'])
    return redirect(url_for('game_list'))

# Simple route to the page where you are able to see the current list of NPCs and add more
@app.route('/npc_list')
def npc_list():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from npcs where dm = ?', [session['username']])
    npcs = cur.fetchall()
    return render_template('npc_list.html', **locals())

# Adds an NPC with a reference to the DM in its table
@app.route('/create_npc', methods=['POST'])
def create_npc():
    db = get_db()
    check = db.execute('select * from npcs where name = ? and dm = ?', [request.form['name'], session['username']])
    if check.fetchall() != []:
        flash('This NPC already exists in this game.')
        return redirect(url_for('npc_list'))
    db.execute('insert into npcs (name, info, dm) values (?, ?, ?)', [request.form['name'], request.form['info'], session['username']])
    db.commit()
    return redirect(url_for('npc_list'))

# Deletes the NPC from the table
@app.route('/delete_npc/', methods=['POST'])
def delete_npc():
    db = get_db()
    db.execute('delete from npcs where name = ? and dm = ?', [request.form['to_delete'], session['username']])
    db.commit()
    return redirect(url_for('npc_list'))

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

# Main rolling function that takes in all the info filled out on the rolling page and rolls the dice and sets all the variables
@app.route("/roll_all/", methods=['POST'])
def roll_all():
    x = str(request.form['DX'])
    # Each dictionary item has an array with the following info, [number of rolls, modifier, list of rolls, modifier as a string, row total], for each die
    dice_to_roll = {
            '4': [request.form['d4_rolls'], request.form['d4_mod'], [], '', 0],
            '6': [request.form['d6_rolls'], request.form['d6_mod'], [], '', 0],
            '8': [request.form['d8_rolls'], request.form['d8_mod'], [], '', 0],
            '10': [request.form['d10_rolls'], request.form['d10_mod'], [], '', 0],
            '20': [request.form['d20_rolls'], request.form['d20_mod'], [], '', 0],
            x: [request.form['dx_rolls'], request.form['dx_mod'], [], '', 0]
    }
    result = 0
    for key in dice_to_roll:
        # Error checking of rolls and mods
        if dice_to_roll[key][0] == '':
            dice_to_roll[key][0] = 0
        elif dice_to_roll[key][1] == '':
            dice_to_roll[key][1] = 0
        # If you have to roll this die
        elif int(dice_to_roll[key][0]) > 0:
            # Loop through as many times as indicated by the user
            for j in range(0, int(dice_to_roll[key][0])):
                # Roll a die with the number indicated by the current key
                roll = random.randint(1, int(key))
                # Add the roll to the final result
                result += roll
                # Add the roll to the list of rolls for the die
                dice_to_roll[key][2] += [roll]
                # Add the roll to the row total
                dice_to_roll[key][4] += roll
            # Format the mod: if > 0, add a + sign, else just make it a string
            mod = int(dice_to_roll[key][1])
            if mod > 0:
                dice_to_roll[key][3] = '+' + str(mod)
            else:
                dice_to_roll[key][3] = str(mod)
            # Add the mod to the row total
            dice_to_roll[key][4] += mod
    # Instantiate all the variables needed to output onto the HTML
    rolls_d4 = dice_to_roll['4'][2] + [str(dice_to_roll['4'][0]) + 'xD4']
    rolls_d6 = dice_to_roll['6'][2] + [str(dice_to_roll['6'][0]) + 'xD6']
    rolls_d8 = dice_to_roll['8'][2] + [str(dice_to_roll['8'][0]) + 'xD8']
    rolls_d10 = dice_to_roll['10'][2] + [str(dice_to_roll['10'][0]) + 'xD10']
    rolls_d20 = dice_to_roll['20'][2] + [str(dice_to_roll['20'][0]) + 'xD20']
    rolls_dx = dice_to_roll[x][2] + [str(dice_to_roll[x][0]) + 'xD' + x]
    mod_d4 = dice_to_roll['4'][3]
    mod_d6 = dice_to_roll['6'][3]
    mod_d8 = dice_to_roll['8'][3]
    mod_d10 = dice_to_roll['10'][3]
    mod_d20 = dice_to_roll['20'][3]
    mod_dx = dice_to_roll[x][3]
    d4_tot = dice_to_roll['4'][4]
    d6_tot = dice_to_roll['6'][4]
    d8_tot = dice_to_roll['8'][4]
    d10_tot = dice_to_roll['10'][4]
    d20_tot = dice_to_roll['20'][4]
    dx_tot = dice_to_roll[x][4]
    return render_template('mult_dice.html', **locals())

# Updates the char_inv value in the database so the user can comstantly update while playing
@app.route("/update_inv/", methods=['POST'])
def update_inv():
    curr_inv = request.form['char_inv']
    db = get_db()
    db.execute('update char_sheets set char_inv = ? where char_name = ? and author = ?', [curr_inv, request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

# Updates the char_notes value in the database so the user can constantly update them while playing
@app.route("/update_notes/", methods=['POST'])
def update_notes():
    curr_notes = request.form['char_notes']
    db = get_db()
    db.execute('update char_sheets set char_notes = ? where char_name = ? and author = ?', [curr_notes, request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

@app.route("/update_skills/", methods=['POST'])
def update_skills():
    curr_skills = request.form['char_skills']
    db = get_db()
    db.execute('update char_sheets set char_skills = ? where char_name = ? and author = ?', [curr_skills, request.form['char_name'], session['username']])
    db.commit()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

# Rolls a d20 to determine a hit, with a 1 meaning a miss and a 20 a crit, and rolls whatever damage dice are specified by character sheet
@app.route("/roll_attack/", methods=['POST'])
def roll_attack():
    weapon = str(request.form['weapon'])
    attack_roll = random.randint(1, 20)
    if attack_roll == 1:
        if weapon == 'Primary':
            prim_result = 'Miss'
        else:
            sec_result = 'Miss'
        db = get_db()
        entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
        return render_template('view_char.html', **locals())
    num = int(request.form['char_weap_num'])
    die = int(request.form['char_weap_die'])
    total = 0
    for i in range(0, num):
        curr = random.randint(1, die)
        total += curr
    if attack_roll == 20:
        result = 'Crit! You deal ' + str(total * 2) + ' damage!'
    else:
        result = 'You deal ' + str(total) + ' damage!'
    if weapon == 'Primary':
        prim_result = result
    else:
        sec_result = result
    db = get_db()
    entry = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    return render_template('view_char.html', **locals())

# Route that rolls strength based on current strength level, adding the modifier accordingly
@app.route("/roll_att/", methods=['POST'])
def roll_att():
    att = request.form['att_val']
    att_roll = random.randint(1, 20)
    init_att_roll = att_roll
    if int(att) == 1:
        att_roll -= 5
        mod_att = "-5"
    elif int(att) == 2 or int(att) == 3:
        att_roll -= 4
        mod_att = "-4"
    elif int(att) == 4 or int(att) == 5:
        att_roll -= 3
        mod_att = "-3"
    elif int(att) == 6 or int(att) == 7:
        att_roll -= 2
        mod_att = "-2"
    elif int(att) == 8 or int(att) == 9:
        att_roll -= 1
        mod_att = "-1"
    elif int(att) == 10 or int(att) == 11:
        mod_att = "+0"
    elif int(att) == 12 or int(att) == 13:
        att_roll += 1
        mod_att = "+1"
    elif int(att) == 14 or int(att) == 15:
        att_roll += 2
        mod_att = "+2"
    elif int(att) == 16 or int(att) == 17:
        att_roll += 3
        mod_att = "+3"
    elif int(att) == 18 or int(att) == 19:
        att_roll += 4
        mod_att = "+4"
    elif int(att) == 20 or int(att) == 21:
        att_roll += 5
        mod_att = "+5"
    elif int(att) == 22 or int(att) == 23:
        att_roll += 6
        mod_att = "+6"
    elif int(att) == 24 or int(att) == 25:
        att_roll += 7
        mod_att = "+7"
    elif int(att) == 26 or int(att) == 27:
        att_roll += 8
        mod_att = "+8"
    elif int(att) == 28 or int(att) == 29:
        att_roll += 9
        mod_att = "+9"
    elif int(att) == 30:
        att_roll += 10
        mod_att = "+10"
    att_name = str(request.form['att_name'])
    if att_name == 'Strength':
        init_str_roll = init_att_roll
        str_roll = att_roll
        mod_str = mod_att
    if att_name == 'Dexterity':
        init_dex_roll = init_att_roll
        dex_roll = att_roll
        mod_dex = mod_att
    if att_name == 'Constitution':
        init_const_roll = init_att_roll
        const_roll = att_roll
        mod_const = mod_att
    if att_name == 'Intelligence':
        init_intel_roll = init_att_roll
        intel_roll = att_roll
        mod_intel = mod_att
    if att_name == 'Wisdom':
        init_wisdom_roll = init_att_roll
        wisdom_roll = att_roll
        mod_wisdom = mod_att
    if att_name == 'Charisma':
        init_charisma_roll = init_att_roll
        charisma_roll = att_roll
        mod_charisma = mod_att
    # Must grab the character from the database again or else the view character page won't be filled out.
    db = get_db()
    cur = db.execute('select * from char_sheets where char_name = ? and author = ?', [request.form['char_name'], session['username']])
    entry = cur.fetchall()
    return render_template('view_char.html', **locals())


# Function that checks various things about the character sheet to make sure the user isn't cheating with updating their stats.
def char_checker(form):

    db_cols_to_readable = {
            'char_name': 'Character Name',
            'char_race': 'Character Race',
            'char_class': 'Character Class',
            'char_lvl': 'Character Level',
            'char_speed': 'Character Speed',
            'char_proficiency': 'Character Proficiency',
            'alignment': 'Alignment',
            'curr_health': 'Current Health',
            'max_health': 'Max Health',
            'char_armor': 'Character Armor',
            'char_str': 'Strength',
            'char_dex': 'Dexterity',
            'char_const': 'Constitution',
            'char_intel': 'Intelligence',
            'char_wisdom': 'Wisdom',
            'char_charisma': 'Charisma',
            'char_perception': 'Perception',
            'char_weap_prim': 'Primary Weapon',
            'char_weap_prim_die': 'Primary Weapon Hit Die',
            'char_weap_prim_num': 'Primary Weapon Number of Dice'
    }
    secondary_weap_check = []
    for i in form:
        # Adds the secondary weapon info to be checked separately
        if i == 'char_weap_sec':
            secondary_weap_check += [form['char_weap_sec']]
            pass
        elif i == 'char_weap_sec_num':
            secondary_weap_check += [form['char_weap_sec_num']]
            pass
        elif i == 'char_weap_sec_die':
            secondary_weap_check += [form['char_weap_sec_die']]
            pass
        if form[i] == '':
            # Inventory, skills, and notes are optional, even though they have default values
            if i == 'char_weap_sec':
                pass
            elif i == 'char_weap_sec_num':
                pass
            elif i == 'char_weap_sec_die':
                pass
            elif i == 'char_inv':
                pass
            elif i == 'char_skills':
                pass
            elif i == 'char_notes':
                pass
            elif i == 'game_pwd':
                pass
            else:
                return db_cols_to_readable[i] + ' was not filled out.'

    # Check if either all 3 secondary weapon fields are filled out, or all 3 are empty
    if secondary_weap_check[0] == '':
        if secondary_weap_check[1] == '' and secondary_weap_check[2] == '':
            pass
        else:
            return 'You must fill out all 3 fields for the secondary weapon if you want to add one.'
    if secondary_weap_check[1] == '':
        if secondary_weap_check[0] == '' and secondary_weap_check[2] == '':
            pass
        else:
            return 'You must fill out all 3 fields for the secondary weapon if you want to add one.'
    if secondary_weap_check[2] == '':
        if secondary_weap_check[0] == '' and secondary_weap_check[1] == '':
            pass
        else:
            return 'You must fill out all 3 fields for the secondary weapon if you want to add one.'

    # Check if the proficiency bonus is correct for your level
    level = int(form['char_lvl'])
    proficiency = int(form['char_proficiency'])
    if level < 5:
        if proficiency > 2:
            return 'Your proficiency is too high for a level ' + str(level) + '. It should be at 2.'
    if level >= 5 and level < 9:
        if proficiency < 3:
            return 'Your proficiency is too low for a level ' + str(level) + '. It should be at 3.'
        if proficiency > 3:
            return 'Your proficiency is too high for a level ' + str(level) + '. It should be at 3.'
    if level >= 9 and level < 13:
        if proficiency < 4:
            return 'Your proficiency is too low for a level ' + str(level) + '. It should be at 4.'
        if proficiency > 4:
            return 'Your proficiency is too high for a level ' + str(level) + '. It should be at 4.'
    if level >= 13 and level < 17:
        if proficiency < 5:
            return 'Your proficiency is too low for a level ' + str(level) + '. It should be at 5.'
        if proficiency > 5:
            return 'Your proficiency is too high for a level ' + str(level) + '. It should be at 5.'
    if level >= 17:
        if proficiency < 5:
            return 'Your proficiency is too low for a level ' + str(level) + '. It should be at 6.'

    # Checks to make sure the user hasn't changed any of their attributes to be greater than 20
    attributes = {
            'Strength': int(form['char_str']),
            'Dexterity': int(form['char_dex']),
            'Constitution': int(form['char_const']),
            'Intelligence': int(form['char_intel']),
            'Wisdom': int(form['char_wisdom']),
            'Charisma': int(form['char_charisma'])}
    for key in attributes:
        if attributes[key] > 20:
            return 'You cannot increase ' + key + ' over level 20.'

    # Check to make sure the current health is less than or equal to the max health
    current_hp = int(form['curr_health'])
    max_hp = int(form['max_health'])
    if current_hp > max_hp:
        return 'Current health cannot be higher than max health.'
    if current_hp == 0:
        return 'Your character is either unconcious or dead.'

    # If everything is okay, return an empty string, meaning 'okay'
    return ''

# Runs the server in debug mode when file is run with "python3 main.py"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
