import openai
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required

app = Flask(__name__)

# Configuration for MySQL
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    
def load_api_key():
    # Load the API key from a file
    with open('project/static/api_key') as file:
        openai.api_key = file.read()


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Your login logic here
        # If login is successful:
        return redirect(url_for('login'))
        return redirect(url_for('index'))
        # If login is not successful, return the login template with error message
        return render_template('login.html', error="Invalid credentials")
    # For GET request, render the login page
    return render_template('login.html')


@app.route("/get_ai_response", methods={'POST'})
def get_ai_response():
    try:
        data = request.json
        user_message = data['message']
        prompt_list = [
            'You will be a doctor who responds to medical conditions and have an abelyte to participate in small talk\n'
            'Human: What time is it?\n'
            "AI: I'm sorry, I'm noe awer of your local time, but i can help you with any medical-related questions."
        ]
        bot_response = get_bot_response(user_message, prompt_list)
        return jsonify({'botResponse': bot_response})
    except Exception as e:
        print(f'ERROR: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500


def get_api_response(prompt: str) -> str:
    try:
        # Send the prompt to OpenAI API for completion
        response = openai.Completion.create(
            model='text-davinci-003',
            prompt=prompt,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[' Human:', ' AI;']
        )
        return response.choices[0].text
    except Exception as e:
        print('ERROR:', e)


def update_list(message: str, prompt_list: list[str]):
    # Add the message to the prompt list
    prompt_list.append(message)


def create_prompt(message: str, prompt_list: list[str]) -> str:
    p_message = f'\nHuman: {message}'
    update_list(p_message, prompt_list)
    prompt = ''.join(prompt_list)

    sql_code = """
 
CREATE DATABASE DiabetesMetabolitesDB;

USE DiabetesMetabolitesDB;

CREATE TABLE IF NOT EXISTS DiabetesMetabolites (
    MetaboliteName VARCHAR(50) PRIMARY KEY,
    HealthyRange VARCHAR(50),
    PreDiabeticRange VARCHAR(50),
    DiabeticRange VARCHAR(50)
);

-- Insert data into the Diabetes Metabolites table
INSERT INTO DiabetesMetabolites (MetaboliteName, HealthyRange, PreDiabeticRange, DiabeticRange)
VALUES
    ('Creatinine', '53 - 106 µmol/L', '107 - 212 µmol/L', '213 - 442 µmol/L'),
    ('Glucose', '4.0 - 5.5 mmol/L', '5.5 - 6.9 mmol/L (Fasting)', '>7.2 mmol/L (Fasting)'),
    ('HDL Cholesterol', '>1.04 mmol/L', '1.04 - 1.55 mmol/L', '<1.04 mmol/L');
    -- ... insert more data ...

-- Create the second table: Diabetes and Obesity Metabolites
CREATE TABLE IF NOT EXISTS DiabetesObesityMetabolites (
    MetaboliteName VARCHAR(50) PRIMARY KEY,
    HealthyRange VARCHAR(50),
    PreDiabeticRange VARCHAR(50),
    DiabeticRange VARCHAR(50)
);

-- Insert data into the Diabetes and Obesity Metabolites table
INSERT INTO DiabetesObesityMetabolites (MetaboliteName, HealthyRange, PreDiabeticRange, DiabeticRange)
VALUES
    ('Albumin', '40 - 55 g/L', '35 - 50 g/L', '<35 g/L'),
    ('ALT', '<40 U/L', '0 - 40 U/L', '>40 U/L'),
    ('AST', '<40 U/L', '0 - 40 U/L', '>40 U/L');
    -- ... insert more data ...


    """

    prompt += sql_code
    return prompt


def get_bot_response(message: str, prompt_list: list[str]) -> str:
    # Generate the prompt and get the bots response
    prompt = create_prompt(message, prompt_list)
    bot_response = get_api_response(prompt)
    if bot_response:
        update_list(bot_response, prompt_list)
        pos = bot_response.find('\nAI: ')
        bot_response = bot_response[pos + 5:]
    else:
        bot_response = 'Something went wrong...'
    return bot_response


"""def main():
    prompt_list = [
        'You will be a doctor who responds only to medical conditions.\n'
        'Human: What time is it?\n'
        'AI: I\'m sorry, but I can only answer medical-related questions.'
    ]
    while True:
        user_input = input('You: ')
        response = get_bot_response(user_input, prompt_list)
        print(f'Bot: {response}')
"""

if __name__ == '__main__':
    load_api_key()
    app.run(debug=True)
