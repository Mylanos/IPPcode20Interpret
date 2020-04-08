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

function interpret_test($src_files, $file_int){
    $index = 1;
    $rc_correct = false;
    foreach ($src_files as &$file){
        echo "<tr><td style=\"background-color: cornflowerblue\">" . $index ."</td>";
        echo "</td><td style=\"background-color:darkgrey;\">".$file."</td>";
        $out_file = replace_suffix($file, ".out");
        $in_file = replace_suffix($file, ".in");
        $rc_file = replace_suffix($file, ".rc");
        $tmp_file = replace_suffix($file, ".tmp");
        $diff_file = replace_suffix($file, ".diff");
        $ret_value = intval(shell_exec("python3.8 ". $file_int ." --source=".$file." --input=". $in_file ." >". $tmp_file ." 2>/dev/null; echo $?"));
        $ref_ret_value = intval(shell_exec("cat ".$rc_file));
        if(!(is_file($in_file))){
            shell_exec("touch ". $in_file);
        }
        else if(!(is_file($out_file))){
            shell_exec("touch ". $out_file);
        }
        else if (!(is_file($rc_file))){
            shell_exec("echo '0' > ". $rc_file);
        }
        if($ret_value == 0){
            if($ret_value == $ref_ret_value){
                $rc_correct = true;
                echo "<td style=\"background-color: green;\">OK</td>";
                echo "<td style=\"background-color: green;\"> (". $ret_value . ")----------(". $ref_ret_value .")</td>";
                $diff_output = intval(shell_exec("diff ". $out_file." ".$tmp_file." ; echo $?"));
                if($diff_output == 0){
                    echo"<td style=\"background-color: green;\">OK</td>" . PHP_EOL;
                }
                else{
                    echo"<td style=\"background-color: red;\">BAD (". $diff_output .")</td>" . PHP_EOL;
                }
                if($diff_output == 0 and $rc_correct){
                    echo"<td style=\"background-color: green;\">PASS</td></tr>" . PHP_EOL;
                }
                else{
                    echo"<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
                }
            }
            else{
                echo "<td style=\"background-color: red;\">BAD</td>";
                echo "<td style=\"background-color: red;\"> got-(". $ret_value . ")  expected-(". $ref_ret_value .")</td>";
                echo"<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL;
                echo"<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
            }
        }
        else{
            if($ret_value == $ref_ret_value){
                echo "<td style=\"background-color: green;\">OK</td>";
                echo "<td style=\"background-color: green;\"> (". $ret_value . ")----------(". $ref_ret_value .")</td>";
                echo"<td style=\"background-color: green;\">OK</td>" . PHP_EOL;
                echo"<td style=\"background-color: green;\">PASS</td></tr>" . PHP_EOL;
            }
            else{
                echo "<td style=\"background-color: red;\">BAD</td>";
                echo "<td style=\"background-color: red;\"> got-(". $ret_value . ")  expected-(". $ref_ret_value .")</td>";
                echo"<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL;
                echo"<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
            }
        }
        shell_exec("rm ". $tmp_file);
        $index = $index + 1;
    }
}

function parser_test($src_files, $file_parse, $file_jexamxml, $file_options){
    $index = 1;
    $rc_correct = false;
    foreach ($src_files as &$file){
        echo "<tr><td style=\"background-color: cornflowerblue\">" . $index ."</td>";
        echo "</td><td style=\"background-color:darkgrey;\">".$file."</td>";
        $out_file = replace_suffix($file, ".out");
        $in_file = replace_suffix($file, ".in");
        $rc_file = replace_suffix($file, ".rc");
        $tmp_file = replace_suffix($file, ".tmp");
        $diff_file = replace_suffix($file, ".diff");
        $ret_value = intval(shell_exec("php7.4 ". $file_parse ." <".$file." >". $tmp_file ." 2>/dev/null; echo $?"));
        $ref_ret_value = intval(shell_exec("cat ".$rc_file));
        if(!(is_file($in_file))){
            shell_exec("touch ". $in_file);
        }
        else if(!(is_file($out_file))){
            shell_exec("touch ". $out_file);
        }
        else if (!(is_file($rc_file))){
            shell_exec("echo '0' > ". $rc_file);
        }
        if($ret_value == 0){
            if($ret_value == $ref_ret_value){
                $rc_correct = true;
                echo "<td style=\"background-color: green;\">OK</td>";
                echo "<td style=\"background-color: green;\"> (". $ret_value . ")----------(". $ref_ret_value .")</td>";
                $diff_output = intval(shell_exec("java -jar ". $file_jexamxml ." ".
                                                 $out_file." ".$tmp_file." ". $diff_file .
                                                 " ". $file_options ." >/dev/null ; echo $?"));
                if($diff_output == 0){
                    echo"<td style=\"background-color: green;\">OK</td>" . PHP_EOL;
                }
                else{
                    echo"<td style=\"background-color: red;\">BAD (". $diff_output .")</td>" . PHP_EOL;
                }
                if($diff_output == 0 and $rc_correct){
                    echo"<td style=\"background-color: green;\">PASS</td></tr>" . PHP_EOL;
                }
                else{
                    echo"<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
                }
            }
            else{
                echo "<td style=\"background-color: red;\">BAD</td>";
                echo "<td style=\"background-color: red;\"> got-(". $ret_value . ")  expected-(". $ref_ret_value .")</td>";
                echo"<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL;
                echo"<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
            }
        }
        else{
            if($ret_value == $ref_ret_value){
                echo "<td style=\"background-color: green;\">OK</td>";
                echo "<td style=\"background-color: green;\"> (". $ret_value . ")----------(". $ref_ret_value .")</td>";
                echo"<td style=\"background-color: green;\">OK</td>" . PHP_EOL;
                echo"<td style=\"background-color: green;\">PASS</td></tr>" . PHP_EOL;
            }
            else{
                echo "<td style=\"background-color: red;\">BAD</td>";
                echo "<td style=\"background-color: red;\"> got-(". $ret_value . ")  expected-(". $ref_ret_value .")</td>";
                echo"<td style=\"background-color: orange;\">BAD RC</td>" . PHP_EOL;
                echo"<td style=\"background-color: red;\">FAIL</td></tr>" . PHP_EOL;
            }
        }
        shell_exec("rm ". $tmp_file);
        $index = $index + 1;
    }
}

#######FUNCTIONS#########

$files = array();
$curr_argument = array();
$file_jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
$file_options = "/pub/courses/ipp/jexamxml/options";
#$file_options = "/Users/marekziska/Desktop/IPP/projekt/jexamxml/options";
#$file_jexamxml = "/Users/marekziska/Desktop/IPP/projekt/jexamxml/jexamxml.jar";
$file_int = "interpret.py";
$file_parse = "parse.php";
if($argc == 1){
    exit(1);
}
else{
    $i = 1;
    while($i < $argc){
        array_push($curr_argument, get_argument($argv[$i], $location_dir, $file_parse, $file_int, $file_jexamxml));
        $i++;
    }
    if(in_array(Arguments::Help, $curr_argument)){
        if(count($curr_argument) == 1){
            echo "napoveda";
            exit(0);
        }
        else{
            fwrite(STDERR, "Argument --help cant be combined with other arguments!" . PHP_EOL);
            exit(10);
        }
    }
    if(!(in_array(Arguments::Directory, $curr_argument))){
            $location_dir = getcwd();
    }
    if(in_array(Arguments::Recursive, $curr_argument)){
            search_subdir($location_dir, $files, True);
            $src_files = get_src_files($files);
    }
    else{
            search_subdir($location_dir, $files, False);
            $src_files = get_src_files($files);
    }
    if(in_array(Arguments::ParseOnly, $curr_argument) || in_array(Arguments::ParseScript, $curr_argument)){
        if(in_array(Arguments::IntOnly, $curr_argument) || in_array(Arguments::IntScript, $curr_argument)){
            fwrite(STDERR, "Restricted combination of arguments!" . PHP_EOL);
            exit(10);
        }
        else{
            search_subdir($location_dir, $files, False);
            $src_files = get_src_files($files);
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
             "<table style=\"align: center; margin: auto;\">" . PHP_EOL .
             "<tr style=\"background-color: dodgerblue;\"><td style=\"width: 80px\">order</td><td style=\"width: 250px;\">file".
             "name</td><td style=\"width: 300px\">.rc status</td><td style=\"width: 300px\">rc - received vs expected</td><td style=\"width:".
             "300px\">.out status</td><td style=\"width:120px\">RESULT</td></tr>" . PHP_EOL;

        parser_test($src_files, $file_parse, $file_jexamxml, $file_options);
    }
    else if(in_array(Arguments::IntOnly, $curr_argument)|| in_array(Arguments::IntScript, $curr_argument)){
        if(in_array(Arguments::ParseOnly, $curr_argument) || in_array(Arguments::ParseScript, $curr_argument)){
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
             "<table style=\"align: center; margin: auto;\">" . PHP_EOL .
             "<tr style=\"background-color: dodgerblue;\"><td style=\"width: 80px\">order</td><td style=\"width: 250px;\">file".
             "name</td><td style=\"width: 300px\">.rc status</td><td style=\"width: 300px\">rc - received vs expected</td><td style=\"width:".
             "300px\">.out status</td><td style=\"width:120px\">RESULT</td></tr>" . PHP_EOL;

        interpret_test($src_files, $file_int);
    }
    else{
        fwrite(STDERR, "Wrong combination of arguments!" . PHP_EOL);
        exit(10);
    }
    echo "</table> " . PHP_EOL .
         "</div>" . PHP_EOL .
         "</section>" . PHP_EOL .
        "</body>" . PHP_EOL .
        "</html>";
    exit(1);
}

?>
