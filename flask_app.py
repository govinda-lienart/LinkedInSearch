from flask import Flask, request, render_template
from dotenv import load_dotenv
from Orchestrator import ice_break_with


# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        name = request.form.get("name")
        result = ice_break_with(name)
        summary = result.summary if result else "No summary found."
    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
