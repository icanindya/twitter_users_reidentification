import matplotlib.pyplot as plt
import numpy as np

x1 = [25, 50, 75, 100, 125, 150]
x2 = [10, 20, 30, 40, 50]

y_gen_1 = [49.87, 53.79, 55.12, 56.59, 57.40, 60.70] #
y_sex_1 = [77.33, 80.09, 82.47, 83.84, 84.59, 87.84] #
y_race_1 = [71.56, 73.51, 74.55, 75.51, 75.88, 79.40] #
y_party_1 = [49.77, 51.20, 51.77, 53.22, 53.36, 55.86] #

y_gen_2 = [56.55, 56.22, 57.32, 57.98, 58.80]
y_sex_2 = [83.99, 85.30, 85.33, 86.28, 86.37]
y_race_2 = [77.97, 78.52, 78.69, 79.08, 79.83]
y_party_2 = [54.24, 54.52, 54.64, 55.08, 55.66]

fig = plt.figure()

ax1 = fig.add_subplot(121)
ax1.set_xlabel('Num. of tweets per row\n(Num. of rows = 37.5K)')
ax1.set_ylabel('Prediction accuracy (%)')

ax1.plot(x1, y_gen_1, color='#009900', alpha=0.8, marker='o', ls='-', label='Generation')
ax1.plot(x1, y_sex_1, color='#ff8000', alpha=0.8, marker='D', ls='-', label='Sex')
ax1.plot(x1, y_race_1, color='#2952a3', alpha=0.8, marker='s', ls='-', label='Race')
ax1.plot(x1, y_party_1, color='#ff1a1a', alpha=0.8, marker="^", ls='-', label='Party Affiliation')

ax1.set_xticks(x1)
ax1.set_xticklabels([str(v) for v in x1[:-1]] + ['(all)'])
ax1.set_ylim(bottom=48, top=90)

# handles, labels = ax1.get_legend_handles_labels()
# fig.legend(handles, labels, loc='lower center', ncol=4)
# plt.tight_layout()
# plt.show()


ax2  = fig.add_subplot(122)
ax2.set_xlabel('Num. of rows\n(Num. of tweets per row >= 50)')
# ax2.set_ylabel('Prediction accuracy (%)')

ax2.plot(x2, y_gen_2, color='#009900', alpha=0.8, marker='o', ls='-', label='Generation')
ax2.plot(x2, y_sex_2, color='#ff8000', alpha=0.8, marker='D', ls='-', label='Gender')
ax2.plot(x2, y_race_2, color='#2952a3', alpha=0.8, marker='s', ls='-', label='Race')
ax2.plot(x2, y_party_2, color='#ff1a1a', alpha=0.8, marker="^", ls='-', label='Party Affiliation')

ax2.set_xticks(x2)
ax2.set_xticklabels([str(v)+ 'K' for v in x2])
ax2.set_ylim(bottom=48, top=90)

handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=4)
plt.tight_layout()
plt.show()



