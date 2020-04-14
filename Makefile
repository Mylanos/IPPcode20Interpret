PHP=php
PYTHON=python3
LINKS=-lm
CFLAGS=-std=c11 -Wall -Wextra -pedantic -g
TEST_PARSER_DIC=tests/parse-only
TEST_INT_DIC=tests/interpret-only
TEST_INT_BOTH=tests/both
TEST_INT_STACK=tests/interpret-advanced/stack_tests
TEST_INT_FLOAT=tests/interpret-advanced/float_tests
TEST_KOULE=tests/hardcore-koule/Lakoc/koule_Lakoc.xml
PARSER=parser/parser.php
TESTER=tester/test.php
INTERPRET=interpreter/interpret.py
PARSER_OUTPUT=test_output/testparser.html
INT_OUTPUT=test_output/testint.html
BOTH_OUTPUT=test_output/testboth.html
STACK_OUTPUT=test_output/teststack.html
FLOAT_OUTPUT=test_output/testfloat.html
STATS_FILE=stats/test.st

test_int_advanced: test_int_stack test_int_float

test_parser:
	$(PHP) $(TESTER) --parse-only --parse-script=$(PARSER) --recursive --directory=$(TEST_PARSER_DIC) > $(PARSER_OUTPUT) ;
	open $(PARSER_OUTPUT)

test_int:
	$(PHP) $(TESTER) --int-only --int-script=$(INTERPRET) --recursive --directory=$(TEST_INT_DIC) > $(INT_OUTPUT) ;
	open $(INT_OUTPUT)

test_both:
	$(PHP) $(TESTER) --recursive --parse-script=$(PARSER) --int-script=$(INTERPRET) --directory=$(TEST_INT_BOTH) > $(BOTH_OUTPUT) ;
	open $(BOTH_OUTPUT)

test_int_stack:
	$(PHP) $(TESTER) --recursive --int-only --int-script=$(INTERPRET) --directory=$(TEST_INT_STACK) > $(STACK_OUTPUT) ;
	open $(STACK_OUTPUT)

test_int_float:
	$(PHP) $(TESTER) --recursive --int-only --int-script=$(INTERPRET) --directory=$(TEST_INT_FLOAT) > $(FLOAT_OUTPUT) ;
	open $(FLOAT_OUTPUT)

test_koule:
	$(PYTHON) $(INTERPRET) --source=$(TEST_KOULE) --stats=$(STATS_FILE) --insts --vars

.PHONY: clean
clean:
	rm -f $(INT_OUTPUT) $(PARSER_OUTPUT) $(BOTH_OUTPUT) 
