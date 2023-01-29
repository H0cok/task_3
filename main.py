from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup

import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

from constants import PATH_TO_CREDENTIALS, SPREADSHEET_URL


def scrap():
    driver = webdriver.Firefox()
    url = 'https://www.olx.ua/d/uk/nedvizhimost/kvartiry/prodazha-kvartir/?currency=UAH&page={}'

    # get total number of pages
    driver.get(url.format(1))
    driver.get(url.format(1))
    html = driver.page_source

    soup = BeautifulSoup(html, features="html.parser")
    d = soup.find_all("a", class_="css-1mi714g")
    pages = int(d[-1].text)

    # creating list for rows
    df_list = []
    # going through all web pages
    for page_number in range(1, pages + 1):

        # getting BeautifulSoup object from new page
        driver.get(url.format(page_number))
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")

        # getting data from web page
        name = soup.find_all("h6")
        location_and_time = soup.find_all("p", class_="css-veheph er34gjf0")
        area = soup.find_all("span", class_="css-643j0o")
        price = soup.find_all("p", class_="css-10b0gli er34gjf0")

        # adding new rows in dict format
        for ad_num in range(len(name)):
            df_tmp = {"Text": name[ad_num].text,
                      "Location": location_and_time[ad_num].text.split("- ")[0],
                      "Time": location_and_time[ad_num].text.split("- ")[1],
                      "Price": price[ad_num].text,
                      "Area": area[ad_num].text}
            df_list.append(df_tmp)

    # creating dataframe from rows
    df = pd.DataFrame.from_records(df_list)
    df = df.drop_duplicates()
    return df


def save_to_spreadsheet(df, path_to_file, spreadsheet_url):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_file(path_to_file, scopes=scopes)
    gc = gspread.authorize(credentials)

    # open a google sheet
    gs = gc.open_by_url(spreadsheet_url)

    # select a work sheet from its name
    worksheet = gs.worksheet('OLX-apartments')

    # write to dataframe
    worksheet.clear()
    set_with_dataframe(worksheet=worksheet, dataframe=df, include_index=False,
                       include_column_header=True, resize=True)


if __name__ == "__main__":
    df = scrap()
    save_to_spreadsheet(df, PATH_TO_CREDENTIALS, SPREADSHEET_URL)
    print("Program parsed Text of the ad,\n"
          "Location of the apartment,\n"
          "Time when the ad was published\n"
          "Price of the apartment and its Area")