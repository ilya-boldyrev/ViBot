import openai
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random


app = Flask(__name__)

#Random scan function 
def random_value_in_range(range_string):
    """Generate a random value within the given range."""
    if '-' in range_string:
        lower, upper = map(float, range_string.split('-'))
        return round(random.uniform(lower, upper), 1)
    elif '<' in range_string:
        upper = float(range_string.strip('<'))
        return round(random.uniform(0, upper), 1)
    elif '>' in range_string:
        lower = float(range_string.strip('>'))
        return round(random.uniform(lower, lower * 3), 2)
    else:
        return round(float(range_string), 2)

# Function to generate random scan
def generate_random_scan():
    diabetes_metabolites = {
        'Creatinine': ['53 - 106', '107 - 212', '213 - 442'],
        'Glucose': ['4.0 - 5.5', '5.5 - 6.9', '>7.2'],
        'HDL Cholesterol': ['>1.04', '1.04 - 1.55', '<1.04']
    }
    diabetes_obesity_metabolites = {
        'Albumin': ['40 - 55', '35 - 50', '<35'],
        'ALT': ['<40', '0 - 40', '>40'],
        'AST': ['<40', '0 - 40', '>40']
    }

    scan_results = {}
    for metabolite, ranges in {**diabetes_metabolites, **diabetes_obesity_metabolites}.items():
        scan_results[metabolite] = random_value_in_range(random.choice(ranges))
    return scan_results

@app.route('/generate_random_scan', methods=['GET'])
def generate_random_scan_endpoint():
    scan_results = generate_random_scan()
    return jsonify(scan_results)
    
# API loading function 
with open('static/API') as file:
    openai.api_key = file.read().strip()


@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    sentences = [
        "ViBot is a demonstration of a chatbot interface for your health and wellness.",
        "For this demo we start with a pre-made profile that reflects one of a few health states (e.g. normal, pre-diabetic, diabetic).",
        "You can then provide the bot with additional information about how you are feeling and ask health related questions.",
        "Optionally, you can mimic a ViBo Health DigiScan and use those results as input to the ViBot to receive an update about your profile's health state.",
        "How can I assist you today? Give me some health updates or questions to begin."
        ]
    welcome_message = '<br>'.join(sentences)
    return render_template('index.html', welcome_message=welcome_message)


@app.route('/chat')
@app.route('/chat/<int:profile_id>')
def chat(profile_id=None):
    if profile_id:
        profile_name = profiles.get(profile_id, {}).get('name', 'Unknown')
        welcome_message = f"You have chosen the {profile_name} profile. How can I assist you today?"
    else:
        # Default welcome message if no profile is selected
        welcome_message = ("Welcome to ViBot\nViBot is a demonstration of a chatbot interface for your health and wellness. "
                           "For this demo we start with a pre-made profile that reflects one of a few health states "
                           "(e.g. normal, pre-diabetic, diabetic). You can then provide the bot with additional information "
                           "about how you are feeling and ask health related questions. Optionally, you can mimic a ViBo "
                           "Health DigiScan and use those results as input to the ViBot to receive an update about your profile's health state.\n"
                           "How can I assist you today? Give me some health updates or questions to begin.")
    
    return render_template('index.html', profile_id=profile_id, welcome_message=welcome_message)


@app.route('/choose-profile')
def choose_profile():
    return render_template('choose_profile.html')


@app.route('/about')
def about():
    return render_template('about_us.html')

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
            #Prompt 
            "ViBot is an advanced chatbot designed to provide preliminary insights into diabetes-related health inquiries. It can offer advice on blood sugar management, dietary suggestions, medication advice, and interpret basic medical test results. ViBot can also engage in small talk and answer general medical questions. However, ViBot always emphasizes that its guidance is not a substitute for professional medical advice, diagnosis, or treatment. Here's a sample conversation:",

            "Human: Hi ViBot, my recent blood test shows a glucose level of 7.5 mmol/L. Is this a concern?",
            "ViBot: A glucose level of 7.5 mmol/L is above the normal fasting glucose range, which may indicate a risk of pre-diabetes or diabetes. It's important to consult with a healthcare professional for a complete evaluation and diagnosis.",

            "Human: Can you suggest a good breakfast for diabetes management?",
            "ViBot: Absolutely! A diabetic-friendly breakfast could include high-fiber carbohydrates like oats, proteins such as eggs, and healthy fats like avocados. It's beneficial to avoid sugary cereals and drinks.",

            "Human: I have a minor foot injury. What should I do?",
            "ViBot: For individuals with diabetes, foot care is crucial. Clean the cut with water, apply antibiotic ointment, and cover it with a bandage. Monitor for signs of infection like redness or swelling. If these symptoms appear, consult a healthcare professional immediately.",

            "Human: Thanks, ViBot. You are quite helpful.",
            "ViBot: You're welcome! Remember, while I can provide helpful information, it's always best to seek advice from healthcare professionals for medical concerns."
        ]

        bot_response = get_bot_response(user_message, prompt_list)
        return jsonify({'botResponse': bot_response})
    except Exception as e:
        print(f'ERROR: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500

profiles = {
    1: {'name': 'Non-Diabetes', 'description': "Characterized by the body's inability to produce insulin. Requires regular insulin administration.", 'recommendations': ['Regular insulin therapy', 'Carbohydrate counting', 'Frequent blood sugar monitoring']},
    2: {'name': 'Pre-Diabetes', 'description': 'Occurs when the body becomes resistant to insulin or doesn\'t make enough insulin', 'recommendations': ['Healthy eating', 'Regular exercise', 'Blood sugar monitoring', 'Diabetes medication or insulin therapy']},
    3: {'name': 'Diabetes', 'description': 'Develops during pregnancy and usually disappears after giving birth.', 'recommendations': ['Monitoring blood sugar level', 'Healthy diet', 'Regular physical activity']}
}

# AI model should be updated sometimes. Be aware that OpenAI change them sometimes.
def get_api_response(prompt: str, prompt_list: list[str]) -> str:
    try:
        full_prompt = "\n".join(prompt_list) + "\n" + prompt

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-1106',
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )

        # Retrieve the response content
        api_response = response['choices'][0]['message']['content']

        # Split the response to address each aspect of the question
        split_responses = api_response.split('. ')
        detailed_response = ".\n".join(split_responses)  # Adding a newline for clarity

        return detailed_response
    except Exception as e:
        print('ERROR:', e)
        raise e



def update_list(message: str, prompt_list: list[str]):
    # Add the message to the prompt list
    prompt_list.append(message)



# DataBase, gives ViBot info about levels.
def create_prompt(message: str, prompt_list: list[str]) -> str:
    p_message = f'\nUser: {message}'
    update_list(p_message, prompt_list)
    prompt = ''.join(prompt_list)

    sql_code = """

    USE DiabetesMetabolitesDB;
    DiabetesMetabolites (
        MetaboliteName VARCHAR(50) PRIMARY KEY,
        HealthyRange VARCHAR(50),
        PreDiabeticRange VARCHAR(50),
        DiabeticRange VARCHAR(50)
    );

    INSERT INTO DiabetesMetabolites (MetaboliteName, HealthyRange, PreDiabeticRange, DiabeticRange)
    VALUES
        ('Creatinine', '53 - 106 µmol/L', '107 - 212 µmol/L', '213 - 442 µmol/L'),
        ('Glucose', '4.0 - 5.5 mmol/L', '5.5 - 6.9 mmol/L (Fasting)', '>7.2 mmol/L (Fasting)'),
        ('HDL Cholesterol', '>1.04 mmol/L', '1.04 - 1.55 mmol/L', '<1.04 mmol/L');
       

    DiabetesObesityMetabolites (
        MetaboliteName VARCHAR(50) PRIMARY KEY,
        HealthyRange VARCHAR(50),
        PreDiabeticRange VARCHAR(50),
        DiabeticRange VARCHAR(50)
    );

    INSERT INTO DiabetesObesityMetabolites (MetaboliteName, HealthyRange, PreDiabeticRange, DiabeticRange)
    VALUES
        ('Albumin', '40 - 55 g/L', '35 - 50 g/L', '<35 g/L'),
        ('ALT', '<40 U/L', '0 - 40 U/L', '>40 U/L'),
        ('AST', '<40 U/L', '0 - 40 U/L', '>40 U/L');
        """

    prompt += sql_code
    return prompt

def get_bot_response(user_message: str, prompt_list: list[str]) -> str:
    # Generate the prompt with the cleaned message
    prompt = "\nUser: " + user_message

    # Get the response from the API
    bot_response = get_api_response(prompt, prompt_list)

    if bot_response:
        # Remove undesired prefixes if present
        bot_response = bot_response.replace("ViBot: ", "")
        # Add to the conversation history
        update_list('ViBot: ' + bot_response, prompt_list)
        return bot_response
    else:
        return 'I am not sure how to respond to that. Can you ask something else?'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="8080")
