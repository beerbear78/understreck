/*
  Understreck – omgångsdata. Skrivs automatiskt av GitHub Actions (python -m understreck).
  Fält per match: folk [1,X,2] %, odds [1,X,2], form (äldst först, V/O/F), xg {home:[för,emot], away:[...]},
  injuries {home:[...], away:[...], impact:[0-3,0-3]}, note, valueNote, lineup. Fält som börjar med _ används bara av skriptet.
*/
window.STRYK_ROUNDS = [
 {
  "id": 7763,
  "draw": "4974",
  "date": "2026-10-10",
  "deadline": "15:59",
  "turnover": 2169019,
  "updated": "2026-10-08",
  "lineupUpdate": null,
  "matches": [
   {
    "n": 1,
    "home": "Manchester United",
    "away": "Tottenham",
    "league": "Premier League",
    "kickoff": "18:30",
    "folk": [
     64,
     20,
     16
    ],
    "odds": [
     1.7,
     4.2,
     4.4
    ],
    "table": {
     "home": "12:e, 5 p (5 matcher)",
     "away": "20:e, 2 p (5 matcher)"
    },
    "form": {
     "home": "FVOFO",
     "away": "FFOOF"
    },
    "xg": {
     "home": [
      2.12,
      1.44
     ],
     "away": [
      1.16,
      1.84
     ]
    },
    "injuries": {
     "home": [
      "Manuel Ugarte (skadad)",
      "Tom Heaton (skadad)",
      "Benjamin Sesko (osäker)",
      "Amad Diallo (osäker)",
      "Kobbie Mainoo (osäker)",
      "Marcus Rashford (osäker)",
      "Patrick Dorgu (osäker)",
      "Noussair Mazraoui (osäker)"
     ],
     "away": [
      "Dejan Kulusevski (skadad)",
      "Wilson Odobert (skadad)",
      "Pedro Porro (skadad)",
      "Xavi Simons (skadad)",
      "Mykhailo Mudryk (skadad)",
      "Jan Paul van Hecke (osäker)",
      "Micky van de Ven (osäker)"
     ],
     "impact": [
      2,
      2
     ]
    },
    "facts": "Manchester United hemma: 1–0–1 (V–O–F). Tottenham borta: 0–1–1.",
    "_src": {
     "kickoff": "2026-10-10T18:30:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Manchester United är favorit med 55 procent hos modellen, och xG talar för hemmalaget med 2,12 framåt mot Tottenhams 1,16. Tottenham ligger 20:e med 2 poäng och har formen FFOOF, och saknar dessutom Kulusevski, Odobert, Porro, Simons och Mudryk. Folket har ändå överstreckat ettan med 64 procent mot modellens 55, medan tvåan är understreckad med 16 mot 22 procent.",
    "valueNote": "",
    "lineup": "Startelvan släpps cirka 17:30, efter spelstopp."
   },
   {
    "n": 2,
    "home": "Chelsea",
    "away": "Bournemouth",
    "league": "Premier League",
    "kickoff": "16:00",
    "folk": [
     64,
     21,
     15
    ],
    "odds": [
     1.7,
     4.1,
     4.5
    ],
    "table": {
     "home": "10:e, 7 p (5 matcher)",
     "away": "17:e, 3 p (5 matcher)"
    },
    "form": {
     "home": "VVFOF",
     "away": "FOOOF"
    },
    "xg": {
     "home": [
      1.79,
      2.06
     ],
     "away": [
      1.62,
      1.4
     ]
    },
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Chelsea hemma: 1–1–0 (V–O–F). Bournemouth borta: 0–1–1.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Chelsea är troligast med 51 procent hos modellen och har 1–1–0 hemma, men släpper in 2,06 xG per match. Bournemouth skapar 1,62 xG och släpper bara in 1,40, vilket gör bortalaget farligare än tabellplatsen 17:e antyder. Folket har 64 procent på ettan mot modellens 51, och tvåan är tydligt understreckad med 15 mot 25 procent.",
    "valueNote": "Tvåan har spelvärde 1,68 eftersom folket bara ger Bournemouth 15 procent medan modellen ger 25."
   },
   {
    "n": 3,
    "home": "Aston Villa",
    "away": "Brentford",
    "league": "Premier League",
    "kickoff": "16:00",
    "folk": [
     42,
     26,
     32
    ],
    "odds": [
     2.62,
     3.55,
     2.55
    ],
    "table": {
     "home": "16:e, 4 p (5 matcher)",
     "away": "4:e, 9 p (5 matcher)"
    },
    "form": {
     "home": "FFOFV",
     "away": "VOOOV"
    },
    "xg": {
     "home": [
      1.0,
      2.17
     ],
     "away": [
      2.1,
      1.5
     ]
    },
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Aston Villa hemma: 0–0–2 (V–O–F). Brentford borta: 0–2–0.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Brentford är troligast med 40 procent hos modellen och ligger 4:e med 9 poäng, med 2,10 xG framåt per match. Aston Villa har förlorat båda hemmamatcherna och släpper in 2,17 xG per match. Folket har överstreckat ettan med 42 mot modellens 34 procent, medan tvåan är understreckad med 32 mot 40 procent.",
    "valueNote": ""
   },
   {
    "n": 4,
    "home": "Sunderland",
    "away": "Brighton",
    "league": "Premier League",
    "kickoff": "16:00",
    "folk": [
     26,
     24,
     50
    ],
    "odds": [
     3.0,
     3.5,
     2.3
    ],
    "table": {
     "home": "14:e, 4 p (5 matcher)",
     "away": "3:e, 10 p (5 matcher)"
    },
    "form": {
     "home": "FVOFF",
     "away": "VFOVV"
    },
    "xg": {
     "home": [
      2.01,
      1.77
     ],
     "away": [
      2.58,
      1.73
     ]
    },
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Sunderland hemma: 1–0–1 (V–O–F). Brighton borta: 1–0–1.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Brighton är troligast med 40 procent hos modellen, ligger 3:e med 10 poäng och skapar 2,58 xG per match. Sunderland är ändå inte chanslöst med 2,01 xG framåt, och modellen ger hemmalaget 34 procent. Folket har överstreckat tvåan med 50 procent, medan ettan är understreckad med 26 procent och har spelvärde 1,32.",
    "valueNote": ""
   },
   {
    "n": 5,
    "home": "Ipswich",
    "away": "Fulham",
    "league": "Premier League",
    "kickoff": "16:00",
    "folk": [
     40,
     27,
     33
    ],
    "odds": [
     2.75,
     3.5,
     2.45
    ],
    "table": {
     "home": "11:e, 6 p (5 matcher)",
     "away": "19:e, 2 p (5 matcher)"
    },
    "form": {
     "home": "VFFVF",
     "away": "FFFOO"
    },
    "xg": {
     "home": [
      1.42,
      2.06
     ],
     "away": [
      1.59,
      2.09
     ]
    },
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Ipswich hemma: 1–0–1 (V–O–F). Fulham borta: 0–1–1.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Modellen lutar svagt åt Ipswich med 38 procent mot 36 för Fulham, så matchen är mycket jämn. Fulham ligger 19:e med 2 poäng och formen FFFOO, men båda lagen släpper in över 2 xG per match. Folket ligger nära modellen med 40, 27 och 33 procent, och inget tecken sticker ut.",
    "valueNote": ""
   },
   {
    "n": 6,
    "home": "Blackburn",
    "away": "Cardiff",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     52,
     24,
     24
    ],
    "odds": [
     2.63,
     3.55,
     2.45
    ],
    "table": {
     "home": "16:e, 9 p (8 matcher)",
     "away": "21:a, 7 p (8 matcher)"
    },
    "form": {
     "home": "OFFVO",
     "away": "FFOFV"
    },
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Blackburn hemma: 2–0–2 (V–O–F). Cardiff borta: 0–1–3.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Modellen ger Cardiff 38 procent mot Blackburns 36, i linje med oddsen. Cardiff har bara 0–1–3 på bortaplan men vann senast, och Blackburn har 2–0–2 hemma. Folket har kraftigt överstreckat ettan med 52 procent mot modellens 36, medan tvåan bara är streckad till 24 procent.",
    "valueNote": "Tvåan har spelvärde 1,58 eftersom folket ger Cardiff 24 procent mot modellens 38."
   },
   {
    "n": 7,
    "home": "Bolton",
    "away": "Stoke",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     34,
     28,
     38
    ],
    "odds": [
     2.63,
     3.35,
     2.5
    ],
    "table": {
     "home": "15:e, 10 p (8 matcher)",
     "away": "7:e, 13 p (8 matcher)"
    },
    "form": {
     "home": "FFFVV",
     "away": "VVOVV"
    },
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Bolton hemma: 2–0–2 (V–O–F). Stoke borta: 1–1–2.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Stoke är troligast med 38 procent och har formen VVOVV samt 13 poäng som 7:e. Bolton har vunnit sina två senaste matcher, så skillnaden är liten. Folket och modellen har exakt samma fördelning med 34, 28 och 38 procent, så inget tecken är felstreckat.",
    "valueNote": ""
   },
   {
    "n": 8,
    "home": "Derby",
    "away": "Wrexham",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     34,
     28,
     38
    ],
    "odds": [
     2.65,
     3.29,
     2.56
    ],
    "table": {
     "home": "22:a, 5 p (8 matcher)",
     "away": "14:e, 10 p (8 matcher)"
    },
    "form": {
     "home": "VFFFO",
     "away": "VOOFV"
    },
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Derby hemma: 0–1–3 (V–O–F). Wrexham borta: 1–2–1.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Modellen ger Wrexham 37 procent mot Derbys 35, alltså nästan jämnt. Derby ligger 22:a med 5 poäng och har 0–1–3 hemma, medan Wrexham har 1–2–1 borta. Folket ligger i princip på modellens nivå med 34, 28 och 38 procent.",
    "valueNote": ""
   },
   {
    "n": 9,
    "home": "Middlesbrough",
    "away": "Wolverhampton",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     52,
     24,
     24
    ],
    "odds": [
     2.21,
     3.63,
     2.9
    ],
    "table": {
     "home": "3:e, 15 p (8 matcher)",
     "away": "4:e, 14 p (7 matcher)"
    },
    "form": {
     "home": "OVVOO",
     "away": "VFOVV"
    },
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Middlesbrough hemma: 3–1–0 (V–O–F). Wolverhampton borta: 2–1–1.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Middlesbrough är troligast med 42 procent hos modellen, ligger 3:e med 15 poäng och är obesegrat hemma med 3–1–0. Wolverhampton ligger strax efter med 14 poäng på 7 matcher och har 2–1–1 borta. Folket har överstreckat ettan med 52 procent, och tvåan är understreckad med 24 mot 32 procent.",
    "valueNote": ""
   },
   {
    "n": 10,
    "home": "Preston",
    "away": "Millwall",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     29,
     27,
     44
    ],
    "odds": [
     2.75,
     3.4,
     2.42
    ],
    "table": {
     "home": "23:e, 4 p (8 matcher)",
     "away": "11:e, 11 p (8 matcher)"
    },
    "form": {
     "home": "FVFFO",
     "away": "FVFOO"
    },
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Preston hemma: 1–0–3 (V–O–F). Millwall borta: 1–1–2.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Millwall är troligast med 39 procent hos modellen, och Preston ligger 23:e med 4 poäng och 1–0–3 hemma. Millwall har dock bara 1–1–2 på bortaplan. Folket har överstreckat tvåan med 44 procent, medan ettan är understreckad med 29 mot modellens 34 procent.",
    "valueNote": ""
   },
   {
    "n": 11,
    "home": "Sheffield United",
    "away": "Lincoln",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     58,
     20,
     22
    ],
    "odds": [
     2.08,
     3.37,
     3.4
    ],
    "table": {
     "home": "18:e, 9 p (8 matcher)",
     "away": "12:e, 11 p (8 matcher)"
    },
    "form": {
     "home": "VFVFF",
     "away": "OOVVF"
    },
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Sheffield United hemma: 1–1–2 (V–O–F). Lincoln borta: 3–0–1.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Sheffield United är troligast med 45 procent hos modellen, men har formen VFVFF och bara 1–1–2 hemma. Lincoln har tagit 3–0–1 på bortaplan. Folket har överstreckat ettan med 58 procent, och krysset är understreckat med 20 mot modellens 28 procent.",
    "valueNote": "Krysset har spelvärde 1,38 eftersom folket bara ger det 20 procent medan modellen ger 28."
   },
   {
    "n": 12,
    "home": "Watford",
    "away": "Burnley",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     44,
     26,
     30
    ],
    "odds": [
     2.9,
     3.49,
     2.27
    ],
    "table": {
     "home": "20:e, 8 p (8 matcher)",
     "away": "24:e, 4 p (8 matcher)"
    },
    "form": {
     "home": "FFVFF",
     "away": "OFOFO"
    },
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": "Watford hemma: 2–1–1 (V–O–F). Burnley borta: 0–1–3.",
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Modellen gör Burnley till favorit med 41 procent, i linje med oddsen, trots att laget ligger sist med 4 poäng och har 0–1–3 borta. Watford ligger 20:e och har formen FFVFF men har 2–1–1 hemma. Folket har överstreckat ettan med 44 mot 32 procent, och tvåan är understreckad med 30 mot 41 procent.",
    "valueNote": ""
   },
   {
    "n": 13,
    "home": "Huddersfield",
    "away": "Sheffield Wednesday",
    "league": "League One",
    "kickoff": "16:00",
    "folk": [
     56,
     25,
     19
    ],
    "odds": [
     1.7,
     4.0,
     4.2
    ],
    "table": null,
    "form": {},
    "xg": null,
    "injuries": {
     "home": [],
     "away": [],
     "impact": null
    },
    "facts": null,
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_england_league1"
    },
    "note": "Huddersfield är klar favorit med 55 procent hos modellen och oddset 1,70. Folket ligger nära med 56 procent på ettan. Tvåan är något understreckad med 19 mot 22 procent och har spelvärde 1,16, medan krysset är lätt överstreckat.",
    "valueNote": ""
   }
  ]
 }
];
