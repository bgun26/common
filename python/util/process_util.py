
import os
import logging
import re
import subprocess


class ProcessExecutor:
    """
    Class providing utility functions for executing a process,
    such as:
        logging,
        getting and/or checking the return code,
        storing and/or filtering the output.
    """

    def __init__(self, command, shell=True, cwd=None, logger=logging.debug):
        """
        Constructor initializing instance variables.
            command: is either a string or a list of strings
            shell:   boolean indicating if the command should be executed through the shell
            cwd:     if not None, the command is executed in the directory given by cwd
            logger:  logger object
        """
        self._command = ' '.join(command) if isinstance(command, list) else str(command)
        self._use_shell = shell
        self._cwd = cwd
        # if logger is given as None, use an empty function as logger
        self._logger = logger or (lambda *x: None)
        self._return_code = None
        self._output_log = None

    # Properties
    @property
    def command(self):
        """ The command executed by the instance """
        return self._command

    @property
    def is_shell_used(self):
        """
        Is the command executed through the shell, see subprocess.Popen
        """
        return self._use_shell

    @property
    def cwd(self):
        """ The directory where the command will be executed """
        return self._cwd

    @property
    def logger(self):
        """ The logger object used by the instance """
        return self._logger

    @property
    def return_code(self):
        """ Return code of the executed command, None if the command is not yet executed """
        return self._return_code

    @property
    def output_log(self):
        """
        Complete output of the executed command stored line by line as a list of strings.
        None if the command is not yet executed or the output is not stored
        """
        return self._output_log

    # Private methods
    def _gen_execute_process(self):
        """
        Returns a generator that produces the output of the executed command line by line.
        Stores the return code of the command in the instance variable.
        """
        self._logger("Executing process '%s'", self._command)
        p = subprocess.Popen(self._command, shell=self._use_shell, cwd=self._cwd,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            out_line = p.stdout.readline().rstrip().decode('utf-8')
            if p.poll() is not None and out_line == "":
                self._return_code = p.returncode
                break
            if out_line:
                self._logger(out_line)
                yield out_line

    # Public methods
    def execute(self, match_regex=None, regex_match_handler=None, store_output_log=False):
        """
        Executes the command, returns return value of the command.

        store_output_log:    if True, stores the output log in an instance variable.
        match_regex:         each line is searched with this pattern,
                             matches are passed to regex_match_handler as a match object.
                             if None, every line is a match and passed as a string
        regex_match_handler: callable which accepts one argument
        """
        match_handler = regex_match_handler or (lambda match: None)
        compiled_regex = re.compile(match_regex) if match_regex else None
        self._output_log = [] if store_output_log else None

        for output_line in self._gen_execute_process():
            if store_output_log:
                self._output_log.append(output_line)
            if compiled_regex:
                match = compiled_regex.match(output_line)
                if match:
                    match_handler(match)
            else:
                match_handler(output_line)

        return self._return_code

    def execute_check_return(self, expected_return_code=os.EX_OK,
                             match_regex=None, regex_match_handler=None,
                             store_output_log=False):
        """
        Convenience wrapper around execute method,
        returns True if the return code of the command is expected_return_code,
        returns False otherwise.

        For other options, see execute method
        """
        result = False
        return_code = self.execute(match_regex=match_regex,
                                   regex_match_handler=regex_match_handler,
                                   store_output_log=store_output_log)
        if return_code == expected_return_code:
            result = True
        return result


if __name__ == '__main__':

    def line_handler(line):
        logging.info("Processing output line: '%s' of type %s", line, type(line))

    def regex_handler(match):
        logging.info("Processing regex match: '%s' of type %s",
                     match.group(0), type(match))

    logging.basicConfig(level=logging.DEBUG)
    # initialization and execution are separated
    p = ProcessExecutor('seq 1 3')
    # same ProcessExecutor instance can be executed many times
    p.execute(regex_match_handler=line_handler)
    # with different output handling options
    p.execute(match_regex=r"^2", regex_match_handler=regex_handler)
    p.execute(store_output_log=True)
    logging.info("Stored output log: '%s'", p._output_log)

    HOST_NAME = 'google.com'
    p2 = ProcessExecutor(['ping', '-q', '-c', '1', HOST_NAME])
    # convenience wrapper
    if p2.execute_check_return():
        logging.info("%s is accessible", HOST_NAME)
    else:
        logging.info("%s is not accessible", HOST_NAME)
