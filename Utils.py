import pickle
from ftplib import FTP
import pandas as pd
import os
import zipfile
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def refreshStocksList():
    print("Connecting to FTP and retrieving stocks list...")
    ftp = FTP('ftp.nasdaqtrader.com')
    ftp.login()
    ftp.cwd('SymbolDirectory')
    ftp.retrbinary('RETR nasdaqlisted.txt', open('nasdaqlisted.txt', 'wb').write)
    ftp.retrbinary('RETR otherlisted.txt', open('otherlisted.txt', 'wb').write)


def readFileContent(i_source, i_separator, i_header=True):
    if (i_source == 'NASDAQ'):
        return pd.read_csv('nasdaqlisted.txt', sep=i_separator, header=i_header)
    else:
        return pd.read_csv('otherlisted.txt', sep=i_separator, header=i_header)


def zip_files(list):

    zip_file_list = zipfile.ZipFile("zipFileList.zip", "w", compression=zipfile.ZIP_DEFLATED,)

    for file in list:
        zip_file_list.write(file)
    zip_file_list.close()

    return os.path.abspath("zipFileList.zip")


def mail_zipped_files(send_from, send_to, subject, text, filename, server="smtp.gmail.com", port=587, username='', password='', isTls=True):

    msg = MIMEMultipart()

    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(filename, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
    msg.attach(part)

    mailServer = smtplib.SMTP(server, port)
    mailServer.ehlo()
    if isTls:
        mailServer.starttls()
    mailServer.ehlo()
    print(username, password)
    mailServer.login(username, password)
    mailServer.sendmail(send_from, send_to, msg.as_string())
    mailServer.close()


def sendMail(send_from, send_to, filename):
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = 'Our family reunion'
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = send_from
    msg['To'] = send_to
    msg.preamble = 'PythonStocksAnalyzer Output'

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(filename, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
    msg.attach(part)

    # Send the email via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.sendmail(send_from, send_to, msg.as_string())
    s.quit()
