#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import sys
from subprocess import check_output
from subprocess import call


def prefix_style(text):
  return '\x1b[38;2;100;100;100m%s\x1b[0m' % text


def session_style(name):
  return '\x1b[33m%s\x1b[0m' % name


def window_style(name):
  return '\x1b[35m%s\x1b[0m' % name


class Tmux(object):

  """The tmux object"""

  def __init__(self):
    self.tmux_client = check_output(
      ['tmux', 'list-clients', '-F', '#{client_tty}'],
      universal_newlines=True,
    ).strip()

    # get session list
    sessions = check_output(
      ['tmux', 'list-session', '-F', '#{session_name}'],
      universal_newlines=True,
    )
    sessions = sessions.splitlines()
    self.tree = {}

    # get window list for each session
    for s in sessions:
      windows = sessions = check_output(
        [
          'tmux',
          'list-windows',
          '-t',
          s,
          '-F',
          '#{window_name}',
        ],
        universal_newlines=True,
      )
      windows = windows.splitlines()
      self.tree[s] = windows

    # fzf_lines & cooresponding tmux switch commands
    self.tmux_commands = []
    lines = []
    count = -1

    for session, windows in self.tree.items():
      count += 1
      self.tmux_commands.append(
        [
          'tmux',
          'switch-client',
          '-c',
          self.tmux_client,
          '-t',
          session,
        ])
      lines.append('{} {}'.format(session_style(session), count))

      index = 0
      for window in windows:
        index += 1
        count += 1
        self.tmux_commands.append(
          [
            'tmux',
            'switch-client',
            '-c',
            self.tmux_client,
            '-t',
            '{}:{}'.format(session, window),
          ])
        if len(windows) == index:
          lines.append(
            '{} {} {}'.format(prefix_style('└─'), window_style(window), count),
          )
        else:
          lines.append(
            '{} {} {}'.format(prefix_style('├─'), window_style(window), count),
          )

    self.fzf_lines = '\n'.join(lines)


tmux = Tmux()
try:
  ret_line = check_output(
    [
      # 'fzf-tmux',
      # '-u30%',
      'fzf',
      '--height=50%',
      '--min-height=15',
      # '--header-lines=2',
      '--ansi',
      '--no-border',
      '--margin=1',
      '--with-nth=..-2',
      # '--nth=1',
      # '--color=bg:-1,bg+:-1',
      '--query={}'.format(sys.argv[1] if len(sys.argv) > 1 else ''),
      '--select-1',
    ],
    input=tmux.fzf_lines,
    universal_newlines=True,
  )
except subprocess.CalledProcessError as e:
  if e.returncode != 130:  # user canceled in fzf
    raise
except:
  raise
else:
  index = int(re.search('\d+$', ret_line).group(0))
  call(tmux.tmux_commands[index])
finally:
  pass
