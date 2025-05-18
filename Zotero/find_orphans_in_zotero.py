# Update this to match your data directory
ZOTERO_STORAGE = r'C:\Users\DTK\Zotero'
ZOTERO_STORAGE_FILES = r'D:\Workspace\OneDrive\vardtk\OneDrive\document\文献'

import sqlite3
import os

# Query all attachments
dbh = sqlite3.connect(ZOTERO_STORAGE + '/zotero.sqlite')
c = dbh.cursor()
c.execute('select path from itemAttachments where linkMode = 2')
# 'select path from itemAttachments where contentType = "application/pdf" and linkMode = 2'

# Fetching all files as a set
files = set()
for dirpath, dirnames, filenames in os.walk(ZOTERO_STORAGE_FILES):
    for f in filenames:
        files.add(os.path.normpath(os.path.normcase(os.path.join(dirpath, f))))

for key in c.fetchall():
    # ('attachments:aaa/bbb.ccc',)
    filename = key[0].split(':')[1].lower()
    filepath = os.path.normpath(
        os.path.normcase(os.path.join(ZOTERO_STORAGE_FILES, filename))
    )
    files.discard(filepath)

# Loop over the non-existing files
if len(files) > 0:
    orphans = sorted(files)
    print('\n'.join(orphans))
else:
    print('no orphan.')
