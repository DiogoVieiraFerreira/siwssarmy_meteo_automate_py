from bs4 import BeautifulSoup as bs
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import date, timedelta
import codecs
import time
import unidecode
import locale
import re

file_name = "meteo"

locale.setlocale(locale.LC_ALL, "fr_FR.utf-8")

def get_swissmeteo_graph(driver: WebDriver) -> bs :
    graph_elem = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div/div[3]/div[1]/div[2]/div/div[1]/div[3]/div/div/section[1]")
    graph_html = graph_elem.get_attribute("outerHTML")
    soup = bs(graph_html, "html.parser")
    # remove flags inform the definition of numbers of red and blue section
    elems = soup.select(".highcharts-axis")
    elems[-1].extract()
    elems[-2].extract()
    # remove useless html elements
    soup.select_one("h2").extract()
    soup.select_one("form").extract()
    soup.select_one("div#forecast-table__holder").extract()
    soup.select_one("div.chart-control.overview-chart-control").extract()
    # remove the line with current hour
    elems = soup.select_one("svg").find_all(recursive=False)
    for i in range(1,4):
        elems[-i].extract()
    # add domain on href of the image tags
    image_tags = soup.select_one("svg").find_all("image")
    for tag in image_tags:
        tag["xlink:href"] = f"https://www.meteosuisse.admin.ch{tag['xlink:href']}" 
    # add the red and blue flag
    soup.select_one("div div div").append(bs('<div style="position: absolute;left: 0px;top: 0px;"><span visibility="visible" zindex="7" style="position: absolute;white-space: nowrap;font-family: FrutigerLTW02-55Roman;font-size: 12px;color: rgb(0, 0, 0);font-weight: normal;margin-left: 0px;margin-top: 0px;transform: rotate(0deg);transform-origin: 0% 13px 0px;left: 0.233334px;top: -13px;"><div style="padding-right: 1em;text-align: left;background-color: #f17777;padding: .4em;padding-right: 0.4em;position: absolute;top: 13px;line-height: 18px;">Précipitations en mm/h<div style="content: &quot;&quot;;position: absolute;display: block;z-index: 2;bottom: -5px;border-style: solid;border-width: 5px 5px 0;margin-left: -20px;left: 2.5em;border-color: #f17777 transparent;"></div></div></span></div>', "html.parser"))
    # <!-- red arrow -->
    # <div style="position: absolute;left: 0px;top: 0px;">
    #     <span visibility="visible" zindex="7" style="position: absolute;white-space: nowrap;font-family: FrutigerLTW02-55Roman;font-size: 12px;color: rgb(0, 0, 0);font-weight: normal;margin-left: 0px;margin-top: 0px;transform: rotate(0deg);transform-origin: 0% 13px 0px;left: 0.233334px;top: -13px;">
    #         <div style="padding-right: 1em;text-align: left;background-color: #f17777;padding: .4em;padding-right: 0.4em;position: absolute;top: 13px;line-height: 18px;">
    #             Précipitations en mm/h
    #             <div style="content: &quot;&quot;;position: absolute;display: block;z-index: 2;bottom: -5px;border-style: solid;border-width: 5px 5px 0;margin-left: -20px;left: 2.5em;border-color: #f17777 transparent;"></div>
    #         </div>
    #     </span>
    # </div>

    soup.select_one("div div div").append(bs('<div style="position: absolute; left: 0px; top: 0px;"><span style="position: absolute; white-space: nowrap; font-family: FrutigerLTW02-55Roman; font-size: 12px; color: rgb(0, 0, 0); font-weight: normal; margin-left: 0px; margin-top: 0px; transform: rotate(0deg); transform-origin: 0% 13px 0px; left: 563.767px; top: -13px;" zindex="7" visibility="visible"><div style="padding-left: 1em;text-align: right;right: 0;background-color: #adddf6;padding: .4em;padding-left: 0.4em;position: absolute;top: 13px;line-height: 18px;">Précipitations en mm/h<div style="content: &quot;&quot;;position: absolute;display: block;z-index: 2;bottom: -5px;border-style: solid;border-width: 5px 5px 0;margin-right: -20px;right: 2.5em;border-color: #adddf6 transparent;"></div></div></span></div>', "html.parser"))
    # <!-- blue arrow -->
    # <div style="position: absolute; left: 0px; top: 0px;">
    #     <span style="position: absolute; white-space: nowrap; font-family: FrutigerLTW02-55Roman; font-size: 12px; color: rgb(0, 0, 0); font-weight: normal; margin-left: 0px; margin-top: 0px; transform: rotate(0deg); transform-origin: 0% 13px 0px; left: 563.767px; top: -13px;" zindex="7" visibility="visible">
    #         <div style="padding-left: 1em;text-align: right;right: 0;background-color: #adddf6;padding: .4em;padding-left: 0.4em;position: absolute;top: 13px;line-height: 18px;">
    #             Précipitations en mm/h
    #             <div style="content: &quot;&quot;;position: absolute;display: block;z-index: 2;bottom: -5px;border-style: solid;border-width: 5px 5px 0;margin-right: -20px;right: 2.5em;border-color: #adddf6 transparent;"></div>
    #         </div>
    #     </span>
    # </div>

    return soup




driver = webdriver.Firefox()
driver.get("https://www.meteosuisse.admin.ch/home.html?tab=overview")
assert "MétéoSuisse" in driver.title
search_bar = driver.find_element_by_id("forecast_local_input")

search_bar.clear()
search_bar.send_keys("romont")
search_bar.send_keys(Keys.RETURN)
driver.implicitly_wait(7)
time.sleep(3)

# Get today graph
today_graph = get_swissmeteo_graph(driver)

# Get six days graph
six_days_button = driver.find_element_by_class_name("day-switch__item.day-switch__item--overview")
six_days_button.click()
time.sleep(3)
six_days_graph = get_swissmeteo_graph(driver)

# create the custom HTML file
html_file_soup = bs("<!DOCTYPE html><html><head><meta charset='utf-8'><title>météo suisse pas chère</title></head><body><h1 style='width: 100%;text-align: center;font-family: \"_SwissArmy\";'>METEO SUR LA PLACE D'ARME DE DROGNENS</h1></body></html>","html.parser")
body = html_file_soup.select_one("body")

today = date.today()
six_day = date.today() + timedelta(days=5)
current_month = today.strftime("%B")
second_title = ""
if(today.month == six_day.month):
    second_title = unidecode.unidecode(f"du {today.day} au {six_day.day} {current_month}")
else:
    next_month = six_day.strftime("%B")
    second_title = unidecode.unidecode(f"du {today.day} {current_month} au {six_day.day} {next_month}")

titles = f"<div style='display: flex;justify-content: space-around;font-family: \"_SwissArmy\";'><h2>AUJOURD'HUI / HEUTE</h2><h2>{second_title}</h2></div>"
main_div = bs("<div style='display: flex;justify-content: space-around;font-family: \"Frutiger Neue W02 Bd\",Times,sans-serif;'></div>", "html.parser")
main_div.select_one("div").append(today_graph)
main_div.select_one("div").append(six_days_graph)
body.append(bs(titles, "html.parser"))
body.append(main_div)
file = codecs.open(f"{file_name}.html","w", "utf-8")
file.writelines(html_file_soup.prettify())
file.close()
# driver.close()
