from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug import utils
import os
import validator

UPLOAD_FOLDER = './uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def output(v, is_format_error):
    result_string = ""

    if is_format_error:
        result_string += "There are errors in the format of your subtitle file, and your file is not checked. Please " \
                         "make sure each of your subtitles conforms to the following format:\n" \
                         "[LINE NUMBER]\n" \
                         "[TIMESTAMP](example: 00:16:43,162 --> 00:16:44,400)\n" \
                         "[CHINESE SUBTITLE LINE]\n" \
                         "[ENGLISH SUBTITLE LINE]\n" \
                         "[EMPTY LINE]\n\n" \
                         "Below is the specific format errors found in your file:\n\n"

    for e in v.error_list:

            try:
                decoded_message = e[1].decode("utf-8")
            except UnicodeDecodeError:
                decoded_message = e[1].decode("gb2312")

            result_string += str(e[0]) + ": " + decoded_message + "\n\n"

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
        res = output(v, True)
        return render_template("result.html", res=res)
    v.perform_all_checks()

    res = output(v, False)
    return render_template("result.html", res=res)

if __name__ == "__main__":
    app.run(debug=True)