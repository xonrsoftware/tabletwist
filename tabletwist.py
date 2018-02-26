#
# TABLETWIST BOARDGAME TOURNAMENT MANAGER
# Version 1.2, 15-Jan-2017
# Copyright © 2017 Joe Czapski
# email contact: czap@tournamentdesign.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details (http://www.gnu.org/licenses/).
#

import sys, os, re, random
from operator import itemgetter
from datetime import datetime
tiebreak2p = True  #If True then a 2-player game is only put at the end to break a 'cowinner' tie.
debug_mode = False  #Set debug_mode to True to create results files with randomly generated game scores.
rndseed = ""
#
# FUNCTION err(msg)
# Displays error message to user then terminates the program.
#
def err(msg):
    try:
        raise IndexError
    finally:
        print('\nTOURNAMENT FILES ERROR:', msg)
        print('\nPlease correct the problem and run again.')
        input('\nPress Enter to close...')

#
# FUNCTION tablecount_randround(numplayers, maxtablesize)
# For a Random type of round, returns number of 5, 4, 3, and 2-player tables
# based on number of players remaining in the tournament.
#
def tablecount_randround(numplayers):
    if numplayers < mintablesize:
        err("Can't determine table seating with fewer than " + str(mintablesize) + " players remaining.")
    if maxtablesize == 4:
        if numplayers >= 6:
            M = [[0,0],[-2,3],[-1,2],[0,1]]
            q, r = divmod(numplayers, 4)
            ntables = {'5': 0, '4': q + M[r][0], '3': M[r][1], '2': 0}
        elif numplayers == 5:
            if mintablesize == 2:
                ntables = {'5': 0, '4': 0, '3': 1, '2': 1}  #a 2-player table is included
            else:
                ntables = {'5': 0, '4': 1, '3': 0, '2': 0, 'bye': 1}  #one player sits out this round
        elif numplayers == 4:
            ntables = {'5': 0, '4': 1, '3': 0, '2': 0}
        elif numplayers == 3:
            ntables = {'5': 0, '4': 0, '3': 1, '2': 0}
        else:  #numplayers is 2
            ntables = {'5': 0, '4': 0, '3': 0, '2': 1}
    else:  #maxtablesize is assumed to be 5
        if numplayers >= 12:
            M = [[0,0],[-3,4],[-2,3],[-1,2],[0,1]]
            q, r = divmod(numplayers, 5)
            ntables = {'5': q + M[r][0], '4': M[r][1], '3': 0, '2': 0}
        elif 3 <= numplayers <= 11:
            M = [[0,0,1],[0,1,0],[1,0,0],[0,0,2],[0,1,1],[0,2,0],[1,1,0],[2,0,0],[0,2,1]]
            r = numplayers - 3
            ntables = {'5': M[r][0], '4': M[r][1], '3': M[r][2], '2': 0}
        else:  #numplayers is 2
            ntables = {'5': 0, '4': 0, '3': 0, '2': 1}
    return ntables

#
# FUNCTION tablecount_splitround(numplayers)
# For a Split By Strikes type of round, returns number of 5, 4, 3, and 2-player tables
# in each strikes-range group, based on number of players remaining in the tournament.
#
def tablecount_splitround(numplayers):
    ntables = tablecount_randround(numplayers)
    if maxtablesize == 4:
        if numplayers >= 31:
            M0 = [[0,0,0,0,0,0],[0,1,0,1,0,1],[0,1,0,1,0,0],[0,1,0,0,0,0]]
            M1 = [[1,0,0,0,0,0],[1,1,0,1,0,1],[1,0,0,1,0,1],[1,0,0,1,0,0]]
            M2 = [[1,0,1,0,0,0],[1,1,1,1,0,1],[0,2,1,0,1,0],[1,0,1,0,0,1]]
            q, rg = divmod(ntables['4'], 3)
            r = numplayers % 4
            if rg == 0: M = M0
            elif rg == 1: M = M1
            else: M = M2
            ngtables = [{'5': 0, '4': q + M[r][0], '3': M[r][1], '2': 0},  #For 31 or more players,
                        {'5': 0, '4': q + M[r][2], '3': M[r][3], '2': 0},  #return 3 groups.
                        {'5': 0, '4': q + M[r][4], '3': M[r][5], '2': 0}]
        elif 6 <= numplayers <= 30:
            M0 = [[0,0,0,0],[0,2,0,1],[0,1,0,1],[0,1,0,0]]
            M1 = [[1,0,0,0],[1,1,0,2],[0,2,1,0],[1,0,0,1]]
            q, rg = divmod(ntables['4'], 2)
            r = numplayers % 4
            if rg == 0: M = M0
            else: M = M1
            ngtables = [{'5': 0, '4': q + M[r][0], '3': M[r][1], '2': 0},  #For 6 to 30 players,
                        {'5': 0, '4': q + M[r][2], '3': M[r][3], '2': 0}]  #return 2 groups.
        elif numplayers == 5:
            if mintablesize == 2:
                ngtables = [{'5': 0, '4': 0, '3': 1, '2': 1}]  #one group, a 3-player table and a 2-player table
            else:
                ngtables = [{'5': 0, '4': 1, '3': 0, '2': 0, 'bye': 1}]  #one player sits out this round
        elif numplayers == 4:
            ngtables = [{'5': 0, '4': 1, '3': 0, '2': 0}]
        elif numplayers == 3:
            ngtables = [{'5': 0, '4': 0, '3': 1, '2': 0}]
        else:  #numplayers is 2
            ngtables = [{'5': 0, '4': 0, '3': 0, '2': 1}]
    else:  #maxtablesize is assumed to be 5
        if numplayers >= 31:
            M0 = [[0,0,0,0,0,0],[0,2,0,1,0,1],[0,1,0,1,0,1],[0,1,0,1,0,0],[0,1,0,0,0,0]]
            M1 = [[1,0,0,0,0,0],[0,2,0,2,1,0],[-1,3,1,0,1,0],[1,0,0,1,0,1],[1,0,0,1,0,0]]
            M2 = [[1,0,1,0,0,0],[1,1,1,1,0,2],[1,1,1,1,0,1],[0,2,1,0,1,0],[1,0,1,0,0,1]]
            q, rg = divmod(ntables['5'], 3)
            r = numplayers % 5
            if rg == 0: M = M0
            elif rg == 1: M = M1
            else: M = M2
            ngtables = [{'5': q + M[r][0], '4': M[r][1], '3': 0, '2': 0},  #For 31 or more players,
                        {'5': q + M[r][2], '4': M[r][3], '3': 0, '2': 0},  #return 3 groups.
                        {'5': q + M[r][4], '4': M[r][5], '3': 0, '2': 0}]
        elif 12 <= numplayers <= 30:
            M0 = [[0,0,0,0],[0,2,0,2],[0,2,0,1],[0,1,0,1],[0,1,0,0]]
            M1 = [[1,0,0,0],[0,3,1,1],[1,1,0,2],[0,2,1,0],[1,0,0,1]]
            q, rg = divmod(ntables['5'], 2)
            r = numplayers % 5
            if rg == 0: M = M0
            else: M = M1
            ngtables = [{'5': q + M[r][0], '4': M[r][1], '3': 0, '2': 0},  #For 12 to 30 players,
                        {'5': q + M[r][2], '4': M[r][3], '3': 0, '2': 0}]  #return 2 groups.
        elif 6 <= numplayers <= 11:
            M = [[0,0,1,0,0,1],[0,1,0,0,0,1],[0,1,0,0,1,0],
                 [1,0,0,0,1,0],[1,0,0,1,0,0],[0,1,1,0,1,0]]
            r = numplayers - 6
            ngtables = [{'5': M[r][0], '4': M[r][1], '3': M[r][2], '2': 0},  #For 6 to 11 players,
                        {'5': M[r][3], '4': M[r][4], '3': M[r][5], '2': 0}]  #return 2 groups and allow 3-player tables.
        else:  #numplayers is 2 to 5
            M = [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]
            r = numplayers - 2
            ngtables = [{'5': M[r][0], '4': M[r][1], '3': M[r][2], '2': M[r][3]}]  #For 2 to 5, it's just one table.
    return ngtables

#
# FUNCTION seating_randround(roundnum, playerset, pairs)
# Generates the tables & seating plan file for the next round, if it's a Random type of round.
#
pmeets = {}  #Dict of possible pairings for different size tables
pmeets['6'] = [[0,1],[0,2],[0,3],[0,4],[0,5],[1,2],[1,3],[1,4],[1,5],[2,3],[2,4],[2,5],[3,4],[3,5],[4,5]]
pmeets['5'] = [[0,1],[0,2],[0,3],[0,4],[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
pmeets['4'] = [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]
pmeets['3'] = [[0,1],[0,2],[1,2]]
pmeets['2'] = [[0,1]]
detptable = [0,1,2,4,7,10]  #Detrimental points by number of times a pair has met

def seating_randround(roundnum, playerset, pairs):
    players = []
    for p in playerset:  #Build array of active players and their strikes
        if playerset[p]['status'] == 'active':
            players.append([p, playerset[p]['strikes']])
    if len(players) < mintablesize:
        err("Fewer than " + str(mintablesize) + " players remain. Tournament has ended. See standings file.")
    flines = []
    flines.append('TABLETWIST ROUND SEATING')
    flines.append(tourname)
    flines.append('Generated,' + datetime.now().strftime('%d-%b-%Y %H:%M'))
    flines.append('Round,' + str(roundnum))
    flines.append('Round Type,Random')
    tableplan = tablecount_randround(len(players))
    if 'bye' in tableplan: players, byeplayer = getbyeplayer(players)
    if maxtablesize > 4: flines.append('Number Of 5-Player Tables,' + str(tableplan['5']))
    flines.append('Number Of 4-Player Tables,' + str(tableplan['4']))
    flines.append('Number Of 3-Player Tables,' + str(tableplan['3']))
    if tableplan['2'] > 0: flines.append('Number Of 2-Player Tables,' + str(tableplan['2']))
    plans = []
    if pairs: nplans = 30
    else: nplans = 1
    for s in range(0, nplans):  #Build array of 30 seating plans
        random.Random(rndseed).shuffle(players)  #Shuffle the list of players
        i = 0
        tables = []
        dscore = 0
        for k in range(5, 1, -1):
            for t in range(0, tableplan[str(k)]):
                tpset = players[i:i+k]  #Deal the players into the table
                i += k
                tables.append(tpset)  #Build tables array of arrays of players and their strikes
                for pmeet in pmeets[str(k)]:  #Calculate detrimental score for this seating plan
                    pset = {tpset[pmeet[0]][0], tpset[pmeet[1]][0]}
                    for pair in pairs:
                        if pair[0] == pset:
                            dscore += detptable[min([pair[1],5])]
        plans.append([tables, dscore])  #plans is an array of pairs of tablesarray and detrimental score
    dscore = plans[0][1]
    dsci = 0
    i = 0
    for plan in plans:
        if plan[1] < dscore:
            dscore = plan[1]
            dsci = i
        i += 1
    planbest = plans[dsci][0]  #planbest is the tables array with the lowest detrimental score
    tablenum = 1
    for tseating in planbest:  #Loop thru the tables in planbest and construct the file lines
        flines.append('Table,' + str(tablenum))
        tablenum += 1
        for p in tseating:
            flines.append(p[0] + ',' + str(p[1]) + ',' + (str(random.randint(15,30)) if debug_mode else ''))
    if 'bye' in tableplan:
        flines.append('Bye')
        flines.append(byeplayer[0] + ',' + str(byeplayer[1]))
    for i in range(0, len(flines)):
        flines[i] += '\n'
    filename = tshortname + ' round ' + str(roundnum) + (' results' if debug_mode else '') + '.csv'
    f = open(os.path.join(mydir, filename), 'w')
    f.writelines(flines)
    f.close()
    print("Generated " + ("" if roundnum == 1 else "new ") + "table seating file '" + filename + "'")

#
# FUNCTION seating_splitround(roundnum, playerset, pairs)
# Generates the tables & seating plan file for the next round, if it's a Split By Strikes type of round.
#
def seating_splitround(roundnum, playerset, pairs):
    players = []
    for p in playerset:  #Build array of active players and their strikes
        if playerset[p]['status'] == 'active':
            players.append([p, playerset[p]['strikes']])
    if len(players) < mintablesize:
        err("Fewer than " + str(mintablesize) + " players remain. Tournament has ended. See standings file.")
    flines = []
    flines.append('TABLETWIST ROUND SEATING')
    flines.append(tourname)
    flines.append('Generated,' + datetime.now().strftime('%d-%b-%Y %H:%M'))
    flines.append('Round,' + str(roundnum))
    flines.append('Round Type,Split By Strikes')
    ngtables = tablecount_splitround(len(players))
    if 'bye' in ngtables[0]: players, byeplayer = getbyeplayer(players)
    tcount5=0; tcount4=0; tcount3=0; tcount2=0
    for ngt in ngtables:
        tcount5 += ngt['5']
        tcount4 += ngt['4']
        tcount3 += ngt['3']
        tcount2 += ngt['2']
    if maxtablesize > 4: flines.append('Number Of 5-Player Tables,' + str(tcount5))
    flines.append('Number Of 4-Player Tables,' + str(tcount4))
    flines.append('Number Of 3-Player Tables,' + str(tcount3))
    if tcount2 > 0: flines.append('Number Of 2-Player Tables,' + str(tcount2))
    plans = []
    if pairs: nplans = 30
    else: nplans = 1
    for s in range(0, nplans):  #Build array of 30 seating plans
        random.Random(rndseed).shuffle(players)  #Shuffle the list of all players
        players.sort(key=itemgetter(1))  #Sort players by number of strikes accumulated
        pgroups = []
        ptr = 0
        for ngt in ngtables:  #Loop thru the groups
            np = ngt['5']*5 + ngt['4']*4 + ngt['3']*3 + ngt['2']*2
            group = players[ptr : ptr + np]  #Deal sorted players into the group
            random.Random(rndseed).shuffle(group)  #Shuffle players again just within this group
            pgroups.append(group)  #Build array of groups of players
            ptr += np
        j = 0
        grouptables = []
        dscore = 0
        for ngt in ngtables:  #Loop thru the groups again
            i = 0
            tables = []
            for k in range(5, 1, -1):
                for t in range(0, ngt[str(k)]):
                    tpset = pgroups[j][i:i+k]  #Deal the players into the table
                    i += k
                    tables.append(tpset)  #Build tables array of arrays of players and their strikes
                    for pmeet in pmeets[str(k)]:  #Calculate detrimental score for this seating plan
                        pset = {tpset[pmeet[0]][0], tpset[pmeet[1]][0]}
                        for pair in pairs:
                            if pair[0] == pset:
                                dscore += detptable[min([pair[1],5])]
            grouptables.append(tables)  #Build grouptables array of tablearrays
            j += 1
        plans.append([grouptables, dscore])  #plans is an array of pairs of grouptablesarray and detrimental score
    dscore = plans[0][1]
    dsci = 0
    i = 0
    for plan in plans:
        if plan[1] < dscore:
            dscore = plan[1]
            dsci = i
        i += 1
    planbest = plans[dsci][0]  #planbest is the grouptables array with the lowest detrimental score
    tablenum = 1
    groupnum = 1
    for group in planbest:  #Loop thru the groups in planbest
        flines.append('Group,' + str(groupnum))
        minstrikes = group[0][0][1]
        maxstrikes = group[0][0][1]
        for tbl in group:
            for plyr in tbl:
                if plyr[1] > maxstrikes: maxstrikes = plyr[1]
                if plyr[1] < minstrikes: minstrikes = plyr[1]
        flines.append('Strikes,' + str(minstrikes) + ' to ' + str(maxstrikes))
        for tseating in group:  #Loop thru the tables within the group and construct the file lines
            flines.append('Table,' + str(tablenum))
            stseating = sorted(tseating, key=itemgetter(1))
            for p in stseating:
                flines.append(p[0] + ',' + str(p[1]) + ',' + (str(random.randint(15,30)) if debug_mode else ''))
            tablenum += 1
        groupnum += 1
    if 'bye' in ngtables[0]:
        flines.append('Bye')
        flines.append(byeplayer[0] + ',' + str(byeplayer[1]))
    for i in range(0, len(flines)):
        flines[i] += '\n'
    filename = tshortname + ' round ' + str(roundnum) + (' results' if debug_mode else '') + '.csv'
    f = open(os.path.join(mydir, filename), 'w')
    f.writelines(flines)
    f.close()
    print("Generated new table seating file '" + filename + "'")
    
#
# FUNCTION getbyeplayer(players)
# Determines which player of the 5 (because maxtablesize is 4) gets a bye in the upcoming round.
# Returns the array of players [name, strikes] minus the one who gets the bye, and the bye player.
# [May need to make this function more sophisticated. In case of a tie for lowest strikes,
#  we could examine in detail the results of the previous round.]
#
def getbyeplayer(playersin):
    playersin.sort(key=itemgetter(1))
    return [playersin[1:], playersin[0]]

#
# FUNCTION resultsfileproc(filename, playersetin, pairsin)
# Processes the result file 'filename'. Returns the set of players who played in the round
# and their updated strikes and statuses. Also returns an updated set of pairs with
# how many times they met.
# Argument 'playersetin' is used for error checking too see if any new players were added
# without stating ADD or any active players were omitted without stating DROP.
#
strikechart = {}  #Dict of strikes awarding by place for different size tables
strikechart['6'] = [0,6,10,14,18,24]
strikechart['5'] = [0,6,12,18,24]
strikechart['4'] = [0,8,16,24]
strikechart['3'] = [0,12,24]
strikechart['2'] = [0,24]

def resultsfileproc(filename, playersetin, pairsin):
    def awardstrikes():  #Nested subfunction to avoid duplication of code lines in different places in parent function.
        #This subfunction is called every time a table of players has finished being read in from the results file.
        #It calculates the new strikes that each player receives based on his score and finishing place in the game,
        #and if determines if the player has been eliminated from the tournament.
        #It also increments the number of time each pair of players at the table has met.
        tables.append(tblscores)
        nplayers = len(tblscores)
        scoresoccur = []
        tblplayers = []
        for tblsc in tblscores:
            scoresoccur.append(tblsc[2])
            tblplayers.append(tblsc[0])
        if not (2 <= nplayers <= 6):
            err("In file '" + filename + "', there's at least one table that doesn't have 2 to 6 players.")
        scoresoccur.sort(reverse=True)
        i = 0
        scorestrike = {}
        for s in strikechart[str(len(scoresoccur))]:
            if str(scoresoccur[i]) in scorestrike:
                scorestrike[str(scoresoccur[i])][0] += 1
                scorestrike[str(scoresoccur[i])][1] += s
            else:
                scorestrike[str(scoresoccur[i])] = [1, s]
            i += 1
        for tblsc in tblscores:
            updstrikes = tblsc[1] + int(scorestrike[str(tblsc[2])][1] / scorestrike[str(tblsc[2])][0])
            if updstrikes < elimstrikes:
                if re.match(r'drop', tblsc[3], re.IGNORECASE):
                    playersetout[tblsc[0]] = {'strikes': updstrikes, 'status': 'dropped out', 'round': roundnum}
                else:
                    playersetout[tblsc[0]] = {'strikes': updstrikes, 'status': 'active'}
            else:  #The player's strikes are greater than or equal to the elimination threshold, so mark him as 'eliminated'.
                playersetout[tblsc[0]] = {'strikes': updstrikes, 'status': 'eliminated', 'round': roundnum}
        for pmeet in pmeets[str(nplayers)]:
            playerpair = {tblplayers[pmeet[0]], tblplayers[pmeet[1]]}
            exists = 0
            for pair in pairsout:
                if pair[0] == playerpair:
                    pair[1] += 1
                    exists = 1
            if not exists:
                pairsout.append([playerpair, 1])
    #resultsfileproc function begins executing here
    m = re.search(r'round\s+(\d+)', filename, re.IGNORECASE)
    if m:
        roundnum = int(m.group(1))
    else:
        err('Could not find round number within results file name.')
    pairsout = pairsin
    playersetout = {}
    ruleapplied = ''
    f = open(os.path.join(mydir, filename))
    flines = f.readlines()  #Read all lines of the results file into the flines array
    f.close()
    print("Loaded round", roundnum, "results file '" + filename + "'")
    inatable = False  #This inatable flag is True if the last line was Table,n
    addplayers = False  #This addplayers flag is True if the last line was ADD PLAYERS
    byeplayers = False
    byeoccurred = False
    tables = []  #Array of tables where each table is a tblscores array
    tblscores = []  #Array of the table's players, strikes, game score, and ADD or DROP command
    for line in flines:  #Loop thru all the lines that were read from the results file
        line = line.strip()
        line = re.sub(r'\s+', ' ', line)
        if line and line[0] != '#':
            L = line.split(',')
            L.extend(['','',''])
            a, b, c, d = L[0:4]  #a, b, c, and d are up to 4 comma-separated values from the line
            a = a.strip(); b = b.strip(); c = c.strip(); d = d.strip()
            m = re.match(r'(table|group|add|bye)\b', a, re.IGNORECASE)
            if m:  #first word is either 'table', 'group', 'add', or 'bye' which each signify the start and/or end of a players list
                mm = m.group(1).lower()  #set mm equal to that first word, all lower case
            if addplayers:
                if not b.isdigit():
                    err("In file '" + filename + "', added player " + a + " requires an initial strikes value.")
                if int(b) < elimstrikes:
                    playersetout[a] = {'strikes': int(b), 'status': 'active'}
                else:
                    err("Can't add a player with initial strikes greater than elimination value.")
            elif byeplayers:
                byeplayers = False  #Only one player can get a bye, so clear this flag
                if not b.isdigit():
                    err("In file '" + filename + "', the Bye player requires a strikes value.")
                if int(b) < elimstrikes:
                    playersetout[a] = {'strikes': int(b), 'status': 'active'}
                else:
                    playersetout[a] = {'strikes': int(b), 'status': 'eliminated', 'round': roundnum - 1}
            elif inatable:
                if m:
                    awardstrikes()  #Call the awardstrikes subfunction defined above
                    tblscores = []  #The previous table we were compiling has ended, so clear the tblscores array
                    if mm == 'group':
                        inatable = False
                    elif mm == 'bye':
                        inatable = False
                        byeplayers = True
                        byeoccurred = True
                    elif mm == 'add':
                        inatable = False
                        addplayers = True
                elif (not c.isdigit()) and re.match(r'drop', d, re.IGNORECASE):
                    playersetout[a] = {'strikes': (int(b) if b.isdigit() else elimstrikes),
                                       'status': 'dropped out', 'round': roundnum}
                else:
                    if not (b.isdigit() and c.isdigit()):
                        err("In file '" + filename + "', player " + a + " requires a strikes value and a game score value.")
                    if not re.match(r'add', d, re.IGNORECASE):
                        if a not in playersetin:
                            err("In file '" + filename + "', " + a + " is not a known player.")
                        if not playersetin[a]['status'] == 'active':
                            err("In file '" + filename + "', " + a + " is no longer active in the tournament.")
                    tblscores.append([a, int(b), int(c), d])  #Add the player to the tblscores array for the current table
            elif m and mm == 'table':
                inatable = True
                tblscores = []  #The previous table we were compiling has ended, so clear the tblscores array
    if inatable:
        awardstrikes()  #Call the awardstrikes subfunction defined above
    for key in playersetin:
        if playersetin[key]['status'] == 'active' and not (key in playersetout):
            err("Expected to find player " + key + " included in results file '" + filename + "'.")
    activeplayers = []
    for key in playersetout:
        if playersetout[key]['status'] == 'active': activeplayers.append(key)
    if len(activeplayers) < mintablesize or (len(activeplayers) == 2 and tiebreak2p and
                                             not (len(tables) == 1 and len(tables[0]) == 2)):
        #Here we have determined that the number of active players left is not enough to fill a table
        #of the minimum table size (3 or 2). So now we must set each of those remaining 'active' players
        #to either 'winner', 'runner-up', or 'cowinner'.
        atables = []
        for tbl in tables:  #Build a new atables array of tables where not all its players were eliminated
            activetable = False
            for plyr in tbl:
                if playersetout[plyr[0]]['status'] == 'active': activetable = True
            if activetable: atables.append(tbl)
        if len(activeplayers) == 1:  #If there's only one player who has not been eliminated, declare him 'winner'.
            playersetout[activeplayers[0]]['status'] = 'winner'
            ruleapplied = "All players but one have been eliminated by strikes. That one is the winner."
        elif len(activeplayers) == 0:
            #If all players are eliminated, the one with the fewest strikes among those who played
            #in this round is 'winner', or all tied with fewest are 'cowinner'.
            strikeslist = []
            for p in playersetout:
                if playersetout[p]['status'] == 'eliminated':
                    strikeslist.append(playersetout[p]['strikes'])
            winstrikes = min(strikeslist)
            winplyrs = []
            for p in playersetout:
                if playersetout[p]['status'] == 'eliminated' and playersetout[p]['strikes'] == winstrikes:
                    winplyrs.append(p)
            ruleapplied = "All players have been eliminated by strikes. "
            if len(winplyrs) == 1:
                playersetout[winplyrs[0]]['status'] = 'winner'
                ruleapplied += "The one with the fewest srikes who played in the last round is the winner."
            else:
                for p in winplyrs:
                    playersetout[p]['status'] = 'cowinner'
                ruleapplied += "Those tied with the fewest strikes who played in the last round are cowinners."
        elif len(atables) == 1:
            #Here we figure out the case where all players are eliminated except 2,
            #and the last round consisted of only one table. The rules are:
            #1. If the player now with the fewest strikes (or tied for fewest) was also the
            #winner of that final game, then he is 'winner' and the other is 'runner-up'.
            #2. If the player with the fewest strikes came in 3rd place or worse in the final game,
            #then he is 'runner-up' and the other is 'winner'.
            #3. If the player with the fewest strikes came in 2nd place in the final game,
            #then the two players are both 'cowinner'.
            #4. If one of the players sat out on a Bye, then the two players are 'cowinner'.
            ruleapplied = "All players but two have been eliminated by strikes. "
            if byeoccurred:  #If a Bye was set, then mintablesize must be 3 not 2
                playersetout[activeplayers[0]]['status'] = 'cowinner'
                playersetout[activeplayers[1]]['status'] = 'cowinner'
                ruleapplied += "One of the two had a bye in the last round. The two players are cowinners."
            else:
                apscores = [0,0]
                for plyr in atables[0]:
                    if plyr[0] == activeplayers[0]:
                        apscores[0] = plyr[2]
                    if plyr[0] == activeplayers[1]:
                        apscores[1] = plyr[2]
                if apscores[0] == apscores[1]:
                    if playersetout[activeplayers[0]]['strikes'] == playersetout[activeplayers[1]]['strikes']:
                        ruleapplied += "The two tied in the last game and finished with the same number of strikes. "
                        if not (mintablesize == 2):
                            playersetout[activeplayers[0]]['status'] = 'cowinner'
                            playersetout[activeplayers[1]]['status'] = 'cowinner'
                            ruleapplied += "They are cowinners."
                        else:
                            ruleapplied += "They will play one tiebreaking 2-player game."
                    elif playersetout[activeplayers[0]]['strikes'] < playersetout[activeplayers[1]]['strikes']:
                        playersetout[activeplayers[0]]['status'] = 'winner'
                        playersetout[activeplayers[1]]['status'] = 'runner-up'
                        ruleapplied += "The two tied in the last game. The one with fewer strikes is the winner."
                    else:
                        playersetout[activeplayers[0]]['status'] = 'runner-up'
                        playersetout[activeplayers[1]]['status'] = 'winner'
                        ruleapplied += "The two tied in the last game. The one with fewer strikes is the winner."
                elif apscores[0] > apscores[1] and playersetout[activeplayers[0]]['strikes'] < playersetout[activeplayers[1]]['strikes']:
                    playersetout[activeplayers[0]]['status'] = 'winner'
                    playersetout[activeplayers[1]]['status'] = 'runner-up'
                    ruleapplied += "The winner of the last game is also the one with fewer strikes. That one is the winner."
                elif apscores[1] > apscores[0] and playersetout[activeplayers[1]]['strikes'] < playersetout[activeplayers[0]]['strikes']:
                    playersetout[activeplayers[0]]['status'] = 'runner-up'
                    playersetout[activeplayers[1]]['status'] = 'winner'
                    ruleapplied += "The winner of the last game is also the one with fewer strikes. That one is the winner."
                elif playersetout[activeplayers[0]]['strikes'] == playersetout[activeplayers[1]]['strikes']:
                    if apscores[0] > apscores[1]:
                        playersetout[activeplayers[0]]['status'] = 'winner'
                        playersetout[activeplayers[1]]['status'] = 'runner-up'
                    else:
                        playersetout[activeplayers[0]]['status'] = 'runner-up'
                        playersetout[activeplayers[1]]['status'] = 'winner'
                    ruleapplied += "The two players finished with the same number of strikes. " \
                                   "The winner of the last game is the tournament winner."
                else:
                    tblsorted = sorted(atables[0], key=itemgetter(2), reverse=True)
                    if min(apscores) == tblsorted[1][2]:
                        ruleapplied += "The one who finished with fewer strikes came in 2nd place in the last game. "
                        if not (mintablesize == 2):
                            playersetout[activeplayers[0]]['status'] = 'cowinner'
                            playersetout[activeplayers[1]]['status'] = 'cowinner'
                            ruleapplied += "The two players are cowinners."
                        else:
                            ruleapplied += "The two will play one tiebreaking 2-player game."
                    elif apscores[0] == max(apscores):
                        playersetout[activeplayers[0]]['status'] = 'winner'
                        playersetout[activeplayers[1]]['status'] = 'runner-up'
                        ruleapplied += "The one who finished with fewer strikes came in 3rd place or worse in the last game. " \
                                       "The winner of the last game is the tournament winner."
                    else:
                        playersetout[activeplayers[0]]['status'] = 'runner-up'
                        playersetout[activeplayers[1]]['status'] = 'winner'
                        ruleapplied += "The one who finished with fewer strikes came in 3rd place or worse in the last game. " \
                                       "The winner of the last game is the tournament winner."
        elif playersetout[activeplayers[0]]['strikes'] == playersetout[activeplayers[1]]['strikes']:
            #Here we figure out the case where all players are eliminated except 2,
            #and the last round consisted of two tables. The rules are:
            #1. If the players have a different number of strikes now accumulated, then the one
            #with the fewest strikes is 'winner' and the other is 'runner-up'.
            #2. If the players have ended with the same number of strikes, then the player who had
            #the largest margin of victory in his final game is 'winner' and the other is 'runner-up'.
            #If tied for margin of victory, then they are both 'cowinner'.
            ruleapplied = "All players but two have been eliminated by strikes. "
            for tblplayer in atables[0]:
                if tblplayer[0] == activeplayers[0]:
                    tblindex = [0,1]
                elif tblplayer[0] == activeplayers[1]:
                    tblindex = [1,0]
            scorediff = []
            for tbl in atables:
                tblsorted = sorted(tbl, key=itemgetter(2), reverse=True)
                scorediff.append(tblsorted[0][2] - tblsorted[1][2])
            if scorediff[0] == scorediff[1]:
                ruleapplied += "The two played at different tables in the last round. They finished with the same number of strikes " \
                               "and had the same margin of victory in their games. "
                if not (mintablesize == 2):
                    playersetout[activeplayers[0]]['status'] = 'cowinner'
                    playersetout[activeplayers[1]]['status'] = 'cowinner'
                    ruleapplied += "They are cowinners."
                else:
                    ruleapplied += "The two will play one tiebreaking 2-player game."
            elif scorediff[0] > scorediff[1]:
                playersetout[activeplayers[tblindex[0]]]['status'] = 'winner'
                playersetout[activeplayers[tblindex[1]]]['status'] = 'runner-up'
                ruleapplied += "The two played at different tables in the last round and finished with the same number of strikes. " \
                               "The one with the larger margin of victory in his/her last game is the winner."
            else:
                playersetout[activeplayers[tblindex[1]]]['status'] = 'winner'
                playersetout[activeplayers[tblindex[0]]]['status'] = 'runner-up'
                ruleapplied += "The two played at different tables in the last round and finished with the same number of strikes. " \
                               "The one with the larger margin of victory in his/her last game is the winner."
        elif playersetout[activeplayers[0]]['strikes'] < playersetout[activeplayers[1]]['strikes']:
            playersetout[activeplayers[0]]['status'] = 'winner'
            playersetout[activeplayers[1]]['status'] = 'runner-up'
            ruleapplied = "All players but two have been eliminated by strikes. " \
                          "The two played at different tables in the last round. The one with fewer strikes is the winner."
        else:
            playersetout[activeplayers[0]]['status'] = 'runner-up'
            playersetout[activeplayers[1]]['status'] = 'winner'
            ruleapplied = "All players but two have been eliminated by strikes. " \
                          "The two played at different tables in the last round. The one with fewer strikes is the winner."
    elif len(activeplayers) == 2 and len(tables) == 1 and len(tables[0]) == 2:
        #Here the last round consisted of just one 2-player table, but both players emerged still active.
        #Rather than play another round, end the tournament here.
        #Make the last game winner the 'winner' regardless of strikes. The other player is 'runner-up'.
        #If the last game ended in a tie, then the player with fewer strikes is 'winner'.
        #If that also results in a tie, then both players are 'cowinner'.
        tbl = tables[0]
        if tbl[0][2] > tbl[1][2]:
            playersetout[tbl[0][0]]['status'] = 'winner'
            playersetout[tbl[1][0]]['status'] = 'runner-up'
            ruleapplied = "The winner of a final 2-player game is the winner regardless of strikes accumulated."
        elif tbl[0][2] < tbl[1][2]:
            playersetout[tbl[0][0]]['status'] = 'runner-up'
            playersetout[tbl[1][0]]['status'] = 'winner'
            ruleapplied = "The winner of a final 2-player game is the winner regardless of strikes accumulated."
        else:  #the last game ended in a tie
            ruleapplied = "The final 2-player game ended in a tie. "
            if playersetout[tbl[0][0]]['strikes'] < playersetout[tbl[1][0]]['strikes']:
                playersetout[tbl[0][0]]['status'] = 'winner'
                playersetout[tbl[1][0]]['status'] = 'runner-up'
                ruleapplied += "The player with fewer strikes is the winner."
            elif playersetout[tbl[0][0]]['strikes'] > playersetout[tbl[1][0]]['strikes']:
                playersetout[tbl[0][0]]['status'] = 'runner-up'
                playersetout[tbl[1][0]]['status'] = 'winner'
                ruleapplied += "The player with fewer strikes is the winner."
            else:  #and the players finished with the same number of strikes
                playersetout[tbl[0][0]]['status'] = 'cowinner'
                playersetout[tbl[1][0]]['status'] = 'cowinner'
                ruleapplied += "The two players finished with the same number of strikes. They are cowinners."
    return [playersetout, pairsout, ruleapplied]

#
# FUNCTION standings(roundnum, playerset)
# Called after the latest round results have been processed.
# Generates the player standings file.
# Returns a boolean telling whether or not to continue on to another round.
#
def standings(roundnum, playerset, ruleapplied):
    flines = []
    flines.append('TABLETWIST PLAYER STANDINGS')
    flines.append(tourname)
    flines.append('Generated,' + datetime.now().strftime('%d-%b-%Y %H:%M'))
    flines.append('At End Of Round,' + str(roundnum))
    flines.append('Place,Name,Strikes,Status')
    playerlist = []
    statuses = ['winner','cowinner','runner-up','active','eliminated']
    place = 1
    strikesmax = 0
    for key in playerset:
        if playerset[key]['strikes'] > strikesmax:
            strikesmax = playerset[key]['strikes']
    for stat in statuses:  #These deep-nested 'for' and 'if' sections sort the players in tournament 'place' ranking
        for rnd in range(roundnum, 0, -1):
            if stat == 'eliminated' or rnd == 1:
                for j in range(0, (2 if stat == 'eliminated' else 1)):
                    for i in range(0, strikesmax + 1):
                        pcount = 0
                        for key in playerset:
                            if playerset[key]['strikes'] == i and \
                               playerset[key]['status'] == (stat if j == 0 else 'dropped out') and \
                               ((not (stat == 'eliminated')) or playerset[key]['round'] == rnd):
                                playerlist.append([place, key, i, playerset[key]['status']])
                                pcount += 1
                        place += pcount
    activecount = 0
    for p in playerlist:
        if p[3] == 'active': activecount += 1
        elif p[3] == 'cowinner': p[0] = 1
    keepgoing = (activecount >= mintablesize)
    for p in playerlist:  #Construct each player's line for the standings file
        flines.append(str(p[0]) + ',' + p[1] + ',' + str(p[2]) + ('' if p[3] == 'active' else (',' + p[3].upper())))
    if ruleapplied: flines.append('\nRule Applied,' + ruleapplied)
    for i in range(0, len(flines)):
        flines[i] += '\n'
    filename = tshortname + ' standings ' + str(roundnum) + '.csv'
    f = open(os.path.join(mydir, filename), 'w')
    f.writelines(flines)  #Write all lines to the standings file
    f.close()
    print("Generated " + ("" if roundnum == 1 else "new ") + "standings file '" + filename + "'")
    if keepgoing: print("Number of players remaining:", activecount)
    return keepgoing

#
# MAIN PROGRAM BEGINS HERE
#
print("Tabletwist Boardgame Tournament Manager v1.2")

#Build fileset - the set of all files in this program's folder
mydir = sys.path[0]
dirfiles = set()
for item in os.scandir(mydir):
    if not item.name.startswith('.') and item.is_file():
        dirfiles.add(item.name)

#Check that there's exactly one start.csv file and get tournament short name
sfiles = set()
for file in dirfiles:
    m = re.match(r'(.+?)\s+start\.csv', file, re.IGNORECASE)
    if m:
        sfiles.add(m.group(0))
        tshortname = m.group(1)
if len(sfiles) == 0:
    err("No start file found. File name must be like '<tournament short name> start.csv'.")
if len(sfiles) > 1:
    err('More than one start file found in folder.')
startfile = next(iter(sfiles))

#Parse start file and build starting set of players
f = open(os.path.join(mydir, startfile))
flines = f.readlines()
f.close()
print("\nLoaded tournament start file '" + startfile + "'")
tourname = 'Unnamed Tournament'
elimstrikes = 35
maxtablesize = 5
mintablesize = 3
listflag = False
players = list()
for line in flines:
    line = line.strip()
    line = re.sub(r'\s+', ' ', line)
    if listflag:
        if line and line[0] != '#':
            if line in players:
                err("Repeated player name '" + line + "' found in start file.")
            players.append(line)
    else:
        L = line.split(',')
        L.extend(['',''])
        a, b = L[0:2]; a = a.strip(); b = b.strip()
        if re.match(r'name\s+of\s+t', a, re.IGNORECASE):
            tourname = b
        elif re.match(r'number\s+of\s+strikes', a, re.IGNORECASE):
            elimstrikes = int(b)
        elif re.match(r'maximum\s+number\s+of\s+p', a, re.IGNORECASE):
            maxtablesize = int(b)
        elif re.match(r'minimum\s+number\s+of\s+p', a, re.IGNORECASE):
            mintablesize = int(b)
        elif re.match(r'list\s+of\s+p', a, re.IGNORECASE):
            listflag = True
if len(players) < 3:
    err('Fewer than three players found in start file.')
if not (maxtablesize == 4 or maxtablesize == 5):
    err('Maximum Number Of Players must equal 5 or 4.')
if not (mintablesize == 2 or mintablesize == 3):
    err('Minimum Number Of Players must equal 3 or 2.')
if mintablesize >= maxtablesize:
    err('Maximum Number Of Players must be more than Minimum.')
print("Tournament name:", tourname)
print("Tournament short name:", tshortname)
print("Elimination strikes:", elimstrikes)

#Find all results files and determine round number that just finished
rfiles = {}
lastroundnum = 0
for file in dirfiles:
    m = re.match(tshortname + r'\s+round\s+(\d+)\s+results?\.csv', file, re.IGNORECASE)
    if m:
        r = m.group(1)
        if r in rfiles:
            err('More than one results file found for round ' + r +'.')
        rfiles[r] = m.group(0)
        if int(r) > lastroundnum: lastroundnum = int(r)
rflist = []
for i in range(0, lastroundnum):
    r = str(i+1)
    if r in rfiles:
        rflist.append(rfiles[r])
    else:
        err('Missing results file for round ' + r + '.')

#Process all results files, generate player standings file,
#and generate table seating file for next round.

#Build initial playerset dict. Key is player name. Value is a dict including 'strikes',
#'status' of active, eliminated, dropped out, winner, cowinner, or runner-up,
#and optional 'round' which is round number in which player was eliminated or dropped out.
playerset = {}
for p in players:
    playerset[p] = {'strikes': 0, 'status': 'active'}
pairs = []
if lastroundnum == 0:  #First round, just generate first table seating file.
    print('Players in a game:', mintablesize, 'to', maxtablesize)
    print('Number of players:', len(players))
    seating_randround(1, playerset, pairs)
    keepgoing = True
elif lastroundnum == 1:  #Second round, process one results file and generate second table seating.
    playerset, pairs, ruleapplied = resultsfileproc(rflist[0], playerset, pairs)
    keepgoing = standings(1, playerset, ruleapplied)
    if keepgoing:
        seating_splitround(2, playerset, pairs)
else:  #Subsequent rounds, process all results files, updating the playerset and pairs structures in a loop.
    for i in range(0, lastroundnum):
        playersetx, pairs, ruleapplied = resultsfileproc(rflist[i], playerset, pairs)
        playerset.update(playersetx)
    keepgoing = standings(lastroundnum, playerset, ruleapplied)
    if keepgoing:
        if lastroundnum % 2 == 0:  #Alternate Random type and Split By Strikes type of round.
            seating_randround(lastroundnum + 1, playerset, pairs)
        else:
            seating_splitround(lastroundnum + 1, playerset, pairs)
if not keepgoing:
    print('\nEND OF TOURNAMENT - SEE FINAL STANDINGS FILE.')
input('\nPress Enter to close...')

#
# END OF MAIN PROGRAM
#
