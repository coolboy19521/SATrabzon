import pypdf
import camelot

file = 'vocab.pdf'

tables = camelot.read_pdf(file, pages='all', flavor='lattice', strip_text='\n')
tables.export('try/foo.csv', f='csv', compress=False)