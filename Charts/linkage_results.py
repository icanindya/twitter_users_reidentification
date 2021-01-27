import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# set width of bar
barWidth = 0.15

# set height of bar
city_y1 = [(x / 9965) * 100 for x in [4742, 5036, 5863, 6812, 9177, 9439, 9780]]
city_y2 = [(x / 9965) * 100 for x in [3384, 3090, 2263, 740, 788, 526, 185]]
city_y3 = [(x / 9965) * 100 for x in [1839, 1839, 1839, 2413, 0, 0, 0]]

zip_y1 = [(x / 9965) * 100 for x in [5370, 5650, 6051, 7070, 9738, 9815, 9916]]
zip_y2 = [(x / 9965) * 100 for x in [2633, 2353, 1952, 305, 227, 150, 49]]
zip_y3 = [(x / 9965) * 100 for x in [1962, 1962, 1962, 2590, 0, 0, 0]]

county_y1 = [(x / 9965) * 100 for x in [4279, 4646, 5222, 6441, 8481, 8958, 9598]]
county_y2 = [(x / 9965) * 100 for x in [4274, 3907, 3331, 1290, 1484, 1007, 367]]
county_y3 = [(x / 9965) * 100 for x in [1412, 1412, 1412, 2234, 0, 0, 0]]


# Set position of bar on X axis
r1 = np.arange(len(city_y1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]

# Make the plot
# fig = plt.figure()

plt.figure(figsize = (3,1))
gs1 = gridspec.GridSpec(3, 1)
gs1.update(wspace=0.05, hspace=0.5) # set the spacing between axes.

# ax1 = fig.add_subplot(311)
ax1 = plt.subplot(gs1[0])

ax1.bar(r1, city_y1, color='#4472c4', width=barWidth, edgecolor='white', label='True Matches')
ax1.bar(r2, city_y2, color='#ed7d31', width=barWidth, edgecolor='white', label='False Matches')
ax1.bar(r3, city_y3, color='#a5a5a5', width=barWidth, edgecolor='white', label='Unmatched')

# Add xticks on the middle of the group bars
ax1.set_xlabel('(a) City information available for Twitter users', fontweight='bold')
ax1.set_xticks([r + barWidth for r in range(len(city_y1))])
ax1.set_xticklabels(['(i)\nTwitter Name',
                        '(ii)\nTwitter Name\nPredicted Attributes',
                        '(iii)\nTwitter Name\nOriginal Attributes',
                        '(iv)\nTwitter Name\nPredicted Attributes\nBirth Day',
                        '(v)\nActual Name',
                        '(vi)\nActual Name\nPredicted Attributes',
                        '(vii)\nActual Name\nOriginal Attributes'])
ax1.set_ylabel('% of Occurences', fontweight='bold')
# Create legend & Show graphic
ax1.legend()

# ax2 = fig.add_subplot(312)
ax2 = plt.subplot(gs1[1])

ax2.bar(r1, zip_y1, color='#4472c4', width=barWidth, edgecolor='white', label='True Matches')
ax2.bar(r2, zip_y2, color='#ed7d31', width=barWidth, edgecolor='white', label='False Matches')
ax2.bar(r3, zip_y3, color='#a5a5a5', width=barWidth, edgecolor='white', label='Unmatched')

# Add xticks on the middle of the group bars
ax2.set_xlabel('(b) ZIP code information available for Twitter users', fontweight='bold')
ax2.set_xticks([r + barWidth for r in range(len(city_y1))])
ax2.set_xticklabels(['(i)\nTwitter Name',
                        '(ii)\nTwitter Name\nPredicted Attributes',
                        '(iii)\nTwitter Name\nOriginal Attributes',
                        '(iv)\nTwitter Name\nPredicted Attributes\nBirth Day',
                        '(v)\nActual Name',
                        '(vi)\nActual Name\nPredicted Attributes',
                        '(vii)\nActual Name\nOriginal Attributes'])
ax2.set_ylabel('% of Occurences', fontweight='bold')
# Create legend & Show graphic
ax2.legend()

# ax3 = fig.add_subplot(313)
ax3 = plt.subplot(gs1[2])

ax3.bar(r1, county_y1, color='#4472c4', width=barWidth, edgecolor='white', label='True Matches')
ax3.bar(r2, county_y2, color='#ed7d31', width=barWidth, edgecolor='white', label='False Matches')
ax3.bar(r3, county_y3, color='#a5a5a5', width=barWidth, edgecolor='white', label='Unmatched')

# Add xticks on the middle of the group bars
ax3.set_xlabel('(c) County information available for Twitter users', fontweight='bold')
ax3.set_xticks([r + barWidth for r in range(len(city_y1))])
ax3.set_xticklabels(['(i)\nTwitter Name',
                        '(ii)\nTwitter Name\nPredicted Attributes',
                        '(iii)\nTwitter Name\nOriginal Attributes',
                        '(iv)\nTwitter Name\nPredicted Attributes\nBirth Day',
                        '(v)\nActual Name',
                        '(vi)\nActual Name\nPredicted Attributes',
                        '(vii)\nActual Name\nOriginal Attributes'])
ax3.set_ylabel('% of Occurences', fontweight='bold')
# Create legend & Show graphic
ax3.legend()
plt.subplots_adjust(wspace=None, hspace=None)
plt.tight_layout()
plt.show()
