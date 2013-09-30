import re
import datetime
import sys
import os
from flask import Flask, render_template
import validator

app = Flask(__name__)


def output(v):
    result = ""
    for e in v.error_list:
        result += str(e[0]) + ": " + e[1] + "\n\n"

    return result


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/result")
def web_main():
    v = validator.Validator("sample.srt", False)
    if not v.parse_file():
        output(v)
        return
    v.whitespace_check()
    v.upper_case_check()
    v.lower_case_check()
    v.double_whitespace_check()
    v.single_whitespace_check()
    v.ellipsis_check()

    return output(v)


if __name__ == "__main__":
    app.run(debug=True)