#!/usr/bin/env python3
"""Qualitätsupdate für Zeitreise: Issues #3, #4 und #5.

Wird nach „Website vorbereiten“ auf _site/ angewendet.
Keine externen Python-Pakete erforderlich.
"""

from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "_site"
RELEASE = "quality-3-4-5-v1"

# Format je Zeile:
# Sachverhaltsindex | direkte Frage | Jahresfrage |
# drei falsche direkte Antworten, getrennt durch ~ |
# zusätzliche Frage | deren richtige Antwort |
# drei falsche Antworten dazu, getrennt durch ~
#
# Die richtige Antwort der direkten Frage sowie die bestehenden IDs,
# Kategorien, Jahrzehnte und Quellen werden aus dem Original übernommen.
DATA = r"""
0|Welcher Black-Sabbath-Titel erreichte Ende 1970 Platz eins der deutschen Singlecharts?|In welchem Jahr erreichte Black Sabbaths „Paranoid“ erstmals Platz eins der deutschen Singlecharts?|„Smoke on the Water“ – Deep Purple~„Whole Lotta Love“ – Led Zeppelin~„Black Night“ – Deep Purple|Welche Band veröffentlichte „Paranoid“?|Black Sabbath|Deep Purple~Led Zeppelin~Uriah Heep
1|Mit welchem Lied landete Danyel Gérard 1971 einen großen Hit in Deutschland?|In welchem Jahr stand Danyel Gérards „Butterfly“ in Deutschland auf Platz eins?|„A Song of Joy“ – Miguel Ríos~„Mamy Blue“ – Pop-Tops~„Seasons in the Sun“ – Terry Jacks|Wer sang den Hit „Butterfly“?|Danyel Gérard|Miguel Ríos~Terry Jacks~Gilbert O’Sullivan
2|Welches elektronische Instrumentalstück machte Hot Butter 1972 international bekannt?|In welchem Jahr wurde Hot Butters „Popcorn“ ein deutscher Nummer-eins-Hit?|„Oxygène IV“ – Jean-Michel Jarre~„Autobahn“ – Kraftwerk~„Magic Fly“ – Space|Welche Gruppe veröffentlichte die erfolgreiche Version von „Popcorn“ aus dem Jahr 1972?|Hot Butter|Kraftwerk~Space~Tangerine Dream
3|Mit welchem Titel erreichte The Sweet 1973 Platz eins in Deutschland?|In welchem Jahr wurde „Block Buster!“ von The Sweet ein deutscher Nummer-eins-Hit?|„Cum On Feel the Noize“ – Slade~„Children of the Revolution“ – T. Rex~„All the Young Dudes“ – Mott the Hoople|Welche Band veröffentlichte „Block Buster!“?|The Sweet|Slade~T. Rex~Mott the Hoople
4|Mit welchem Lied gewann ABBA den Eurovision Song Contest 1974?|In welchem Jahr gewann ABBA mit „Waterloo“ den Eurovision Song Contest?|„Ring Ring“ – ABBA~„SOS“ – ABBA~„Fernando“ – ABBA|Für welches Land trat ABBA beim Eurovision-Sieg mit „Waterloo“ an?|Schweden|Norwegen~Dänemark~Finnland
5|Mit welchem deutschsprachigen Lied über Gastarbeiter hatte Udo Jürgens 1975 einen Nummer-eins-Hit?|In welchem Jahr erreichte Udo Jürgens mit „Griechischer Wein“ Platz eins der deutschen Singlecharts?|„Ein ehrenwertes Haus“ – Udo Jürgens~„Aber bitte mit Sahne“ – Udo Jürgens~„Mit 66 Jahren“ – Udo Jürgens|Wer sang „Griechischer Wein“?|Udo Jürgens|Peter Alexander~Howard Carpendale~Michael Holm
6|Welcher ABBA-Hit über eine junge Tänzerin erreichte 1976 Platz eins in Deutschland?|In welchem Jahr erreichte ABBAs „Dancing Queen“ erstmals Platz eins in Deutschland?|„Mamma Mia“ – ABBA~„Knowing Me, Knowing You“ – ABBA~„Take a Chance on Me“ – ABBA|Welche Gruppe veröffentlichte „Dancing Queen“?|ABBA|Boney M.~Baccara~Bee Gees
7|Mit welchem Lied landete das Duo Baccara 1977 seinen großen Disco-Hit?|In welchem Jahr wurde „Yes Sir, I Can Boogie“ von Baccara ein deutscher Nummer-eins-Hit?|„Daddy Cool“ – Boney M.~„Love Is in the Air“ – John Paul Young~„I Feel Love“ – Donna Summer|Welches Duo sang „Yes Sir, I Can Boogie“?|Baccara|Maywood~Ottawan~The Pointer Sisters
8|Welcher Boney-M.-Hit aus dem Jahr 1978 trägt Babylon im Titel?|In welchem Jahr wurde „Rivers of Babylon“ von Boney M. ein deutscher Nummer-eins-Hit?|„Daddy Cool“ – Boney M.~„Sunny“ – Boney M.~„Ma Baker“ – Boney M.|Welche Gruppe veröffentlichte den Disco-Hit „Rivers of Babylon“?|Boney M.|Baccara~Eruption~Village People
9|Welcher Blondie-Hit mit „Glass“ im Titel stand 1979 in Deutschland auf Platz eins?|In welchem Jahr erreichte Blondies „Heart of Glass“ Platz eins in Deutschland?|„Denis“ – Blondie~„Hanging on the Telephone“ – Blondie~„Sunday Girl“ – Blondie|Welche Band veröffentlichte „Heart of Glass“?|Blondie|The Pretenders~The Runaways~Siouxsie and the Banshees
10|Mit welcher Folge begann die ARD-Krimireihe „Tatort“ am 29. November 1970?|In welchem Jahr wurde die erste „Tatort“-Folge „Taxi nach Leipzig“ ausgestrahlt?|„Reifezeugnis“~„Duisburg-Ruhrort“~„Tote Taube in der Beethovenstraße“|Welche Krimireihe startete mit „Taxi nach Leipzig“?|Tatort|Derrick~Der Alte~Polizeiruf 110
11|Welche Kindersendung startete 1971 als „Lach- und Sachgeschichten“ mit einer orangefarbenen Maus?|In welchem Jahr feierte „Die Sendung mit der Maus“ ihre Fernsehpremiere?|„Löwenzahn“~„Sesamstraße“~„Die Rappelkiste“|Welche Farbe hat die namensgebende Maus der „Sendung mit der Maus“?|Orange|Gelb~Braun~Grau
12|Welcher Mafiafilm von Francis Ford Coppola kam 1972 erstmals ins Kino?|In welchem Jahr kam der erste Film „Der Pate“ in die Kinos?|„Es war einmal in Amerika“~„GoodFellas“~„Scarface“|Wer führte bei „Der Pate“ Regie?|Francis Ford Coppola|Martin Scorsese~Brian De Palma~Sergio Leone
13|Welcher Horrorfilm von William Friedkin handelt von der besessenen Regan MacNeil?|In welchem Jahr kam William Friedkins „Der Exorzist“ erstmals in die US-Kinos?|„Das Omen“~„Rosemaries Baby“~„Amityville Horror“|Wer führte bei „Der Exorzist“ Regie?|William Friedkin|John Carpenter~Wes Craven~George A. Romero
14|In welcher deutschen Familienserie steht „Ekel Alfred“ Tetzlaff im Mittelpunkt?|In welchem Jahr wurde „Ein Herz und eine Seele“ erstmals im WDR ausgestrahlt?|„Familie Heinz Becker“~„Die Unverbesserlichen“~„Diese Drombuschs“|Wie heißt das Familienoberhaupt aus „Ein Herz und eine Seele“?|Alfred Tetzlaff|Heinz Becker~Kurt Drombusch~Alfred Doolittle
15|Welcher Steven-Spielberg-Film machte 1975 einen menschenfressenden Hai zum Kinostar?|In welchem Jahr kam Steven Spielbergs „Der weiße Hai“ erstmals in die US-Kinos?|„Orca – Der Killerwal“~„Piranhas“~„Tentacles“|Wer führte bei „Der weiße Hai“ Regie?|Steven Spielberg|John Carpenter~Ridley Scott~Brian De Palma
16|Welcher Boxerfilm mit Sylvester Stallone kam 1976 erstmals ins Kino?|In welchem Jahr kam der erste „Rocky“-Film in die Kinos?|„Wie ein wilder Stier“~„Die Kampfmaschine“~„Die Bären sind los“|Wer spielt den Boxer Rocky Balboa?|Sylvester Stallone|Robert De Niro~Al Pacino~Burt Reynolds
17|Welcher Weltraumfilm von George Lucas kam 1977 erstmals ins Kino?|In welchem Jahr kam der ursprüngliche Film „Krieg der Sterne“ erstmals in die US-Kinos?|„Kampfstern Galactica“~„Star Trek – Der Film“~„Buck Rogers“|Wer führte beim ursprünglichen Film „Krieg der Sterne“ Regie?|George Lucas|Steven Spielberg~Ridley Scott~Stanley Kubrick
18|Welches Filmmusical vereinte 1978 John Travolta und Olivia Newton-John?|In welchem Jahr kam das Filmmusical „Grease“ erstmals in die Kinos?|„Saturday Night Fever“~„Hair“~„Fame“|Welche Schauspielerin spielt neben John Travolta die Sandy in „Grease“?|Olivia Newton-John|Liza Minnelli~Barbra Streisand~Stockard Channing
19|Welches Familiendrama von 1979 zeigt Dustin Hoffman und Meryl Streep in einem Sorgerechtsstreit?|In welchem Jahr kam „Kramer gegen Kramer“ erstmals in die US-Kinos?|„Eine ganz normale Familie“~„Eine entheiratete Frau“~„Zeit der Zärtlichkeit“|Welches Schauspielerpaar spielt die Eltern in „Kramer gegen Kramer“?|Dustin Hoffman und Meryl Streep|Robert Redford und Jane Fonda~Jack Nicholson und Shirley MacLaine~Woody Allen und Diane Keaton
20|Welches frühe Atari-Arcadespiel zeigt vereinfachtes Tischtennis mit zwei Schlägern?|In welchem Jahr veröffentlichte Atari das Arcade-Spiel „Pong“?|Breakout~Space Invaders~Asteroids|Welche Firma veröffentlichte das ursprüngliche Arcade-Spiel „Pong“?|Atari|Taito~Namco~Sega
21|Welches Systemspielzeug mit Figuren von Hans Beck wurde 1974 auf der Nürnberger Spielwarenmesse vorgestellt?|In welchem Jahr wurde Playmobil auf der Nürnberger Spielwarenmesse vorgestellt?|LEGO~Fischer-Technik~Baufix|Wer entwickelte die ursprünglichen Playmobil-Figuren?|Hans Beck|Ole Kirk Christiansen~Artur Fischer~Rolf Kauka
22|Welche neue Volljährigkeitsgrenze galt in der Bundesrepublik ab dem 1. Januar 1975?|In welchem Jahr trat in der Bundesrepublik die Volljährigkeit mit 18 in Kraft?|Volljährigkeit ab 16~Volljährigkeit ab 20~Volljährigkeit ab 21|Von welchem Alter wurde die Volljährigkeitsgrenze auf 18 Jahre gesenkt?|21 Jahre|20 Jahre~23 Jahre~25 Jahre
23|Welche IKEA-Niederlassung war 1974 die erste in Deutschland?|In welchem Jahr eröffnete IKEA sein erstes deutsches Einrichtungshaus in Eching?|IKEA in Hamburg~IKEA in Köln~IKEA in Frankfurt|In der Nähe welcher Großstadt liegt das erste deutsche IKEA-Einrichtungshaus in Eching?|München|Stuttgart~Frankfurt am Main~Nürnberg
24|Welchen farbfähigen Computer brachte Apple 1977 mit Gehäuse und Tastatur auf den Markt?|In welchem Jahr wurde der Apple II vorgestellt?|Commodore PET~TRS-80~Atari 800|Welcher Hersteller brachte den Apple II heraus?|Apple|Atari~Commodore~Tandy
25|Welcher Commodore-Computer von 1977 vereinte Monitor, Tastatur und Kassettenlaufwerk in einem Gehäuse?|In welchem Jahr wurde der Commodore PET vorgestellt?|TRS-80~Apple II~Atari 800|Welches Speichermedium nutzte das eingebaute Laufwerk des ursprünglichen Commodore PET?|Kompaktkassette|5,25-Zoll-Diskette~8-Zoll-Diskette~Lochstreifen
26|Welcher Heimcomputer von Tandy Radio Shack erschien 1977 zunächst mit Z80-Prozessor und 4 KB RAM?|In welchem Jahr brachte Tandy Radio Shack den ersten TRS-80 heraus?|Commodore PET~Apple II~Sinclair ZX80|Welcher Anbieter brachte den TRS-80 auf den Markt?|Tandy Radio Shack|Commodore~Sinclair~Atari
27|Wie hieß Sonys erster Walkman von 1979?|In welchem Jahr kam der Sony Walkman TPS-L2 auf den Markt?|Sony WM-DD~Sony WM-D6~Sony TC-D5|Welches Tonmedium spielt der Walkman TPS-L2 ab?|Kompaktkassetten|Mikrokassetten~8-Track-Kassetten~Compact Discs
28|Welches Brettspiel gewann 1979 die erste Auszeichnung „Spiel des Jahres“?|In welchem Jahr wurde „Hase und Igel“ zum ersten „Spiel des Jahres“ gekürt?|Rummikub~Scotland Yard~Dampfross|Wer entwickelte das Brettspiel „Hase und Igel“?|David Parlett|Sid Sackson~Alex Randolph~Wolfgang Kramer
29|Welches elektronische Spielgerät von Parker bot sechs verschiedene Spiele?|In welchem Jahr erschien das elektronische Spielgerät Merlin in Deutschland?|Senso~Little Professor~Speak & Spell|Wie viele Spiele bot das elektronische Spielgerät Merlin?|Sechs|Vier~Acht~Zehn
30|Welche Olympischen Sommerspiele wurden vom Attentat auf die israelische Mannschaft überschattet?|In welchem Jahr fanden die Olympischen Sommerspiele in München statt?|Olympische Sommerspiele in Montreal~Olympische Sommerspiele in Moskau~Olympische Sommerspiele in Mexiko-Stadt|In welcher deutschen Stadt fanden die Olympischen Sommerspiele 1972 statt?|München|Berlin~Hamburg~Frankfurt am Main
31|Welches Ereignis betraf am 18. September 1973 beide deutschen Staaten?|In welchem Jahr wurden die Bundesrepublik und die DDR Mitglieder der UNO?|Aufnahme von BRD und DDR in die EG~Aufnahme von BRD und DDR in die NATO~Aufnahme von BRD und DDR in den Europarat|Welcher internationalen Organisation traten BRD und DDR 1973 gemeinsam bei?|Vereinte Nationen|Europäische Gemeinschaften~NATO~Europarat
32|Welche Verkehrsbeschränkung führte die Bundesrepublik während der Ölkrise 1973 an vier Sonntagen ein?|In welchem Jahr gab es in der Bundesrepublik vier autofreie Sonntage als Reaktion auf die Ölkrise?|Autofreie Samstage~Dauerhafte Fahrverbote für Dieselautos~Wechselnde Fahrtage nach gerader und ungerader Kennzeichennummer|Welche Krise führte 1973 zu den autofreien Sonntagen?|Ölkrise|Stahlkrise~Kohlekrise~Währungskrise
33|Welcher Rücktritt folgte 1974 auf die Guillaume-Affäre?|In welchem Jahr trat Willy Brandt als Bundeskanzler zurück?|Rücktritt Helmut Schmidts~Rücktritt Ludwig Erhards~Rücktritt Kurt Georg Kiesingers|Welche Affäre führte unmittelbar zu Willy Brandts Rücktritt als Bundeskanzler?|Guillaume-Affäre|Spiegel-Affäre~Flick-Affäre~Lockheed-Affäre
34|Wer folgte Willy Brandt 1974 als Bundeskanzler nach?|In welchem Jahr wurde Helmut Schmidt erstmals Bundeskanzler?|Helmut Kohl wird Bundeskanzler~Walter Scheel wird Bundeskanzler~Hans-Dietrich Genscher wird Bundeskanzler|Wessen unmittelbarer Nachfolger als Bundeskanzler wurde Helmut Schmidt?|Willy Brandts|Ludwig Erhards~Kurt Georg Kiesingers~Helmut Kohls
35|Wie endete das deutsch-deutsche Gruppenspiel bei der Fußball-WM 1974?|In welchem Jahr gewann die DDR bei einer Fußball-WM mit 1:0 gegen die BRD?|DDR schlägt BRD 2:0~BRD schlägt DDR 1:0~DDR und BRD spielen 1:1|Wer erzielte das einzige Tor im WM-Spiel DDR gegen BRD 1974?|Jürgen Sparwasser|Joachim Streich~Gerd Müller~Jürgen Croy
36|Welche Mannschaft gewann das WM-Finale 1974 gegen die Niederlande?|In welchem Jahr gewann die BRD das Fußball-WM-Finale in München gegen die Niederlande?|Niederlande wird Fußballweltmeister~Brasilien wird Fußballweltmeister~Italien wird Fußballweltmeister|Wie endete das Fußball-WM-Finale 1974 aus Sicht der BRD?|2:1|1:0~3:1~3:2
37|Welcher Rücktritt eines US-Präsidenten folgte 1974 auf die Watergate-Affäre?|In welchem Jahr trat Richard Nixon als US-Präsident zurück?|Gerald Ford tritt zurück~Lyndon B. Johnson tritt zurück~Jimmy Carter tritt zurück|Welche Affäre führte zu Richard Nixons Rücktritt?|Watergate-Affäre|Iran-Contra-Affäre~Profumo-Affäre~Teapot-Dome-Affäre
38|Bei welcher Geiselbefreiung setzte die GSG 9 im Oktober 1977 in Mogadischu an?|In welchem Jahr befreite die GSG 9 die Geiseln der „Landshut“ in Mogadischu?|Befreiung der Geiseln in Entebbe~Beendigung der Botschaftsbesetzung in London~Beendigung der Entführung der „Achille Lauro“|In welcher Stadt befreite die GSG 9 die Geiseln der „Landshut“?|Mogadischu|Entebbe~Aden~Dschibuti
39|Welcher Rock-’n’-Roll-Star starb im August 1977 in Memphis?|In welchem Jahr starb Elvis Presley?|Tod von Buddy Holly~Tod von Roy Orbison~Tod von Bill Haley|In welcher Stadt starb Elvis Presley?|Memphis|Nashville~Las Vegas~New York
40|Mit welchem Disco-Hit wurde Lipps Inc. 1980 international bekannt?|In welchem Jahr wurde „Funkytown“ von Lipps Inc. ein deutscher Nummer-eins-Hit?|„Le Freak“ – Chic~„Boogie Wonderland“ – Earth, Wind & Fire~„Celebration“ – Kool & the Gang|Welche Gruppe veröffentlichte „Funkytown“?|Lipps Inc.|Chic~Kool & the Gang~The Gap Band
41|Welcher Phil-Collins-Solohit aus dem Jahr 1981 ist für seinen markanten Schlagzeugeinsatz bekannt?|In welchem Jahr wurde Phil Collins’ „In the Air Tonight“ ein deutscher Nummer-eins-Hit?|„Against All Odds“ – Phil Collins~„Easy Lover“ – Philip Bailey & Phil Collins~„Another Day in Paradise“ – Phil Collins|Wer veröffentlichte „In the Air Tonight“ als Solokünstler?|Phil Collins|Peter Gabriel~Mike Rutherford~Steve Hackett
42|Mit welchem Lied gewann Nicole den Eurovision Song Contest?|In welchem Jahr gewann Nicole mit „Ein bißchen Frieden“ den Eurovision Song Contest?|„Dschinghis Khan“ – Dschinghis Khan~„Theater“ – Katja Ebstein~„Johnny Blue“ – Lena Valaitis|Welche Sängerin gewann mit „Ein bißchen Frieden“ den Eurovision Song Contest?|Nicole|Katja Ebstein~Lena Valaitis~Mary Roos
43|Welcher Nena-Hit erzählt von Ballons, die einen militärischen Alarm auslösen?|In welchem Jahr erreichte Nenas „99 Luftballons“ erstmals Platz eins in Deutschland?|„Nur geträumt“ – Nena~„Leuchtturm“ – Nena~„Irgendwie, irgendwo, irgendwann“ – Nena|Welche Band veröffentlichte „99 Luftballons“?|Nena|Ideal~Extrabreit~Fräulein Menke
44|Mit welchem Lied landete Alphaville 1984 einen internationalen Synthpop-Hit?|In welchem Jahr wurde Alphavilles „Big in Japan“ ein deutscher Nummer-eins-Hit?|„Forever Young“ – Alphaville~„Sounds Like a Melody“ – Alphaville~„A Victory of Love“ – Alphaville|Welche Band veröffentlichte „Big in Japan“?|Alphaville|Camouflage~Depeche Mode~Ultravox
45|Welcher a-ha-Hit wurde durch ein Musikvideo mit gezeichneten Szenen berühmt?|In welchem Jahr erreichte die erfolgreiche Neuaufnahme von a-has „Take On Me“ Platz eins in Deutschland?|„The Sun Always Shines on T.V.“ – a-ha~„Hunting High and Low“ – a-ha~„Cry Wolf“ – a-ha|Welche Band veröffentlichte „Take On Me“?|a-ha|Duran Duran~Tears for Fears~Spandau Ballet
46|Welcher Europe-Hit beginnt mit einem besonders bekannten Synthesizer-Motiv?|In welchem Jahr wurde Europes „The Final Countdown“ ein deutscher Nummer-eins-Hit?|„Jump“ – Van Halen~„Here I Go Again“ – Whitesnake~„Livin’ on a Prayer“ – Bon Jovi|Welche Band veröffentlichte „The Final Countdown“?|Europe|Bon Jovi~Whitesnake~Def Leppard
47|Mit welchem Lied standen die Pet Shop Boys 1987 in Deutschland auf Platz eins?|In welchem Jahr wurde „It’s a Sin“ ein deutscher Nummer-eins-Hit?|„West End Girls“ – Pet Shop Boys~„Suburbia“ – Pet Shop Boys~„Always on My Mind“ – Pet Shop Boys|Welches Duo veröffentlichte „It’s a Sin“?|Pet Shop Boys|Erasure~Soft Cell~Tears for Fears
48|Welcher A-cappella-Hit von Bobby McFerrin wurde 1988 international erfolgreich?|In welchem Jahr wurde „Don’t Worry, Be Happy“ ein deutscher Nummer-eins-Hit?|„Only You“ – The Flying Pickets~„Caravan of Love“ – The Housemartins~„Tom’s Diner“ – Suzanne Vega|Wer sang „Don’t Worry, Be Happy“?|Bobby McFerrin|Al Jarreau~George Benson~Lionel Richie
49|Mit welchem Lied landete David Hasselhoff 1989 einen Nummer-eins-Hit in Deutschland?|In welchem Jahr erreichte David Hasselhoffs „Looking for Freedom“ Platz eins in Deutschland?|„Limbo Dance“ – David Hasselhoff~„Crazy for You“ – David Hasselhoff~„Do the Limbo Dance“ – David Hasselhoff|Wer veröffentlichte die in Deutschland erfolgreiche Version von „Looking for Freedom“ aus dem Jahr 1989?|David Hasselhoff|David Cassidy~Don Johnson~Rick Springfield
50|Welche japanische Zeichentrickserie um einen Weltraumhelden startete 1980 im ZDF?|In welchem Jahr wurde „Captain Future“ erstmals im deutschen ZDF ausgestrahlt?|„Captain Harlock“~„Saber Rider“~„Die Königin der tausend Jahre“|Welcher deutsche Fernsehsender zeigte „Captain Future“ erstmals?|ZDF|ARD~RTL~Sat.1
51|In welchem Film spielte Harrison Ford erstmals den Archäologen Indiana Jones?|In welchem Jahr kam „Jäger des verlorenen Schatzes“ erstmals in die Kinos?|„Indiana Jones und der Tempel des Todes“~„Indiana Jones und der letzte Kreuzzug“~„Auf der Jagd nach dem grünen Diamanten“|Welchen Beruf hat Indiana Jones?|Archäologe|Geologe~Ethnologe~Paläontologe
52|Welcher Spielberg-Film zeigt die Freundschaft des Jungen Elliott mit einem Außerirdischen?|In welchem Jahr startete „E.T. – Der Außerirdische“ in westdeutschen Kinos?|„Unheimliche Begegnung der dritten Art“~„Explorers“~„Der Flug des Navigators“|Wie heißt der Junge, der sich in „E.T.“ mit dem Außerirdischen anfreundet?|Elliott|Marty~Billy~David
53|Welche Fernsehserie handelt von Colt Seavers, einem Stuntman und Kopfgeldjäger?|In welchem Jahr startete „Ein Colt für alle Fälle“ im deutschen ZDF?|„Ein Duke kommt selten allein“~„Trio mit vier Fäusten“~„Das A-Team“|Welche beiden Tätigkeiten übt Colt Seavers aus?|Stuntman und Kopfgeldjäger|Rennfahrer und Privatdetektiv~Mechaniker und Polizist~Pilot und Geheimagent
54|Welche Filmkomödie zeigt Geisterjäger und ein riesiges Marshmallow-Maskottchen?|In welchem Jahr kam der erste „Ghostbusters“-Film in die Kinos?|„Beetlejuice“~„Die Geister, die ich rief …“~„Die Gespenster von Flatterfels“|Aus welchem Material besteht das riesige Stay-Puft-Maskottchen in „Ghostbusters“?|Marshmallow|Zuckerwatte~Kaugummi~Schokolade
55|In welchem Film reist Marty McFly mit einem DeLorean in die Vergangenheit?|In welchem Jahr kam der erste Film „Zurück in die Zukunft“ in die Kinos?|„Bill & Teds verrückte Reise durch die Zeit“~„Die Reise in die Zeit“~„Time Bandits“|Welches Auto dient in „Zurück in die Zukunft“ als Zeitmaschine?|DeLorean DMC-12|Pontiac Firebird~Chevrolet Corvette~Porsche 928
56|Welche Sitcom zeigt den Außerirdischen Gordon Shumway bei Familie Tanner?|In welchem Jahr startete „ALF“ erstmals im US-Fernsehen?|„Mork vom Ork“~„Mein Onkel vom Mars“~„Small Wonder“|Wie heißt ALF mit seinem ursprünglichen Namen?|Gordon Shumway|Mork~Uncle Martin~Roger Smith
57|Welcher Tanzfilm vereinte Patrick Swayze und Jennifer Grey?|In welchem Jahr kam „Dirty Dancing“ erstmals in die Kinos?|„Footloose“~„Flashdance“~„Fame“|Wer spielt Johnny Castle in „Dirty Dancing“?|Patrick Swayze|Kevin Bacon~John Travolta~Rob Lowe
58|Welcher Film zeigt Dustin Hoffman und Tom Cruise als Brüder auf einer Reise durch die USA?|In welchem Jahr kam „Rain Man“ erstmals in die US-Kinos?|„Die Farbe des Geldes“~„Die Glücksritter“~„Das Geheimnis meines Erfolges“|Welches Schauspielerpaar spielt die Brüder in „Rain Man“?|Dustin Hoffman und Tom Cruise|Paul Newman und Tom Cruise~Robert De Niro und Sean Penn~Al Pacino und Chris O’Donnell
59|Welcher Film setzt Marty McFlys Zeitreisen mit einem Besuch im Jahr 2015 fort?|In welchem Jahr kam „Zurück in die Zukunft II“ erstmals in die Kinos?|„Zurück in die Zukunft III“~„Bill & Teds verrückte Reise in die Zukunft“~„Timecop“|In welches Zukunftsjahr reisen Marty und Doc in „Zurück in die Zukunft II“?|2015|2005~2020~2025
60|Welches Zahlenlegespiel gewann 1980 die Auszeichnung „Spiel des Jahres“?|In welchem Jahr wurde Rummikub zum „Spiel des Jahres“ gewählt?|Hase und Igel~Scotland Yard~Dampfross|Was ist auf den üblichen Rummikub-Spielsteinen hauptsächlich abgebildet?|Zahlen|Buchstaben~Länderkarten~Tierbilder
61|Welcher Commodore-Heimcomputer von 1982 wurde als „Brotkasten“ bekannt?|In welchem Jahr wurde der Commodore 64 vorgestellt?|Commodore VIC-20~Commodore 16~Commodore Plus/4|Wie viel Arbeitsspeicher besitzt ein ursprünglicher Commodore 64?|64 KB|16 KB~32 KB~128 KB
62|Welcher Sinclair-Heimcomputer erschien 1982 mit 16 oder 48 KB RAM und Farbgrafik?|In welchem Jahr wurde der ursprüngliche ZX Spectrum vorgestellt?|Sinclair ZX80~Sinclair ZX81~Sinclair QL|Mit welchen RAM-Größen wurde der ursprüngliche ZX Spectrum angeboten?|16 und 48 KB|16 und 64 KB~32 und 64 KB~48 und 128 KB
63|Bei welchem Brettspiel jagt ein Detektivteam Mister X durch London?|In welchem Jahr wurde Scotland Yard zum „Spiel des Jahres“ gewählt?|Cluedo~Die Scotland-Yard-Kriminalakte~Das verrückte Labyrinth|In welcher Stadt spielt das ursprüngliche Brettspiel Scotland Yard?|London|Paris~Berlin~Wien
64|Welcher Apple-Computer wurde 1984 mit grafischer Oberfläche und Maus eingeführt?|In welchem Jahr wurde der ursprüngliche Apple Macintosh vorgestellt?|Apple Lisa~Apple II~Apple III|Welche Firma entwickelte den Macintosh?|Apple|Commodore~Atari~Sinclair
65|Welche nichtflüchtige Speichertechnik entwickelte Fujio Masuoka bei Toshiba?|In welchem Jahr stellte Fujio Masuoka seine Flash-Speichertechnik auf der IEDM öffentlich vor?|DRAM~SRAM~Magnetblasenspeicher|Wer entwickelte bei Toshiba die Flash-Speichertechnik?|Fujio Masuoka|Federico Faggin~Ted Hoff~Jack Kilby
66|Wie hieß Sonys kompakter tragbarer CD-Spieler aus dem Jahr 1984?|In welchem Jahr kam der Sony Discman D-50 auf den Markt?|Sony Walkman TPS-L2~Sony MZ-1~Sony WM-D6|Welches Medium spielt der Sony D-50 ab?|Audio-CD|Kompaktkassette~MiniDisc~DAT-Kassette
67|Welches erste Amiga-Modell stellte Commodore 1985 vor?|In welchem Jahr wurde der Commodore Amiga 1000 vorgestellt?|Commodore Amiga 500~Commodore Amiga 2000~Commodore Amiga 3000|Welcher Hersteller brachte den Amiga 1000 auf den Markt?|Commodore|Atari~Apple~Acorn
68|Welche Walkman-Neuerung führte Sony 1988 mit dem Modell WM-505 ein?|In welchem Jahr brachte Sony den Walkman WM-505 mit drahtlosen Kopfhörern heraus?|Walkman mit MiniDisc-Aufnahme~Walkman mit DAB-Empfänger~Walkman mit MP3-Wiedergabe|Welches Walkman-Modell verband Sony 1988 mit drahtlosen Kopfhörern?|WM-505|TPS-L2~WM-DD~WM-D6
69|Welche tragbare Nintendo-Konsole von 1989 wurde unter anderem mit Tetris besonders erfolgreich?|In welchem Jahr erschien der ursprüngliche Nintendo Game Boy erstmals in Japan?|Atari Lynx~Sega Game Gear~NEC PC Engine GT|Welches Unternehmen entwickelte den ursprünglichen Game Boy?|Nintendo|Sega~Atari~NEC
70|Wer wurde 1982 durch ein konstruktives Misstrauensvotum Bundeskanzler?|In welchem Jahr löste Helmut Kohl Helmut Schmidt als Bundeskanzler ab?|Hans-Dietrich Genscher wird Bundeskanzler~Franz Josef Strauß wird Bundeskanzler~Richard von Weizsäcker wird Bundeskanzler|Durch welches parlamentarische Verfahren wurde Helmut Kohl 1982 Bundeskanzler?|Konstruktives Misstrauensvotum|Direktwahl durch die Bevölkerung~Vertrauensfrage des Bundespräsidenten~Neuwahl des Bundesrates
71|Welche Mannschaft gewann das Fußball-WM-Finale 1982 gegen die BRD?|In welchem Jahr gewann Italien das Fußball-WM-Finale in Madrid gegen die BRD?|Argentinien wird Fußballweltmeister~Brasilien wird Fußballweltmeister~Frankreich wird Fußballweltmeister|Wie endete das Fußball-WM-Finale 1982 aus italienischer Sicht?|3:1|2:1~2:0~3:2
72|Wie heißt der Krieg von 1982 zwischen Großbritannien und Argentinien um eine Inselgruppe?|In welchem Jahr fand der Falklandkrieg statt?|Suezkrieg~Golfkrieg~Beagle-Konflikt|Welche Staaten kämpften im Falklandkrieg gegeneinander?|Großbritannien und Argentinien|Großbritannien und Chile~Spanien und Argentinien~Großbritannien und Uruguay
73|Welche Reaktorkatastrophe führte 1986 auch in der Bundesrepublik zu erhöhter Strahlenbelastung?|In welchem Jahr ereignete sich die Reaktorkatastrophe von Tschernobyl?|Reaktorunfall von Three Mile Island~Reaktorunfall von Windscale~Reaktorkatastrophe von Fukushima|In welchem heutigen Staat liegt das Kernkraftwerk Tschernobyl?|Ukraine|Belarus~Russland~Litauen
74|Welche US-Raumfähre zerbrach 1986 kurz nach dem Start?|In welchem Jahr ereignete sich das Challenger-Unglück?|Columbia-Unglück~Apollo-1-Unglück~Sojus-11-Unglück|Wie viele Besatzungsmitglieder starben beim Challenger-Unglück?|Sieben|Fünf~Sechs~Acht
75|Welches neue Bundesressort übernahm Walter Wallmann 1986 als erster Minister?|In welchem Jahr wurde das Bundesumweltministerium gegründet?|Gründung des Bundesforschungsministeriums~Gründung des Bundesgesundheitsministeriums~Gründung des Bundesentwicklungsministeriums|Wer war der erste Bundesumweltminister?|Walter Wallmann|Klaus Töpfer~Jürgen Trittin~Norbert Röttgen
76|Welche Mannschaft gewann das Fußball-WM-Finale 1986 gegen die BRD?|In welchem Jahr gewann Argentinien das Fußball-WM-Finale gegen die BRD?|Italien wird Fußballweltmeister~Brasilien wird Fußballweltmeister~Frankreich wird Fußballweltmeister|Wie endete das Fußball-WM-Finale 1986 aus argentinischer Sicht?|3:2|2:1~3:1~2:0
77|Welche Leistung gelang Steffi Graf 1988 mit vier Grand-Slam-Titeln und Olympiagold?|In welchem Jahr gelang Steffi Graf ihr Golden Slam?|Steffi Grafs Karriere-Grand-Slam~Steffi Grafs Grand-Slam-Doppel~Steffi Grafs Saison ohne Niederlage|Welche Kombination bezeichnet Steffi Grafs Golden Slam von 1988?|Vier Grand-Slam-Einzeltitel und Olympiagold im selben Jahr|Drei Grand-Slam-Einzeltitel und Olympiagold im selben Jahr~Vier Grand-Slam-Einzeltitel und der Fed-Cup-Sieg im selben Jahr~Vier Grand-Slam-Doppeltitel und Olympiagold im selben Jahr
78|Welche regelmäßigen Proteste begannen im September 1989 nach Friedensgebeten in Leipzig?|In welchem Jahr begannen die Leipziger Montagsdemonstrationen?|Beginn der Berliner Freitagsdemonstrationen~Beginn der Dresdner Dienstagsdemonstrationen~Beginn der Hallenser Samstagsdemonstrationen|In welcher Stadt begannen die bekannten Montagsdemonstrationen im September 1989?|Leipzig|Dresden~Berlin~Halle
79|Welches Ereignis folgte am 9. November 1989 auf Günter Schabowskis Pressekonferenz?|In welchem Jahr wurde die Berliner Mauer geöffnet?|Deutsche Wiedervereinigung~Unterzeichnung des Zwei-plus-Vier-Vertrags~Währungsunion von BRD und DDR|An welchem Datum wurde die Berliner Mauer geöffnet?|9. November 1989|3. Oktober 1989~17. Juni 1989~13. August 1989
"""

# Enger gefasste Alternativen für einzelne Fragen:
# Diese überschreiben die entsprechende DATA-Zeile gezielt.
EASY_OVERRIDES = {
    49: [
        "„Crazy for You“ – David Hasselhoff",
        "„Is Everybody Happy“ – David Hasselhoff",
        "„Flying on the Wings of Tenderness“ – David Hasselhoff",
    ],
    54: [
        "„Beetlejuice“",
        "„Die Geister, die ich rief …“",
        "„High Spirits“",
    ],
    63: [
        "Cluedo",
        "Heimlich & Co.",
        "Inkognito",
    ],
    68: [
        "Walkman mit integriertem Lautsprecher",
        "Walkman mit digitaler Kassettenaufzeichnung",
        "Walkman mit automatischem Kassettenwechsel",
    ],
    78: [
        "Beginn der Leipziger Freitagsdemonstrationen",
        "Beginn der Leipziger Dienstagsdemonstrationen",
        "Beginn der Leipziger Samstagsdemonstrationen",
    ],
}

SOURCES = {
    14: "https://www.fernsehserien.de/ein-herz-und-eine-seele",
    22: "https://www.bundestag.de/resource/blob/196082/Kapitel_01_03_Wahlalter.pdf",
    65: "https://www.shmj.or.jp/shimura/shimura_E/ssis_shimura2_33E.html",
}

YEAR_OVERRIDES = {
    14: "1973",
    22: "1975",
}

EXPLANATION_OVERRIDES = {
    14: (
        "„Ein Herz und eine Seele“ startete am 15. Januar 1973 im WDR. "
        "Im Mittelpunkt steht die Familie Tetzlaff mit „Ekel Alfred“."
    ),
    22: (
        "Die Volljährigkeitsgrenze sank von 21 auf 18 Jahre. "
        "Das Gesetz stammt aus dem Jahr 1974 und trat am 1. Januar 1975 in Kraft."
    ),
    65: (
        "Fujio Masuoka entwickelte Flash-Speicher bei Toshiba bereits um 1980. "
        "Die öffentliche Vorstellung auf der IEDM erfolgte 1984. "
        "Entwicklung und Vorstellung sind unterschiedliche Ereignisse."
    ),
    74: (
        "Die Raumfähre Challenger zerbrach am 28. Januar 1986 kurz nach dem Start. "
        "Alle sieben Besatzungsmitglieder kamen ums Leben."
    ),
}

ROUND_CORE = r"""
/* QUALITY-3-4-5: Auswahl immer erst filtern, dann Sachverhalte gruppieren. */
(() => {
  'use strict';

  function filter(questions, options) {
    return questions.filter(q =>
      (options.decade === 'beide' || q.decade === options.decade) &&
      options.categories.includes(q.category) &&
      (options.difficulty === 'alle' || q.difficulty === options.difficulty)
    );
  }

  function groups(pool) {
    const map = new Map();
    for (const q of pool) {
      if (!q.factId || typeof q.factId !== 'string') {
        throw new Error('Frage ohne gültige factId: ' + q.id);
      }
      if (!map.has(q.factId)) map.set(q.factId, []);
      map.get(q.factId).push(q);
    }
    return [...map.values()];
  }

  function select(pool, count, random = Math.random) {
    const wanted = Math.max(0, Math.floor(Number(count) || 0));
    const candidates = groups(pool).map(
      variants => variants[Math.floor(random() * variants.length)]
    );

    for (let i = candidates.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [candidates[i], candidates[j]] = [candidates[j], candidates[i]];
    }

    return candidates.slice(0, wanted);
  }

  window.QuizRounds = Object.freeze({
    filter,
    select,
    count: pool => groups(pool).length
  });
})();
"""

TEST_JS = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const questions = JSON.parse(fs.readFileSync(0, 'utf8'));
const R = window.QuizRounds;
const categories = [...new Set(questions.map(q => q.category))];
let checks = 0;

assert.equal(questions.length, 240);
assert.equal(new Set(questions.map(q => q.id)).size, 240);
assert.equal(R.count(questions), 80);

for (const q of questions) {
  assert.equal(q.answers.length, 4);
  const normalized = q.answers.map(
    a => a.normalize('NFC').trim().toLocaleLowerCase('de')
  );
  assert.equal(new Set(normalized).size, 4, 'Doppelte Option: ' + q.id);
  assert.equal(q.answers.filter(a => a === q.correct).length, 1);
  assert.ok(!/Was ist gemeint|zu dieser Zeitreise/i.test(q.question));
  assert.ok(/^https:\/\//.test(q.source));
  assert.ok(q.factId);
}

for (const factId of new Set(questions.map(q => q.factId))) {
  const variants = questions.filter(q => q.factId === factId);
  assert.equal(variants.length, 3);
  assert.equal(new Set(variants.map(q => q.difficulty)).size, 3);
  assert.equal(new Set(variants.map(q => q.category)).size, 1);
  assert.equal(new Set(variants.map(q => q.decade)).size, 1);
}

const before = JSON.stringify(questions);
let seed = 123456789;
const random = () => {
  seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
  return seed / 4294967296;
};

for (const decade of ['70er', '80er', 'beide']) {
  for (let mask = 1; mask < (1 << categories.length); mask++) {
    const chosen = categories.filter((_, i) => mask & (1 << i));

    for (const difficulty of ['alle', 'leicht', 'mittel', 'schwer']) {
      const options = {decade, categories: chosen, difficulty};
      const pool = R.filter(questions, options);

      for (const q of pool) {
        assert.ok(decade === 'beide' || q.decade === decade);
        assert.ok(chosen.includes(q.category));
        assert.ok(difficulty === 'alle' || q.difficulty === difficulty);
      }

      for (const count of [10, 20, 30, 40]) {
        for (let repeat = 0; repeat < 10; repeat++) {
          const round = R.select(pool, count, random);
          assert.equal(round.length, Math.min(count, R.count(pool)));
          assert.equal(new Set(round.map(q => q.factId)).size, round.length);
          assert.ok(round.every(q => pool.includes(q)));
          checks++;
        }
      }
    }
  }
}

assert.deepEqual(R.select([], 20), []);
assert.deepEqual(
  R.filter(questions, {decade: 'beide', categories: [], difficulty: 'alle'}),
  []
);
assert.equal(R.select(questions, 0).length, 0);
assert.equal(JSON.stringify(questions), before, 'Auswahl verändert Daten');

for (const index of [42, 65, 69]) {
  const factId = questions[index * 3].factId;
  const variants = questions.filter(q => q.factId === factId);
  assert.equal(R.select(variants, 40, random).length, 1);
}

console.log(
  `OK: ${questions.length} Varianten, ${R.count(questions)} Sachverhalte, ` +
  `${checks} geprüfte Auswahlrunden ohne doppelte factId.`
);
"""


def fail(message):
    raise SystemExit(message)


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        fail(
            f"Patch abgebrochen: Erwartete Stelle für {label!r} "
            "nicht eindeutig gefunden. Keine geänderte Website veröffentlicht."
        )
    return text.replace(old, new, 1)


def repair_known_encoding(text):
    # Nur bekannte fehlerhaft doppelt interpretierte Zeichen korrigieren.
    replacements = {
        "â†’": "→",
        "â€¦": "…",
        "â€“": "–",
        "â€”": "—",
        "â€ž": "„",
        "â€œ": "“",
        "â€™": "’",
        "Ã¶": "ö",
        "Ã¼": "ü",
        "Ã¤": "ä",
        "Ã–": "Ö",
        "Ãœ": "Ü",
        "Ã„": "Ä",
        "ÃŸ": "ß",
        "Â·": "·",
        "Â ": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def parse_data():
    result = {}
    for line_number, line in enumerate(DATA.strip().splitlines(), 1):
        fields = [part.strip() for part in line.split("|")]
        if len(fields) != 7:
            fail(f"Ungültige redaktionelle Daten in Zeile {line_number}")
        index = int(fields[0])
        if index in result:
            fail(f"Doppelter Sachverhaltsindex: {index}")
        result[index] = fields[1:]

    if set(result) != set(range(80)):
        fail("Die redaktionellen Daten müssen alle 80 Sachverhalte abdecken.")
    return result


def year_choices(year):
    year = int(year)
    decade_start = (year // 10) * 10
    candidates = [
        n for n in range(decade_start, decade_start + 10)
        if n != year
    ]
    # Nahegelegene Jahreszahlen, ohne Duplikate oder Jahrzehntwechsel.
    candidates.sort(key=lambda n: (abs(n - year), n))
    return [str(year)] + [str(n) for n in candidates[:3]]


def main():
    needed = [
        "questions.js", "app.js", "index.html",
        "pwa.js", "sw.js", "cache-version.js"
    ]
    if not all((SITE / name).is_file() for name in needed):
        fail(
            "_site/ ist unvollständig. Diesen Schritt nach "
            "„Website vorbereiten“ einfügen."
        )

    app = (SITE / "app.js").read_text(encoding="utf-8")
    if "QUALITY-3-4-5" in app:
        fail("Qualitätsupdate ist bereits enthalten. Keine erneute Anwendung.")

    source = (SITE / "questions.js").read_text(encoding="utf-8")
    marker = "window.QUIZ_QUESTIONS"
    if marker not in source:
        fail("Fragenvariable nicht gefunden.")
    payload = source.split(marker, 1)[1].split("=", 1)[1].lstrip()
    original, _ = json.JSONDecoder().raw_decode(payload)

    if len(original) != 240:
        fail("Dieser Patch erwartet das Original mit 240 Fragevarianten.")

    editorial = parse_data()
    updated = []

    for index in range(80):
        base, dated, extra = original[index * 3:index * 3 + 3]
        if (
            base["difficulty"] != "leicht"
            or dated["difficulty"] != "mittel"
            or extra["difficulty"] != "schwer"
            or len({q["category"] for q in [base, dated, extra]}) != 1
            or len({q["decade"] for q in [base, dated, extra]}) != 1
        ):
            fail(f"Unerwartete Originalstruktur bei Sachverhalt {index}")

        (
            direct_question,
            year_question,
            direct_wrong,
            extra_question,
            extra_correct,
            extra_wrong,
        ) = editorial[index]

        direct_wrong = EASY_OVERRIDES.get(index, direct_wrong.split("~"))
        extra_wrong = extra_wrong.split("~")
        if len(direct_wrong) != 3 or len(extra_wrong) != 3:
            fail(f"Drei falsche Alternativen erwartet: Sachverhalt {index}")

        fact_id = f"fact-{base['id']:03d}"
        year = YEAR_OVERRIDES.get(index, dated["correct"])
        explanation = EXPLANATION_OVERRIDES.get(index, base["explanation"])
        source_url = SOURCES.get(index, base["source"])

        definitions = [
            (
                base,
                direct_question,
                base["correct"],
                [base["correct"]] + direct_wrong,
                explanation,
            ),
            (
                dated,
                year_question,
                year,
                year_choices(year),
                f"Das gesuchte Jahr ist {year}. {explanation}",
            ),
            (
                extra,
                extra_question,
                extra_correct,
                [extra_correct] + extra_wrong,
                f"{extra_correct}. {explanation}",
            ),
        ]

        for old, question, correct, answers, detail in definitions:
            q = dict(old)
            q.update({
                "factId": fact_id,
                "question": question,
                "correct": correct,
                "answers": answers,
                "explanation": detail,
                "source": source_url,
            })
            updated.append(q)

    # Prüfung vor dem Schreiben der Website.
    subprocess.run(
        ["node", "-e", "const window = {};\n" + ROUND_CORE + "\n" + TEST_JS],
        input=json.dumps(updated, ensure_ascii=False),
        text=True,
        check=True,
    )

    app = replace_once(
        app,
        "const pool=getPool(); $('#availableNote').textContent="
        "`${pool.length} passende Fragen verfügbar`;",
        """const pool=getPool();
    const unique=window.QuizRounds.count(pool);
    const actual=Math.min(state.count,unique);
    $('#availableNote').textContent=unique===0
      ? 'Keine passenden Fragen für diese Auswahl.'
      : `${unique} unterschiedliche Sachverhalte verfügbar (${pool.length} Fragevarianten).`
        + (actual<state.count
          ? ` Die Runde wird auf ${actual} Fragen verkürzt – ohne Wiederholungen.`
          : ` Deine Runde enthält ${actual} Fragen ohne Wiederholungen.`);""",
        "Verfügbarkeitsanzeige",
    )

    app = replace_once(
        app,
        "function getPool(){return Q.filter(q=>"
        "(state.decade==='beide'||q.decade===state.decade)&&"
        "state.categories.includes(q.category)&&"
        "(state.difficulty==='alle'||q.difficulty===state.difficulty))}",
        "function getPool(){return window.QuizRounds.filter(Q,state)}",
        "Filter",
    )

    app = replace_once(
        app,
        "state.round=shuffle(pool).slice(0,Math.min(state.count,pool.length));",
        """state.round=window.QuizRounds.select(pool,state.count);
    if(state.round.length<state.count){
      toast(`Runde auf ${state.round.length} unterschiedliche Fragen verkürzt`);
    }""",
        "Rundenauswahl",
    )

    app = app.replace(
        "${Q.length} eigenständige Fragen · keine Anmeldung · Daten bleiben im Browser",
        "${window.QuizRounds.count(Q)} Sachverhalte · ${Q.length} Fragevarianten"
        " · keine Anmeldung · Daten bleiben im Browser",
    )
    app = ROUND_CORE + "\n" + repair_known_encoding(app)

    html = repair_known_encoding(
        (SITE / "index.html").read_text(encoding="utf-8")
    )
    html = html.replace(
        "Zwei Jahrzehnte. 240 Fragen.",
        "80 Sachverhalte. 240 Fragevarianten.",
    )
    html = html.replace(
        "240 eigenständig formulierte Fragen",
        "240 Fragevarianten zu 80 Sachverhalten",
    )
    html = html.replace(
        "240 eigenständige Fragen",
        "240 Fragevarianten zu 80 Sachverhalten",
    )

    pwa = repair_known_encoding(
        (SITE / "pwa.js").read_text(encoding="utf-8")
    )
    pwa = replace_once(
        pwa,
        "function setStatus(text) { status.textContent = text; }",
        "function setStatus(text) { "
        "status.textContent = text + ' · Qualitätsupdate Q3–5'; }",
        "sichtbare Update-Kennung",
    )

    manifest_path = SITE / "manifest.webmanifest"
    manifest_text = None
    if manifest_path.is_file():
        manifest = json.loads(
            repair_known_encoding(manifest_path.read_text(encoding="utf-8"))
        )
        manifest["description"] = (
            "Das Quiz mit 80 Sachverhalten und 240 Fragevarianten "
            "aus den 70ern und 80ern."
        )
        manifest_text = json.dumps(
            manifest, ensure_ascii=False, indent=2
        ) + "\n"

    output = {
        "questions.js": (
            "// Redaktionell überarbeitet: Issues #3, #4 und #5.\n"
            "window.QUIZ_QUESTIONS = "
            + json.dumps(updated, ensure_ascii=False, indent=2)
            + ";\n"
        ),
        "app.js": app,
        "index.html": html,
        "pwa.js": pwa,
    }
    if manifest_text is not None:
        output["manifest.webmanifest"] = manifest_text

    # Syntaxprüfung der JavaScript-Ausgaben vor dem Schreiben.
    for filename in ["questions.js", "app.js", "pwa.js"]:
        subprocess.run(
            ["node", "--check"],
            input=output[filename],
            text=True,
            check=True,
        )

    # Version aus dem zukünftigen Website-Inhalt berechnen.
    digest = hashlib.sha256()
    for path in sorted(SITE.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(SITE).as_posix()
        if relative in {"sw.js", "cache-version.js"}:
            continue
        content = (
            output[relative].encode("utf-8")
            if relative in output
            else path.read_bytes()
        )
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
    version = digest.hexdigest()[:16]

    sw = (SITE / "sw.js").read_text(encoding="utf-8")
    sw, replacements = re.subn(
        r"const VERSION = '[^']+';",
        f"const VERSION = '{version}';",
        sw,
        count=1,
    )
    if replacements != 1:
        fail("Cache-Version im Service Worker nicht gefunden.")

    output["sw.js"] = sw
    output["cache-version.js"] = (
        "window.ZEITREISE_CACHE = 'zeitreise-' + "
        "encodeURIComponent(new URL('./', document.baseURI).href)"
        f" + '-{version}';\n"
        f"window.ZEITREISE_RELEASE = '{RELEASE}';\n"
    )

    for filename in ["sw.js", "cache-version.js"]:
        subprocess.run(
            ["node", "--check"],
            input=output[filename],
            text=True,
            check=True,
        )

    for filename, text in output.items():
        (SITE / filename).write_text(text, encoding="utf-8")

    print(
        f"Qualitätsupdate angewendet: {len(updated)} Varianten, "
        f"80 Sachverhalte, Cache {version}."
    )


if __name__ == "__main__":
    main()