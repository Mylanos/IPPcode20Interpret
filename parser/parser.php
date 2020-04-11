<?php 

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

//************************classes****************************//

class OutputXML{
    public $xml;
    public $root;
    public $insElement;
    public $argElement;

    public function initXML(){
        $this->xml=new DomDocument('1.0', 'UTF-8');
        $this->xml->formatOutput=true;
        $this->root = $this->xml->createElement("program");
        $this->root->setAttribute("language", "IPPcode20");
        $this->root = $this->xml->appendChild($this->root);
    }

    public function appendInstruction($partitions, &$insCount, $argCount, $argTypes, $symbParts){
        $symbCount = 0;
        $this->insElement = $this->xml->createElement("instruction");
        for($i = 1; $i < $argCount; $i++){
            if(!(is_null($symbParts))){
                $this->appendArgument($i, $argTypes[$i-1], $partitions[$i], $symbParts[$symbCount], $symbCount);
            }
            else{
                $this->appendArgumentNull($i, $argTypes[$i-1], $partitions[$i], $symbCount);
            }
        }
        $this->insElement->setAttribute("order", $insCount);
        $this->insElement->setAttribute("opcode", $partitions[0]);
        $this->insElement = $this->root->appendChild($this->insElement);
        $insCount++;
    }

    public function appendArgument($argCount, $argType, $argument, $symbParts, &$symbCount){
        $this->argElement = $this->xml->createElement("arg".$argCount);
        switch($argType){
            case "var":
                $this->argElement->setAttribute("type", "var");
                $this->argElement->nodeValue = $argument;
            break;
            case "symb":
                $symbCount++;
                    if(in_array($symbParts[0],["int", "string", "nil", "bool"])){
                        $this->argElement->setAttribute("type", $symbParts[0]);
                        if(count($symbParts) == 1){
                            $this->argElement->nodeValue = "";
                        }
                        else{
                            $this->argElement->nodeValue = $symbParts[1];
                        }
                    }
                    else{
                        $this->argElement->setAttribute("type", "var");
                        if(count($symbParts) == 1){
                            $this->argElement->nodeValue = "";
                        }
                        else{
                            $this->argElement->nodeValue = $symbParts[0]."@".$symbParts[1];
                        }
                    }

            break;
            case "label":
                $this->argElement->setAttribute("type", "label");
                $this->argElement->nodeValue = $argument;
            break;
            case "type":
                $this->argElement->setAttribute("type", "type");
                $this->argElement->nodeValue = $argument;
            break;
            default:
                echo $argument;
                fwrite(STDERR, "unknown argument type!\n");
                exit(23);
        }
        $this->argElement = $this->insElement->appendChild($this->argElement);
    }

    public function appendArgumentNull($argCount, $argType, $argument, &$symbCount){
        $this->argElement = $this->xml->createElement("arg".$argCount);
        switch($argType){
            case "var":
                $this->argElement->setAttribute("type", "var");
                $this->argElement->nodeValue = $argument;
            break;
            case "symb":
                $symbCount++;
                $this->argElement->setAttribute("type", "var");
                $this->argElement->nodeValue = $argument;
            break;
            case "label":
                $this->argElement->setAttribute("type", "label");
                $this->argElement->nodeValue = $argument;
            break;
            case "type":
                $this->argElement->setAttribute("type", "type");
                $this->argElement->nodeValue = $argument;
            break;
            default:
                echo $argument;
                fwrite(STDERR, "unknown argument type!\n");
                exit(23);
        }
        $this->argElement = $this->insElement->appendChild($this->argElement);
    }

    public function printXML(){
        echo $this->xml->saveXML();
    }
}

class Instruction{

    public $partitions;
    public $argCount;
    public $insCount;

    public function __construct(){
        $this->insCount = 1;
    }

    public function checkHeader($Instruct, $header){
        $Instruct->checkComment($header);
        $header = trim($header);
        if($header != ".IPPcode20"){
            exit(21);
        }
    }

    public function checkArgCount($expectedCount){
        if($this->argCount == $expectedCount){
            return;
        }
        else{
            fwrite(STDERR, "WRONG AMMOUNT OF ARGUMENTS\n");
            exit(23);
        }
    }

    public function correctVarSyntax($inputLine){
        $inputLine = trim($inputLine);
        preg_match('/^([LF,GF,TF].@.[a-z,A-Z,0-9,\_,\-,\$,\&,\%,\*,\!,\?]*)$/', $inputLine, $outputArray);
        if(empty($outputArray)){
            fwrite(STDERR, "Wrong variable syntax!\n");
            exit(23);
        }
    }

    public function correctSymbSyntax($inputLine, &$symbParts){
        $inputLine = trim($inputLine);
        preg_match('/^(int|bool|string|nil)@.*/', $inputLine, $outputArray);
        if(empty($outputArray)){
            $symbParts = explode("@", $inputLine);
            preg_match('/^([LF,GF,TF].@.[a-z,A-Z,0-9,\_,\-,\$,\&,\%,\*,\!,\?]*)$/', $inputLine, $outputArray2);
            if(empty($outputArray2)){
                fwrite(STDERR, "Wrong symbol syntax!\n");
                exit(23);
            }
        }
        else{
            $symbParts = explode("@", $inputLine);
            switch($symbParts[0]){
                case "string":
                    preg_match('/^string@(\\[0-9]{3}|[^\\#])*$/', $inputLine, $outputArray3);
                    if(empty($outputArray3)){
                        fwrite(STDERR, "Wrong symbol syntax!\n");
                        exit(23);
                    }
                break;
                case "int":
                    preg_match('/^int@([^\\#])*$/', $inputLine, $outputArray3);
                    if($symbParts[1] == NULL){
                        fwrite(STDERR, "Empty int!\n");
                        exit(23);
                    }
                     
                    if(empty($outputArray3)){
                        fwrite(STDERR, "Wrong symbol syntax!\n");
                        exit(23);
                    }
                break;
                case "bool":
                    preg_match('/^bool@(true|false)$/', $inputLine, $outputArray3);
                    if(empty($symbParts[1])){
                        fwrite(STDERR, "Empty bool!\n");
                        exit(23);
                    }
                    if(empty($outputArray3)){
                        fwrite(STDERR, "Wrong symbol syntax!\n");
                        exit(23);
                    }
                break;
                case "nil":
                    preg_match('/^nil@nil$/', $inputLine, $outputArray3);
                    if(empty($symbParts[1])){
                        fwrite(STDERR, "Empty nil!\n");
                        exit(23);
                    }
                    if(empty($outputArray3)){
                        fwrite(STDERR, "Wrong symbol syntax!\n");
                        exit(23);
                    }
                break;
                default:
                    fwrite(STDERR, "Unknown datatype!\n");
                    exit(23);
            }
        }
    }

    public function correctLabelSyntax($inputLine){
        preg_match('/^([a-z,A-Z,0-9,\_,\-,\$,\&,\%,\*,\!,\?]*)$/', $inputLine, $outputArray);
        if(empty($outputArray)){
            fwrite(STDERR, "Wrong label syntax!\n");
            exit(23);
        }
    }

    public function correctType($inputLine){
        preg_match('/^(int|string|bool)$/', $inputLine, $outputArray);
        if(empty($outputArray)){
            fwrite(STDERR, "Wrong type syntax!\n");
            exit(23);
        }
    }

    public function parse(&$line, &$Output){
        $argTypes = ["buzna"];
        $symbParts = array(array());
        $this->checkComment($line);
        if(ctype_space($line)){
            return;
        }
        $line = trim($line);
        $this->partitions = explode(" ", $line);
        $this->argCount = count($this->partitions);
        $this->partitions[0] = strtoupper($this->partitions[0]);
        switch ($this->partitions[0]){
            case "MOVE":
            case "NOT":
                $this->checkArgCount(3);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $argTypes = ['var', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "CREATEFRAME":
                $this->checkArgCount(1);
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, NULL);
            break;
            case "PUSHFRAME":
                $this->checkArgCount(1);
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, NULL);
            break;
            case "POPFRAME":
                $this->checkArgCount(1);
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, NULL);
            break;
            case "DEFVAR":
                $this->checkArgCount(2);
                $this->correctVarSyntax($this->partitions[1]);
                $argTypes = ['var'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, NULL);
            break;
            case "CALL":
                $this->checkArgCount(2);
                $this->correctLabelSyntax($this->partitions[1]);
                $argTypes = ['label'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, NULL);
            break;
            case "RETURN":
                $this->checkArgCount(1);
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "PUSHS":
                $this->checkArgCount(2);
                $this->correctSymbSyntax($this->partitions[1], $symbParts[0]);
                $argTypes = ['symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "POPS":
                $this->checkArgCount(2);
                $this->correctVarSyntax($this->partitions[1]);
                $argTypes = ['var'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "ADD":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "SUB":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "MUL":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "IDIV":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "LT":
            case "GT":
            case "EQ":
            case "AND":
            case "OR":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "INT2CHAR":
                $this->checkArgCount(3);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $argTypes = ['var', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "STRI2INT":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "READ":
                $this->checkArgCount(3);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctType($this->partitions[2]);
                $argTypes = ['var', 'type'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, NULL);
            break;
            case "WRITE":
                $this->checkArgCount(2);
                $this->correctSymbSyntax($this->partitions[1], $symbParts[0]);
                $argTypes = ['symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "CONCAT":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "STRLEN":
                $this->checkArgCount(3);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $argTypes = ['var', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "GETCHAR":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "SETCHAR":
                $this->checkArgCount(4);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['var', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "TYPE":
                $this->checkArgCount(3);
                $this->correctVarSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $argTypes = ['var', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "LABEL":
                $this->checkArgCount(2);
                $this->correctLabelSyntax($this->partitions[1]);
                $argTypes = ['label'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "JUMP":
                $this->checkArgCount(2);
                $this->correctLabelSyntax($this->partitions[1]);
                $argTypes = ['label'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                $this->checkArgCount(4);
                $this->correctLabelSyntax($this->partitions[1]);
                $this->correctSymbSyntax($this->partitions[2], $symbParts[0]);
                $this->correctSymbSyntax($this->partitions[3], $symbParts[1]);
                $argTypes = ['label', 'symb', 'symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "EXIT":
                $this->checkArgCount(2);
                $this->correctSymbSyntax($this->partitions[1], $symbParts[0]);
                $argTypes = ['symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "DPRINT":
                $this->checkArgCount(2);
                $this->correctSymbSyntax($this->partitions[1], $symbParts[0]);
                $argTypes = ['symb'];
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            case "BREAK":
                $this->checkArgCount(1);
                $Output->appendInstruction($this->partitions, $this->insCount, $this->argCount, $argTypes, $symbParts);
            break;
            default:
                if ((trim($this->partitions[0])) == "") {
                    break;
                }
                fwrite(STDERR, "Unknown instruction!".$this->partitions[0]."\n");
                exit(22);
        }
   }

   public function checkComment(&$line){
        if(($charsToNeedle = strpos($line, '#')) !== false){
            $line = substr($line, 0, strpos($line, "#"));
            $line = trim($line);
            $line = $line."\n";
        }
   }
}
?>
