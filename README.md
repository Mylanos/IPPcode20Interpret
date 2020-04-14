# Zadání projektu z předmětu IPP 2019/

# 1 Základní charakteristika projektu

Navrhněte, implementujte, dokumentujte a testujte sadu skriptů pro interpretaci nestrukturovaného
imperativního jazyka IPPcode20. K implementaci vytvořte odpovídající stručnou programovou do-
kumentaci. Projekt se skládá ze dvou úloh a je individuální.
První úloha se skládá ze skriptuparse.php v jazyce PHP 7.4 (viz sekce 3 ) a dokumentace
k tomuto skriptu (viz sekce2.1). Druhá úloha se skládá ze skriptuinterpret.pyv jazyce Python
3.8 (viz sekce 4 ), testovacího skriptutest.phpv jazyce PHP 7.4 (viz sekce 5 ) a dokumentace těchto
dvou skriptů (viz sekce2.1).


## 2 Programová část

Zadání projektu vyžaduje implementaci tří skriptů, které mají parametry příkazové řádky a je defi-
nováno, jakým způsobem manipulují se vstupy a výstupy. Skript (vyjmatest.php) nesmí spouštět
žádné další procesy či příkazy operačního systému. Veškerá chybová hlášení, varování a ladicí výpisy
směřujte pouze na standardní chybový výstup, jinak pravděpodobně nedodržíte zadání kvůli mo-
difikaci definovaných výstupů (ať již do externích souborů nebo do standardního výstupu). Jestliže
proběhne činnost skriptu bez chyb, vrací se návratová hodnota 0 (nula). Jestliže došlo k nějaké chybě,
vrací se chybová návratová hodnota větší jak nula. Chyby mají závazné chybové návratové hodnoty:


# 3 Popis jazyka IPPcode

Nestrukturovaný imperativní jazyk IPPcode20 vznikl úpravou jazyka IFJcode19 (jazyk pro mezikód
překladače jazyka IFJ19, viz [ 3 ]), který zahrnuje instrukce tříadresné (typicky se třemi argumenty)
a případně zásobníkové (typicky méně parametrů a pracující s hodnotami na datovém zásobníku).
Každá instrukce se skládá z operačního kódu (klíčové slovo s názvem instrukce), u kterého nezáleží
na velikosti písmen (tj. case insensitive). Zbytek instrukcí tvoří operandy, u kterých na velikosti
písmen záleží (tzv. case sensitive). Operandy oddělujeme libovolným nenulovým počtem mezer či
tabulátorů. Také před operačním kódem a za posledním operandem se může vyskytnout libovolný
počet mezer či tabulátorů. Odřádkování slouží pro oddělení jednotlivých instrukcí, takže na každém
řádku je maximálně jedna instrukce a není povoleno jednu instrukci zapisovat na více řádků. Každý
operand je tvořen proměnnou, konstantou, typem nebo návěštím. V IPPcode20 jsou podporovány
jednořádkové komentáře začínající mřížkou (#). Kód v jazyce IPPcode20 začíná úvodním řádkem^14
s tečkou následovanou jménem jazyka (nezáleží na velikosti písmen):

```
.IPPcode
```

## 4 Paměťový model

Hodnoty během interpretace nejčastěji ukládáme do pojmenovaných proměnných, které jsou sdružo-
vány do tzv. rámců, což jsou v podstatě slovníky proměnných s jejich hodnotami. IPPcode20 nabízí
tři druhy rámců:

- globální, značímeGF(Global Frame), který je na začátku interpretace automaticky inicializován
    jako prázdný; slouží pro ukládání globálních proměnných;
- lokální, značímeLF(Local Frame), který je na začátku nedefinován a odkazuje na vrcholový/ak-
    tuální rámec na zásobníku rámců; slouží pro ukládání lokálních proměnných funkcí (zásobník
    rámců lze s výhodou využít při zanořeném či rekurzivním volání funkcí);
- dočasný, značímeTF(Temporary Frame), který slouží pro chystání nového nebo úklid starého
    rámce (např. při volání nebo dokončování funkce), jenž může být přesunut na zásobník rámců
    a stát se aktuálním lokálním rámcem. Na začátku interpretace je dočasný rámec nedefinovaný.
K překrytým (dříve vloženým) lokálním rámcům v zásobníku rámců nelze přistoupit dříve, než
vyjmeme později přidané rámce.
Další možností pro ukládání nepojmenovaných hodnot je datový zásobník využívaný zásobníko-
vými instrukcemi.

## 5 Datové typy

IPPcode20 pracuje s typy operandů dynamicky, takže je typ proměnné (resp. paměťového místa) dán
obsaženou hodnotou. Není-li řečeno jinak, jsou implicitní konverze zakázány. Interpret podporuje
speciální hodnotu/typ nil a tři základní datové typy (int, bool a string), jejichž rozsahy i přesnosti
jsou kompatibilní s jazykem Python 3.
Zápis každé konstanty v IPPcode20 se skládá ze dvou částí oddělených zavináčem (znak@; bez
bílých znaků), označení typu konstanty (int, bool, string, nil) a samotné konstanty (číslo, literál, nil).
Např.bool@true,nil@nilneboint@-5.
Typ int reprezentuje celé číslo (přetečení/podtečení neřešte). Typ bool reprezentuje pravdivostní
hodnotu (falsenebotrue). Literál pro typ string je v případě konstanty zapsán jako sekvence
tisknutelných znaků v kódování UTF-8 (vyjma bílých znaků, mřížky (#) a zpětného lomítka (\))
a escape sekvencí, takže není ohraničen uvozovkami. Escape sekvence, která je nezbytná pro znaky
s dekadickým kódem 000-032, 035 a 092, je tvaru\xyz, kdexyzje dekadické číslo v rozmezí 000-
složené právě ze tří číslic^15 ; např. konstanta

(^15) Zápis znaků s kódem Unicode větším jak 126 pomocí těchto escape sekvencí nebudeme testovat.


```
string@řetězec\ 032 s\ 032 lomítkem\ 032 \ 092 \ 032 a\ 010 novým\ 035 řádkem
```
reprezentuje řetězec

```
řetězec s lomítkem \ a
novým#řádkem
```

## 6.4 Instrukční sada

U popisu instrukcí sázíme operační kód tučně a operandy zapisujeme pomocí neterminálních symbolů
(případně číslovaných) v úhlových závorkách. Neterminál⟨ _var_ ⟩značí proměnnou,⟨ _symb_ ⟩konstantu
nebo proměnnou,⟨ _label_ ⟩značí návěští. Identifikátor proměnné se skládá ze dvou částí oddělených
zavináčem (znak@; bez bílých znaků), označení rámceLF,TFneboGFa samotného jména proměnné
(sekvence libovolných alfanumerických a speciálních znaků bez bílých znaků začínající písmenem nebo
speciálním znakem, kde speciální znaky jsou:_,-,$,&,%,*,!,?). Např.GF@_xznačí proměnnou_x
uloženou v globálním rámci.
Na zápis návěští se vztahují stejná pravidla jako na jméno proměnné (tj. část identifikátoru za
zavináčem).

```
Příklad jednoduchého programu v IPPcode20:
```
```
.IPPcode
DEFVAR GF@counter
MOVE GF@counter string@ #Inicializace proměnné na prázdný řetězec
#Jednoduchá iterace, dokud nebude splněna zadaná podmínka
LABEL while
JUMPIFEQ end GF@counter string@aaa
WRITE string@Proměnná\032GF@counter\032obsahuje\
WRITE GF@counter
WRITE string@\
CONCAT GF@counter GF@counter string@a
JUMP while
LABEL end
```

Instrukční sada nabízí instrukce pro práci s proměnnými v rámcích, různé skoky, operace s da-
tovým zásobníkem, aritmetické, logické a relační operace, dále také konverzní, vstupně/výstupní a
ladicí instrukce.
