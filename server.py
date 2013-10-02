from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug import utils
import os
import validator

UPLOAD_FOLDER = './uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
        res = v.produce_result_file(True)
        return render_template("result.html", res=res)
    v.perform_all_checks()

    res = v.produce_result_file(False)
    return render_template("result.html", res=res)

if __name__ == "__main__":
    app.run(debug=True)