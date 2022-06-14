from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    """Shows home page with Survery title/start"""

    title = survey.title
    instructions = survey.instructions
    questions = survey.questions

    return render_template(
        "home.html", title=title, instructions=instructions, questions=questions
    )


@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses."""

    session[RESPONSES_KEY] = []

    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""

    # get the response choice
    choice = request.form["answer"]

    # add this response to the session
    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    if len(responses) == len(survey.questions):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""
    responses = session.get(RESPONSES_KEY)

    if responses is None:
        # trying to access question page too soon
        return redirect("/")

    if len(responses) == len(survey.questions):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    if len(responses) != qid:
        # Trying to access questions out of order.
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template("question.html", question_num=qid, question=question)


@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""

    return render_template("completion.html")
