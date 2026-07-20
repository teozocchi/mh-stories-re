"""Master species database for the scale trainer.
English names sourced from https://mhst1.monsterbuddy.app/monsters/ (authoritative,
verified against in-game pedia numbers and screenshots this session).
Joined against buddy_full_map.txt (from table.arc's buddyPath, gives the real
mo### scale-LMT folder + per-buddy battleScale) via pedia number.
"""

# pedia number -> English name, from the full monsterbuddy.app listing (#001-#112)
PEDIA_NAMES = {
    1: 'Aptonoth', 2: 'Velociprey', 3: 'Konchu (Yellow)', 4: 'Kelbi', 5: 'Hermitaur',
    6: 'Bullfango', 7: 'Velocidrome', 8: 'Arzuros', 9: 'Yian Kut-Ku', 10: 'Blue Yian Kut-Ku',
    11: 'Popo', 12: 'Zamite', 13: 'Bnahabra (Green)', 14: 'Konchu (Blue)', 15: 'Lagombi',
    16: 'Bulldrome', 17: 'Zamtrios', 18: 'Khezu', 19: 'Red Khezu', 20: 'Barrel Felyne',
    21: 'Apceros', 22: 'Genprey', 23: 'Ludroth', 24: 'Altaroth', 25: 'Slagtoth (Green)',
    26: 'Vespoid', 27: 'Bnahabra (Brown)', 28: 'Cephalos', 29: 'Gendrome', 30: 'Royal Ludroth',
    31: 'Gypceros', 32: 'Nerscylla', 33: 'Shrouded Nerscylla', 34: 'Qurupeco', 35: 'Rathian',
    36: 'Pink Rathian', 37: 'Daimyo Hermitaur', 38: 'Plum Daimyo Hermitaur', 39: 'Barroth',
    40: 'Cephadrome', 41: 'Diablos', 42: 'Black Diablos', 43: 'Tigrex', 44: 'Barroth EX',
    45: 'Slagtoth (Brown)', 46: 'Bnahabra (Red)', 47: 'Konchu (Red)', 48: 'Ioprey', 49: 'Uroktor',
    50: 'Iodrome', 51: 'Basarios', 52: 'Gravios', 53: 'Uragaan', 54: 'Brute Tigrex',
    55: 'Agnaktor', 56: 'Aptonoth EX', 57: 'Uroktor EX', 58: 'Uragaan EX', 59: 'Agnaktor EX',
    60: 'Gargwa', 61: 'Bnahabra (Blue)', 62: 'Jaggi', 63: 'Jaggia', 64: 'Conga',
    65: 'Konchu (Green)', 66: 'Great Thunderbug', 67: 'Shakalaka', 68: 'Great Jaggi',
    69: 'Kecha Wacha', 70: 'Purple Ludroth', 71: 'Yian Garuga', 72: 'Congalala',
    73: 'Emerald Congalala', 74: 'Crimson Qurupeco', 75: 'Black Gravios', 76: 'Zinogre',
    77: 'Ruby Basarios', 78: 'Nargacuga', 79: 'Green Nargacuga', 80: 'Rathalos',
    81: 'Azure Rathalos', 82: 'Tigrex EX', 83: 'Purple Gypceros', 84: 'Ash Kecha Wacha',
    85: 'Lagiacrus', 86: 'Ivory Lagiacrus', 87: 'Deviljho', 88: 'Baggi',
    89: 'Great Dracophage Bug', 90: 'Remobra', 91: 'Great Baggi', 92: 'Jade Barroth',
    93: 'Barioth', 94: 'Sand Barioth', 95: 'Glacial Agnaktor', 96: 'Stygian Zinogre',
    97: 'Brachydios', 98: 'Rajang', 99: 'Kirin', 100: 'Versa Pietru', 101: 'Makili Pietru',
    102: 'Monoblos', 103: 'Seregios', 104: 'Gold Rathian', 105: 'Silver Rathalos',
    106: 'Kushala Daora', 107: 'Teostra', 108: 'Fatalis', 109: 'Great Poogie',
    110: 'White Monoblos', 111: 'Molten Tigrex', 112: 'Oroshi Kirin',
}

# buddyId -> (otm/mo folder number as 3-digit str, battleScale float, pedia number or None)
# from buddy_full_map.txt (decoded from table.arc's buddyPath)
BUDDY_ROWS = [
    (1, '016', 0.75, 7),
    (2, '001', 0.28, 35),
    (3, '003', 0.28, 36),
    (4, '005', 0.28, 104),
    (5, '002', 0.28, 80),
    (6, '004', 0.28, 81),
    (7, '006', 0.28, 105),
    (8, '017', 0.5, 72),
    (9, '018', 0.5, 73),
    (10, '007', 0.28, 9),
    (11, '008', 0.28, 10),
    (12, '052', 0.5, 1),
    (13, '014', 0.75, 50),
    (14, '011', 0.231, 43),
    (15, '012', 0.231, 54),
    (16, '080', 0.231, 111),
    (19, '047', 0.6, 15),
    (20, '342', 0.6, 8),
    (21, '359', 0.231, 78),
    (22, '360', 0.231, 79),
    (23, '036', 0.3, 18),
    (24, '037', 0.3, 19),
    (25, '099', 0.28, 41),
    (26, '100', 0.28, 42),
    (27, '013', 0.75, 29),
    (28, '105', 0.32, 40),
    (29, '316', 0.3, 30),
    (30, '317', 0.3, 70),
    (31, '009', 0.2519, 31),
    (32, '010', 0.2519, 83),
    (33, '038', 0.35, 51),
    (34, '039', 0.35, 77),
    (35, '040', 0.35, 52),
    (36, '041', 0.35, 75),
    (37, '030', 0.28, 71),
    (38, '088', 0.28, 103),
    (39, '101', 0.28, 102),
    (40, '102', 0.28, 110),
    (41, '053', 0.5, 11),
    (42, '118', 0.5, 21),
    (43, '015', 0.45, 68),
    (44, '314', 0.45, 91),
    (45, '020', 0.37, 69),
    (46, '090', 0.37, 84),
    (47, '027', 0.21, 32),
    (48, '096', 0.21, 33),
    (49, '034', 1.15, 99),
    (50, '035', 1.15, 112),
    (51, '042', 0.27, 87),
    (52, '044', 0.25, 97),
    (53, '048', 0.27, 76),
    (54, '049', 0.27, 96),
    (55, '330', 1.12, 16),
    (56, '318', 0.22, 39),
    (57, '319', 0.22, 92),
    (58, '325', 0.2, 93),
    (59, '326', 0.2, 94),
    (60, '345', 0.2, 53),
    (62, '022', 0.27, 17),
    (63, '340', 0.38, 34),
    (64, '341', 0.38, 74),
    (65, '346', 0.22, 85),
    (66, '347', 0.22, 86),
    (68, '401', 0.28, None),
    (69, '302', 0.28, None),
    (70, '303', 0.7, 109),
    (71, '400', 0.28, None),
    (72, '325', 0.2, None),
    (73, '302', 0.28, None),
    (74, '302', 0.28, None),
    (75, '001', 0.28, None),
    (78, '500', 0.27, None),
    (79, '503', 1.15, None),
    (80, '502', 0.6, None),
    (81, '501', 0.27, None),
    (82, '002', 0.28, None),
    (84, '019', 0.25, 98),
    (85, '031', 0.25, 106),
    (86, '032', 0.25, 107),
    (88, '506', 0.25, None),
    (89, '507', 0.27, None),
    (90, '508', 0.231, None),
    (91, '509', 0.3, None),
    (92, '505', 0.28, None),
    (93, '510', 0.45, None),
    (94, '511', 0.28, None),
    (95, '512', 0.28, None),
    (96, '513', 0.38, None),
]

# mo-folder overrides for special/story companions with no standard pedia entry
# (confirmed in-game by process of elimination, not from any data table)
SPECIAL_NAMES = {
    'mo302': 'Ratha',
}


def build_master_list():
    by_mo = {}
    for buddy_id, otm, battle_scale, pedia in BUDDY_ROWS:
        mo = f'mo{otm}'
        name = SPECIAL_NAMES.get(mo) or PEDIA_NAMES.get(pedia, f'Unknown (mo{otm})')
        row = {
            'mo': mo,
            'buddy_id': buddy_id,
            'pedia': pedia,
            'battle_scale': battle_scale,
            'name': name,
        }
        existing = by_mo.get(mo)
        if existing is None or (existing['pedia'] is None and pedia is not None):
            by_mo[mo] = row
    rows = list(by_mo.values())
    rows.sort(key=lambda r: r['name'])
    return rows

if __name__ == '__main__':
    for r in build_master_list():
        print(f"{r['mo']:8s} {r['name']:28s} pedia={r['pedia']}")
