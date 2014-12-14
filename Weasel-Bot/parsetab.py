
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = ' \x96\x06\xa7\x04\x9f:\xdeS\xb56\xfd\xcb\xba&n'
    
_lr_action_items = {'FILESTR':([8,],[10,]),'STRING':([1,4,],[8,9,]),'EXEC':([0,],[4,]),'PING':([0,],[3,]),'PUT':([0,],[1,]),'$end':([2,3,5,6,7,9,10,],[-2,-6,-3,0,-1,-5,-4,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'put':([0,],[7,]),'start':([0,],[6,]),'ping':([0,],[5,]),'exec':([0,],[2,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> start","S'",1,None,None,None),
  ('start -> put','start',1,'p_start','/home/dan/Dropbox/Weasel/Weasel-Bot/weasel/shared/parser.py',68),
  ('start -> exec','start',1,'p_start','/home/dan/Dropbox/Weasel/Weasel-Bot/weasel/shared/parser.py',69),
  ('start -> ping','start',1,'p_start','/home/dan/Dropbox/Weasel/Weasel-Bot/weasel/shared/parser.py',70),
  ('put -> PUT STRING FILESTR','put',3,'p_put','/home/dan/Dropbox/Weasel/Weasel-Bot/weasel/shared/parser.py',74),
  ('exec -> EXEC STRING','exec',2,'p_exec','/home/dan/Dropbox/Weasel/Weasel-Bot/weasel/shared/parser.py',78),
  ('ping -> PING','ping',1,'p_ping','/home/dan/Dropbox/Weasel/Weasel-Bot/weasel/shared/parser.py',82),
  ('createuser -> CREATEUSER STRING STRING','createuser',3,'p_createuser','/home/dan/Dropbox/Weasel/Weasel-Bot/weasel/shared/parser.py',86),
]
