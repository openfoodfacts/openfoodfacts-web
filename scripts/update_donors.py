#!/usr/bin/env python3
"""
Update donor status in data/reuses.json
"""

import json

def main():
    with open("data/reuses.json", "r", encoding="utf-8") as f:
        reuses = json.load(f)

    new_reuses = []
    for r in reuses:
        # Merge duplicate macrofactor-diet-sidekick into macrofactor
        if r["id"] == "macrofactor-diet-sidekick":
            continue

        if r["id"] == "macrofactor":
            r["donates_to_ngo"] = True
            r["donation_note"] = (
                "Financial supporter of the Open Food Facts NGO through donations, as well as an active "
                "contributor of thousands of food products and nutritional data. Recognized with the "
                "2025 Contributor Trophy."
            )
            r["donation_note_fr"] = (
                "Soutien financier de l'association Open Food Facts par des dons, et contributeur actif "
                "de milliers de produits et données alimentaires. Lauréat du Trophée des Contributeurs 2025."
            )
            r["featured"] = True
            r["contributes_data"] = True
            r["contributes_photos"] = True
            r["installs"] = "500K+"
            r["installs_numeric"] = 500000
            r["rating"] = 4.8
            r["cached_icon"] = "/images/reuses/icons/macrofactor.png"

        if r["id"] == "yuka":
            r["donates_to_ngo"] = True
            r["donation_note"] = (
                "Financial contributor to the Open Food Facts open infrastructure, and contributes packaging "
                "photos and select product data back to the global commons."
            )
            r["donation_note_fr"] = (
                "Contributeur financier de l'infrastructure ouverte d'Open Food Facts, et contribue en retour "
                "des photos d'emballage et certaines données produits au bien commun."
            )

        new_reuses.append(r)

    with open("data/reuses.json", "w", encoding="utf-8") as f:
        json.dump(new_reuses, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(new_reuses)} reuses to data/reuses.json")
    donors = [r for r in new_reuses if r.get("donates_to_ngo")]
    print(f"Total NGO Donors: {len(donors)}")
    for d in donors:
        print(f" - {d['name']} ({d['id']})")

if __name__ == "__main__":
    main()
