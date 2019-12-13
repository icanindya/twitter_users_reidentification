import recordlinkage as rl
from recordlinkage.datasets import load_krebsregister

krebs_X, krebs_true_links = load_krebsregister(missing_values=0)

print(krebs_true_links)

# Train the classifier
ecm = rl.ECMClassifier(binarize=0.8)
result_ecm = ecm.fit_predict(krebs_X)

len(result_ecm)

print(rl.confusion_matrix(krebs_true_links, result_ecm, len(krebs_X)))

# The F-score for this classification is
print(rl.fscore(krebs_true_links, result_ecm))

print(ecm.log_weights)
