from empirical.sources import merge_recent, get_census, get_nyt
import math
import matplotlib.pyplot as plt
import numpy as np


# Density and population data, US only
# https://colab.research.google.com/drive/1ueS_UtIHshtN-68yJKBzdUfo9ressSqy#scrollTo=J2k7KOEGiZZj


if __name__=="__main__":
    nyt    = get_nyt()
    census = get_census()
    merged = merge_recent(nyt, census)
    print(merged[:4])
    merged['cases_per_capita'] = merged['cases'] / merged['pop']
    merged['deaths_per_capita'] = merged['deaths'] / merged['pop']
    merged['log_cases_per_capita'] = merged['cases_per_capita'].apply(math.log)
    merged['log_density'] = merged['density'].apply(math.log)
    merged['log_deaths_per_capita'] = merged['deaths_per_capita'].apply(lambda n: math.log(n + 1))


    plt.close()
    plt.scatter(x=merged['log_density'].values, y=merged['log_cases_per_capita'].values)
    coef = np.polyfit(x=merged['log_density'].values, y=merged['log_cases_per_capita'], deg=1)
    print(coef)
    plt.scatter(merged['log_density'].values, np.poly1d(coef)(merged['log_density'].values))
    plt.xlabel('Log population density')
    plt.ylabel('Log cases')
    plt.title(str(coef))
    plt.show()
