<?php
setlocale(LC_ALL, 'cs_CZ.UTF-8');

#######FUNCTIONS#########

//enum for better readability
abstract class Arguments
{
    const Help = 0;
    const Directory = 1;
    const Recursive = 2;
    const ParseScript = 3;
    const ParseOnly = 4;
    const IntScript = 5;
    const IntOnly = 6;
    const Jexamxml = 7;
}

function get_argument($argString, &$scan_dir, &$file_parse, &$file_int, &$file_jexamxml){
    if($argString == "--help"){
        $argument = Arguments::Help;
    }
    else if($argString == "--recursive"){
        $argument = Arguments::Recursive;
    }
    else if($argString == "--parse-only"){
        $argument = Arguments::ParseOnly;
    }
    else if($argString == "--int-only"){
        $argument = Arguments::IntOnly;
    }
    else if(preg_match('/^(--directory=.*)$/', $argString, $output_arg)){
        $scan_dir = substr($argString, strlen("--directory="));
        if(!(is_dir($scan_dir))){
            fwrite(STDERR, "Entered directory is not valid!");
            exit(11);
        }
        if(substr($scan_dir, -1) == "/"){
            $scan_dir = substr($scan_dir, 0, -1);
            echo $scan_dir;
        }
        $argument = Arguments::Directory;
    }
    else if(preg_match('/^(--parse-script=.*)$/', $argString, $output_arg)){
        $file_parse = substr($argString, strlen("--parse-script="));
        if(!(is_file($file_parse))){
            fwrite(STDERR, "Entered file is not valid!");
            exit(11);
        }
        $argument = Arguments::ParseScript;
    }
    else if(preg_match('/^(--int-script=.*)$/', $argString, $output_arg)){
        $file_int = substr($argString, strlen("--int-script="));
        if(!(is_file($file_int))){
            fwrite(STDERR, "Entered file is not valid!");
            exit(11);
        }
        $argument = Arguments::IntScript;
    }
    else if(preg_match('/^(--jexamxml=.*)$/', $argString, $output_arg)){
        $file_jexamxml = substr($argString, strlen("--jexamxml="));
        if(!(is_file($file_jexaml))){
            fwrite(STDERR, "Entered file is not valid!");
            exit(11);
        }
        $argument = Arguments::Jexamxml;
    }
    else{
        fwrite(STDERR, "Error 10: Unknown argument!\n");
        exit(10);
    }
    return $argument;
}

//checks if string contains given suffix
function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }
    return (substr($haystack, -$length) === $needle);
}

function search_subdir($location, &$files, $recursively){
    $curr_dir = scandir($location);
    foreach ($curr_dir as &$curr_item){
        //if its directory and recursively is true search continues
        if(is_dir($location."/".$curr_item)){
            //ignore . and .. dirs
            if(!($curr_item == "." || $curr_item == "..")){
                if($recursively){
                    $new_location = $location."/".$curr_item;
                    search_subdir($new_location, $files, $recursively);
                }
            }
        }
        else{
            // if its src file append it
            if(endsWith($curr_item, ".src")){
                array_push($files, $location."/".$curr_item);
            }
        }
    }
}

//replaces suffix with given suffix
function replace_suffix($src_file, $suffix){
    $new_file = substr($src_file, 0, -4);
    $new_file = $new_file.$suffix;
    return $new_file;
}

function compare_script_outputs($src_files, $file_int, $file_parse, $arguments, $file_jexamxml, $file_options){
    $index = 1;
    $rc_correct = false;
    $parse_ret_value = 1;
    $passed_count = 0;
    $fail_count = 0;
    $rate = 0;
    //loop over all src files
    foreach ($src_files as &$file){
        //flag if src file is not XML
        $not_XML_flag = intval(shell_exec("file -b ".$file." | grep XML >/dev/null ; echo $?"));
        $in_file_format = shell_exec("file -b ".$file);
        echo "<tr><td style=\"background-color: cornflowerblue\">" . $index ."</td>".PHP_EOL.
             "</td><td style=\"background-color:darkgrey;\">".$file."</td>";
        $out_file = replace_suffix($file, ".out");
        $in_file = replace_suffix($file, ".in");
        $rc_file = replace_suffix($file, ".rc");
        $tmp_file = replace_suffix($file, ".tmp");
        $tmp_file2 = replace_suffix($file, ".tmp2");
        $diff_file = replace_suffix($file, ".diff");
        if(!(is_file($in_file))){
            shell_exec("touch ". $in_file);
        }
        if(!(is_file($out_file))){
            shell_exec("touch ". $out_file);
        }
        if (!(is_file($rc_file))){
            shell_exec("echo '0' > ". $rc_file);
        }
        //if --int-only nor --parse-only given try to parse src file with parse.php, use interpret straight away
        //if its not XML
        if(!(in_array(Arguments::IntOnly, $arguments)) && !(in_array(Arguments::ParseOnly, $arguments))){
            if($not_XML_flag){
                $parse_ret_value = intval(shell_exec("php ". $file_parse ." < ".$file." > ". $tmp_file .
                                                 " 2>/dev/null ; echo $?"));
            }
            else{
                $parse_ret_value = 0;
            }
            if($parse_ret_value == 0){
                if($not_XML_flag){
                     $ret_value = intval(shell_exec("pythonš ". $file_int ." --source=".$tmp_file." --input=".$in_file." > ".
                                       $tmp_file2 ." 2>/dev/null; echo $?"));
                }
                else{
                    $ret_value = intval(shell_exec("python3 ". $file_int ." --source=".$file." --input=".$in_file." > ".
                                       $tmp_file2 ." 2>/dev/null; echo $?"));
                }
                shell_exec("cat ". $tmp_file2." > ".$tmp_file."");
                shell_exec("rm ".$tmp_file2);
                $diff_output = intval(shell_exec("diff ". $out_file." ".$tmp_file." ; echo $?"));
                $out_file_format = trim(shell_exec("file -b ".$tmp_file));
            }
            else{
                $ret_value = $parse_ret_value;
                //error parser
            }
        }
        //--int-only use intepreter straight away
        else if(in_array(Arguments::IntOnly, $arguments)){
            $ret_value = intval(shell_exec("python3 ". $file_int ." --source=".$file." --input=".$in_file." > ".
                                       $tmp_file ." 2>/dev/null; echo $?"));
            $diff_output = intval(shell_exec("diff ". $out_file." ".$tmp_file." ; echo $?"));
            $out_file_format = trim(shell_exec("file -b ".$tmp_file));
        }
        //--parse-only use jexamxml for output comparison
        else{
            $ret_value = intval(shell_exec("php ". $file_parse ." < ".$file." > ". $tmp_file .
                                                 " 2>/dev/null; echo $?"));
            $out_file_format = trim(shell_exec("file -b ".$tmp_file));
            $expected_format = trim(shell_exec("file -b ".$tmp_file));
            if($out_file_format != "empty" && $expected_format != "empty"){
                $diff_output = intval(shell_exec("java -jar ". $file_jexamxml ." ".
                                                 $out_file." ".$tmp_file." ". $diff_file .
                                                 " ". $file_options ." >/dev/null ; echo $?"));
            }
            else{
                $diff_output = 0;
            }
        }
        $ref_ret_value = intval(shell_exec("cat ".$rc_file));
        //if correct value check outputs
        if($ret_value == $ref_ret_value){
            $rc_correct = true;
            echo "<td style=\"background-color: green;\">OK</td>" .PHP_EOL.
                 "<td style=\"background-color: green;\"> (". $ret_value . ")----------(". $ref_ret_value ."
                  )</td>".PHP_EOL;
            if($diff_output == 0){
                if ($not_XML_flag == 0){
                    echo"<td style=\"background-color: green;\">XML</td>" . PHP_EOL;
                    echo"<td style=\"background-color: green;\">OK</td>" . PHP_EOL;
                }
                else{
                    echo"<td style=\"background-color: green;\">".$in_file_format."</td>" . PHP_EOL;
                    echo"<td style=\"background-color: green;\">".$out_file_format."</td>" . PHP_EOL;
                }
                echo "<td style=\"background-color: green;\">OK</td>" . PHP_EOL;
            }
            else{
                echo"<td style=\"background-color: green;\">".$in_file_format."</td>" . PHP_EOL;
                echo"<td style=\"background-color: red;\">".$out_file_format."</td>" . PHP_EOL;
                echo"<td style=\"background-color: red;\">BAD (". $diff_output .")</td>" . PHP_EOL;
            }
            if($diff_output == 0 and $rc_correct){
                $passed_count += 1;
                echo"<td style=\"background-color: green;\">PASS</td></tr>" . PHP_EOL;
            }
            else{
                $fail_count += 1;
                echo"<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
            }
        }
        //error wrong RC
        else{
            $fail_count += 1;
            echo "<td style=\"background-color: red;\">BAD</td>".PHP_EOL.
                 "<td style=\"background-color: red;\">".
                 "got-(". $ret_value . ")----------(". $ref_ret_value .")".
                 "</td>".PHP_EOL;
            if ($not_XML_flag == 0){
                echo"<td style=\"background-color: red;\">XML</td>" . PHP_EOL;
            }
            else{
                echo"<td style=\"background-color: red;\">".$in_file_format."</td>" . PHP_EOL;
            }
            echo "<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL.
                 "<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL.
                 "<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
        }

        if(is_file($diff_file)){
            shell_exec("rm ". $diff_file);
        }

        //remove tmp files
        shell_exec("rm ". $tmp_file);
        $index = $index + 1;
    }
    $test_count = $index - 1;
    //cal success rate
    if($test_count != 0){
        $percento = $test_count / 100;
        $rate = $passed_count / $percento;
        $rate = round($rate);
    }
    //end table
    echo "</table> " . PHP_EOL .
         "<div style=\"font-size: 20px;\">" . PHP_EOL .
         "<h3> TOTAL TESTS: ". $test_count ."</h3>" . PHP_EOL .
         "<h3>      PASSED: ".$passed_count."</h3>" . PHP_EOL .
         "<h3>        FAIL: ".$fail_count."</h3>" . PHP_EOL .
         "<h2>SUCCESS RATE: ".$rate."%</h2>" . PHP_EOL .
         "</div>" . PHP_EOL .
         "</div>" . PHP_EOL .
         "</section>" . PHP_EOL .
         "</body>" . PHP_EOL .
         "</html>";
}

#######FUNCTIONS#########

$src_files = array();
$arguments = array();
#$file_jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
#$file_options = "/pub/courses/ipp/jexamxml/options";
#$file_int = "interpret.py";
#$file_parse = "parser.php";
$file_options = "/Users/marekziska/Desktop/IPP/projekt/jexamxml/options";
$file_jexamxml = "/Users/marekziska/Desktop/IPP/projekt/jexamxml/jexamxml.jar";
$file_int = "interpreter/interpret.py";
$file_parse = "parser/parser.php";
if($argc == 1){
    exit(1);
}
else{
    $i = 1;
    //parses all arguments
    while($i < $argc){
        array_push($arguments, get_argument($argv[$i], $location_dir, $file_parse, $file_int, $file_jexamxml));
        $i++;
    }
    //print hints
    if(in_array(Arguments::Help, $arguments)){
        if(count($arguments) == 1){
            echo "SUPPORTED ARGUMENTS
                   --directory=path testybudehledatvzadanemadresari(chybi-litentoparametr,takskript"."
                   prochazi aktualni adresar; v pripade zadani neexistujiciho adresare dojde k chybe 11);".PHP_EOL."
                   --recursive testy bude hledat nejen v zadanem adresari, ale i rekurzivne ve vsech jeho"."
                   podadresarich;".PHP_EOL."
                   --parse-script=file soubor se skriptem v PHP 7.4 pro analyzu zdrojoveho kodu v IPP- code20 (chybi"."
                   -li tento parametr, tak implicitni hodnotou je parse.php ulozeny v aktualnim adresari);".PHP_EOL."
                   --int-script=file soubor se skriptem v Python 3.8 pro interpret XML reprezentace kodu v IPPcode20"."
                   (chybi-li tento parametr, tak implicitni hodnotou je interpret.py ulozeny v ak- tualnim"."
                   adresari);".PHP_EOL."
                   --parse-only bude testovan pouze skript pro analyzu zdrojoveho kodu v IPPcode20 (tento parametr "."
                   se nesmi kombinovat s parametry --int-only a --int-script), vystup s referencnim vystupem (soubor"."
                   s priponou out) porovnavejte nastrojem A7Soft JExamXML (viz [2]);".PHP_EOL."
                   --int-only bude testovan pouze skript pro interpret XML reprezentace kodu v IPPcode20 (tento"."
                   parametr se nesmi kombinovat s parametry --parse-only a --parse-script). Vstupni program reprezen"."
                   tovan pomoci XML bude v souboru s priponou src.".PHP_EOL."
                   --jexamxml=file soubor s JAR balickem s nastrojem A7Soft JExamXML. Je-li parametr vynechan uvazuje"."
                   se implicitni umisteni /pub/courses/ipp/jexamxml/jexamxml.jar na ser- veru Merlin, kde bude"."
                   test.php hodnocen.".PHP_EOL;
            exit(0);
        }
        else{
            fwrite(STDERR, "Argument --help cant be combined with other arguments!" . PHP_EOL);
            exit(10);
        }
    }
    if(!(in_array(Arguments::Directory, $arguments))){
        $location_dir = getcwd();
    }
    if(in_array(Arguments::Recursive, $arguments)){
            //search subdirs recursively
            search_subdir($location_dir, $src_files, True);
            sort($src_files);
    }
    else{
            //search subdir
            search_subdir($location_dir, $src_files, False);
            sort($src_files);
    }
    if((in_array(Arguments::ParseOnly, $arguments) && in_array(Arguments::IntScript, $arguments)) ||
       (in_array(Arguments::ParseOnly, $arguments) && in_array(Arguments::IntOnly, $arguments)) ||
       (in_array(Arguments::ParseScript, $arguments) && in_array(Arguments::IntOnly, $arguments))){
            fwrite(STDERR, "Restricted combination of arguments!" . PHP_EOL);
            exit(10);
    }

    echo "<!DOCTYPE html>" . PHP_EOL .
         "<html lang=\"en\">" . PHP_EOL .
         "<head>" . PHP_EOL .
         "<meta charset=\"utf-8\"/>" . PHP_EOL .
         "<title> IPP - principy programovacich jazykov</title>" . PHP_EOL .
         "</head>" . PHP_EOL .
         "<body style=\"text-align: center\">" . PHP_EOL .
         "<section class=\"container\">" . PHP_EOL .
         "<h2>TESTY K INTERPRETU Z PREDMETU IPP</h2>" . PHP_EOL .
         "<div>" . PHP_EOL .
         "<table style=\"text-align: center; margin: auto;\">" . PHP_EOL .
         "<tr style=\"background-color: dodgerblue;\">". PHP_EOL .
         "<td style=\"width: 80px\">order</td>". PHP_EOL .
         "<td style=\"width: 250px;\">filename</td>". PHP_EOL .
         "<td style=\"width: 300px\">.rc status</td>". PHP_EOL .
         "<td style=\"width: 300px\">rc - received vs expected</td>". PHP_EOL .
         "<td style=\"width:300px\">.src content</td>". PHP_EOL .
         "<td style=\"width:300px\">.out content</td>". PHP_EOL .
         "<td style=\"width:300px\">.out status</td>". PHP_EOL .
         "<td style=\"width:120px\">RESULT</td></tr>" . PHP_EOL;

    compare_script_outputs($src_files, $file_int, $file_parse, $arguments, $file_jexamxml, $file_options);
    exit(0);
}

?>
