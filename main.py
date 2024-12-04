from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import smtplib
from email.mime.text import MIMEText
from datetime import datetime  # For timestamp

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Used for session management

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "ims.agri24@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "qjxq crcl pxur zcgn"  # Replace with your email app password

# Dummy user credentials
USERS = {
    "Noon": "Noon",
    "Chloe": "Chloe"
}

@app.route("/")
def index():
    # If the user is logged in, redirect to the lab info page
    if "username" in session:
        return redirect(url_for("lab_info"))
    return render_template("login.html")  # Login page

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    # Check if credentials are valid
    if username in USERS and USERS[username] == password:
        session["username"] = username
        return redirect(url_for("lab_info"))
    return "Invalid credentials, please go back and try again!"

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/lab_info")
def lab_info():
    # Show lab information and navigation options
    if "username" in session:
        return render_template("lab_info.html", username=session["username"])
    return redirect(url_for("index"))

@app.route("/sequencing")
def sequencing():
    # Display the sequencing request form
    if "username" in session:
        return render_template("sequencing.html", username=session["username"])
    return redirect(url_for("index"))

@app.route("/submit", methods=["POST"])
def submit_request():
    try:
        data = request.json
        samples = data.get("samples", [])
        user_name = session.get("username", "Unknown User")  # Get the logged-in user's name
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current date and time

        # Prepare email body
        subject = "New DNA Sequencing Request"
        body = f"The following samples have been submitted:\n\n"
        body += f"By {user_name} at {timestamp}\n\n"
        for idx, sample in enumerate(samples, start=1):
            body += (
                f"No.{idx} Sample ID: {sample['sampleID']}, "
                f"Description: {sample['description']}, "
                f"Primer: {sample['primer']}\n"
            )

        # Send the email
        send_email(subject, body)

        return jsonify({"message": "Samples submitted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_email(subject, body):
    """Send an email notification."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS  # You can also customize this to send to others

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    app.run(debug=True)
