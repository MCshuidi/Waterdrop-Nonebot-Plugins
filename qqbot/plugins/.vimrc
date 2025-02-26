"User Costume Vim file : .vimrc

colorscheme evening
set termguicolors

set nocompatible

call plug#begin()
    Plug 'yianwillis/vimcdoc'
    "Plug 'scrooloose/nerdtree'
    Plug 'majutsushi/tagbar'
    Plug 'vim-airline/vim-airline'
    Plug 'vim-airline/vim-airline-themes'
    "Plug 'ludovicchabant/vim-gutentags'
    Plug 'esukram/vim-taglist'
    Plug 'vim-scripts/winmanager'
    Plug 'lervag/vimtex'
call plug#end()

filetype on
filetype plugin on
filetype indent on

syntax on

set mouse=a

set fdm=marker

set number
set ruler
set showmode

set cursorline
hi CursorLine cterm=NONE ctermbg=242
hi CursorLineNr cterm=NONE ctermfg=43
"set cursorcolumn

set scrolloff=10

set tabstop=4
set softtabstop=4
set shiftwidth=4
set expandtab
"set autoindent
set smartindent
"set cindent

set noeb

set undofile
set backup
set noswapfile
set undodir=~/.vim/.undo/
set backupdir=~/.vim/.backup/
"set directory=~/.vim/.swp/

set incsearch
set showmatch
set hlsearch

set wildmenu
set wildmode=list:longest

inoremap ( ()<ESC>i
:inoremap ) <c-r>=ClosePair(')')<CR>
inoremap { {<CR>}<ESC>O
:inoremap } <c-r>=ClosePair('}')<CR>
inoremap [ []<ESC>i
:inoremap ] <c-r>=ClosePair(']')<CR>
inoremap " ""<ESC>i
inoremap ' ''<ESC>i

function! ClosePair(char)
    if getline('.')[col('.') - 1] == a:char
        return "\<Right>"
    else
        return a:char
    endif
endfunction



let g:vimtex_view_method='zathura'
let g:vimtex_quickfix_mode=0
set conceallevel=1

let g:Tex_CompileRule_pdf = 'xelatex -synctex=1 --interaction=nonstopmode $*'


let Tlist_Ctags_Cmd = 'ctags'
let Tlist_Show_One_File = 1
let Tlist_Exit_OnlyWindow = 1
let Tlist_Auto_Open = 1
let Tlist_Use_Right_Window = 1
let Tlist_File_Fold_Auto_Close = 1
"let Tlist_Sort_Type =’name’
let Tlist_GainFocus_On_ToggleOpen = 0
let Tlist_WinWidth = 42
let Tlist_Use_SingleClick=1


let g:airline_theme = "bubblegum"
let g:airline#extensions#tabline#enabled = 1
let g:airline_powerline_fonts = 1
let g:airline#extensions#tabline#formatter = 'unique_tail'

if !exists('g:airline_symbols')
    let g:airline_symbols = {}
endif
let g:airline_left_sep = ''
let g:airline_left_alt_sep = ''
"let g:airline_right_sep = ''
let g:airline_right_sep = '«'
let g:airline_right_alt_sep = ''
let g:airline_symbols.branch = '⎇ '
let g:airline_symbols.colnr = ' ℅:'
let g:airline_symbols.readonly = 'R'
let g:airline_symbols.linenr = '☰ '
let g:airline_symbols.maxlinenr = ''
let g:airline_symbols.dirty = 'X'
let g:airline_symbols.notexists = 'Ɇ'

"set statusline=
"set statusline+=\ %F\ %M\ %Y\ %R
"set statusline+=%=
"set statusline+=\ ascii:\ %b\ hex:\ 0x%B\ row:\ %l\ col:\ %c\ percent:\ %p%%
"set laststatus=2

