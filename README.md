# Scripts for downloading oral history data

1. Download all oral history metadata as json and csv files directly from [oralhistory.nypl.org](http://oralhistory.nypl.org/)

  ```
  python get_metadata.py -out "path/to/output/dir/"
  ```

  This script creates in the output directory:

  - `neighborhoods.json` and `neighborhoods.csv`
  - `interviews.json` and `interviews.csv`
  - individual `.json` files for each interview which contain more metadata and annotations

2. Download all oral history transcripts as json, plain text, and web vtt files directly from [transcribe.oralhistory.nypl.org](http://transcribe.oralhistory.nypl.org/)

  ```
  python get_transcripts.py -out "path/to/output/dir/"
  ```

  This script creates in the output directory:

  - A manifest `transcripts.json` file with links to each interview transcripts
  - Individual folders for each interview that contains three formats of transcripts (`.json`, `.txt`, `.vtt`)  
  - `.json` files contain all the of the edits, while the `.txt` and `.vtt` contain the "best guess" transcriptions for each line
