# PATH to Python

# Replace xx with your Python Scripts folder
export PATH="$PATH:/c/Users/user/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.xx/LocalCache/local-packages/Python3xx/Scripts"

# Bash prompt
. ~/.bash_prompt

# Bash aliases
alias ..='cd ..'
alias ...='cd ../../'
alias ....='cd ../../../'
alias .....='cd ../../../../'
alias bashclear='echo "" > ~/.bash_history'
alias cls='clear'
alias ls='ls -F --color=auto --show-control-chars'
alias ll='ls -la'
alias lls='ls -la --sort=size'
alias llt='ls -la --sort=time'
alias projects='cd ~/Projects'
alias repos='cd ~/Projects/Repos'

# Python aliases
alias new_venv='python -m venv venv'
alias source_venv='source venv/Scripts/activate'
alias pip_req='pip install -r requirements.txt'
alias pip_no_ssl='python -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org'

# Bash shell settings
# Typing a directory name just by itself will automatically change into that directory.
shopt -s autocd

# Automatically fix directory name typos when changing directory.
shopt -s cdspell

# Automatically expand directory globs and fix directory name typos whilst completing. 
# Note, this works in conjuction with the cdspell option listed above.
shopt -s direxpand dirspell

# Enable the ** globstar recursive pattern in file and directory expansions.
# For example, ls **/*.txt will list all text files in the current directory hierarchy.
shopt -s globstar

# Ignore lines which begin with a <space> and match previous entries.
# Erase duplicate entries in history file.
HISTCONTROL=ignoreboth:erasedups

# Ignore saving short- and other listed commands to the history file.
HISTIGNORE=?:??:history

# The maximum number of lines in the history file.
HISTFILESIZE=99999

# The number of entries to save in the history file.
HISTSIZE=99999

# Save multi-line commands in one history entry.
shopt -s cmdhist

# Append commands to the history file, instead of overwriting it.
# History substitution are not immediately passed to the shell parser.
shopt -s histappend histverify
