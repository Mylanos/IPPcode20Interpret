##Implementační dokumentace k 1. úloze do IPP 2019/2020 

###Jméno a příjmení: Marek Žiška
###Login: xziska03

###Kontrola argumentov a XML objekt
Po spustení skriptu prebieha kontrola počtu a typu argumentov podporovaných v mojom riešení.
Následne si vytváram inštanciu objektu predstavujúci výstupný XML súbor a volám nad ňou metódu 
__initXML__ na inicializáciu XML súbora na základnú štruktúru. Na vytvorenie XML súbora používam 
objekt __DomDocument__, ktorý mi umožnil jednoduchú prácu s XML súborom. 

###DOM Document
Medzi metódy ktoré používam nad týmto objektom patria napríklad __createElement()__ - vytvára nový element v XML,
 __appendChild()__ - vytvorí synovský element XML pre nejaký ďalší element, __setAttribute__ - nastavuje atribúty daného elementu. 
Pár krát som potreboval použiť aj špeciálnu premennu __$nodeValue__, vďaka ktorej som bol schopný vložiť obsah 
do elementu.
```php
$this->xml=new DomDocument('1.0', 'UTF-8');
```
###Načítanie vstupu a syntaktická kontrola
Vytváram si nový objekt __Instruction__ predstavujúci inštrukciu, o ktorej si evidujem počet argumentov, poradie 
 inštrukcie a pole tvoriace časti inštrukcie s argumentami. Kontrola hlavičky prebieha pomocou funkcie __checkHeader()__ 
a následne načítavam vstup zo STDIN po riadkoch. Každý riadok posielamdo hlavnej metódy __parse()__. V ktorej
sa zo začiatku vysporadúvavam s prebytočnýmy bielymi miestami a komentármi. Následne riadok rozdelím na časti, podľa ktorých
rozhodujem o akú inštrukciu sa na riadku jedná. Pre každú inštrukciu volám metódu __checkArgCount()__ na kontrolu počtov argumentov, po 
ktorej kontrolujem prípadnú syntax premenných, symbolov alebo labelov. Syntax kontrolujem v metódach __correctSymbSyntax()__, 
correctVarSyntax() a correctLabelSyntax. Syntax kontrolujem pomocou regulárnych výrazov funkciou __preg_match()__.
```php
preg_match('/^(int|string|bool)$/', $inputLine, $outputArray);
```
###Generovanie inštrukcií
Inštrukciu a argumenty generujem pomocou metódy __appendInstruction__, kde znova využívam __createElement()__. V tejto metóde 
volám ďalšiu metódu __appendArgument()__. Ktorá mi vytvorí element s príslušnými atribútmi a obsahom. Po vytvorené elementu argumentu
ho vložím ako synovský element inštrukcie. Takto pokračujem až pokým nenačítam koniec súbora.