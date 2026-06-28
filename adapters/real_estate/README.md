# adapters/real_estate/

Real Estate Adapter — Tampa Bay, Florida

This adapter is responsible for all real-estate-specific logic:
- Ingesting public county records (Hillsborough, Pinellas)
- Parsing raw file formats
- Classifying entities (is this a buyer? what kind of entity?)
- Normalizing data into LUX Core schemas

## Boundary Rule

This adapter outputs only LUX Core entities:
`Participant`, `Asset`, `Transaction`, `Signal`

Core never reads raw county data directly.

## Sources

| County | Status | Source |
|---|---|---|
| Hillsborough | 🟡 In Progress | publicrec.hillsclerk.com |
| Pinellas | 🔲 Stub | pcpao.gov |

## Structure

```
ingestion/       # download and cache raw files
parsing/         # parse raw county file formats
classification/  # entity classification (buyer? what type?)
normalization/   # transform to Core schemas
sources/         # one file per county
```
