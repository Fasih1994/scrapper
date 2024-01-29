from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime, date
import pandas as pd
import json
import os


t1 = datetime.now()
if t1 > datetime(2025,1,1) :
    print('Driver Licensed Expired!')
    exit(0)

def get_ids(html):
    soup = bs(html)
    return [x['id'] for x in soup.find_all('mat-option')]

def write(json_path,data):
    with open(json_path, 'w') as file:
        json.dump(data,file,indent=2)

def read_file(json_pah):
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

def check_exists_by_xpath(xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def scrap(No,RUC, Razón_social, Nombre_comercial, Fecha_corte):
    sub_retries = 0
    time.sleep(0.5)

    while True:
        try:
            element = 'sub_tbody'
            sub_tbody = driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/mat-dialog-container/sri-modal-mostrar-detalle-deudas-ranking/div/div[2]/div[1]/p-datatable/div/div[2]/table/tbody')
            sub_soup = bs(sub_tbody.get_attribute('innerHTML'),"html.parser")
            sub_trs = sub_soup.find_all('tr')

            for sub_tr in sub_trs:
                sub_tds = sub_tr.find_all('td')
                sub_spans = [sub_td.find_all('span') for sub_td in sub_tds]
                Provincia = sub_spans[0][1].text
                Impuesto = sub_spans[1][1].text
                Periodo = sub_spans[2][1].text
                Saldo_impuesto = sub_spans[3][1].text
                Saldo_interés = sub_spans[4][1].text
                Saldo_multa = sub_spans[5][1].text
                Saldo_recargo = sub_spans[6][1].text
                Saldo_deuda = sub_spans[7][1].text
                Fecha_emisión = sub_spans[8][1].text

                data['No'].append(No)
                data['RUC'].append(RUC)
                data['Razón_social'].append(Razón_social)
                data['Nombre_comercial'].append(Nombre_comercial)
                data['Fecha_corte'].append(Fecha_corte)
                data['Provincia'].append(Provincia)
                data['Impuesto'].append(Impuesto)
                data['Periodo'].append(Periodo)
                data['Saldo_impuesto'].append(Saldo_impuesto)
                data['Saldo_interés'].append(Saldo_interés)
                data['Saldo_multa'].append(Saldo_multa)
                data['Saldo_recargo'].append(Saldo_recargo)
                data['Saldo_deuda'].append(Saldo_deuda)
                data['Fecha_emisión'].append(Fecha_emisión)


            element="sub_next_btn"
            sub_next_btn = driver.find_element(By.XPATH,'/html/body/div[4]/div[2]/div/mat-dialog-container/sri-modal-mostrar-detalle-deudas-ranking/div/div[2]/div[1]/p-datatable/div/p-paginator/div/a[3]')
            if "ui-state-disabled" in sub_next_btn.get_attribute('class'):
                break
            else:
                sub_next_btn.click()

            time.sleep(0.3)
        except NoSuchElementException:
            if sub_retries<10:
                time.sleep(1)
                sub_retries+=1
#                 print(f"sub_retries: {sub_retries} for no element")
            else:
                break
        except ElementClickInterceptedException:
            if sub_retries<3:
                sub_retries+=1
#                 print(f"sub_retries: {sub_retries} for click")
                time.sleep(1)
            else:
                print("An Exception Occerred.")
                write(json_path, data)
                break

    element='cancel_btn'
    cancel_btn = driver.find_element(By.XPATH,'//*[@id="tabla-mostrar-deuda"]')
    cancel_btn.click()
    overlay_open=False
    time.sleep(1)


url = "https://srienlinea.sri.gob.ec/sri-en-linea/SriPagosWeb/ConsultaRankingDeudas/Consultas/consultaRankingDeudas"
driver = webdriver.Chrome()
driver.get(url)
time.sleep(1)

file_name = input('Output File Name:')

retries = 0
row_count = 1
page_count = 1
element = None
path = file_name + '.csv'
data = dict(
    No = [],
    RUC = [],
    Razón_social = [],
    Nombre_comercial  = [],
    Fecha_corte = [],
    Provincia = [],
    Impuesto = [],
    Periodo = [],
    Saldo_impuesto = [],
    Saldo_interés = [],
    Saldo_multa = [],
    Saldo_recargo = [],
    Saldo_deuda = [],
    Fecha_emisión = [],
    scraped_count = 0,

)
json_path = file_name+'.json'
if os.path.exists(json_path):
    data = read_file(json_path)
t1 = datetime.now()
while True:

    try:
        if row_count==1:
            data_btn = driver.find_element(By.XPATH,'//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ranking-deudas-web-app/div/sri-ruta-mostrar-ranking-deudas/div[1]/div[1]/div[4]/button')
            time.sleep(0.1)
            data_btn.click()
        element='tbody'
        tbody = driver.find_element(By.XPATH,'//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ranking-deudas-web-app/div/sri-ruta-mostrar-ranking-deudas/div[1]/div[2]/div/div[2]/div[2]/sri-mostrar-tabla-deudas/div/p-datatable/div/div[2]/table/tbody')
        soup = bs(tbody.get_attribute('innerHTML'),"html.parser")
        trs = soup.find_all('tr')

        for tr in trs:
            if row_count > data['scraped_count']:
                tds = tr.find_all('td')
                spans = [td.find_all('span') for td in tds]
                No = spans[0][1].text
                RUC = spans[1][1].text
                Razón_social = spans[2][1].text
                Nombre_comercial  = spans[3][1].text
                Fecha_corte = date.strftime(datetime.now(), '%d/%m/%Y')
                i= data['scraped_count']%10 +1

                element='detail_btn'
                detail_btn = driver.find_element(By.XPATH,f'//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ranking-deudas-web-app/div/sri-ruta-mostrar-ranking-deudas/div[1]/div[2]/div/div[2]/div[2]/sri-mostrar-tabla-deudas/div/p-datatable/div/div[2]/table/tbody/tr[{i}]/td[7]/span[2]/div/button')
                detail_btn.click()
                overlay_open=True
                time.sleep(0.5)
                scrap(No,RUC, Razón_social, Nombre_comercial, Fecha_corte)
                data['scraped_count']+=1
                retries = 0
                if data['scraped_count'] % 25 == 0:
                    write(json_path, data)
                print(f"scrapped_count: {data['scraped_count']}")

            row_count+=1
#             print(f"scrapped_count: {data['scraped_count']}")
#             print(i)


        element = "next_btn"
        next_btn = driver.find_element(By.XPATH,'//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ranking-deudas-web-app/div/sri-ruta-mostrar-ranking-deudas/div[1]/div[2]/div/div[2]/div[2]/sri-mostrar-tabla-deudas/div/p-datatable/div/p-paginator/div/a[3]')
        if "ui-state-disabled" in next_btn.get_attribute('class'):
            data.pop('scraped_count')
            pd.DataFrame(data).to_csv(path,index=False)
            if os.path.exists(json_path):
                os.remove(json_path)
            break
        else:
            next_btn.click()

            time.sleep(0.3)
            page_count+=1
    except NoSuchElementException:
        if retries<3:
            retries+=1
            print(f"retries: {retries} for element '{element}'")
            time.sleep(1)
        elif retries==3:
            print("Session Expired, Start a new session!")
            write(json_path, data)
            break
    except ElementClickInterceptedException:
            if retries<3:
                if check_exists_by_xpath('/html/body/div[4]/div[2]/div/mat-dialog-container/sri-modal-mostrar-detalle-deudas-ranking/div/div[2]/div[1]/p-datatable/div/div[2]/table/tbody'):
                    element = 'cancel_btn'
                    cancel_btn = driver.find_element(By.XPATH,'//*[@id="tabla-mostrar-deuda"]')
                    cancel_btn.click()

                print(f"retries: {retries} for click")
                retries+=1
                time.sleep(1)
            elif retries==3:
                print("Session Expired, Start a new session!")
                write(json_path, data)
                break
print("Total Time running: ",datetime.now()-t1)

driver.close()