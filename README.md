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
vfzavAhanaH    Entity=(e2661-person---Siva)||base_name=vfzavAhana|ittnim=2661,Siva,vol_13,ver_1347

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

# sent_id = MBh_13_1_18_39
# mnd_reference = MND_vol-ix_18_39

```

- **MBh_13_1** → Calcutta Edition, Volume 13, Chapter 1  
- **MND_vol-ix_18_39** → Reference to the [Itihasa dataset](https://github.com/rahular/itihasa), mapping to M. N. Dutt’s English translation (Volume IX, Subchapter 18, Verse 39)  

---

### Knowledge Base

The **Knowledge Base (KB)** that links each entity cluster to cross-lingual descriptions in English (derived from *Index to the Names in Mahābhārata*).  

The KB is stored as a JSON file, where each entry corresponds to an entity ID (`eid`) and contains:  

- **key** → unique ID  
- **description** → description from the Index after removing the references   
- **cleaned_description** → description prepared for readability  
- **aliases** → list of other entity IDs that are name variants of the same entity  
- **cluster_head** → boolean flag indicating the canonical head entry of the cluster  

---

#### Example

```json
"e3699": {
  "key": "druma",
  "description": "Druma, king of the Kimpuruṣas. ...",
  "cleaned_description": "Druma was the king of the Kimpuruṣas, known as Kimpuruṣeśaḥ. ...", 
  "aliases": ["e5752", "e5753", "e5754"],
  "cluster_head": true
},

"e5752": {
  "key": "kimpuruzAcArya",
  "description": "Kimpuruṣācārya (“leader of the Kimpuruṣas”) = Druma, ( °, ( °",
  "cleaned_description": "Kimpuruṣācārya means leader of the Kimpuruṣas and is identified as Druma.",
  "cluster_head": false
}
````

In this example:

* `e3699` is the **cluster head** for **Druma**, the king of the Kimpuruṣas.
* `e5752` is a **name variant** (*Kimpuruṣācārya*), connected to the same cluster via the `aliases` field.


```

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

