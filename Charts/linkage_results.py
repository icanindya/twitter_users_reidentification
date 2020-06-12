import numpy as np
import matplotlib.pyplot as plt

# set width of bar
barWidth = 0.15

# set height of bar
bars1 = [(x/9965) * 100 for x in [4742, 5036, 5863, 6812, 9177, 9439, 9780]]
bars2 = [(x/9965) * 100 for x in [3384, 3090, 2263, 740, 788, 526, 185]]
bars3 = [(x/9965) * 100 for x in [1839, 1839, 1839, 2413, 0, 0, 0]]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]

# Make the plot
plt.bar(r1, bars1, color='#4472c4', width=barWidth, edgecolor='white', label='True Matches')
plt.bar(r2, bars2, color='#ed7d31', width=barWidth, edgecolor='white', label='False Matches')
plt.bar(r3, bars3, color='#a5a5a5', width=barWidth, edgecolor='white', label='Unmatched')

# Add xticks on the middle of the group bars
plt.xlabel('Different Scenarios for Re-identification', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], ['(i)\nTwitter Name',
                                                       '(ii)\nTwitter Name\nPredicted Attributes',
                                                       '(iii)\nTwitter Name\nOriginal Attributes',
                                                       '(iv)\nTwitter Name\nPredicted Attributes\nBirthday',
                                                       '(v)\nActual Name',
                                                       '(vi)\nActual Name\nPredicted Attributes',
                                                       '(vii)\nActual Name\nOriginal Attributes'])
plt.ylabel('% of Occurances', fontweight='bold')
# Create legend & Show graphic
plt.legend()
plt.tight_layout()
plt.show()
