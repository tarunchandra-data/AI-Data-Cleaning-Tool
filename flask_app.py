from flask import Flask, render_template, request, send_file, redirect, url_for, session
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"csv", "xlsx"}

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB



# ==============================
# DASHBOARD COUNTERS
# ==============================

dataset_count = 0
cleaned_count = 0
analysis_count = 0


# ==============================
# PERMANENT HISTORY STORAGE
# ==============================

HISTORY_FILE = "history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    return []


def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


history = load_history()

# ==============================
# PERMANENT MEMBERS STORAGE
# ==============================

MEMBERS_FILE = "members.json"


def load_members():
    if os.path.exists(MEMBERS_FILE):
        try:
            with open(MEMBERS_FILE, "r", encoding="utf-8") as file:
                members_data = json.load(file)

                if isinstance(members_data, list):
                    return members_data

        except (json.JSONDecodeError, OSError):
            pass

    # Default project member
    return [
        {
            "id": 1,
            "name": "Tarun Chandra",
            "role": "Project Developer"
        }
    ]


def save_members():
    with open(MEMBERS_FILE, "w", encoding="utf-8") as file:
        json.dump(members, file, indent=4, ensure_ascii=False)


members = load_members()




# ==============================
# READ DATASET
# ==============================
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def read_dataset(file_path, filename):

    if filename.lower().endswith(".csv"):
        return pd.read_csv(file_path)

    elif filename.lower().endswith(".xlsx"):
        return pd.read_excel(file_path)

    return None


# ==============================
# AI CLEANING RECOMMENDATIONS
# ==============================

def generate_recommendations(df):

    recommendations = []

    missing_count = int(
        df.isnull().sum().sum()
    )

    duplicate_count = int(
        df.duplicated().sum()
    )

    # Missing values
    if missing_count > 0:

        recommendations.append({

            "icon": "⚠️",

            "title": "Missing Values Detected",

            "text": (
                f"{missing_count} missing value(s) found in the dataset. "
                "Consider filling numeric values with the median and "
                "text values with 'Unknown'."
            ),

            "priority": "High Priority",

            "priority_class": "high"

        })

    else:

        recommendations.append({

            "icon": "✅",

            "title": "No Missing Values",

            "text": (
                "The dataset does not contain any missing values."
            ),

            "priority": "Good",

            "priority_class": "good"

        })


    # Duplicate rows
    if duplicate_count > 0:

        recommendations.append({

            "icon": "🔄",

            "title": "Duplicate Rows Found",

            "text": (
                f"{duplicate_count} duplicate row(s) detected. "
                "Removing duplicates is recommended to improve data quality."
            ),

            "priority": "High Priority",

            "priority_class": "high"

        })

    else:

        recommendations.append({

            "icon": "✅",

            "title": "No Duplicate Rows",

            "text": (
                "No duplicate rows were detected in the dataset."
            ),

            "priority": "Good",

            "priority_class": "good"

        })


    # Numeric columns
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns


    if len(numeric_columns) > 0:

        recommendations.append({

            "icon": "📊",

            "title": "Numeric Data Available",

            "text": (
                f"{len(numeric_columns)} numeric column(s) detected. "
                "Statistical analysis such as average, minimum and maximum "
                "can be performed."
            ),

            "priority": "Medium Priority",

            "priority_class": "medium"

        })

    else:

        recommendations.append({

            "icon": "ℹ️",

            "title": "No Numeric Columns",

            "text": (
                "No numeric columns were detected. "
                "Statistical analysis may be limited."
            ),

            "priority": "Medium Priority",

            "priority_class": "medium"

        })


    # Dataset size
    if len(df) > 1000:

        recommendations.append({

            "icon": "📁",

            "title": "Large Dataset",

            "text": (
                "This is a large dataset. Consider checking "
                "data types and memory usage for better performance."
            ),

            "priority": "Medium Priority",

            "priority_class": "medium"

        })

    else:

        recommendations.append({

            "icon": "🚀",

            "title": "Dataset Size",

            "text": (
                "The dataset size is suitable for standard "
                "cleaning and analysis operations."
            ),

            "priority": "Good",

            "priority_class": "good"

        })


    return recommendations


# ==============================
# CREATE ANALYSIS
# ==============================

def create_analysis(df):

    analysis = []

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns


    for column in numeric_columns:

        analysis.append({

            "column": column,

            "count": int(
                df[column].count()
            ),

            "average": round(
                float(
                    df[column].mean()
                ),
                2
            ),

            "minimum": round(
                float(
                    df[column].min()
                ),
                2
            ),

            "maximum": round(
                float(
                    df[column].max()
                ),
                2
            )

        })


    return analysis


# ==============================
# DASHBOARD / UPLOAD
# ==============================

@app.route("/", methods=["GET", "POST"])
def home():

    global dataset_count
    global analysis_count

    data = None

    if request.method == "POST":

        uploaded_file = request.files.get("dataset")


        if uploaded_file and uploaded_file.filename:

            if not allowed_file(uploaded_file.filename):
                return render_template(
                    "dashboard.html",
                    error="Only CSV and XLSX files are supported.",
                    dataset_count=dataset_count,
                    cleaned_count=cleaned_count,
                    analysis_count=analysis_count,
                    history=history
                )

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                secure_filename(uploaded_file.filename)
            )


            uploaded_file.save(file_path)


            try:

                df = read_dataset(
                    file_path,
                    uploaded_file.filename
                )


                if df is None:

                    return render_template(

                        "dashboard.html",

                        error="Only CSV and XLSX files are supported.",

                        dataset_count=dataset_count,

                        cleaned_count=cleaned_count,

                        analysis_count=analysis_count,

                        history=history

                    )


                # ==============================
                # UPDATE COUNTERS
                # ==============================

                dataset_count += 1

                analysis_count += 1


                # ==============================
                # ADD HISTORY RECORD
                # ==============================

                history.append({

                    "filename":
                        uploaded_file.filename,

                    "action":
                        "Dataset Analysis",

                    "status":
                        "Analyzed",

                    "time":
                        datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        )

                })
                save_history()


                # ==============================
                # DATASET INFORMATION
                # ==============================

                rows = len(df)

                columns = len(df.columns)


                missing_count = int(
                    df.isnull().sum().sum()
                )


                duplicate_count = int(
                    df.duplicated().sum()
                )


                total_cells = rows * columns


                if total_cells > 0:

                    missing_percentage = (
                        missing_count / total_cells
                    ) * 100

                else:

                    missing_percentage = 0


                duplicate_percentage = (

                    (duplicate_count / rows) * 100

                    if rows > 0

                    else 0

                )


                quality_score = max(

                    0,

                    round(

                        100

                        - (missing_percentage * 0.6)

                        - (duplicate_percentage * 0.4),

                        1

                    )

                )


                # ==============================
                # ANALYSIS
                # ==============================

                analysis = create_analysis(df)


                # ==============================
                # AI RECOMMENDATIONS
                # ==============================

                recommendations = (
                    generate_recommendations(df)
                )


                # ==============================
                # DATA OBJECT
                # ==============================

                data = {

                    "filename":
                        uploaded_file.filename,

                    "rows":
                        rows,

                    "columns":
                        columns,

                    "missing":
                        missing_count,

                    "duplicates":
                        duplicate_count,

                    "quality":
                        quality_score,

                    "preview":
                        df.head(10).to_html(
                            classes="data-table",
                            index=False
                        ),

                    "analysis":
                        analysis,

                    "recommendations":
                        recommendations

                }


            except Exception as e:

                return render_template(

                    "dashboard.html",

                    error=f"Could not read file: {e}",

                    dataset_count=dataset_count,

                    cleaned_count=cleaned_count,

                    analysis_count=analysis_count,

                    history=history

                )


    return render_template(

        "dashboard.html",

        data=data,

        dataset_count=dataset_count,

        cleaned_count=cleaned_count,

        analysis_count=analysis_count,

        history=history

    )


# ==============================
# CLEAN DATASET
# ==============================

@app.route("/clean", methods=["POST"])
def clean_dataset():

    global cleaned_count


    files = os.listdir(
        app.config["UPLOAD_FOLDER"]
    )


    if not files:

        return "No dataset uploaded."


    dataset_files = [

        file

        for file in files

        if file.lower().endswith(
            (".csv", ".xlsx")
        )

        and not file.startswith("cleaned_")

    ]


    if not dataset_files:

        return "No dataset available for cleaning."


    filename = dataset_files[-1]


    file_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )


    try:

        df = read_dataset(

            file_path,

            filename

        )


        if df is None:

            return "Unsupported file format."


        # ==============================
        # ORIGINAL INFORMATION
        # ==============================

        original_rows = len(df)


        duplicates_removed = int(

            df.duplicated().sum()

        )


        # ==============================
        # REMOVE DUPLICATES
        # ==============================

        df = df.drop_duplicates()


        # ==============================
        # FILL NUMERIC MISSING VALUES
        # ==============================

        numeric_columns = df.select_dtypes(

            include="number"

        ).columns


        for column in numeric_columns:

            if df[column].isnull().any():

                median_value = df[column].median()


                if pd.notna(median_value):

                    df[column] = df[column].fillna(

                        median_value

                    )


        # ==============================
        # FILL TEXT MISSING VALUES
        # ==============================

        text_columns = df.select_dtypes(

            exclude="number"

        ).columns


        for column in text_columns:

            df[column] = df[column].fillna(

                "Unknown"

            )


        # ==============================
        # SAVE CLEANED DATASET
        # ==============================

        cleaned_filename = (

            "cleaned_"

            + filename.rsplit(".", 1)[0]

            + ".csv"

        )


        cleaned_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            cleaned_filename

        )


        df.to_csv(

            cleaned_path,

            index=False

        )


        # ==============================
        # UPDATE CLEANED COUNTER
        # ==============================

        cleaned_count += 1


        # ==============================
        # ADD CLEANING HISTORY
        # ==============================

        history.append({

            "filename":
                filename,

            "action":
                "Dataset Cleaning",

            "status":
                "Cleaned",

            "time":
                datetime.now().strftime(
                    "%d %b %Y, %I:%M %p"
                )

        })
        save_history()


        cleaned_rows = len(df)


        remaining_missing = int(

            df.isnull().sum().sum()

        )


        # ==============================
        # ANALYSIS AFTER CLEANING
        # ==============================

        analysis = create_analysis(df)


        # ==============================
        # AI RECOMMENDATIONS
        # ==============================

        recommendations = (
            generate_recommendations(df)
        )


        return render_template(

            "dashboard.html",

            data={

                "filename":
                    filename,

                "rows":
                    original_rows,

                "columns":
                    len(df.columns),

                "missing":
                    remaining_missing,

                "duplicates":
                    duplicates_removed,

                "quality":
                    100.0,

                "preview":
                    df.head(10).to_html(

                        classes="data-table",

                        index=False

                    ),

                "cleaned":
                    True,

                "cleaned_filename":
                    cleaned_filename,

                "duplicates_removed":
                    duplicates_removed,

                "cleaned_rows":
                    cleaned_rows,

                "analysis":
                    analysis,

                "recommendations":
                    recommendations

            },

            dataset_count=dataset_count,

            cleaned_count=cleaned_count,

            analysis_count=analysis_count,

            history=history

        )


    except Exception as e:

        return render_template(

            "dashboard.html",

            error=f"Could not clean file: {e}",

            dataset_count=dataset_count,

            cleaned_count=cleaned_count,

            analysis_count=analysis_count,

            history=history

        )


# ==============================
# DOWNLOAD CLEANED DATASET
# ==============================

@app.route("/download/<filename>")
def download_file(filename):

    file_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )


    if os.path.exists(file_path):

        return send_file(

            file_path,

            as_attachment=True

        )


    return "Cleaned file not found."

# ==============================
# ADMIN LOGIN
# ==============================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin_username = os.environ.get("ADMIN_USERNAME")
        admin_password = os.environ.get("ADMIN_PASSWORD")

        if (
            admin_username
            and admin_password
            and username == admin_username
            and password == admin_password
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))

        error = "Invalid username or password."

    return render_template("admin_login.html", error=error)

@app.route("/admin")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    datasets = []

    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):

        if filename.lower().endswith((".csv", ".xlsx")):

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            if os.path.isfile(file_path):

                file_size = os.path.getsize(file_path)

                datasets.append({
                    "filename": filename,
                    "size": round(file_size / 1024, 2)
                })

    return render_template(
        "admin.html",
        datasets=datasets,
        dataset_count=dataset_count,
        cleaned_count=cleaned_count,
        analysis_count=analysis_count,
        history=history[-10:][::-1],
        members=members
    )

@app.route("/admin/download/<path:filename>")
def admin_download_dataset(filename):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    # Prevent path traversal
    filename = os.path.basename(filename)

    if not filename.lower().endswith((".csv", ".xlsx")):
        return "Unsupported file type.", 400

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)

    return "Dataset file not found.", 404

@app.route("/admin/delete/<path:filename>", methods=["POST"])
def admin_delete_dataset(filename):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    # Restrict the filename to the uploads folder
    filename = os.path.basename(filename)

    if not filename.lower().endswith((".csv", ".xlsx")):
        return "Unsupported file type.", 400

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if os.path.isfile(file_path):
        os.remove(file_path)
        return redirect(url_for("admin_dashboard"))

    return "Dataset file not found.", 404

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


# ==============================
# ADMIN MEMBER MANAGEMENT
# ==============================

@app.route("/admin/members/add", methods=["POST"])
def add_member():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()

    if name and role:
        next_id = max(
            [member.get("id", 0) for member in members],
            default=0
        ) + 1

        members.append({
            "id": next_id,
            "name": name,
            "role": role
        })

        save_members()

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/members/delete/<int:member_id>", methods=["POST"])
def delete_member(member_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    global members

    members = [
        member for member in members
        if member.get("id") != member_id
    ]

    save_members()

    return redirect(url_for("admin_dashboard"))
# ==============================
# RUN FLASK
# ==============================

if __name__ == "__main__":

    app.run(debug=False)