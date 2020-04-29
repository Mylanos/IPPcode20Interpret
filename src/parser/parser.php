<?php 
include "outputxml.php";
include "instruction.php";

setlocale(LC_ALL, 'cs_CZ.UTF-8');

if($argc == 2){
    if(($argv[1] == "--help")){
        echo "NAPOVEDA\n";
        exit(0);
    }
    else{
        echo "WRONG ARGUMENT\n";
        exit(10);
    }
}
else if($argc > 2){
    echo "WRONG AMMOUNT OF ARGUMENTS\n";
    exit(1);
}

$headerNotFound = True;
$Output = new OutputXML();
$Output->initXML();
$Instruct = new Instruction();
$header = fgets(STDIN);
while($header == "\n"){
    echo "wtf\n";
    $header = fgets(STDIN);
}

$Instruct->checkHeader($Instruct, $header);
while(!feof(STDIN)){
    if($headerNotFound){

    }
    $line = fgets(STDIN);
    if ((trim($line)) != "") {
         $Instruct->parse($line, $Output);
    }
}
$Output->printXML();

?>