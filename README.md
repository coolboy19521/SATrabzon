# SATrabzon
SAT vocabulary preparation program. Words are extracted from SATashkent vocabulary book (vocab.pdf).

Repository includes all the scripts used to collect the data. Some data is added via hand (1-2 rows in total for some csv files). Flask and vanilla HTML/CSS/JS is used. Program depends on the sets directory. To create this directory you can either run the scripts or just extract the sets directory from the backups directory. Latter is recommended, as it includes some manual fixes.

To extract data from the pdf conflate-py is used.

Note: There is a buried feature of the app, which enables having more or less than 4 options for a question. I added it for modularity, but I don't find it practical to have in the interface. LOL.
