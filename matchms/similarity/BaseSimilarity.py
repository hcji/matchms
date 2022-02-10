from abc import abstractmethod
from typing import List
import numpy
from matchms.typing import SpectrumType


class BaseSimilarity:
    """Similarity function base class.
    When building a custom similarity measure, inherit from this class and implement
    the desired methods.

    Attributes
    ----------
    is_commutative
       Whether similarity function is commutative, which means that the order of spectrums
       does not matter (similarity(A, B) == similarity(B, A)). Default is True.
    """
    # Set key characteristics as class attributes
    is_commutative = True
    # Set output data type, e.g. "float" or [("score", "float"), ("matches", "int")]
    score_datatype = numpy.float64

    @abstractmethod
    def pair(self, reference: SpectrumType, query: SpectrumType) -> float:
        """Method to calculate the similarity for one input pair.

        Parameters
        ----------
        reference
            Single reference spectrum.
        query
            Single query spectrum.

        Returns
            score as numpy array (using self.score_datatype). For instance returning
            numpy.asarray(score, dtype=self.score_datatype)
        """
        raise NotImplementedError

    def matrix(self, references: List[SpectrumType], queries: List[SpectrumType],
               is_symmetric: bool = False) -> numpy.ndarray:
        """Optional: Provide optimized method to calculate an numpy.array of similarity scores
        for given reference and query spectrums. If no method is added here, the following naive
        implementation (i.e. a double for-loop) is used.

        Parameters
        ----------
        references
            List of reference objects
        queries
            List of query objects
        is_symmetric
            Set to True when *references* and *queries* are identical (as for instance for an all-vs-all
            comparison). By using the fact that score[i,j] = score[j,i] the calculation will be about
            2x faster.
        """
        n_rows = len(references)
        n_cols = len(queries)
        scores = numpy.empty([n_rows, n_cols], dtype=self.score_datatype)
        for i_ref, reference in enumerate(references[:n_rows]):
            if is_symmetric and self.is_commutative:
                for i_query, query in enumerate(queries[i_ref:n_cols], start=i_ref):
                    scores[i_ref][i_query] = self.pair(reference, query)
                    scores[i_query][i_ref] = scores[i_ref][i_query]
            else:
                for i_query, query in enumerate(queries[:n_cols]):
                    scores[i_ref][i_query] = self.pair(reference, query)
        return scores

    def sparse_matrix(self, references: List[SpectrumType], queries: List[SpectrumType],
                      idx_row, idx_col, is_symmetric: bool = False):
        """Optional: Provide optimized method to calculate an sparse matrix of similarity scores.

        Compute similarity scores for pairs of reference and query spectrums as given by the indices
        idx_row (references) and idx_col (queries). If no method is added here, the following naive
        implementation (i.e. a for-loop) is used.

        Parameters
        ----------
        references
            List of reference objects
        queries
            List of query objects
        idx_row
            List/array of row indices
        idx_col
            List/array of column indices
        is_symmetric
            Set to True when *references* and *queries* are identical (as for instance for an all-vs-all
            comparison). By using the fact that score[i,j] = score[j,i] the calculation will be about
            2x faster.
        """
        # pylint: disable=too-many-arguments
        if is_symmetric is True:
            pass  # TODO: consider implementing faster method for symmetric cases

        assert idx_row.shape == idx_col.shape, "col and row indices must be of same shape"
        scores = numpy.zeros((len(idx_row)), dtype=self.score_datatype)  # TODO: switch to sparse matrix
        for i, row in enumerate(idx_row):
            col = idx_col[i]
            scores[i] = self.pair(references[row], queries[col])
        return scores

    def sort(self, scores: numpy.ndarray):
        """Return array of indexes for sorted list of scores.

        This method can be adapted for different styles of scores.

        Parameters
        ----------
        scores
            1D Array of scores.

        Returns
        -------
        idx_sorted
            Indexes of sorted scores.
        """
        return scores.argsort()[::-1]
