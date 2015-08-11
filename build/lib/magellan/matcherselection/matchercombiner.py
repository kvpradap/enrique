import numpy as np

class MajorityVote(object):
    def combine(self, predictions):
        """
        Combine predictions from multiple classifiers

        Parameters
        ----------
        predictions : numpy array, shape = [num_samples, num_classifiers]

        Returns
        -------
        combined_prediction : numpy array, shape = [num_samples]
            predicted class labels
        """
        combined_prediction = np.apply_along_axis(lambda x: np.argmax(np.bincount(x)), axis=1, arr=predictions)
        return combined_prediction

