import json
from flask import Flask, render_template, redirect, request, session
# The Session instance is not used for direct access, you should always use flask.session
from flask_session import Session
from supabase_py import create_client, Client

url: str = "https://imhdpixsmgwlrvpqiqel.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltaGRwaXhzbWd3bHJ2cHFpcWVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY2OTQ5OTAxOSwiZXhwIjoxOTg1MDc1MDE5fQ.uAz7zAsOnv0bp_jVce2U99UokDkbkUdTWU5JFSHs46Y"

supabase: Client = create_client(url,key)
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

 
@app.route("/")
def index():
    return redirect("/laporan")
 
@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect("/")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = supabase.auth.sign_up(email=email, password=password)
        if user.get('msg') is not None:
            return render_template("register.html", error=user['msg'])
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if session.get("user_id"):
        return redirect("/")
    if request.method == "POST":
        email: str = request.form.get("email")
        password: str = request.form.get("password")
        user = supabase.auth.sign_in(email=email, password=password)
        if user.get("error") is not None:
            return render_template('login.html', error=user['error_description'])
        session["user_id"] = user['user']['id']
        session["email"] = user['user']['email']
        return redirect("/")
    return render_template("login.html")
 
@app.route("/logout")
def logout():
    session["user_id"] = None
    session["email"] = None
    return redirect("/")

@app.route("/penerimaan", methods=["GET"])
def penerimaan():
    if not session.get("user_id"):
        return redirect("/login")
    pencatatan = supabase.table("pencatatan").select("*").eq("user_id", session.get("user_id")).execute()
    data = pencatatan['data']
    columns = [
        {"name": "tanggal", "label": "Tanggal"},
        {"name": "keterangan", "label": "Keterangan"},
        {"name": "jumlah", "label": "Jumlah"},
    ]
    penerimaan = [x for x in data if x['penerimaan'] == True]
    return render_template("list.html", data=penerimaan, columns=columns, judul="Penerimaan", method_tambah="tambah_penerimaan", method_edit="edit_penerimaan", method_hapus="hapus_penerimaan")

@app.route("/pengeluaran", methods=["GET"])
def pengeluaran():
    if not session.get("user_id"):
        return redirect("/login")
    pencatatan = supabase.table("pencatatan").select("*").eq("user_id", session.get("user_id")).execute()
    data = pencatatan['data']
    columns = [
        {"name": "tanggal", "label": "Tanggal"},
        {"name": "keterangan", "label": "Keterangan"},
        {"name": "jumlah", "label": "Jumlah"},
    ]
    pengeluaran = [x for x in data if x['penerimaan'] == False]
    return render_template("list.html", data=pengeluaran, columns=columns, judul="Pengeluaran", method_tambah="tambah_pengeluaran", method_edit="edit_pengeluaran", method_hapus="hapus_pengeluaran")


@app.route("/penerimaan/tambah", methods=["POST", "GET"])
def tambah_penerimaan():
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session.get("user_id")
    if request.method == "POST":
        jumlah = request.form.get("jumlah")
        keterangan = request.form.get("keterangan")
        catatan = request.form.get("catatan")
        tanggal = request.form.get("tanggal")
        penerimaan = True
        data = {
            "user_id": user_id,
            "jumlah": jumlah,
            "keterangan": keterangan,
            "catatan": catatan,
            "penerimaan": penerimaan,
            "tanggal": tanggal
        }
        supabase.table("pencatatan").insert(data).execute()
        return redirect("/penerimaan")
    form = {
        "action": "",
        "inputs": [
            {
                "_name": "keterangan",
                "_type": "text",
                "_text": "Keterangan",
            },
            {
                "_name": "jumlah",
                "_type": "number",
                "_text": "Jumlah",
            },
            {
                "_name": "catatan",
                "_type": "text",
                "_text": "Catatan",
            },
            {
                "_name": "tanggal",
                "_type": "date",
                "_text": "Tanggal",
            }
        ]
    }
    return render_template("tambah.html", form=form)

@app.route("/penerimaan/edit/<id>", methods=["POST", "GET"])
def edit_penerimaan(id):
    data = supabase.table("pencatatan").select("*").eq("id", id).execute()['data']
    if not data:
        return redirect("/penerimaan")
    data = data[0]
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session.get("user_id")
    if request.method == "POST":
        jumlah = request.form.get("jumlah")
        keterangan = request.form.get("keterangan")
        catatan = request.form.get("catatan")
        tanggal = request.form.get("tanggal")
        penerimaan = True
        data = {
            "user_id": user_id,
            "jumlah": jumlah,
            "keterangan": keterangan,
            "catatan": catatan,
            "penerimaan": penerimaan,
            "tanggal": tanggal
        }
        supabase.table("pencatatan").update(data).eq("id", id).execute()
        return redirect("/penerimaan")
    form = {
        "action": "",
        "inputs": [
            {
                "_name": "keterangan",
                "_type": "text",
                "_text": "Keterangan",
            },
            {
                "_name": "jumlah",
                "_type": "number",
                "_text": "Jumlah",
            },
            {
                "_name": "catatan",
                "_type": "text",
                "_text": "Catatan",
            },
            {
                "_name": "tanggal",
                "_type": "date",
                "_text": "Tanggal",
            }
        ]
    }
    return render_template("edit.html", form=form, data=data)

@app.route("/pengeluaran/tambah", methods=["POST", "GET"])
def tambah_pengeluaran():
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session.get("user_id")
    if request.method == "POST":
        jumlah = request.form.get("jumlah")
        keterangan = request.form.get("keterangan")
        catatan = request.form.get("catatan")
        tanggal = request.form.get("tanggal")
        penerimaan = False
        data = {
            "user_id": user_id,
            "jumlah": jumlah,
            "keterangan": keterangan,
            "catatan": catatan,
            "penerimaan": penerimaan,
            "tanggal": tanggal
        }
        supabase.table("pencatatan").insert(data).execute()
        return redirect("/pengeluaran")
    form = {
        "action": "",
        "inputs": [
            {
                "_name": "keterangan",
                "_type": "text",
                "_text": "Keterangan",
            },
            {
                "_name": "jumlah",
                "_type": "number",
                "_text": "Jumlah",
            },
            {
                "_name": "catatan",
                "_type": "text",
                "_text": "Catatan",
            },
            {
                "_name": "tanggal",
                "_type": "date",
                "_text": "Tanggal",
            }
        ]
    }
    return render_template("tambah.html", form=form)

@app.route("/pengeluaran/edit/<id>", methods=["POST", "GET"])
def edit_pengeluaran(id):
    data = supabase.table("pencatatan").select("*").eq("id", id).execute()['data']
    if not data:
        return redirect("/pengeluaran")
    data = data[0]
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session.get("user_id")
    if request.method == "POST":
        jumlah = request.form.get("jumlah")
        keterangan = request.form.get("keterangan")
        catatan = request.form.get("catatan")
        tanggal = request.form.get("tanggal")
        penerimaan = False
        data = {
            "user_id": user_id,
            "jumlah": jumlah,
            "keterangan": keterangan,
            "catatan": catatan,
            "penerimaan": penerimaan,
            "tanggal": tanggal
        }
        supabase.table("pencatatan").update(data).eq("id", id).execute()
        return redirect("/pengeluaran")
    form = {
        "action": "",
        "inputs": [
            {
                "_name": "keterangan",
                "_type": "text",
                "_text": "Keterangan",
            },
            {
                "_name": "jumlah",
                "_type": "number",
                "_text": "Jumlah",
            },
            {
                "_name": "catatan",
                "_type": "text",
                "_text": "Catatan",
            },
            {
                "_name": "tanggal",
                "_type": "date",
                "_text": "Tanggal",
            }
        ]
    }
    return render_template("edit.html", form=form, data=data)

@app.route("/penerimaan/hapus/<id>")
def hapus_penerimaan(id):
    data = supabase.table("pencatatan").select("*").eq("id", id).execute()['data']
    if not data:
        return redirect("/penerimaan")
    data = data[0]
    if not session.get("user_id"):
        return redirect("/login")
    try:
        supabase.table("pencatatan").delete().eq("id", id).execute()
    except json.decoder.JSONDecodeError:
        return redirect("/penerimaan")
    return redirect("/penerimaan")

@app.route("/pengeluaran/hapus/<id>")
def hapus_pengeluaran(id):
    data = supabase.table("pencatatan").select("*").eq("id", id).execute()['data']
    if not data:
        return redirect("/pengeluaran")
    data = data[0]
    if not session.get("user_id"):
        return redirect("/login")
    try:
        supabase.table("pencatatan").delete().eq("id", id).execute()
    except json.decoder.JSONDecodeError:
        return redirect("/pengeluaran")
    return redirect("/pengeluaran")

@app.route("/laporan")
def laporan():
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session.get("user_id")
    data = supabase.table("pencatatan").select("*").eq("user_id", user_id).execute()['data']
    return render_template("laporan.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)