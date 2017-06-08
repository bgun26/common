set nocp
syntax enable        " Set up syntax highlighting, etc
filetype indent on   " Set up automatic indentation
filetype plugin on   " Set up loading filetype plugins when certain files are edited

" 256-color terminal
set t_Co=256

" Activate undo folder
set undofile
set undodir=~/.vim/undodir

" code folding
" au BufWinLeave ?* mkview
" au BufWinEnter ?* silent loadview

set nu " line numbers
set relativenumber
set noignorecase " case sensitive search
set nohlsearch " don't highlight search results
set incsearch " incremental search
" copy and paste using the system's clipboard
" set clipboard=unnamed
" set clipboard=unnamedplus

" 3 character tabs and indents 
set tabstop=3
set shiftwidth=3
set softtabstop=3
set noexpandtab " Tabs not to be expanded to spaces

set ruler " Show line and column numbers, as well as percent of file
set showcmd " Show partial command in status line

" split positions
set splitright
set splitbelow

" Bottom status line
set statusline="%f%m%r%h%w [%Y] [0x%02.2B]%< %F%=%4v,%4l %3p%%"

"""""""""""""""""""""""""""""""""""""""""""""""
""" PLUGINS 
" Pathogen plugin manager
call pathogen#infect() 
Helptags
" TagBar plugin
nmap <F8> :TagbarOpenAutoClose<CR>
nmap <F9> :TagbarToggle<CR>
" Tabular plugin
vnoremap <leader>t :Tab<space>/
"""""""""""""""""""""""""""""""""""""""""""""""

" Relative numbering
function! RelativeNumberToggle()
	if(&relativenumber == 1)
		set norelativenumber
	else
		set relativenumber
	endif
endfunc

" key mappings
" nmap <leader>lj ^
" nmap <leader>lk $
nmap <C-n> :call RelativeNumberToggle()<cr>
	" globally replace word under cursor
nmap <leader>cg :%s/\<<c-r>=expand("<cword>")<cr>\>/
	" (prefix) paste the output of shell command
nmap <leader>sc :r !

" Load the colorscheme
set background=light
colorscheme light-bg
