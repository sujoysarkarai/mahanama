# Mahānāma: A Unique Testbed for Literary Entity Discovery and Linking

[![Paper](https://img.shields.io/badge/Paper-EMNLP%202025-blue)](link)

---

## Description
**Mahānāma** is a large-scale dataset for end-to-end **Entity Discovery and Linking (EDL)** in Sanskrit.  
Drawn from the *Mahābhārata*, the world’s longest epic, the dataset comprises **over 109,000 named entity mentions**, and is aligned with an **English knowledge base** to support cross-lingual linking.  

- Entity mentions are extracted from the reference work:  
  *Index to the Names in Mahābhārata*  
  [Online edition](https://www.sanskrit-lexicon.uni-koeln.de/scans/INMScan/2020/web/index.php)  
- The dataset is divided into **18 volumes**.
- Each entity cluster is linked to the knowledge base, which provides cross-lingual descriptions in English
---

##  Data
- **Annotated Text (`data/mahanama_conllu/`)**  
  - Organized by **18 volumes**, each containing multiple **subchapters**.  
  - Each subchapter is stored in **CoNLL-U (CorefUD)** format.
  -  The text tokens are encoded in the  
    **[Sanskrit Library Phonetic Basic Encoding Scheme (SLP1)](https://en.wikipedia.org/wiki/SLP1)**.  
    
  
- **Knowledge Base (`data/kb/`)**  
  - `knowledge_base.json`: English descriptions of all entries of the index.
---

##  Format
The dataset follows the **CorefUD** standard for representing entities and mentions.  
For more details, see the [CorefUD format documentation](https://ufal.mff.cuni.cz/corefud).  

## Data Format Examples

Entity information is stored in the **`MISC` column** of the CoNLL-U files using the key:

```
global.Entity = eid-etype-head-identity-other
```

- **eid** → entity/cluster ID  
- **etype** → entity type (e.g., `person`)  
- **head** → index of head word (not used in this dataset → left blank)  
- **identity** → canonical name chosen from the variants of the entity  

---
### Entity annotation
```
vfzavAhanaH    Entity=(e2661-person---Siva)|ittnim=2661,Siva,vol\_13,ver\_1347,vfzavAhana

```
- **Entity=(e2661-person---Siva)**  
  - `e2661`: entity ID  
  - `person`: entity type  
  - `---`: (no head word)  
  - `Siva`: canonical identity name  

- **base_name=vfzavAhana**  
  - uninflected form of the matched name in the verse  

- **ittnim=2661,Siva,vol_13,ver_1347**  
  - `2661`: entry number in the [digitized *Index to the Names in Mahābhārata*](https://www.sanskrit-lexicon.uni-koeln.de/scans/INMScan/2020/web/index.php)  
  - `Siva`: English gloss (lookup key in the index, linked to ID 2661)  
  - `vol_13, ver_1347`: Calcutta Edition reference (Volume 13, Verse 1347)  

Thus, **vfzavAhanaH** refers to **Siva (e2661)**.

---

### Sentence identifier

```

# sent_id = MBh_CE_13_1_MND_vol-ix_18_39

```

- **MBh_CE_13_1** → Calcutta Edition, Volume 13, Chapter 1  
- **MND_vol-ix_18_39** → Reference to the [Itihasa dataset](https://github.com/rahular/itihasa), mapping to M. N. Dutt’s English translation (Volume IX, Subchapter 18, Verse 39)  


---


[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

