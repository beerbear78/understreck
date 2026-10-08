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
  "turnover": 1998543,
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
      "Matthijs de Ligt (skadad)",
      "Tom Heaton (skadad)",
      "Amad Diallo (osäker)",
      "Benjamin Sesko (osäker)",
      "Patrick Dorgu (osäker)",
      "Noussair Mazraoui (osäker)",
      "Kobbie Mainoo (osäker)",
      "Marcus Rashford (osäker)",
      "Karl Darlow (osäker)"
     ],
     "away": [
      "Pedro Porro (skadad)",
      "Dejan Kulusevski (skadad)",
      "Xavi Simons (skadad)",
      "Wilson Odobert (skadad)",
      "Mykhailo Mudryk (skadad)",
      "Micky van de Ven (osäker)",
      "Jan Paul van Hecke (osäker)"
     ],
     "impact": [
      2,
      2
     ]
    },
    "facts": null,
    "_src": {
     "kickoff": "2026-10-10T18:30:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Modellen ger Manchester United 55 % mot folkets 64 %, så ettan är överstreckad med spelvärde 0,86. United skapar 2,12 xG per match mot Tottenhams 1,16, och Tottenham ligger sist med 2 poäng utan vinst på fem matcher (FFOOF). Tottenham saknar bland annat Pedro Porro, Dejan Kulusevski och Xavi Simons. Tvåan är understreckad med 16 % hos folket mot modellens 22 % och har spelvärde 1,35.",
    "valueNote": ""
   },
   {
    "n": 2,
    "home": "Chelsea",
    "away": "Bournemouth",
    "league": "Premier League",
    "kickoff": "16:00",
    "folk": [
     63,
     21,
     16
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
    "facts": null,
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Chelsea är favorit med 51 % hos modellen, men folket streckar ettan till 63 %, vilket ger spelvärde 0,80. Chelsea släpper in 2,06 xG per match, och Bournemouth skapar 1,62 xG framåt. Tvåan är tydligt understreckad med 16 % hos folket mot modellens 25 %.",
    "valueNote": "Tvåan har spelvärde 1,58 eftersom modellen ger Bournemouth 25 % medan folket bara streckar 16 %, och Chelsea släpper till 2,06 xG per match."
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
     3.5,
     2.6
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
     "home": [
      "Ian Maatsen (skadad)",
      "Brian Madjo (skadad)",
      "Pau Torres (skadad)",
      "Leon Goretzka (skadad)",
      "Marco Bizot (skadad)",
      "Alysson (skadad)",
      "Matty Cash (skadad)",
      "Amadou Onana (skadad)"
     ],
     "away": [
      "Mikkel Damsgaard (osäker)",
      "Nathan Collins (osäker)"
     ],
     "impact": [
      2,
      1
     ]
    },
    "facts": null,
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Brentford är troligast med 40 % hos modellen, ligger 4:a med 9 poäng och har formen VOOOV. Brentford skapar 2,10 xG per match mot Villas 1,00, och Villa släpper in 2,17 xG. Villa har åtta skadade, bland dem Pau Torres, Amadou Onana och Matty Cash. Folket streckar ettan till 42 % mot modellens 33 %, medan tvåan är understreckad med 32 % mot 40 % och spelvärde 1,24.",
    "valueNote": ""
   },
   {
    "n": 4,
    "home": "Sunderland",
    "away": "Brighton",
    "league": "Premier League",
    "kickoff": "16:00",
    "folk": [
     27,
     24,
     49
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
     "home": [
      "Romaine Mundle (skadad)",
      "Daniel Ballard (skadad)",
      "Habib Diarra (skadad)",
      "Reinildo Mandava (avstängd)",
      "Brian Brobbey (osäker)"
     ],
     "away": [
      "Stefanos Tzimas (skadad)",
      "Yankuba Minteh (skadad)",
      "Kaoru Mitoma (skadad)",
      "Jack Hinshelwood (skadad)",
      "Mats Wieffer (skadad)",
      "Femi Azeez (skadad)",
      "Zadok Yohanna (skadad)",
      "Evan Ferguson (skadad)",
      "Yasin Ayari (osäker)",
      "Lewis Dunk (osäker)"
     ],
     "impact": [
      2,
      2
     ]
    },
    "facts": null,
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Brighton är troligast med 39 % hos modellen, ligger 3:a med 10 poäng, har formen VFOVV och skapar 2,58 xG per match. Samtidigt saknar Brighton många spelare, bland dem Kaoru Mitoma, Yankuba Minteh och Evan Ferguson. Folket streckar tvåan till 49 %, vilket gör den överstreckad med spelvärde 0,81. Ettan är understreckad med 27 % hos folket mot modellens 34 % och har spelvärde 1,27.",
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
     "home": [
      "Abdul Fatawu (avstängd)",
      "Jack Taylor (osäker)"
     ],
     "away": [
      "Tom Cairney (skadad)"
     ],
     "impact": [
      1,
      1
     ]
    },
    "facts": null,
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_epl"
    },
    "note": "Modellen ser en jämn match med 38, 27 och 36 %, där Ipswich är en aning troligast. Ipswich ligger 11:a med 6 poäng, medan Fulham är 19:e med 2 poäng och saknar vinst (FFFOO). Båda lagen släpper in över 2 xG per match, 2,06 för Ipswich och 2,09 för Fulham. Strecken ligger nära modellen med spelvärden mellan 0,94 och 1,09, så inget tecken sticker ut.",
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
    "table": null,
    "form": {},
    "xg": {
     "home": [
      0.88,
      1.41
     ],
     "away": [
      1.75,
      1.36
     ]
    },
    "injuries": {
     "home": [
      "Lewis Miller (skadad)",
      "Yuki Ohashi (skadad)",
      "Matty Litherland (skadad)",
      "Yuri Ribeiro (skadad)",
      "Mathias Jørgensen (osäker)"
     ],
     "away": [
      "Will Fish (skadad)",
      "Calum Chambers (skadad)",
      "Isaak Davies (skadad)",
      "Krystian Bielik (skadad)",
      "Rubin Colwill (osäker)"
     ],
     "impact": [
      1,
      2
     ]
    },
    "facts": null,
    "_src": {
     "kickoff": "2026-10-10T16:00:00+02:00",
     "sport": "soccer_efl_champ"
    },
    "note": "Cardiff är troligast med 37 % hos modellen och skapar 1,75 xG per match mot Blackburns 0,88. Folket streckar ändå Blackburn till 52 % mot modellens 36 %, så ettan är kraftigt överstreckad med spelvärde 0,69. Cardiff har fyra skadade, bland dem Calum Chambers och Krystian Bielik, men tvåan streckas bara till 24 %.",
    "valueNote": "Tvåan har spelvärde 1,53 när modellen ger Cardiff 37 % och folket bara 24 %, och Cardiff skapar dubbelt så mycket xG som Blackburn."
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
     "sport": "soccer_efl_champ"
    },
    "note": "Modellen ger 35, 28 och 37 %, så Stoke är bara marginellt troligast. Folket streckar nästan exakt likadant med 34, 28 och 38 %, och spelvärdena ligger mellan 0,98 och 1,04. Underlaget saknar form och xG, så matchen är öppen.",
    "valueNote": ""
   },
   {
    "n": 8,
    "home": "Derby",
    "away": "Wrexham",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     35,
     28,
     37
    ],
    "odds": [
     2.65,
     3.29,
     2.56
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
     "sport": "soccer_efl_champ"
    },
    "note": "Modellen ger 35, 28 och 36 %, och Wrexham är en hårsmån troligast. Folket streckar 35, 28 och 37 %, så inget tecken är felstreckat och spelvärdena ligger mellan 0,98 och 1,01. Underlaget saknar form och xG.",
    "valueNote": ""
   },
   {
    "n": 9,
    "home": "Middlesbrough",
    "away": "Wolverhampton",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     51,
     24,
     25
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
     "sport": "soccer_efl_champ"
    },
    "note": "Middlesbrough är troligast med 42 % hos modellen och ligger 3:a med 15 poäng på 8 matcher, strax före Wolverhampton som har 14 poäng på 7 matcher. Folket streckar ettan till 51 %, så den är överstreckad med spelvärde 0,83. Tvåan är understreckad med 25 % hos folket mot modellens 32 % och har spelvärde 1,29.",
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
     "sport": "soccer_efl_champ"
    },
    "note": "Millwall är troligast med 39 % hos modellen, i linje med oddset 2,42. Folket streckar tvåan till 44 %, vilket ger spelvärde 0,88. Ettan är understreckad med 29 % hos folket mot modellens 34 % och har spelvärde 1,17.",
    "valueNote": ""
   },
   {
    "n": 11,
    "home": "Sheffield United",
    "away": "Lincoln",
    "league": "Championship",
    "kickoff": "16:00",
    "folk": [
     57,
     21,
     22
    ],
    "odds": [
     2.08,
     3.37,
     3.4
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
     "sport": "soccer_efl_champ"
    },
    "note": "Sheffield United är troligast med 45 % hos modellen, men folket streckar ettan till 57 %, vilket ger spelvärde 0,79. Krysset är understreckat med 21 % hos folket mot modellens 28 % och har spelvärde 1,32. Även tvåan har spelvärde med 22 % hos folket mot modellens 27 %.",
    "valueNote": ""
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
     2.95,
     3.47,
     2.27
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
     "sport": "soccer_efl_champ"
    },
    "note": "Burnley är troligast med 41 % hos modellen, och oddset 2,27 pekar åt samma håll. Folket streckar ändå Watford till 44 % mot modellens 32 %, så ettan är överstreckad med spelvärde 0,72. Tvåan streckas bara till 30 %.",
    "valueNote": "Tvåan har spelvärde 1,38 eftersom modellen ger Burnley 41 % medan folket bara streckar 30 %."
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
    "note": "Huddersfield är troligast med 55 % hos modellen, och folket streckar nästan exakt likadant med 56 %. Ettan är alltså rätt streckad med spelvärde 0,98. Tvåan är något understreckad med 19 % hos folket mot modellens 22 % och har spelvärde 1,16.",
    "valueNote": ""
   }
  ]
 }
];
