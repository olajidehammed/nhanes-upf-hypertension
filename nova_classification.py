"""
Ultra-processed food classification.

NHANES doesn't ship Nova classification out of the box. The standard
reference (Martinez Steele et al. 2023) classifies at the individual
8-digit food-code level, but that lookup table isn't published as clean,
machine-readable data - it's a narrative methods paper. What USDA does
publish cleanly is the WWEIA food category crosswalk (food_code ->
~150-170 broad categories like "frankfurters", "candy", "100% fruit
juice"), so that's the level this classification works at.

This is a coarser approximation than the original paper's food-code-level
approach, which is disclosed as a limitation in the manuscript. Match rate
against actual NHANES dietary recall records came out to ~99.6-99.8% in
both cycles, and the resulting population-level UPF share (~52% of energy)
lines up well with published NHANES estimates, so the category-level
approximation seems reasonable in practice.

NOVA_GROUP values: 1 = unprocessed/minimally processed, 2 = processed
culinary ingredient, 3 = processed food, 4 = ultra-processed food.
"""

import numpy as np
import pandas as pd

# WWEIA category number -> Nova group. Built by going through USDA's
# category list by hand and applying the Nova logic (purpose + degree of
# industrial processing) category by category. A handful are genuinely
# ambiguous because a single WWEIA category can span more than one
# processing level (e.g. "salad dressings and vegetable oils" mixes
# UPF dressings with minimally-processed oils) - those calls are noted
# inline and flagged as a limitation in the manuscript rather than hidden.
NOVA_GROUP = {
    1002: 1, 1004: 1, 1006: 1, 1008: 1,                      # plain milk
    1202: 4, 1204: 4, 1206: 4, 1208: 4,                      # flavored/sweetened milk
    1402: 4, 1404: 4,                                        # milkshakes, milk substitutes
    1602: 3, 1604: 3,                                        # cheese
    1820: 3, 1822: 3,                                        # yogurt
    2002: 1, 2004: 1, 2006: 1, 2008: 1, 2010: 1,             # unprocessed meats
    2202: 1, 2204: 4, 2206: 1,                               # chicken (nuggets/patties = UPF)
    2402: 1, 2404: 1,                                        # fish/shellfish
    2502: 1,                                                 # eggs
    2602: 4, 2604: 3, 2606: 4, 2608: 4,                      # cold cuts/bacon/franks/sausage
    2802: 1, 2804: 1, 2806: 3,                               # legumes, nuts, soy products
    3002: 3, 3004: 3, 3006: 3,                               # meat/poultry/seafood mixed dishes
    3202: 3, 3204: 3, 3206: 4, 3208: 4,                      # rice/pasta dishes; mac&cheese
    3402: 3, 3404: 3, 3406: 3,                               # stir-fry, egg rolls etc
    3502: 3, 3504: 4, 3506: 3,                               # burritos/nachos/other Mexican
    3602: 4,                                                 # pizza
    3702: 4, 3703: 4, 3704: 4, 3706: 4, 3708: 3, 3720: 3, 3722: 3, 3730: 3,  # sandwiches
    3802: 4,                                                 # soups, mostly canned/packaged
    4002: 1, 4004: 1,                                        # rice, plain grains
    4202: 4, 4204: 4, 4206: 4, 4208: 3,                      # breads/rolls/bagels/tortillas
    4402: 4, 4404: 4,                                        # biscuits/pancakes (commercial)
    4602: 4, 4604: 4,                                        # RTE cereal
    4802: 1, 4804: 1,                                        # oatmeal/grits, plain
    5002: 4, 5004: 4, 5006: 4, 5008: 4,                      # chips/popcorn/pretzels
    5202: 4, 5204: 4,                                        # crackers
    5402: 4, 5404: 4,                                        # cereal/nutrition bars
    5502: 4, 5504: 4, 5506: 4,                               # cakes/cookies/pastries
    5702: 4, 5704: 4,                                        # candy
    5802: 4, 5804: 4, 5806: 4,                               # ice cream/pudding/gelatin
    6002: 1, 6004: 1, 6006: 1, 6008: 1, 6010: 1, 6012: 1, 6014: 1, 6016: 1, 6018: 1,
    6009: 1, 6011: 1, 6020: 1, 6022: 1, 6024: 1,             # fruit (incl 17-18 splits)
    6402: 1, 6404: 1, 6406: 1, 6408: 1, 6410: 1, 6412: 1, 6414: 1, 6416: 1, 6418: 1, 6420: 1,
    6407: 1, 6409: 1, 6411: 1, 6413: 1, 6432: 1, 6489: 1,    # vegetables (incl 17-18 splits)
    6422: 3, 3102: 3, 3104: 3,                               # vegetable/bean mixed dishes
    6430: 4,                                                 # fried vegetables
    6802: 1, 6804: 4, 6806: 3,                               # potatoes (fries = UPF)
    7002: 1, 7004: 1, 7006: 1,                               # 100% fruit juice
    7008: 3,                                                 # vegetable juice, added sodium
    7102: 4, 7104: 4, 7106: 4, 7202: 4, 7204: 4, 7206: 4, 7208: 4, 7220: 4,  # sodas/drinks
    7302: 1, 7304: 1,                                        # coffee/tea, plain
    7502: 3, 7504: 3, 7506: 3,                               # alcohol
    7702: 1, 7704: 1,                                        # water
    7802: 4, 7804: 4,                                        # flavored/enhanced water
    8002: 2, 8004: 4,                                        # butter vs. margarine
    8006: 3, 8008: 3,                                        # cream cheese/sour cream/cream
    8010: 4, 8012: 4,                                        # mayo, dressings/oils (mixed category, see docstring)
    8402: 4, 8404: 3, 8406: 3, 8408: 3, 8410: 3, 8412: 4,    # condiments/sauces
    8802: 2, 8804: 4, 8806: 3,                               # sugar/sweeteners/jam
    9002: 4, 9004: 3, 9006: 3, 9008: 3, 9010: 3, 9012: 4,    # baby food
    9202: 1, 9204: 1,                                        # baby juice/water
    9402: 4, 9404: 4, 9406: 4,                               # infant formula
    9602: 1,                                                 # human milk
    9802: 4,                                                 # protein powders
    9999: None,                                              # "not included in a food category"
}


def load_wweia_crosswalk(path_2015_16, path_2017_18):
    """USDA publishes a food_code -> WWEIA category crosswalk separately
    for each cycle (category numbers shift slightly between cycles)."""
    fc15 = pd.read_excel(path_2015_16, sheet_name="FNDDS_foodcat")
    fc17 = pd.read_excel(path_2017_18, sheet_name="17-18 FNDDS_foodcat")
    return {"2015-2016": fc15, "2017-2018": fc17}


def classify_food_records(iff_df, crosswalks):
    """Attach a Nova group to every row of a (pooled, cycle-tagged)
    individual foods dataframe."""
    lookups = {
        cycle: dict(zip(df["food_code"], df["category_number"].map(NOVA_GROUP)))
        for cycle, df in crosswalks.items()
    }
    iff_df = iff_df.copy()
    iff_df["nova_group"] = iff_df.apply(
        lambda r: lookups[r["cycle"]].get(int(r["DR1IFDCD"]))
        if pd.notna(r["DR1IFDCD"]) else np.nan,
        axis=1,
    )
    return iff_df


def upf_share_per_person(classified_iff):
    """Percent of daily energy coming from Nova group 4 (ultra-processed)
    items, one row per SEQN."""
    valid = classified_iff.dropna(subset=["DR1IKCAL", "nova_group"])
    totals = valid.groupby("SEQN")["DR1IKCAL"].sum().rename("total_kcal")
    upf = valid[valid["nova_group"] == 4].groupby("SEQN")["DR1IKCAL"].sum().rename("upf_kcal")
    out = pd.concat([totals, upf], axis=1).fillna({"upf_kcal": 0})
    out["pct_upf"] = 100 * out["upf_kcal"] / out["total_kcal"]
    return out.reset_index()
