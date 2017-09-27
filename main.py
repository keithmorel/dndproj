from flask import Flask, render_template, request, session, abort, redirect, Response, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
app = Flask(__name__)
import random
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
import os

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@app.route('/')
def index():
    return render_template('./home.html', **locals())

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.username = "User_" + str(id)
        self.password = self.username + "_pwd"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.username, self.password)

users = [User(id) for id in range(1,21)]

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User(id)
        login_user(user)
        flash('Logged in successfully.')
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(url_for('mkchar'))
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route('/roll')
#""" Default home page with all information filled in as blanks, showing you how the information is formatted. """
def all_dice():
    rolls_d4 = []    #""" Lists of accumulated rolls for all the different dice """
    rolls_d6 = []
    rolls_d8 = []
    rolls_d10 = []
    rolls_d20 = []
    rolls_dx = []
    mod_d4 = 0    #""" All the modifiers, + or -, that are added to the total of that dice's rolls, not each individual roll """
    mod_d6 = 0
    mod_d8 = 0
    mod_d10 = 0
    mod_d20 = 0
    mod_dx = 0
    d4_tot = 0    #""" Accumulated totals of each row from the lists above, mostly just for the result calculation """
    d6_tot = 0
    d8_tot = 0
    d10_tot = 0
    d20_tot = 0
    dx_tot = 0
    result = 0    #""" Final result that appears at the bottom right of the table """
    return render_template('./mult_dice.html', **locals())

@app.route('/<sides>') 
#""" Simple page that rolls an arbitrary-sided die: 36-sided, 27-sided, 378-sided, etc. """
def arb_sides(sides):
    roll = random.randint(1, int(sides))
    return render_template('./dice.html', **locals())

@app.route("/roll_all/", methods=['POST'])
#""" Main method that does the most amount of work on the site. Takes in all of the inputs and modifiers from all of the different dice available and calculates the total amount rolled for each row and total. """
def roll_all():
    num_rolls = []    #""" Initializing a list to store the number of times to roll each individual die, using a GET request to pull this information from the inputs. """
    num_rolls += [request.form.get('d4_rolls')]
    num_rolls += [request.form.get('d6_rolls')]
    num_rolls += [request.form.get('d8_rolls')]
    num_rolls += [request.form.get('d10_rolls')]
    num_rolls += [request.form.get('d20_rolls')]
    num_rolls += [request.form.get('dx_rolls')]
    mods = []    #""" Initializing a list to store the modifiers that are added or subtracted to the totals of each row using a GET request, not to each individual roll. """
    mods += [request.form.get('d4_mod')]
    mods += [request.form.get('d6_mod')]
    mods += [request.form.get('d8_mod')]
    mods += [request.form.get('d10_mod')]
    mods += [request.form.get('d20_mod')]
    mods += [request.form.get('dx_mod')]
    for i in range(0,6):
        #""" Error checking of number of rolls:
        # If any of the rolls weren't filled out, don't roll them. This avoids TypeErrors with trying to add empty strings to integers. """
        if num_rolls[i] == '':
            num_rolls[i] = 0
    for j in range(0,6):
        #""" Error checking of modifiers:
        # If any modifiers weren't filled out, don't add anything. This avoids TypeErrors with trying to add empty strings to integers. """
        if mods[j] == '':
            mods[j] = 0
    result = 0    #""" Initialize final result as 0, just in case nothing is filled out. """
    row_tots = []   # """ Initialize list to hold the row totals, which will be added together at the end to the final result. """
    for x in range(0,6):
        #""" Since the dice chosen on this page are fixed and not in order, this is needed to be able to loop through the list of the number of rolls of each die and the modifiers for each die. e.g. [d4_rolls, d6_rolls, d8_rolls, d10_rolls, d20_rolls], and [d4_mod, d6_mod, d8_mod, d10_mod, d20_mod] """
        if x == 0:
            #''' D4 '''
            rolls_d4 = []
            d4_tot = 0
            for y in range(0, int(num_rolls[x])):
                #""" Loop through rolling the die the amount of times specified by d4_rolls. """
                curr_roll = random.randint(1,4)    #""" Save current roll to variable so the number is the same when called multiple times. """
                rolls_d4 += [curr_roll]    #""" Add current roll to the list of rolls for this die. """
                d4_tot += curr_roll    #""" Add current roll to the row total. """
            d4_tot += int(mods[0])    #""" Once done with rolls for this die, add d4_mod to total. """
            row_tots += [d4_tot]    #""" Add the total for the row into the list of all row totals. """
        elif x == 1:
            #''' D6 '''
            rolls_d6 = []
            d6_tot = 0
            for z in range(0, int(num_rolls[x])):
                #""" Same as if case, but for d6. """
                curr_roll = random.randint(1,6)
                rolls_d6 += [curr_roll]
                d6_tot += curr_roll
            d6_tot += int(mods[1])
            row_tots += [d6_tot]
        elif x == 2:
            #''' D8 '''
            rolls_d8 = []
            d8_tot = 0
            for c in range(0, int(num_rolls[x])):
                #""" Same as if case, but for d8. """
                curr_roll = random.randint(1,8)
                rolls_d8 += [curr_roll]
                d8_tot += curr_roll
            d8_tot += int(mods[2])
            row_tots += [d8_tot]
        elif x == 3:
            #''' D10 '''
            rolls_d10 = []
            d10_tot = 0
            for n in range(0, int(num_rolls[x])):
                #""" Same as if case, but for d10. """
                curr_roll = random.randint(1,10)
                rolls_d10 += [curr_roll]
                d10_tot += curr_roll
            d10_tot += int(mods[3])
            row_tots += [d10_tot]
        elif x == 4:
            #''' D20 '''
            rolls_d20 = []
            d20_tot = 0
            for m in range(0, int(num_rolls[x])):
                #""" Same as if case, but for d20. """
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

    #''' Cumulative Total '''
    for k in range(0, len(row_tots)):
        #""" Loop through the list of row totals, adding them all to the cumulative total. """
        result += row_tots[k]
    if int(mods[0]) > 0:
        mod_d4 = '+' + str(mods[0])
    elif int(mods[1]) > 0:
        mod_d6 = '+' + str(mods[1])
    elif int(mods[2]) > 0:
        mod_d8 = '+' + str(mods[2])
    elif int(mods[3]) > 0:
        mod_d10 = '+' + str(mods[3])
    elif int(mods[4]) > 0:
        mod_d20 = '+' + str(mods[4])
    elif int(mods[5]) > 0:
        mod_dx = '+' + str(mods[5])
    else:
        mod_d4 = str(mods[0])
        mod_d6 = str(mods[1])
        mod_d8 = str(mods[2])
        mod_d10 = str(mods[3])
        mod_d20 = str(mods[4])
        mod_dx = str(mods[5])

    # For aesthetic purposes only
    rolls_dx += ['D' + str(to_roll)]

    return render_template('./mult_dice.html', **locals())

@app.route("/mkchar")
#@login_required
#""" Route to basic character design sheet creation, not fully implemented until user system up and running so users are able to save their characters to a database for future viewing/editing/deleting/etc. """
def mkchar():
    return render_template('./mkchar.html', **locals())

# Sets up a secret key for flask-login, and starts up the server on localhost:5000 with debug mode on
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='127.0.0.1', port=5000)
