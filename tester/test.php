<?php
setlocale(LC_ALL, 'cs_CZ.UTF-8');

#######FUNCTIONS#########

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

function search_subdir($location, &$files, $recursively){
    $curr_dir = scandir($location);
    foreach ($curr_dir as &$curr_item){
        if(is_dir($location."/".$curr_item)){
            if(!($curr_item == "." || $curr_item == "..")){
                if($recursively){
                    $new_location = $location."/".$curr_item;
                    search_subdir($new_location, $files, $recursively);
                }
            }
        }
        else{
            array_push($files, $location."/".$curr_item);
        }
    }
}

function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }
    return (substr($haystack, -$length) === $needle);
}

function get_src_files($files){
    $src_files = array();
    foreach ($files as &$curr_item){
        if(endsWith($curr_item, ".src")){
            array_push($src_files, $curr_item);
        }
    }
    return $src_files;
}

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
    foreach ($src_files as &$file){
        $XML_flag = shell_exec("file -b ".$file." | grep XML >/dev/null ; echo $?");
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
        if(!(in_array(Arguments::IntOnly, $arguments)) && !(in_array(Arguments::ParseOnly, $arguments))){
            if($XML_flag != 0){
                $parse_ret_value = intval(shell_exec("php ". $file_parse ." < ".$file." > ". $tmp_file .
                                                 " 2>/dev/null; echo $?"));
            }
            else{
                $parse_ret_value = 0;
            }

            if($parse_ret_value == 0){
                $ret_value = intval(shell_exec("python3 ". $file_int ." --source=".$tmp_file." --input=".$in_file." > ".
                                       $tmp_file2 ." 2>/dev/null; echo $?"));
                $diff_output = intval(shell_exec("diff ". $out_file." ".$tmp_file2." ; echo $?"));
                 $out_file_format = shell_exec("file -b ".$tmp_file2);
            }
            else{
                $ret_value = $parse_ret_value;
                //error parser
            }
        }
        else if(in_array(Arguments::IntOnly, $arguments)){
            $ret_value = intval(shell_exec("python3 ". $file_int ." --source=".$file." --input=".$in_file." > ".
                                       $tmp_file ." 2>/dev/null; echo $?"));
            $diff_output = intval(shell_exec("diff ". $out_file." ".$tmp_file." ; echo $?"));
            $out_file_format = shell_exec("file -b ".$tmp_file);
        }
        else{
            $ret_value = intval(shell_exec("php ". $file_parse ." < ".$file." > ". $tmp_file .
                                                 " 2>/dev/null; echo $?"));
            $diff_output = intval(shell_exec("java -jar ". $file_jexamxml ." ".
                                                 $out_file." ".$tmp_file." ". $diff_file .
                                                 " ". $file_options ." >/dev/null ; echo $?"));
             $out_file_format = shell_exec("file -b ".$tmp_file);
        }
        $ref_ret_value = intval(shell_exec("cat ".$rc_file));
        if($ret_value == $ref_ret_value){
            $rc_correct = true;
            echo "<td style=\"background-color: green;\">OK</td>" .PHP_EOL.
                 "<td style=\"background-color: green;\"> (". $ret_value . ")----------(". $ref_ret_value .")</td>";
            if($diff_output == 0){
                if($out_file_format != "empty"){
                     echo"<td style=\"background-color: green;\">".$out_file_format."</td>" . PHP_EOL;
                }
                else{
                    echo"<td style=\"background-color: green;\">.</td>" . PHP_EOL;
                }
                echo"<td style=\"background-color: green;\">OK</td>" . PHP_EOL;
            }
            else{
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
        else{
            $fail_count += 1;
            echo "<td style=\"background-color: red;\">BAD</td>".PHP_EOL.
                 "<td style=\"background-color: red;\">".
                 "got-(". $ret_value . ")  expected-(". $ref_ret_value .")".
                 "</td>".PHP_EOL.
                 "<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL.
                 "<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL.
                 "<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
        }

        shell_exec("rm ". $tmp_file);
        if ($parse_ret_value == 0){
            shell_exec("rm ". $tmp_file2);
        }
        $index = $index + 1;
    }
    $test_count = $index - 1;
    if($fail_count != 0){
        $percento = $test_count / 100;
        $rate = $passed_count / $percento;
        $rate = round($rate);
    }
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

$files = array();
$arguments = array();
#$file_jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar"
#$file_options = "/pub/courses/ipp/jexamxml/options"
$file_options = "/Users/marekziska/Desktop/IPP/projekt/jexamxml/options";
$file_jexamxml = "/Users/marekziska/Desktop/IPP/projekt/jexamxml/jexamxml.jar";
$file_int = "../interpreter/interpret.py";
$file_parse = "../parser/parser.php";
if($argc == 1){
    exit(1);
}
else{
    $i = 1;
    while($i < $argc){
        array_push($arguments, get_argument($argv[$i], $location_dir, $file_parse, $file_int, $file_jexamxml));
        $i++;
    }
    if(in_array(Arguments::Help, $arguments)){
        if(count($arguments) == 1){
            echo "napoveda";
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
            search_subdir($location_dir, $files, True);
            $src_files = get_src_files($files, $arguments);
    }
    else{
            search_subdir($location_dir, $files, False);
            $src_files = get_src_files($files, $arguments);
    }
    if((in_array(Arguments::ParseOnly, $arguments) && in_array(Arguments::IntScript, $arguments)) ||
       (in_array(Arguments::ParseOnly, $arguments) && in_array(Arguments::IntOnly, $arguments)) ||
       (in_array(Arguments::ParseScript, $arguments) && in_array(Arguments::IntOnly, $arguments))){
            fwrite(STDERR, "Restricted combination of arguments!" . PHP_EOL);
            exit(10);
    }

    echo "<!DOCTYPE html5>" . PHP_EOL .
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
         "<td style=\"width:300px\">.out content</td>". PHP_EOL .
         "<td style=\"width:300px\">.out status</td>". PHP_EOL .
         "<td style=\"width:120px\">RESULT</td></tr>" . PHP_EOL;

    compare_script_outputs($src_files, $file_int, $file_parse, $arguments, $file_jexamxml, $file_options);
    exit(0);
}

?>
