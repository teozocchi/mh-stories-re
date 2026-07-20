# Derived Species Map

Monstie species -> scale-LMT folder (`nativeDX11x64\mod\scale\mo\mo###`),
plus the per-monstie `mBattleScale` value the game ships for each.

Reconstructed by joining two tables extracted from `archive/table.arc`
(`monster_book_data` and `buddyPath`) on the Monsterpedia number, then
cross-checked against the community species list at
<https://mhst1.monsterbuddy.app/monsters/>. No copyrighted game data is
reproduced here -- only the functional ID/scale mapping.

| Species | Scale folder | Pedia # | Shipped battleScale |
|---|---|---|---|
| Apceros | `mo118` | 21 | 0.5 |
| Aptonoth | `mo052` | 1 | 0.5 |
| Arzuros | `mo342` | 8 | 0.6 |
| Ash Kecha Wacha | `mo090` | 84 | 0.37 |
| Azure Rathalos | `mo004` | 81 | 0.28 |
| Barioth | `mo325` | 93 | 0.2 |
| Barroth | `mo318` | 39 | 0.22 |
| Basarios | `mo038` | 51 | 0.35 |
| Black Diablos | `mo100` | 42 | 0.28 |
| Black Gravios | `mo041` | 75 | 0.35 |
| Blue Yian Kut-Ku | `mo008` | 10 | 0.28 |
| Brachydios | `mo044` | 97 | 0.25 |
| Brute Tigrex | `mo012` | 54 | 0.231 |
| Bulldrome | `mo330` | 16 | 1.12 |
| Cephadrome | `mo105` | 40 | 0.32 |
| Congalala | `mo017` | 72 | 0.5 |
| Crimson Qurupeco | `mo341` | 74 | 0.38 |
| Deviljho | `mo042` | 87 | 0.27 |
| Diablos | `mo099` | 41 | 0.28 |
| Emerald Congalala | `mo018` | 73 | 0.5 |
| Gendrome | `mo013` | 29 | 0.75 |
| Gold Rathian | `mo005` | 104 | 0.28 |
| Gravios | `mo040` | 52 | 0.35 |
| Great Baggi | `mo314` | 91 | 0.45 |
| Great Jaggi | `mo015` | 68 | 0.45 |
| Great Poogie | `mo303` | 109 | 0.7 |
| Green Nargacuga | `mo360` | 79 | 0.231 |
| Gypceros | `mo009` | 31 | 0.2519 |
| Iodrome | `mo014` | 50 | 0.75 |
| Ivory Lagiacrus | `mo347` | 86 | 0.22 |
| Jade Barroth | `mo319` | 92 | 0.22 |
| Kecha Wacha | `mo020` | 69 | 0.37 |
| Khezu | `mo036` | 18 | 0.3 |
| Kirin | `mo034` | 99 | 1.15 |
| Kushala Daora | `mo031` | 106 | 0.25 |
| Lagiacrus | `mo346` | 85 | 0.22 |
| Lagombi | `mo047` | 15 | 0.6 |
| Molten Tigrex | `mo080` | 111 | 0.231 |
| Monoblos | `mo101` | 102 | 0.28 |
| Nargacuga | `mo359` | 78 | 0.231 |
| Nerscylla | `mo027` | 32 | 0.21 |
| Oroshi Kirin | `mo035` | 112 | 1.15 |
| Pink Rathian | `mo003` | 36 | 0.28 |
| Popo | `mo053` | 11 | 0.5 |
| Purple Gypceros | `mo010` | 83 | 0.2519 |
| Purple Ludroth | `mo317` | 70 | 0.3 |
| Qurupeco | `mo340` | 34 | 0.38 |
| Rajang | `mo019` | 98 | 0.25 |
| Ratha | `mo302` | - | 0.28 |
| Rathalos | `mo002` | 80 | 0.28 |
| Rathian | `mo001` | 35 | 0.28 |
| Red Khezu | `mo037` | 19 | 0.3 |
| Royal Ludroth | `mo316` | 30 | 0.3 |
| Ruby Basarios | `mo039` | 77 | 0.35 |
| Sand Barioth | `mo326` | 94 | 0.2 |
| Seregios | `mo088` | 103 | 0.28 |
| Shrouded Nerscylla | `mo096` | 33 | 0.21 |
| Silver Rathalos | `mo006` | 105 | 0.28 |
| Stygian Zinogre | `mo049` | 96 | 0.27 |
| Teostra | `mo032` | 107 | 0.25 |
| Tigrex | `mo011` | 43 | 0.231 |
| Uragaan | `mo345` | 53 | 0.2 |
| Velocidrome | `mo016` | 7 | 0.75 |
| White Monoblos | `mo102` | 110 | 0.28 |
| Yian Garuga | `mo030` | 71 | 0.28 |
| Yian Kut-Ku | `mo007` | 9 | 0.28 |
| Zamtrios | `mo022` | 17 | 0.27 |
| Zinogre | `mo048` | 76 | 0.27 |

*The shrunk "chibi" look comes from the per-bone SCALE channel in each
`mo###_body.lmt`, independent of `battleScale`. Kirin ships at 1.15 -- the
only Monstie the game scales up.*
