"""certctc -- certified-exact CTC decoding: mode, runner-up and margin, with a proof-carrying search.

    from certctc import decode, verify
    cert = decode(table, blank=0)      # table: (T, W) posteriors, numpy array or list of lists
    assert verify(table, cert)
    print(cert.to_json(indent=1))

Algorithm: T2b variant 1c ("exact backward suffix modes"), independently re-verified in T9.
See README.md in this directory.
"""
from .decoder import decode, Certificate, BudgetExceeded
from .verify import verify, ctc_prob, VerifyReport, VerificationError

__version__ = '0.1.0'
__all__ = ['decode', 'Certificate', 'BudgetExceeded', 'verify', 'ctc_prob', 'VerifyReport', 'VerificationError', '__version__']
