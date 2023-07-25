from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, request, flash,  jsonify
from flask_mysqldb import MySQL, MySQLdb
from functools import wraps
from werkzeug.utils import secure_filename
import numpy as np
from flask_cors import CORS
import os
import pickle
import random
import numpy as np
import pickle
import json
import nltk
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import re


#-------------------- Konfigurasi ----------------

app = Flask(__name__)
app.secret_key = "bigtuing"
CORS(app)
#Konfigurasi Database
#remot
app.config['MYSQL_HOST'] = '45.143.81.40'
app.config['MYSQL_USER'] = 'u1547396_doni'
app.config['MYSQL_PASSWORD'] = 'Y2-)u--*r,VU'
app.config['MYSQL_DB'] = 'u1547396_doni'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
#local

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'virtualassisten'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# mysql = MySQL(app)

#Konfigurasi folder menyiman dataset
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_KOLEKSI'] = 'static/img/'

PATH = '\\'.join(os.path.abspath(__file__).split('\\')[0:-1])
DATASET_PATH = os.path.join(PATH, "train_img")


#menampilkan  halaman admin
@app.route('/')
def admin():
    return render_template("login.html")

#roses login admin
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form["username"]
        pwd=request.form["password"]
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username=%s and password=%s",(username,pwd))
        data=cur.fetchone()
        if data:
            session['logged_in']=True
            session['username']=data["username"]
            flash('Login Berhasil','success')
            return redirect('login')
        else:
            flash('Login Gagal. Coba Lagi','danger')
    return render_template("login.html")

def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Mohon Login','danger')
			return redirect(url_for('login'))
	return wrap

#logout admin
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



#-------------------- Dashboard dan Total Tamu ----------------

#menampilkan  total tamu hari ini
@app.route('/tamuHari')
def tamuHari():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT COUNT(*) FROM daftarpengunjung WHERE tanggal = CURDATE()')
    total_hari_ini =  [v for v in cur.fetchone().values()][0]
    return total_hari_ini

#menampilkan  total tamu minggu ini
@app.route('/tamuMinggu')
def tamuMinggu():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT COUNT(*) FROM daftarpengunjung GROUP BY YEARWEEK(tanggal);')
    total_minggu_ini =  [v for v in cur.fetchone().values()][0]
    return total_minggu_ini

#menampilkan  total tamu bulan ini
@app.route('/tamuBulan')
def tamuBulan():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT COUNT(*) FROM daftarpengunjung WHERE MONTH(NOW());')
    total_bulan_ini =  [v for v in cur.fetchone().values()][0]
    return total_bulan_ini

#menampilkan  total keseluruhan tamu
@app.route('/totalTamu')
def totalTamu():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT COUNT(*) FROM daftarpengunjung')
    total_tamu =  [v for v in cur.fetchone().values()][0]
    return total_tamu


#melakukan roses rerosesing
# @app.route("/preproses")
# def preproses():
#     input_datadir = './train_img'
#     output_datadir = './pre_img'

#     obj=preprocesses(input_datadir,output_datadir)
#     nrof_images_total,nrof_successfully_aligned=obj.collect_data()

#     return render_template("proses.html")


#-------------------- Daftar Karyawan ----------------

#menampilkan  halaman tambah data
@app.route('/tambahData')
def tambahData():
    return render_template('tambahData.html')

#roses memasukan data karyawan ke database
# @app.route('/daftarKaryawan', methods=["POST"])
# def daftarKaryawan():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     if request.method == "POST":
#         nama_karyawan = request.form['karyawan']
#         email = request.form['email']
#         no_telp = request.form['no_telp']
#         alamat = request.form['alamat']
#         if not re.match(r'[A-Za-z]+', nama_karyawan):
#             flash("Nama harus pakai huruf Dong!")
#         elif not re.match(r'[0-9]+', no_telp):
#             flash("No.Telepon harus pakai angka Dong!")
#         else:
#             cur.execute("INSERT INTO karyawan (nama_lengkap,email, no_telp, alamat) VALUES (%s,%s,%s,%s)", (nama_karyawan,email, no_telp, alamat))
#             mysql.connection.commit()
#             # flash("Karyawan berhasil ditambahkan")
#             return render_template("face_registration.html")

#     return render_template("tambahData.html")

#menampilkan  fof uf karyawan
@app.route('/popuptambah')
def popuptambah():
    return render_template('popUpTambah.html')

#menampilkan  database karyawan
# @app.route('/karyawan')
# def karyawan():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
 
#     cur.execute('SELECT * FROM karyawan')
#     data = cur.fetchall()
  
#     cur.close()
#     return render_template('karyawan.html', karyawan = data)

#menampilkan  form edit data
@app.route('/editKaryawan/<id>', methods = ['POST', 'GET'])
def editKaryawan(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  
    cur.execute('SELECT * FROM karyawan WHERE id = %s', [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('editKaryawan.html', editKaryawan = data[0])

#melakukan roses edit data
@app.route('/updateKaryawan/<id>', methods=['POST'])
def updateKaryawan(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        nama = request.form['karyawan']
        email = request.form['email']
        no_telp = request.form['no_telp']
        alamat = request.form['alamat']
        if not re.match(r'[A-Za-z]+', nama):
            flash("Nama harus pakai huruf Dong!")
        elif not re.match(r'[0-9]+', no_telp):
            flash("No.Telepon harus pakai angka Dong!")
        else:
            cur.execute("""
                UPDATE karyawan
                SET nama_lengkap = %s,
                    email = %s,
                    no_telp = %s,
                    alamat = %s
                WHERE id = %s
            """, (nama, email, no_telp, alamat, id))
            flash('Layanan berhasil diupdate')
            mysql.connection.commit()
            return render_template("popUpEdit.html")

    return render_template("karyawan.html")

#menghaus daftar karyawan
@app.route('/hapusKaryawan/<string:id>', methods = ['POST','GET'])
def hapusKaryawan(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  
    cur.execute('DELETE FROM karyawan WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Karyawan Berhasil Dihapus!')
    return redirect(url_for('karyawan'))

#Prodfil Koleksi
@app.route('/koleksi')
def koleksi():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM koleksi')
    data = cur.fetchall()
    cur.close()
    return render_template('koleksi.html', koleksi = data)

#menampilkan  form tambah data
@app.route('/tambahkoleks', methods = ['POST', 'GET'])
def tambahkoleksi():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name_koleksi = request.form['namakoleksi']
        desk_koleksi = request.form['deskoleksi']
        gbr_koleksi = request.files['gambar']

        filename = secure_filename(gbr_koleksi.filename)
        gbr_koleksi.save(os.path.join(app.config['UPLOAD_KOLEKSI'], filename))
    
        cur.execute("insert into koleksi (namakoleksi,deskripsikoleksi,gambarkoleksi) values(%s,%s,%s)",(name_koleksi,desk_koleksi,filename))
        mysql.connection.commit()
        cur.close()
        return render_template('PopUpEditKoleksi.html')
    
    return render_template('koleksi.html')

@app.route('/tambahKolek')
def tambahKolek():
    return render_template('tambahkoleksi.html')

#menampilkan  form edit data
@app.route('/editkoleksi/<id>', methods = ['POST', 'GET'])
def editkoleksi(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM koleksi WHERE id = %s', [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('editkoleksi.html', editkoleksi = data[0])

#melakukan roses edit data Koleksi
@app.route('/updatekoleksi/<id>', methods=['POST'])
def updatekoleksi(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name_koleksi = request.form['namekoleksi']
        desk_koleksi = request.form['deskoleksi']
        gbr_koleksi = request.files['gambar']

        filename = secure_filename(gbr_koleksi.filename)
        gbr_koleksi.save(os.path.join(app.config['UPLOAD_KOLEKSI'], filename))
                  
        cur.execute("""
                UPDATE koleksi
                SET namakoleksi = %s,
                  deskripsikoleksi = %s,
                    gambarkoleksi = %s
                WHERE id = %s
            """, (name_koleksi, desk_koleksi, filename, id))
        flash('Layanan berhasil diupdate')
        mysql.connection.commit()
        return render_template("PopUpEditKoleksi.html")

    return render_template("koleksi.html")

@app.route('/hapuskoleksi/<string:id>', methods = ['POST','GET'])
def hapuskoleksi(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('DELETE FROM koleksi WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Admin Berhasil Dihapus!')
    return redirect(url_for('koleksi'))


#Prodfil Admin
@app.route('/profil')
def profil():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM about')
    data = cur.fetchall()
    cur.close()
    return render_template('profil.html', profil = data)

#menampilkan  form edit data Profil
@app.route('/editprofil/<id>', methods = ['POST', 'GET'])
def editprofil(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM about WHERE id = %s', [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('editprofil.html', editprofil = data[0])

#melakukan roses edit profil data
@app.route('/updateprofil/<id>', methods=['POST'])
def updateprofil(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        nama_profil = request.form['profil']
        nama_visi = request.form['visi']
        nama_misi = request.form['misi']
        cur.execute("""
                UPDATE about
                SET profil = %s,
                    visi = %s,
                    misi = %s
                    WHERE id = %s
            """, (nama_profil, nama_visi, nama_misi, id))
        flash('Layanan berhasil diupdate')
        mysql.connection.commit()
        return render_template("popupedit.html")

    return render_template("profil.html")


#.........MENAMPILKAN CHATBOT ADMIN.........#
#menampilkan  daftar tamu
@app.route('/chatbotadmin')
def chatbotadmin():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM chatbot')
    data = cur.fetchall()
    cur.close()
    return render_template('chatbotadmin.html', chatbotadmin = data)

#menampilkan  form tambah data
@app.route('/tambahChatbot', methods = ['POST'])
def tambahdataChatbot():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    name_patterns = request.form['Patterns']
    
    name_patterns = name_patterns.split(",")
    print(name_patterns)
    desk_responses = request.form['Responses']
    desk_responses = desk_responses.split(",")
    print(desk_responses)
    cur.execute("insert into chatbot (patterns,responses) values(%s,%s)",(str(name_patterns),str(desk_responses)))
    mysql.connection.commit()
    cur.close()
    print( 'chatbot\intents.json')
    with open('chatbot\intents.json', "r+") as f:
        inten = json.loads(f.read())
        import uuid,string
        letters = string.ascii_lowercase
        rando = ''.join(random.choice(letters) for i in range(4))
        y = {"tag":str(rando),
            "patterns": name_patterns,
            "responses": desk_responses,
            "context": [""]
            }
        inten['intents'].append(y)
        
        with open('chatbot\intents.json', "w+") as k:
            json.dump(inten,k)
        
    from retraining import retraining
    retraining()

    return redirect('chatbotadmin')
   

@app.route('/tambahdatachatbot')
def tambahdatachatbot():
    return render_template('tambahdatachatbot.html')

#daftar admin

@app.route('/daftaradmin')
def daftaradmin():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM admin')
    data = cur.fetchall()
    cur.close()
    return render_template('daftaradmin.html', admin = data)


@app.route('/hapusAdmin/<string:id>', methods = ['POST','GET'])
def hapusAdmin(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('DELETE FROM admin WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Admin Berhasil Dihapus!')
    return redirect(url_for('daftaradmin'))

@app.route('/tambahAdmin')
def tambahAdmin():
    return render_template('tambahAdmin.html')

@app.route('/registerAdmin',methods=['POST','GET'])
def registerAdmin():
    status=False
    if request.method=='POST':
        name=request.form["nama"]
        username=request.form["username"]
        pwd=request.form["password"]
        cur=mysql.connection.cursor()
        cur.execute("insert into admin(nama,username,password) values(%s,%s,%s)",(name,username,pwd))
        mysql.connection.commit()
        cur.close()
        flash('Daftar Berhasil. Silahkan Login...','success')
        return redirect('popupTambahAdmin')
    return render_template("tambahAdmin.html",status=status)

@app.route('/popupTambahAdmin')
def popupTambahAdmin():
    return render_template('popupTambahAdmin.html')

@app.route('/backToLogin')
def backToLogin():
    session.clear()
    return redirect(url_for('login'))

#.........MENAMPILKAN KONTAK ADMIN.........#
#menampilkan  daftar tamu
@app.route('/kontakadmin')
def kontakadmin():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM kontak')
    data = cur.fetchall()
    cur.close()
    return render_template('kontakadmin.html', kontakadmin = data)

#menampilkan  form edit data kontak
@app.route('/editkontak/<id>', methods = ['POST', 'GET'])
def editkontak(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM kontak WHERE id = %s', [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('editkontak.html', editkontak = data[0])

#melakukan roses edit profil kontak
@app.route('/updatekontak/<id>', methods=['POST'])
def updatekontak(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        nama_email = request.form['email']
        nama_nohp = request.form['notelpon']
        nama_facebook = request.form['facebook']
        nama_instagram = request.form['instagram']
        nama_youtube = request.form['youtube']
        nama_twitter = request.form['twitter']
        cur.execute("""
                UPDATE kontak
                SET email = %s,
                    nohp = %s,
                    facebook = %s,
                    instagram = %s,
                    youtube = %s,
                    twitter = %s
                    WHERE id = %s
            """, (nama_email, nama_nohp, nama_facebook, nama_instagram, nama_youtube, nama_twitter, id))
        flash('Layanan berhasil diupdate')
        mysql.connection.commit()
        return render_template("popUpEditKontak.html")

    return render_template("kontak.html")

#....HAPUS KONTAK......
@app.route('/hapuskontak/<string:id>', methods = ['POST','GET'])
def hapuskontak(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  
    cur.execute('DELETE FROM kontak WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Kontak Berhasil Dihapus!')
    return redirect(url_for('tabelTamu'))

#-------------------- Daftar Tamu ----------------

#menampilkan  daftar tamu
@app.route('/tabelTamu',methods=["POST", "GET"])
def tabelTamu():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM daftarpengunjung ORDER BY id desc")
    data = cur.fetchall()
    return render_template('dataPengunjung.html', tabelTamu = data )

#melakukan roses filter tanggal
@app.route("/jarakTanggal",methods=["POST","GET"])
def jarakTanggal(): 
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    if request.method == 'POST':
        From = request.form['From']
        to = request.form['to']
        print(From)
        print(to)
        query = "SELECT * from daftarpengunjung WHERE tanggal BETWEEN '{}' AND '{}'".format(From,to)
        cur.execute(query)
        tgl = cur.fetchall()
    return jsonify({'htmlresponse': render_template('responDataTamu.html', tgl=tgl)})

#menghaus daftar tamu
@app.route('/hapusTamu/<string:id>', methods = ['POST','GET'])
def hapusTamu(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  
    cur.execute('DELETE FROM daftarpengunjung WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Tamu Berhasil Dihapus!')
    return redirect(url_for('tabelTamu'))



#-------------------- Chatbot ----------------

@app.route("/")
def root():
    return render_template("face.html")



model = load_model("chatbot\chatbot_model.h5")
intents = json.loads(open("chatbot\intents.json").read())
print(intents)
words = pickle.load(open("chatbot\words.pkl", "rb"))
classes = pickle.load(open("chatbot\classes.pkl", "rb"))

@app.route("/get", methods=["POST"])
def chatbot_response():
    msg = request.form["msg"]
    print(msg)
    if msg.startswith('my name is'):
        name = msg[11:]
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res =res1.replace("{n}",name)
    elif msg.startswith('hi my name is'):
        name = msg[14:]
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res =res1.replace("{n}",name)
    else:
        print("jln")
        ints = predict_class(msg, model)
        print(ints)
        res = getResponse(ints, intents)
    return res

def clean_up_sentence(sentence):
    import nltk
    nltk.download('popular')
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    print(sentence_words)
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    print(bag)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    print(p)
    res = model.predict(np.array([p]))[0]
    print(res)
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    if res == []:
        return_list.append({"intent": "error", "probability": 0})
    else:
        for r in results:
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    print(return_list)
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]["intent"]
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        print(tag)
        print(i['tag'])
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break
        else:
            result = "Maaf saya tidak bisa menjawab"
    return result




if __name__ == '__main__':
    app.run(debug=True, port=5001)

