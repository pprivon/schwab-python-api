"""getOptionChains must emit one row per (strike, optionRoot).

On a monthly expiry Schwab lists an AM root and a PM root under the same
strike. The parser used to take [0] of each list and lose one root.

    python3 tests/test_am_pm_roots_per_strike.py

All data below is synthetic (root names AAA/AAAW, made-up numbers).
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from schwab_python_api.market_data import MarketData  # noqa: E402


def contract(root, putcall, strike, tag):
    return {
        "symbol": f"{root}_{putcall}_{strike}", "optionRoot": root, "putCall": putcall,
        "strikePrice": float(strike), "quoteTimeInLong": 1, "totalVolume": 1,
        "openInterest": 1, "last": 1.0, "bid": 1.0, "ask": 2.0,
        "intrinsicValue": 0.0, "netChange": 0.0, "delta": 0.5, "gamma": 0.1,
        "theta": -0.1, "vega": 0.1, "rho": 0.0, "volatility": 20.0 + tag,
    }


def chain(monthly_map, weekly_map):
    """monthly_map / weekly_map: {strike: [roots in list order]} for calls and puts alike."""
    def side(putcall):
        return {
            "2099-01-16:10": {str(k): [contract(r, putcall, k, i) for i, r in enumerate(v)]
                              for k, v in monthly_map.items()},
            "2099-01-09:3": {str(k): [contract(r, putcall, k, i) for i, r in enumerate(v)]
                             for k, v in weekly_map.items()},
        }
    return {"callExpDateMap": side("CALL"), "putExpDateMap": side("PUT")}


class Resp:
    status_code = 200

    def __init__(self, payload):
        self._p = payload

    def json(self):
        return self._p


def run(payload, put_override=None):
    if put_override is not None:
        payload["putExpDateMap"]["2099-01-16:10"] = put_override
    md = MarketData(mock.Mock(accessToken="x"))
    with mock.patch("schwab_python_api.market_data.requests.get", return_value=Resp(payload)):
        return md.getOptionChains("$AAA")


class AmPmRoots(unittest.TestCase):
    def setUp(self):
        # 100: both roots; 105: PM only; 110: AM only. Weekly expiry: one root.
        self.df = run(chain({100: ["AAA", "AAAW"], 105: ["AAAW"], 110: ["AAA"]},
                            {100: ["AAAW"], 105: ["AAAW"]}))
        self.m = self.df[self.df.expiration_day == 16]

    def rows(self, strike):
        return self.m[self.m.call_strike_price == strike]

    def test_both_roots_at_shared_strike(self):
        r = self.rows(100.0)
        self.assertEqual(sorted(r.call_option_root), ["AAA", "AAAW"])

    def test_call_put_paired_by_root(self):
        for _, row in self.m.iterrows():
            self.assertEqual(row.call_option_root, row.put_option_root)
            self.assertEqual(row.call_strike_price, row.put_strike_price)

    def test_pm_only_and_am_only_strikes(self):
        self.assertEqual(list(self.rows(105.0).call_option_root), ["AAAW"])
        self.assertEqual(list(self.rows(110.0).call_option_root), ["AAA"])

    def test_total_monthly_rows(self):
        self.assertEqual(len(self.m), 4)

    def test_non_monthly_unchanged(self):
        w = self.df[self.df.expiration_day == 9]
        self.assertEqual(len(w), 2)
        self.assertEqual(set(w.call_option_root), {"AAAW"})

    def test_call_side_is_call_and_put_side_is_put(self):
        # A call/put swap anywhere in the pairing must be visible.
        for _, row in self.m.iterrows():
            self.assertEqual(row.call_option_type, "CALL")
            self.assertEqual(row.put_option_type, "PUT")
            self.assertTrue(row.call_symbol.startswith(row.call_option_root + "_CALL_"))
            self.assertTrue(row.put_symbol.startswith(row.put_option_root + "_PUT_"))
            self.assertEqual(row.call_osi, row.call_symbol)
            self.assertEqual(row.put_osi, row.put_symbol)

    def test_pairing_ignores_list_order(self):
        # puts list the roots in the opposite order to calls
        payload = chain({100: ["AAA", "AAAW"]}, {})
        put_map = {"100": [contract("AAAW", "PUT", 100, 1), contract("AAA", "PUT", 100, 0)]}
        df = run(payload, put_override=put_map)
        m = df[df.expiration_day == 16]
        self.assertEqual(len(m), 2)
        for _, row in m.iterrows():
            self.assertEqual(row.call_option_root, row.put_option_root)

    def test_root_missing_on_put_side_is_skipped(self):
        payload = chain({100: ["AAA", "AAAW"]}, {})
        put_map = {"100": [contract("AAA", "PUT", 100, 0)]}
        m = run(payload, put_override=put_map)
        m = m[m.expiration_day == 16]
        self.assertEqual(list(m.call_option_root), ["AAA"])

    def test_duplicate_root_in_list_emits_one_row(self):
        payload = chain({100: ["AAA", "AAA", "AAAW"]}, {})
        m = run(payload)
        m = m[m.expiration_day == 16]
        self.assertEqual(sorted(m.call_option_root), ["AAA", "AAAW"])

    def test_put_missing_optionRoot_is_skipped_not_paired(self):
        # Behaviour change from 0.1.2, which paired by position: a call whose
        # root is present is NOT paired with a put that carries no root.
        payload = chain({100: ["AAA"]}, {})
        bad = contract("AAA", "PUT", 100, 0)
        del bad["optionRoot"]
        m = run(payload, put_override={"100": [bad]})
        self.assertEqual(len(m[m.expiration_day == 16]), 0)

    def test_call_missing_optionRoot_is_skipped_not_paired(self):
        payload = chain({100: ["AAA"]}, {})
        bad = contract("AAA", "CALL", 100, 0)
        del bad["optionRoot"]
        payload["callExpDateMap"]["2099-01-16:10"] = {"100": [bad]}
        m = run(payload)
        self.assertEqual(len(m[m.expiration_day == 16]), 0)


if __name__ == "__main__":
    unittest.main()
