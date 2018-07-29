
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

    def __init__(self, command, shell=True, cwd=None):
        """
        Constructor initializing instance variables.

        Args:
            command (str or List): is either a string or a list of strings,

        Keyword Args:
            shell (bool): indicating if the command should be executed through the shell.
                without the shell, environment variables like ~ and $EDITOR are not expanded,
                aliases are not effective etc.
            cwd (str): the command is executed in the directory given by cwd,
                if None, the command is executed in the current directory
            logger (Callable): logger object, use None to disable logging

        Attributes:
            All private attributes are wrapped by properties and documented there.

        Create an instance by specifying the execution options of the command.

        >>> p1 = ProcessExecutor(['ls', '-l', '~/Documents'])
        >>> p2 = ProcessExecutor('pwd', cwd='..')
        """
        self._command = ' '.join(command) if isinstance(command, list) else str(command)
        self._use_shell = shell
        self._cwd = cwd
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
    def _gen_execute_process(self, logger_obj=logging.debug):
        """
        Executes the command parameterized by the instance variables,
        stores the exit code into an instance variable.
        Logs the output line by line.

        Yields:
            A generator that produces the output line by line

        The process executing the command is run uninterrupted from start to finish.
        The generator instead of a function only makes a difference about how the
        output of the command is stored. Generator is more memory efficient than
        storing the entire output as a list.

        >>> for line in self._gen_execute_process():
        >>>     print("Processing line: '%s'" % line)
        """

        logger_obj("Executing process '%s'", self._command)
        p = subprocess.Popen(self._command, shell=self._use_shell, cwd=self._cwd,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             encoding='utf-8')
        while True:
            out_line = p.stdout.readline().rstrip()
            if p.poll() is not None and out_line == "":
                self._return_code = p.returncode
                break
            if out_line:
                logger_obj(out_line)
                yield out_line

    # Public methods
    def execute(self, logger=logging.debug, store_output=False,
                match_regex=None, regex_match_handler=None):
        """
        Executes the command, optionally stores the output log
        and/or redirects matching output lines to a handler.

        Keyword Args:
            logger (Callable): this callable is used to log the execution
            store_output (bool): if True, stores the output log in an instance variable
            match_regex (str): each line is searched with this regex pattern,
                matches are passed to regex_match_handler as a re.match object.
                if None, every line is a match and passed as a string
            regex_match_handler (Callable): callable object which accepts one argument

        Returns:
            The exit code of the executed process

        It is used after initializing a ProcessExecutor object.

        >>> p = ProcessExecutor('seq 1 3')
        >>> return_code = p.execute(store_output_log=True)
        >>> assert return_code == p.return_code
        >>> output_log = p.output_log
        """

        # if logger is given as None, an empty function is used as logger
        logger_obj = logger or (lambda *x: None)
        match_handler = regex_match_handler or (lambda match: None)
        compiled_regex = re.compile(match_regex) if match_regex else None
        self._output_log = [] if store_output else None

        for output_line in self._gen_execute_process(logger_obj=logger_obj):
            if store_output:
                self._output_log.append(output_line)
            if compiled_regex:
                match = compiled_regex.match(output_line)
                if match:
                    match_handler(match)
            else:
                match_handler(output_line)

        return self._return_code

    def execute_check_return(self, expected_return_code=os.EX_OK,
                             logger=logging.debug, store_output=False,
                             match_regex=None, regex_match_handler=None):
        """
        Convenience wrapper around ProcessExecutor.execute method.

        Keyword Args:
            expected_return_code (int): compared to the exit code of the executed command

        Returns:
            True if the return code of the command is expected_return_code
            False otherwise

        Can be used to quickly check a resource, connection etc.

        >>> HOST_NAME = 'google.com'
        >>> p = ProcessExecutor(['ping', '-q', '-c', '1', HOST_NAME])
        >>> if p.execute_check_return(): print("%s is accessible" % HOST_NAME)
        """
        result = False
        return_code = self.execute(logger=logger,
                                   store_output=store_output,
                                   match_regex=match_regex,
                                   regex_match_handler=regex_match_handler)
        if return_code == expected_return_code:
            result = True
        return result


if __name__ == '__main__':

    def line_handler(line):
        logging.info("Processing output line: '%s' of type %s", line, type(line))
        # import time
        # time.sleep(1)

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
    p.execute(store_output=True, logger=None)
    logging.info("Stored output: '%s'", p._output_log)

    HOST_NAME = 'google.com'
    p2 = ProcessExecutor(['ping', '-q', '-c', '1', HOST_NAME])
    # convenience wrapper
    if p2.execute_check_return():
        logging.info("%s is accessible", HOST_NAME)
    else:
        logging.info("%s is not accessible", HOST_NAME)
