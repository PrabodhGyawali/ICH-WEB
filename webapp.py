import ast
import json
import os
import secrets

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from numpy import arange
from scipy import stats
from scipy.optimize import curve_fit
matplotlib.use('Agg')


def run(game, colour, line, func):

    # Defining the objective function for curve fitting
    def objective(x, a, b, c):
        return a * x + b * x**2 + c

    # Converting a string list to a list
    def stringlist_to_list(list_as_string):
        list_as_list = json.loads(list_as_string)
        return list_as_list

    # Function to get the list of files in a folder
    def games(game):
        folder = game
        files = os.listdir(folder)
        files = [file for file in files if os.path.isfile(os.path.join(folder, file))]
        return files, folder

    # Function to get the odds for a game
    def get_odds_for_game(file, name, odd, folder):

        wanted = False
        linedup = []

        with open(f'{folder}/{file}', 'r') as f:
            ope = 0
            lines = f.readlines()
            newlist = []
            for i in name:
                newlist.append(i)

            for line in lines:
                ope += 1

                if ope > 16:

                    userx = line.split(', ')

                    if userx[0] == 'oddname':

                        old = line.split(f'{newlist[-1]}, ')

                        new = old[-1].split('\n')
                        newnew = ast.literal_eval(new[0])

                        if newnew == []:
                            pass

                        else:

                            try:
                                wanted = newnew.index(odd)

                            except:
                                wanted = False


                    if wanted != False:


                        if userx[0] == 'bookmakerodds':

                            old = line.split(f's, ')
                            new = old[-1].split('\n')
                            newnew = ast.literal_eval(new[0])

                            if newnew == []:
                                pass

                            else:

                                empty = []
                                for i in newnew[wanted]:
                                    num = i.split('/')
                                    newnum = round(int(num[0])/int(num[-1]), 2) + 1

                                    empty.append(newnum)


                                linedup.append(round(max(empty), 2))


        return linedup

    # Function to plot the graph
    def map(gamedhsa, colord, line, func):

        # Curve fitting using polynomial function
        if func == 'polynomial':
            fig, ax = plt.subplots()
            folder = 'table'
            funny = games(folder)[0]
            ind = funny.index(gamedhsa)

            u = funny[ind]

            name = 'oddname'
            ypoints = np.array(get_odds_for_game(u, name, f'Over {line}', games(folder)[1]))

            xlits = []
            for x in range(len(ypoints)): xlits.append(x)
            xpoints = np.array(xlits)

            popt, _ = curve_fit(objective, xpoints, ypoints)

            a, b, c = popt

            plt.scatter(xpoints, ypoints)

            x_line = arange(min(xpoints), max(xpoints), 1)

            y_line = objective(x_line, a, b, c)

            colors = [colord]

            # Plotting the graph
            plt.plot(x_line, y_line, '--', color=colors[0], linewidth=2, markersize=8, label=f'{round(a, 3)}x + {round(b, 3)}x^2 + {round(c, 3)}')

            plt.xlabel('Time', fontsize=14, fontweight='bold')
            plt.ylabel('Odd', fontsize=14, fontweight='bold')
            plt.title(u, fontsize=16, fontweight='bold')

            plt.grid(True, linestyle='--', alpha=0.5)

            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)

            plt.xlim(min(x_line), max(x_line))
            plt.ylim(min(y_line), max(y_line))

            slope, intercept, r_value, p_value, std_err = stats.linregress(xpoints, ypoints)
            r_squared = r_value ** 2
            plt.annotate(f'R-squared = {r_squared:.2f}', xy=(0.8, 0.1), xycoords='axes fraction')

            plt.legend(loc='upper right', fontsize=12, fancybox=True, framealpha=1, shadow=True)

            plt.gca().set_facecolor('#f7f7f7')

            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['bottom'].set_linewidth(0.5)
            plt.gca().spines['left'].set_linewidth(0.5)

            plt.tight_layout()

            os.makedirs('static/images', exist_ok=True)

            newu = u.split('.txt')
            plt.savefig(f'static/images/{newu[0]}.png')
            plt.close()

    return map(game, colour, line, func)


def generate_new_api_key():
    new_key = secrets.token_hex(16)
    # maybe create another db to add to
    # "api_key" would be a foreign key
    return new_key