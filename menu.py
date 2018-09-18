import curses
import json
from curses import wrapper
import webbrowser
import ConfigParser
''' This script implements a simple viewer to browse the list of labelled and unlabelled papers from
eprint.

It shows wether the papers are labelled as mpc/non-mpc or unlablled but predicted to be mpc papers.
Also has functionality to display the paper abstracts and open the browser on the given e-print
entry. Additionally, this tool can be used to label or re-label the papers. The new labelling will
be written to the file of labelled papers. '''

def main(stdscr):
  ## Read path to unlabelled and labelled papers from config
  config = ConfigParser.RawConfigParser()
  config.read('config.cfg')
  unlabelled_path = config.get('Data', 'unlabelled')
  labelled_path = config.get('Data', 'labelled')
  # Load labelled and unlabelled records
  with open(unlabelled_path) as recordFile:
    records = json.load(recordFile)
  with open(labelled_path) as labelled_file:
    old_records = json.load(labelled_file)
  old_ids = [(p['year'], p['serial']) for p in old_records]
  all_records = [p for p in records if (int(p['year']), int(p['serial'])) not in old_ids] + old_records
  all_records.sort(key=lambda p : (p['year'], p['serial']))
  # Setup curses
  curses.start_color()
  curses.use_default_colors()
  curses.curs_set(False)
  # Start loop
  selectloop(stdscr, all_records[::-1], 0)

def selectloop(stdscr, records, focus):
  header = 'PAPERS'
  all_records = records
  offset = 0
  while True:
    stdscr.clear()
    stdscr.addstr(0, 0, padline(header), curses.A_UNDERLINE)
    stdscr.addstr(curses.LINES - 1, 0, padline("t/f = toggle mpc | ENTER/SPACE = display info | q = quit | 1 = all records | 2 = mpc records | 3 = non mpc records"), curses.A_STANDOUT)
    for index in range(offset, min(curses.LINES - 2 + offset, len(records))):
      record = records[index]
      title = record['title']
      eprint_id = ' - ' + str(record['year']) + '/' + str(record['serial'])
      if ('mpc' in record):
        if record['mpc']:
          prefix = '[+] '
        else:
          prefix = '[-] '
      else:
        if ('pred' in record and record['pred']):
          prefix = '[*] '
        else:
          prefix = '[?] '
      item = prefix + title + eprint_id
      if (focus == index - offset):
        stdscr.addstr(index + 1 - offset, 0, safeline(item), curses.A_STANDOUT)
      else:
        stdscr.addstr(index + 1 - offset, 0, safeline(item))
    stdscr.refresh()
    key = stdscr.getch()
    if key == ord('p') or key == curses.KEY_UP:
      if focus == 0:
        offset = max(0, offset - 1)
      else:
        focus -= 1
    if key == ord('n') or key == curses.KEY_DOWN:
      if focus == curses.LINES - 3:
        offset = min(len(records) - curses.LINES - 3, offset + 1)
      else:
        focus = min(len(records) - 1, focus + 1)
    if key == ord('\n') or key== ord(' '):
      displayloop(stdscr, records[focus + offset])
    if key == ord('q'):
      ## Read path to unlabelled and labelled papers from config
      config = ConfigParser.RawConfigParser()
      config.read('config.cfg')
      labelled_path =  config.get('Data', 'labelled')
      records = [r for r in all_records if 'mpc' in r]
      with open(labelled_path, 'w') as labelled_file:
        json.dump(records[::-1], labelled_file, separators=(',', ':'), indent=0)
      break
    if key == ord('1'):
      focus = 0
      offset = 0
      records = all_records
    if key == ord('2'):
      focus = 0
      offset = 0
      records = [r for r in all_records if 'mpc' in r and r['mpc']]
    if key == ord('3'):
      offset = 0
      focus = 0
      records = [r for r in all_records if 'mpc' in r and not r['mpc']]
    if key == ord('t'):
      record = records[focus + offset]
      record['mpc'] = True
    if key == ord('f'):
      record = records[focus + offset]
      record['mpc'] = False

def displayloop(stdscr, record):
  curses.init_pair(1, curses.COLOR_RED, -1)
  curses.init_pair(2, curses.COLOR_MAGENTA, -1)
  while True:
    stdscr.clear()
    stdscr.addstr(curses.LINES - 1, 0, padline("ENTER/SPACE/q = back to selection"), curses.A_STANDOUT)
    greet = str(record['year']) + '/' + str(record['serial']) + ' - ' + record['title']
    greet.upper()
    lin_num = 0
    stdscr.addstr(lin_num, 0, safeline("TITLE:"), curses.A_DIM)
    lin_num += 1
    stdscr.addstr(lin_num, 0, safeline(greet), curses.color_pair(1))    
    lin_num = lin_num + 2
    stdscr.addstr(lin_num,0, safeline('AUTHORS:'), curses.A_DIM)
    lin_num = lin_num + 1
    stdscr.addstr(lin_num,0, safeline(", ".join(record['authors'])), curses.color_pair(2))
    lin_num = lin_num + 2
    stdscr.addstr(lin_num,0, safeline('ABSTRACT:'), curses.A_DIM)
    lin_num = lin_num + 1
    for line in multiline(record['abstract']):
      if (lin_num > curses.LINES - 6):
        stdscr.addstr(lin_num, 0, "... ")
        lin_num = lin_num + 1
        break
      stdscr.addstr(lin_num, 0, line)
      lin_num = lin_num + 1
    lin_num = lin_num + 1
    stdscr.addstr(lin_num,0, safeline('KEYWORDS:'), curses.A_DIM)
    lin_num = lin_num + 1
    stdscr.addstr(lin_num,0, safeline(", ".join(record['kw'])))
    stdscr.refresh()
    key = stdscr.getch()
    if key == ord('i'):
      webbrowser.open_new_tab('https://eprint.iacr.org/' + str(record['year']) + '/' + str(record['serial']).rjust(3, '0'))
    if key == ord('\n') or key == ord('q') or key == ord(' '):
      break

def safeline(line):
  line = line[:min(curses.COLS - 1, len(line))]
  line = line
  return line.encode('utf-8')

def padline(line, padding=' '):
  line = safeline(line)
  line = line + (curses.COLS - len(line) - 1) * ' '
  line = line
  return line.encode('utf-8')

def multiline(line):
  natural_lines = line.split('\n')
  return fitlines(natural_lines)

def fitlines(natural_lines):
  lines = []
  length = min(curses.COLS - 1, 100)
  for line in natural_lines:
    lines = lines + [line[i: i + length].encode('utf-8') for i in range(0,len(line), length)]
  return lines

wrapper(main)

