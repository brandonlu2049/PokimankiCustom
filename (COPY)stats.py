# -*- coding: utf-8 -*-

# Pokémanki
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import List, Tuple

from anki.dbproxy import DBProxy

from aqt import mw
from anki.utils import ids2str

from .utils import *
from .custom_py.count_time import shigeTaskTimer


# for item in nograndchildren:
#     resultlist.append(deckStats([item]))

def cardIdsFromDeckIds(queryDb:DBProxy, deckIds: List[int]) -> List[int]:
    query = f"select id from cards where did in {ids2str(deckIds)}"
    cardIds = [i[0] for i in queryDb.all(query)]
    return cardIds


def cardInterval(queryDb: DBProxy, cid: int):
    revLogIvl = queryDb.scalar(
        "select ivl from revlog where cid = %s "
        "order by id desc limit 1 offset 0" % cid
    )
    ctype = queryDb.scalar(
        "select type from cards where id = %s "
        "order by id desc limit 1 offset 0" % cid
    )

    # card interval is "New"
    if ctype == 0:
        ivl = 0
    elif revLogIvl is None:
        ivl = 0
    elif revLogIvl < 0:
        # Anki represents "learning" card review log intervals as negative minutes
        # So, convert to days
        ivl = revLogIvl * -1 / 60 / 1440
    else:
        ivl = revLogIvl

    return ivl


def deckStats(deck_ids: List[int]) -> List[Tuple[int, int]]:
    """
    deck_ids: list
    returns [(card_id, card_interval), ...]
    """
    cardIds = cardIdsFromDeckIds(mw.col.db, deck_ids)

    # result = self.col.db.all("""select id, ivl from cards where did in %s""" %
    #             ids2str(self.col.decks.active()))
    result = []
    for cid in cardIds:
        ivl = cardInterval(mw.col.db, cid)
        result.append((cid, ivl))

    return result


def deckStatsV4(deck_ids):
    queryDb = mw.col.db
    if not deck_ids:
        return []

    deck_ids_str = ','.join(map(str, deck_ids))

    query = f"""
        SELECT
            c.did,
            c.id as cid,
            CASE
                WHEN c.type = 0 THEN 0
                WHEN r.ivl IS NULL THEN 0
                WHEN r.ivl < 0 THEN (r.ivl * -1) / 86400.0
                ELSE r.ivl
            END AS ivl
        FROM cards c
        LEFT JOIN (
            SELECT
                cid,
                ivl,
                ROW_NUMBER() OVER (PARTITION BY cid ORDER BY id DESC) as rn
            FROM revlog
        ) r ON c.id = r.cid AND r.rn = 1
        WHERE c.did IN ({deck_ids_str})
        ORDER BY c.did
    """

    rows = queryDb.all(query)

    grouped = {}
    for did, cid, ivl in rows:
        if did not in grouped:
            grouped[did] = []
        grouped[did].append((cid, ivl))

    resultlist = []
    for did in deck_ids:
        resultlist.append(grouped.get(did, []))

    return resultlist


def deckStatsV3(deck_ids):
    queryDb = mw.col.db
    resultlist = []

    for item in deck_ids:
        ids = f"({','.join(str(i) for i in [item])})"
        query = f"select id from cards where did in {ids}"
        cardIds = []

        for i in queryDb.all(query):
            cardIds.append(i[0])

        result = []
        for cid in cardIds:
            query = f"""
                SELECT
                    CASE
                        WHEN c.type = 0 THEN 0
                        WHEN r.ivl IS NULL THEN 0
                        WHEN r.ivl < 0 THEN r.ivl * -1 / 60 / 1440
                        ELSE r.ivl
                    END AS ivl
                FROM cards c
                LEFT JOIN (
                    SELECT ivl, cid
                    FROM revlog
                    WHERE cid = {cid}
                    ORDER BY id DESC
                    LIMIT 1
                ) r ON c.id = r.cid
                WHERE c.id = {cid}
            """
            ivl = queryDb.scalar(query)
            result.append((cid, ivl))

        resultlist.append(result)

    return resultlist

def deckStatsV2(deck_ids):
    queryDb = mw.col.db
    resultlist = []
    for item in deck_ids:
        query = f"select id from cards where did in {ids2str([item])}"
        cardIds = []
        for i in queryDb.all(query):
            cardIds.append(i[0])
        result = []
        for cid in cardIds:
            revLogIvl = queryDb.scalar(
                "select ivl from revlog where cid = %s "
                "order by id desc limit 1 offset 0" % cid
            )
            ctype = queryDb.scalar(
                "select type from cards where id = %s "
                "order by id desc limit 1 offset 0" % cid
            )
            # card interval is "New"
            if ctype == 0:
                ivl = 0
            elif revLogIvl is None:
                ivl = 0
            elif revLogIvl < 0:
                # Anki represents "learning" card review log intervals as negative minutes
                # So, convert to days
                ivl = revLogIvl * -1 / 60 / 1440
            else:
                ivl = revLogIvl
            result.append((cid, ivl))
        resultlist.append(result)

    return resultlist


# ...existing code...

def deckStatsV2(deck_ids):
    queryDb = mw.col.db
    resultlist = []
    for item in deck_ids:
        query = f"""
            SELECT c.id, c.type,
            (
                SELECT ivl
                FROM revlog r
                WHERE r.cid = c.id
                ORDER BY r.id DESC
                LIMIT 1
            ) as revLogIvl
            FROM cards c
            WHERE c.did IN {ids2str([item])}
        """
        rows = queryDb.all(query)
        result = []
        for cid, ctype, revLogIvl in rows:
            if ctype == 0:
                ivl = 0
            elif revLogIvl is None:
                ivl = 0
            elif revLogIvl < 0:
                ivl = revLogIvl * -1 / 60 / 1440
            else:
                ivl = revLogIvl
            result.append((cid, ivl))
        resultlist.append(result)

    return resultlist




def MultiStats(wholeCollection: bool) -> List[Tuple[int, List[Tuple[int, int]]]]:
    """Retrieve id and ivl for each subdeck that does not have subdecks itself

    :param bool wholeCollection:
    :return: List of tuples with decks and their cards (deck_id, [(card_id, interval), ...])
    :rtype: List
    """
    # Get list of subdecks
    if wholeCollection:
        shigeTaskTimer.start("MultiStats: Get all subdecks")
        # Get results for all subdecks in collection
        alldecks = mw.col.decks.all_names_and_ids()
        # Determine which subdecks do not have their own subdecks
        nograndchildren = []
        for item in alldecks:
            if len(mw.col.decks.children(int(item.id))) == 0:
                nograndchildren.append(int(item.id))
        shigeTaskTimer.end("MultiStats: Get all subdecks")
    else:
        # Get results only for all subdecks of selected deck
        shigeTaskTimer.start("MultiStats02: Get active deck")
        curr_deck = mw.col.decks.active()[0]
        children = mw.col.decks.children(curr_deck)
        if not children:
            nograndchildren = [curr_deck]
        else:
            childlist = [item[1] for item in children]
            # Determine which subdecks do not have their own subdecks
            nograndchildren = []
            for item in childlist:
                if len(mw.col.decks.children(item)) == 0:
                    nograndchildren.append(item)
        shigeTaskTimer.end("MultiStats02: Get active deck")
    resultlist = []
    # Find results for each card in these decks
    shigeTaskTimer.start("04_deckStats")
    for item in nograndchildren:
        resultlist.append(deckStats([item]))
    shigeTaskTimer.end("04_deckStats")

    shigeTaskTimer.start("05_deckStatsV2")
    resultlist_B = deckStatsV4(nograndchildren)
    shigeTaskTimer.end("05_deckStatsV2")

    with open("c:/Users/shigg/AppData/Roaming/Anki2/addons21/1677779223/resultlist.txt", "w", encoding="utf-8") as f:
        f.write("=== resultlist ===\n")
        f.write(str(resultlist))
        f.write("\n====\n")

    with open("c:/Users/shigg/AppData/Roaming/Anki2/addons21/1677779223/resultlist_B.txt", "w", encoding="utf-8") as f:
        f.write("=== resultlist_B ===\n")
        f.write(str(resultlist_B))
        f.write("\n====\n")

    if resultlist == resultlist_B:
        print("Same results")
    else:
        print("not same")

    # Zip the deck ids with the results
    shigeTaskTimer.start("MultiStats03: Zip")
    nograndchildresults = list(zip(nograndchildren, resultlist))
    shigeTaskTimer.end("MultiStats03: Zip")

    return nograndchildresults


def TagStats() -> List[Tuple[str, List[List[int]]]]:
    "Returns List[(tag_name, [[card_id, card_interval], ...]), ...]"
    savedtags = get_synced_conf()["tags"]
    resultlist = []
    for item in savedtags:
        result = mw.col.db.all(
            "select c.id, c.ivl from cards c, notes n where c.nid = n.id and n.tags LIKE '%"
            + item
            + "%'"
        )
        resultlist.append(result)
    results = list(zip(savedtags, resultlist))
    return results
