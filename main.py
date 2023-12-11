from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
from xlsx2html import xlsx2html
from html2excel import ExcelParser
import bs4
import os

app = Flask(__name__)
upload_path = 'convertr/'

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/convert/<var>/<err>")
def convert(var, err):
    return render_template("convert.html", variable = var, err = err)


@app.route("/download", methods=['POST'])
def download():
    if request.method == 'POST':
        name = request.form.get('name')
        html = request.form.get('html')
        try:
            f = open(upload_path+name+".html", "w")
            f.write(html)
            f.close()
            return send_file(name+'.html', as_attachment=True)
        except:
            return render_template('download.html', html = "Due to some error, file cannot be downloaded!", err = "1", name = "0")
        finally:
            if(os.path.isfile(upload_path+name+'.html')):
                os.remove(upload_path+name+'.html')


def x2h(ename, name):
    try:
        out_stream = xlsx2html(ename)
        out_stream.seek(0)
        html = out_stream.read()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        formatter = bs4.formatter.HTMLFormatter(indent=4)
        html = soup.prettify(formatter=formatter)
        return render_template('download.html', html = html, err = "0", name = name)
    except:
        try:
            df = pd.read_excel(ename)
            html = df.to_html(index=False)
            soup = bs4.BeautifulSoup(html, 'html.parser')
            formatter = bs4.formatter.HTMLFormatter(indent=4)
            html = soup.prettify(formatter=formatter)
            return render_template('download.html', html = html, err = "0", name = name)
        except:
            return render_template('download.html', html = "Due to some error, HTML cannot be generated!", err = "1", name = "0")
    finally:
        if(os.path.isfile(ename)):
            os.remove(ename)


def c2h(fname, name):
    try:
        df = pd.read_csv(fname)
        html = df.to_html(index=False, header=False)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        formatter = bs4.formatter.HTMLFormatter(indent=4)
        html = soup.prettify(formatter=formatter)
        return render_template('download.html', html = html, err = "0", name = name)
    except:
        return render_template('download.html', html = "Due to some error, HTML cannot be generated!", err = "1", name="0")
    finally:
        if os.path.isfile(fname):
            os.remove(fname)


def h2x(hname, name):
    try:
        parser = ExcelParser(hname)
        parser.to_excel(upload_path+name+'.xlsx')
        return send_file(name+'.xlsx', as_attachment=True)
    except:
        try:
            table = pd.read_html(hname)
            table.to_excel(upload_path+name+'.xlsx')
            return send_file(name+'.xlsx', as_attachment=True)
        except:
            return render_template('download.html', html = "Due to some error, File cannot be converted!", err = "1", name="0")
    finally:
        if os.path.isfile(hname):
            os.remove(hname)
        if os.path.isfile(upload_path+name+'.xlsx'):
            os.remove(upload_path+name+'.xlsx')


def h2c(hname, name):
    try:
        df = pd.read_html(hname)[0]
        df.to_csv(upload_path+name+".csv", index=False, header=False)
        return send_file(name+'.csv', as_attachment=True)
    except:
        return render_template('download.html', html = "Due to some error, File cannot be converted!", err = "1", name = "0")
    finally:
        if os.path.isfile(hname):
            os.remove(hname)
        if os.path.isfile(upload_path+name+'.csv'):
            os.remove(upload_path+name+'.csv')


@app.route('/success/<var>', methods = ['POST'])
def success(var):
    if request.method == 'POST':
        f = request.files['file']
        try:
            f.save(upload_path+f.filename)
        except:
            return redirect(url_for('convert', var = var, err = "File cannot be fetched. Try again!"))

        if var == 'x2h':
            if f.filename.endswith('xlsx'):
                name = f.filename.replace(".xlsx", "")
                return x2h(upload_path+f.filename, name)
            else:
                if os.path.isfile(upload_path+f.filename):
                    os.remove(upload_path+f.filename)
                return redirect(url_for('convert', var = var, err = "Select XLSX file only!"))
        elif var == 'c2h':
            if f.filename.endswith('csv'):
                name = f.filename.replace(".csv", "")
                return c2h(upload_path+f.filename, name)
            else:
                if os.path.isfile(upload_path+f.filename):
                    os.remove(upload_path+f.filename)
                return redirect(url_for('convert', var = var, err = "Select CSV file only!"))
        elif var == 'h2x':
            if f.filename.endswith('html'):
                name = f.filename.replace(".html", "")
                return h2x(upload_path+f.filename, name)
            else:
                if os.path.isfile(upload_path+f.filename):
                    os.remove(upload_path+f.filename)
                return redirect(url_for('convert', var = var, err = "Select HTML file only!"))
        elif var == 'h2c':
            if f.filename.endswith('html'):
                name = f.filename.replace(".html", "")
                return h2c(upload_path+f.filename, name)
            else:
                if os.path.isfile(upload_path+f.filename):
                    os.remove(upload_path+f.filename)
                return redirect(url_for('convert', var = var, err = "Select HTML file only!"))
        return redirect(url_for('home'))


# if __name__ == "__main__":
#     app.run(debug=True)
