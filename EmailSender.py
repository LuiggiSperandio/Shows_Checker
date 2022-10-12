import requests
from bs4 import BeautifulSoup
import pandas as pd
from os import environ
import smtplib
import email.message
from models.RawData import RawData

def enviar_email(corpo_email='', Subject='', to=''):
    corpo_email = corpo_email

    msg = email.message.Message()
    msg['Subject'] = Subject
    msg['From'] = environ['MY_EMAIL']
    msg['To'] = to
    password = environ['PW_SHOWCHECKER']
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.connect('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], msg['To'], msg.as_string().encode('utf-8'))

def uploadMongo(upload_dict = {}, apiName=''):
    data = upload_dict
    model = RawData(
        data=data,
        apiName=apiName
    )
    model.save()

r = requests.get('https://gilbertogil.com.br/agenda/')
df = pd.DataFrame()
soup = BeautifulSoup(r.text, 'html.parser')

iteracao = 0
for item in soup.find_all('p'):
    iteracao += 1 
    if iteracao == 1:
        temp_dict = {'Data_Show': str(item)[11:-13]}
    if iteracao == 2:
        temp_dict = temp_dict | {'Nome_Show': str(item)[11:-13]}
    if iteracao == 3:
        temp_dict = temp_dict | {'Cidade': str(item)[11:-13]}
    if iteracao == 4:
        temp_dict = temp_dict | {'Local': str(item)[11:-13]}
        df_temp = pd.DataFrame.from_dict([temp_dict])
        df = pd.concat([df, df_temp])
        iteracao = 0

df['Cidade'] = df.Cidade.str.upper()

yesterday_data = RawData.objects.order_by('-createdAt').limit(1)[0]['data']
df1 = pd.DataFrame()
for coluna in yesterday_data:
    df1[coluna] = yesterday_data[coluna]

uploadMongo(upload_dict=df.to_dict(orient='list'), apiName='ShowChecker')

df = df.reset_index()
df.drop(columns=['index'], axis=1, inplace=True)
df = df[:-4]
df1 = df1[:-4]


if df.equals(df1) and df.shape[0] <= df1.shape[0]:
    print('Sem novos shows')
else:
    corpo_email = f"""
    <p>Existem novos shows do Gil disponíveis</p>
    <p>Acesse o site para verificar o novo show</p>
    <p>https://gilbertogil.com.br/agenda/</p>
    <p></p>
    <p><img src="https://portal.unit.br/wp-content/uploads/2022/02/GILBERTO-GIL_Credito_Fernando-Young_Divulgacao-1-492x413.jpg" alt="Foto do Gil"></p>
    """
    Subject = f'Novos Shows do Gil disponíveis!'

    email_list = environ['SEND_EMAIL_TO'].split(',')
    for email_to in email_list:
        enviar_email(corpo_email=corpo_email, Subject=Subject, to=email_to)
        print(f'Email send to {email_to}')