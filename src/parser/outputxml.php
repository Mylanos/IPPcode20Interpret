<?php
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
?>