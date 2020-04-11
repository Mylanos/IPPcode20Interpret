PHP=php
PYTHON=python3
LINKS=-lm
CFLAGS=-std=c11 -Wall -Wextra -pedantic -g
TEST_PARSER_DIC=tests/parse-only/int
TEST_INT_DIC=tests/interpret-only/arithmetic
TEST_INT_BOTH=tests/both
TEST_INT_STACK=tests/interpret-advanced/stack_tests
PARSER=parser/parser.php
TESTER=tester/test.php
INTERPRET=interpreter/interpret.py
PARSER_OUTPUT=test_output/testparser.html
INT_OUTPUT=test_output/testint.html
BOTH_OUTPUT=test_output/testboth.html
STACK_OUTPUT=test_output/teststack.html


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


.PHONY: clean
clean:
	rm -f $(INT_OUTPUT) $(PARSER_OUTPUT) $(BOTH_OUTPUT) 
