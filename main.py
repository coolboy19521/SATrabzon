import flask
import generate

app = flask.Flask(__name__)
package_names = [i[0] for i in generate.packages]

@app.route('/mainloop/<pin>/<int:index>')
def mainloop(pin, index):
    question = generate.get_question(pin, index)
    return flask.render_template('mainloop.html', packages = generate.packages, question = question, index = index, pin = pin)

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