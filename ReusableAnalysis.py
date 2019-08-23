# ---------------------------------------------------------------------------
# John Von Holle, 081819
# Description: Return values from HIFLD fire department API and perform a simple analysis of a State's departments
# grouped by number per City. Display the top five cities in a graph derived from PANDAS and MATHPLOTLIB.
# ---------------------------------------------------------------------------

# Import modules
import os
import json
from datetime import date
import requests
from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time

# api call and data analysis - hifld data
class apiCall:
    def __init__(self, url, paraSt, paraAT):
        self.url = url
        self.paraSt = paraSt
        self.paraAT = paraAT

    def getResp(self):
        try:  # requests will auto encode if formatted with 'params' in a dictionary.
            outfields = 'HIFLDID', 'STATIONNAME', 'PHYSICALADDRESS', 'PHYSICALCITY', 'PHYSICALSTATE', 'PHYSICALZIP'
            response = requests.get(
                self.url,
                params={'returnGeometry': 'true', 'f': 'json', 'outFields': outfields,
                        'where': "PHYSICALSTATE='{0}'".format(self.paraSt)}
            )
            # return response, ex. # ('www.github.com', params={'q': 'query'})
            print(response.status_code)
            print(response.url)
            data = response.json()
            return data
        except Exception as e:
            print("There was an exception: " + str(e))

    # process resp. from dataset, hifld fire dataset, perform a simple analysis and plot with Pandas & Mathplotlib libs.
    def analyzeResp(self, resp_data):
        # the response from esri is dict, 'features': ['attributes'...]
        fs = resp_data['features']  # 'features' is a list of 'attr' dictionaries.
        # create headers list, use the first dict. from features, which is attributes
        headfs = resp_data['features'][0]['attributes']
        headers = [h for h in headfs.keys()]
        print(headers)

        # create pandas df for analysis
        df = pd.DataFrame(columns=headers)
        for i, item in enumerate(fs):
            # add the dictionary of each value to pandas dataframe
            iObj = item['attributes']
            vallist = []
            # loop through each feature/data dictionary and create list of values to add to df.
            for k, v in iObj.items():
                vallist.append(v)
            # add the rows to the df.
            df.loc[i] = vallist

        # show the first five rows of df.  # print(df.head())

        # plot the number of fd's per city in the State from the table with the value_counts() func.
        # df.'column to count'.value_counts(), add nlargest(n) to display the top 5 results.
        plt.style.use('ggplot')
        unqdf = df[self.paraAT].value_counts().nlargest(5)  # PHYSICALCITY or ...ZIP
        # extra only the values from the target field.
        top5Cities = unqdf.index.tolist()

        plt.bar(top5Cities, unqdf, align='center', alpha=0.5, color='blue')
        plt.xlabel('Cities')
        plt.ylabel('Depts. per City')
        plt.title('Top Five - Cities with Most Depts.')

        print(unqdf)
        # example_df = df.loc[['OBJECTID'], ['PHYSICALSTATE']] or #unqdf.plot()
        # plt.plot(unqdf, label='Depts. per City')
        plt.show()

def main():
    # Properties
    url = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Fire_Stations_(2019_Partial_Data_Set)/' \
          'FeatureServer/0/query?'
    # para = {'returnGeometry': 'true', 'f': 'json', 'outFields': outfields, 'where': "PHYSICALSTATE='SD'"}  # '1=1'

    # Collect the input parameters from the form.
    paraSt = 'MS'  # contact.form.State  inp1  #
    paraAT = 'PHYSICALCITY'  # contact.form.analType  inp2  #
    # instantiate the class
    apiC = apiCall(url, paraSt, paraAT)
    resp1 = apiC.getResp()
    print(resp1)
    # pause the application to receive response.
    time.sleep(15)
    # pass in the analysis configuration function with the response
    procR = apiC.analyzeResp(resp1)
    print(procR)

if __name__ == '__main__':
    main()
