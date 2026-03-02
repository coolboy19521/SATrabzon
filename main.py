import os
import flask
import dotenv
import generate

app = flask.Flask(__name__)

dotenv.load_dotenv()
app.secret_key = os.environ.get('SECRET_KEY')

package_names = [i[0] for i in generate.packages]

@app.route('/mainloop/<pin>/<int:index>')
def mainloop(pin, index):
    if pin not in flask.session:
        flask.session[pin] = {"done": {}, "correct_count": 0, "question_count": 0}
    session_data = flask.session[pin]
    correct_count = session_data.get("correct_count", None)
    question_count = session_data.get("question_count", None)
    if index + 1 > question_count:
        flask.session[pin]["question_count"] = (question_count := index + 1)
        flask.session.modified = True
    question = generate.get_question(pin, index)
    choice = session_data["done"].get(str(index + 1), -1)
    is_full = len(session_data.get("done", None)) == question_count
    return flask.render_template('mainloop.html',
        packages = generate.packages, question = question, index = index, pin = pin,
        correct_count = correct_count, question_count = question_count, choice = choice, is_full = is_full
    )

@app.route('/generate', methods=['POST'])
def generate_pin():
    included = flask.request.get_json().get('included', [])
    sterile_included = []
    for include in included:
        package_index = int(package_names.index(include[:include.rindex('-')]))
        set_index = int(include[include.rindex('-') + 1:])
        sterile_included.append((package_index, set_index))
    pin = generate.get_pin(sterile_included)
    return flask.jsonify(pin)

@app.route('/answer', methods=['POST'])
def answer():
    data = flask.request.get_json()
    pin = data.get('pin', None)
    index = data.get('index', None)
    option = data.get('option', None)
    is_correct = data.get('is_correct', None)
    flask.session[pin]["done"][str(index + 1)] = option
    if is_correct: flask.session[pin]["correct_count"] += 1
    flask.session.modified = True
    session_data = flask.session[pin]
    correct_count = flask.session[pin].get('correct_count', None)
    data_length = len(session_data.get("done", None))
    question_count = session_data.get("question_count", None)
    is_full = data_length == question_count
    out = flask.jsonify({
        'correct_count': correct_count,
        'question_count': question_count,
        'is_full': is_full
    })
    return out

@app.route('/clear', methods=['POST'])
def clear():
    pin = flask.request.get_json().get('pin', None)
    if pin in flask.session:
        del flask.session[pin]
        flask.session.modified = True
    return '', 204

@app.route('/selected/<pin>', methods=['GET'])
def selected(pin):
    pin = int(pin, generate.REP_SIZ)
    selected_boxes = []
    package_index, set_index = 0, 0
    for i in range(generate.prefix_sum[-1]):
        if i == generate.prefix_sum[package_index + 1]:
            package_index, set_index = package_index + 1, 0
        if pin & 1 << i: selected_boxes.append(f'{package_names[package_index]}-{set_index}')
        set_index += 1
    return flask.jsonify(selected_boxes)

@app.route('/')
def index():
    return flask.render_template('base.html', packages = generate.packages)

if __name__ == '__main__':
    app.run(debug = True)