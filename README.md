# Mahānāma: A Unique Testbed for Literary Entity Discovery and Linking

[![Paper](https://img.shields.io/badge/Paper-EMNLP%202025-blue)](link)

---

## Description
**Mahānāma** is a large-scale dataset for end-to-end **Entity Discovery and Linking (EDL)** in Sanskrit.  
Drawn from the *Mahābhārata*, the world’s longest epic, the dataset comprises **over 109,000 named entity mentions**.  

- Entity mentions are extracted from the reference work:  
  *Index to the Names in Mahābhārata*  
  [Online edition](https://www.sanskrit-lexicon.uni-koeln.de/scans/INMScan/2020/web/index.php)  
- The dataset is divided into **18 volumes**.  
---


##  Format
The dataset follows the **CorefUD** standard for representing entities and mentions.  
For more details, see the [CorefUD format documentation](https://ufal.mff.cuni.cz/corefud).  

---

##  Data
- **Annotated Text (`data/mahanama_conllu/`)**  
  - Organized by **18 volumes**, each containing multiple **subchapters**.  
  - Each subchapter is stored in **CoNLL-U (CorefUD)** format.
  -  The text tokens are encoded in the  
    **[Sanskrit Library Phonetic Basic Encoding Scheme (SLP1)](https://en.wikipedia.org/wiki/SLP1)**.  
    
  
- **Knowledge Base (`data/kb/`)**  
  - `entity_metadata.json`: English descriptions of all entries of the index.
---

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

