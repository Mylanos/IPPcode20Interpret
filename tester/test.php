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

function get_argument($argString, &$scan_dir, &$file_parse, &$file_int, &$file_jexaml){
    if($argString == "--help"){
        echo "NAPOVEDA\n";
        $argument = Arguments::Help;
    }
    else if($argString == "--recursive"){
        echo "recursive\n";
        $argument = Arguments::Recursive;
    }
    else if($argString == "--parse-only"){
        echo "parse-only\n";
        $argument = Arguments::ParseOnly;
    }
    else if($argString == "--int-only"){
        echo "int-only\n";
        $argument = Arguments::IntOnly;
    }
    else if(preg_match('/^(--directory=.*)$/', $argString, $output_arg)){
        $scan_dir = substr($argString, strlen("--directory="));
        if(!(is_dir($scan_dir))){
            fwrite(STDERR, "Entered directory is not valid!");
            exit(11);
        }
        echo "directory specification\n";
        $argument = Arguments::Directory;
    }
    else if(preg_match('/^(--parse-script=.*)$/', $argString, $output_arg)){
        $file_parse = substr($argString, strlen("--parse-script="));
        if(!(is_file($file_parse))){
            fwrite(STDERR, "Entered file is not valid!");
            exit(11);
        }

        echo "parse-script\n";
        $argument = Arguments::ParseScript;
    }
    else if(preg_match('/^(--int-script=.*)$/', $argString, $output_arg)){
        $file_int = substr($argString, strlen("--int-script="));
        if(!(is_file($file_int))){
            fwrite(STDERR, "Entered file is not valid!");
            exit(11);
        }
        echo "int-script\n";
        $argument = Arguments::IntScript;
    }
    else if(preg_match('/^(--jexamxml=.*)$/', $argString, $output_arg)){
        $file_jexaml = substr($argString, strlen("--jexamxml="));
        if(!(is_file($file_jexaml))){
            fwrite(STDERR, "Entered file is not valid!");
            exit(11);
        }
        echo "jexamxml\n";
        $argument = Arguments::Jexamxml;
    }
    else{
        fwrite(STDERR, "Si dojebaaaauuuuuu 1. arg unknown!\n");
        exit(1);
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

function execute_files($src_files){
    foreach ($src_files as &$file){
        $out_file = replace_suffix($file, ".out");
        $in_file = replace_suffix($file, ".in");
        $rc_file = replace_suffix($file, ".rc");
        $ret_value = intval(shell_exec("php parser.php <".$file.">".$in_file." 2>/dev/null; echo $?"));
        $ref_ret_value = intval(shell_exec("cat ".$rc_file));
        $diff_file = replace_suffix($file, ".diff");
        if($ret_value != $ref_ret_value){
            echo "Return values in ".$file." are not matching!\n";
        }
        #$diff_output = intval(shell_exec("java -jar /Users/marekziska/Desktop/IPP/projekt/jexamxml/jexamxml.jar ".$in_file." ".$out_file." ".$diff_file." /Users/marekziska/Desktop/IPP/projekt/jexamxml/options >/dev/null; echo $?"));
        #echo $file." \t - \t ".$diff_output."\n";
    }
}

#######FUNCTIONS#########

$files = array();
$curr_argument = array();
if($argc == 1){
    exit(1);
}
else{
    $i = 1;
    while($i < $argc){
        array_push($curr_argument, get_argument($argv[$i], $location_dir, $file_parse, $file_int, $file_jexaml));
        $i++;
    }
    if($curr_argument[0] == Arguments::ParseOnly){
        if(in_array(Arguments::IntOnly, $curr_argument) || in_array(Arguments::IntScript, $curr_argument)){
            fwrite(STDERR, "Restricted combination of arguments!\n");
            exit(10);
        }
        if(!(in_array(Arguments::Directory, $curr_argument))){
            $location_dir = getcwd();
        }
        if(in_array(Arguments::Recursive, $curr_argument)){
            $recursively = True;
            search_subdir($location_dir, $files, True);
            $src_files = get_src_files($files);
        }
        else{
            search_subdir($location_dir, $files, False);
            $src_files = get_src_files($files);
        }
        execute_files($src_files);
        
    }
    exit(1);
}

?>
