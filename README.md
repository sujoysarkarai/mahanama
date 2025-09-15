# Mahānāma: A Unique Testbed for Literary Entity Discovery and Linking

[![Paper](https://img.shields.io/badge/Paper-EMNLP%202025-blue)](link)

---

## 📖 Description
**Mahānāma** is a large-scale dataset for end-to-end **Entity Discovery and Linking (EDL)** in Sanskrit.  
Drawn from the *Mahābhārata*, the world’s longest epic, the dataset comprises **over 109,000 named entity mentions**.  

- Entity mentions are extracted from the reference work:  
  *Index to the Names in Mahābhārata*  
  [Online edition](https://www.sanskrit-lexicon.uni-koeln.de/scans/INMScan/2020/web/index.php)  
- The dataset is divided into **18 volumes**.  
---


## ⚡ Format
The dataset follows the **CorefUD** standard for representing entities and mentions.  
For more details, see the [CorefUD format documentation](https://ufal.mff.cuni.cz/corefud).  

---

[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)
python scripts/load_dataset.py --input data/volume_1.conllu
