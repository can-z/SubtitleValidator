from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug import utils
import os
import validator

UPLOAD_FOLDER = './uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def output(v):
    result_string = ""
    for e in v.error_list:
        result_string += str(e[0]) + ": " + e[1] + "\n\n"

    return result_string


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['subtitle_file']
        filename = utils.secure_filename(f.filename)
        if filename is None or filename == "":
            return redirect("/")

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('result',
                                filename=filename))


@app.route("/result/<filename>")
def result(filename):
    v = validator.Validator(os.path.join(app.config['UPLOAD_FOLDER'], filename), False)
    if not v.parse_file():
        res = output(v)
        return render_template("result.html", res=res)
    v.perform_all_checks()

    res = output(v)
    return render_template("result.html", res=res)

if __name__ == "__main__":
    app.run(debug=True)