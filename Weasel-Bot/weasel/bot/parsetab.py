
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = "\x8b\xac,\xed\xbb'7\xb0\xce\xd3D>SvY\xd5"
    
_lr_action_items = {'EXECSH':([0,],[3,]),'FILESTR':([10,],[13,]),'STRING':([2,3,6,],[10,11,12,]),'EXEC':([0,],[6,]),'PING':([0,],[5,]),'PUT':([0,],[2,]),'$end':([1,4,5,7,8,9,11,12,13,],[-3,-2,-8,-4,0,-1,-7,-6,-5,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'put':([0,],[9,]),'start':([0,],[8,]),'execsh':([0,],[1,]),'ping':([0,],[7,]),'exec':([0,],[4,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> start","S'",1,None,None,None),
  ('start -> put','start',1,'p_start','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',70),
  ('start -> exec','start',1,'p_start','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',71),
  ('start -> execsh','start',1,'p_start','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',72),
  ('start -> ping','start',1,'p_start','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',73),
  ('put -> PUT STRING FILESTR','put',3,'p_put','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',77),
  ('exec -> EXEC STRING','exec',2,'p_exec','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',81),
  ('execsh -> EXECSH STRING','execsh',2,'p_execsh','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',85),
  ('ping -> PING','ping',1,'p_ping','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',89),
  ('createuser -> CREATEUSER STRING STRING','createuser',3,'p_createuser','/usr/local/lib/python2.7/dist-packages/weasel-1.0-py2.7.egg/weasel/shared/parser.py',93),
]