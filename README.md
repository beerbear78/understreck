# Understreck

Hittar tecken som svenska folket har understreckat på Stryktipset. Sidan visar modellens
sannolikheter, spelvärde, en kort analys per match och färdiga 64-raderssystem (balanserat och skräll).

Allt uppdateras automatiskt av GitHub Actions:

| När | Vad |
|---|---|
| Fredag 19:00 (18:00 vintertid) | Hämtar lördagens kupong, odds, form, tabell, xG och skador. Claude skriver analyserna. |
| Lördag, cirka en timme före första match | Lägger in startelvor, färska odds och folkets senaste streck. Räknar om allt. |

## Kom igång (en gång)

### 1. Ladda upp filerna
1. Öppna ditt repo **understreck** på GitHub (det ska vara **Public**, annars kostar GitHub Pages pengar).
2. Klicka **Add file → Upload files**.
3. Dra in **allt innehåll** i den här mappen: mapparna `.github`, `site`, `understreck` och filerna
   `README.md` och `requirements.txt`. Mappstrukturen måste vara kvar.
4. Klicka **Commit changes**.

> Syns inte mappen `.github` i filväljaren? Dra den från Utforskaren i stället, eller skapa filen
> `.github/workflows/update.yml` för hand via **Add file → Create new file** och klistra in innehållet.

### 2. Lägg in nycklarna
**Settings → Secrets and variables → Actions → New repository secret.** Skapa tre stycken:

| Name | Värde |
|---|---|
| `ODDS_API_KEY` | Nyckeln från the-odds-api.com |
| `API_FOOTBALL_KEY` | Nyckeln från api-football.com (dashboard.api-football.com) |
| `ANTHROPIC_API_KEY` | Nyckeln från platform.claude.com → API Keys |

Nycklarna syns aldrig i koden eller loggarna.

### 3. Slå på sidan
**Settings → Pages → Build and deployment → Source: GitHub Actions.**

### 4. Testkör
1. **Actions → Uppdatera Understreck → Run workflow**, välj `friday`, klicka **Run workflow**.
2. Vänta 3–6 minuter. Klicka på körningen för att se veckans topp 3 och 64-raderna i sammanfattningen.
3. Sidan finns på `https://<ditt-användarnamn>.github.io/understreck/`.

Om körningen blir röd: öppna den och läs loggen under **Hämta data och räkna**. Vanligaste orsaken är
en felstavad nyckel.

## Inställningar (valfritt)
**Settings → Secrets and variables → Actions → Variables:**

| Variabel | Standard | Betydelse |
|---|---|---|
| `CLAUDE_MODEL` | `claude-opus-5-5` | Sätt `claude-sonnet-5-5` för halva kostnaden. |
| `RESEARCH` | `1` | `0` stänger av Claudes webbsökning när de gratis API:erna saknar data. |

## Kostnad
* The Odds API: 4–6 krediter per körning av 500 gratis i månaden.
* API-Football: cirka 25 anrop per körning av 100 gratis per dag.
* understat.com (xG för Premier League) och tipsrader.se (folkets streck): gratis.
* Claude: analyserna kostar några cent per körning. Webbsökningen (om API-Football inte täcker säsongen,
  eller för xG utanför Premier League) kostar cirka 0,1–0,5 dollar per körning. Följ förbrukningen på
  platform.claude.com.

## Bra att veta
* GitHub kan fördröja schemalagda körningar 5–20 minuter. Lördagskörningen har marginal för det.
* Startelvor läggs bara in för matcher som startar vid första avspark. Spelstoppet är vid första matchen,
  så senare startelvor kan ändå inte påverka raden.
* Om tipsrader.se är nere eller har ändrat sidan avbryts fredagskörningen och GitHub mejlar dig.
  Folkets streck kan också skrivas in för hand direkt på sidan.
* Spel om pengar kan vara beroendeframkallande. Stödlinjen: 020-81 91 00, stodlinjen.se.

## Köra lokalt
```bash
pip install -r requirements.txt
python -m understreck --mode friday --dry-run
```
Utan nycklar körs det som går: kupong och streck från tipsrader.se, xG från understat.com och
analystexter från mallar.
