##Implementační dokumentace k 2. úloze do IPP 2019/2020 

###Jméno a příjmení: Marek Žiška
###Login: xziska03

##Interpret
Pri implementácií interpretu som sa snažil o objektovo orientovaný prístup, z ktorého vyšli nasledovné moduly

###Hlavná trieda Interpret v __interpret.py__
Riadi hlavnú smyčku programu, zberá štatistiky pre rožšírenie STATI a vykonáva sémantické kontroly. pri implementácií 
som som využil dátové štruktúry ako zoznam:

* zoznam som používal pri implementácií stacku __value_stack__, ukladal som doňho triedy inštrukcií __Instruction__, 
v ktorom poradí sa program interpretoval, 
* používal som ho na uloženie indexov volaní funkcií, ktoré som využil v rekurzívnom zanorení funkcií 
(__call_index_stack__).
* na uloženie tried kontextov __Frame__ (__local_frame__)

a knižnica:

* použil som ju na uloženie indexov __LABEL__, kľúč predstavoval názov __LABEL__ a hodnota bol index.(__label_dict__)

###Trieda Arguments v __argument.py__
Kontroluje podporované argumenty pomocou regexov, ukladá prípadné zdrojové/vstupné súbory a ukladá argumenty do zoznamu.

###Trieda Parser v __parser.py__
Spracováva zdrojový XML súbor, ktorého formu kontroluje podľa zadania, konštruuje inštrukcie pomocou triedy
 __Instruction__. Pri implementácií som narazil na problémy so zoradením argumentov inštrukcí podľa poradia ktoré mohlo
 byť rozhádzané. Volá metódy triedy __Instruction__ pre kontrolu správnosti argumentov pre danú inštrukciu, prípadne pre
 inštrukcie.
 
###Trieda Instruction v __instruction.py__
Prevádza syntaktické kontroly argumentov a inštrukcií, ukladá si hondnoty a typy argumentov, prevádza escape sekvencie 
v reťazcoch.

###Trieda Stats v __stats.py__
Ukladá si počet vykonaných inštrukcií a maximálny počet definovaných premenných v čase behu programu v ktoromkoľvek
rámci. Tlačí štatistiky na stdin.

###Trieda Frame v __frame.py__
Ukladá premenné definované v danom rámci. Obsahuje metódy na definovanie a inicializovanie premennej.

###Trieda Error v __myerrors.py__
Je to hlavná trieda ktorá má dve metódy na výpis a vrátenie návratového kódu. Z tejto metódy dedia mnohé
ďalšie triedy predstavujúce špecifické chyby v zadaní. Používa sa na prehľadné nastavenie výnimiek v kóde.