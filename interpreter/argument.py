import re


class Arguments:
    def __init__(self, args):
        self.args = args
        self.check_arg_count()

        self.sourceFile = None
        self.inputFile = None
        self.passedArgs = []
        self.parse_args()

    def parse_args(self):
        for argument in self.args:
            source_arg = re.match("^(--source=(([A-Z]|[a-z]|/|_|[0-9]|.)+))$", argument)
            input_arg = re.match("^(--input=(([A-Z]|[a-z]|/|_|[0-9]|.)+))$", argument)
            help_arg = re.match("^--help$", argument)
            if source_arg:
                self.sourceFile = source_arg.group(2)
                print(self.sourceFile)
                self.passedArgs.append("source")
            elif input_arg:
                self.inputFile = input_arg.group(2)
                print(self.inputFile)
                self.passedArgs.append("input")
            elif help_arg:
                print("napoveda")
                self.passedArgs.append("help")
            else:
                raise Exception("napixu argument format")

    def check_arg_count(self):
        if len(self.args) > 3:
            raise ValueError("Napixu argcount")

    def get_source_file(self):
        return self.sourceFile

    def get_input_file(self):
        return self.inputFile



