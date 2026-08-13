# E1605 — Common Crawl 2015 Tor2web body acquisition

The frozen corpus was limited to `CC-MAIN-2015-06` and `CC-MAIN-2015-11`, using the 3,204-line September 2014 inventory and only the declared root mirror forms. Every index hit required exact WARC range retrieval, unnormalized response extraction, recorded metadata and hashes, and a direct SHA-512 comparison. If index access or exact byte retrieval was unavailable, the required result was `COMMON_CRAWL_BODY_ACQUISITION_BLOCKED`. Live pages, reconstructed HTML, and filenames were forbidden substitutes.
