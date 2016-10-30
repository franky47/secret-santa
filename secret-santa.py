# -*- coding: utf-8 -*-

import random
import smtplib
import copy
import csv

# ------------------------------------------------------------------------------

class Person:
    def __init__(self, name, email):
        self.name  = name
        self.email = email

    # --

    def __eq__(self, other):
        return self.name == other.name and self.email == other.email

    # --

    def __repr__(self):
        return '<%s>' % self.name

    def __str__(self):
        return '%s <%s>' % (self.name, self.email)

# ------------------------------------------------------------------------------

class Pair:
    def __init__(self, giver, receiver):
        assert isinstance(giver,    Person)
        assert isinstance(receiver, Person)
        self.giver    = giver
        self.receiver = receiver

    # --

    def reverse(self):
        return Pair(self.receiver, self.giver)

    # --

    def __eq__(self, other):
        return self.giver == other.giver and self.receiver == other.receiver

    # --

    def __str__(self):
        return '%s -> %s' % (self.giver.name, self.receiver.name)

    def __repr__(self):
        return '<Pair %s, %s>' % (self.giver.name, self.receiver.name)

# ------------------------------------------------------------------------------

class Engine:
    def __init__(self):
        random.seed()
        self.players = [
            Person('Franky',    'francoisbest@gmail.com'),
            Person('Penny',     'penny.rose.buckley@gmail.com'),
            # Person('Ellie',     'elliejvj@hotmail.com'),
            # Person('Ben',       'benjamin.leger.40@gmail.com'),
            Person('Adrien',    'adrien59cadri@gmail.com'),
            Person('Emma',      'emma.l.armitage@gmail.com'),
            Person('Grace',     'ghollon163@gmail.com'),
            Person('Marco',     'antoniusbloch@hotmail.it'),
            Person('Rhiannon',  'rhiannon_batcup@hotmail.com'),
            Person('Loic',      'loic.baesso@yahoo.fr'),
            Person('Kate',      'katastrphic@hotmail.com'),
            Person('Ryan',      'ryan.rumble@hotmail.co.uk'),
            Person('Patrick',   'patrickbriggs89@gmail.com'),
            # Person('Eleanor',   'et8231@my.bristol.ac.uk'),
            # Person('Philippe',  'philippebest@yahoo.fr'),
            # Person('Myriam',    'myriam.best@yahoo.fr'),
            Person('Charlotte', 'charliestillwell@yahoo.com'),
            Person('Katherine', 'katherine-moynihan@outlook.com'),
            Person('Danielle',  'danielletaylor0910@gmail.com'),
            Person('Jennifer',  'jennifer.channell@gmail.com'),
            Person('Jess',      'jessicasmall23@aol.com'),
            Person('Adam',      'adam.carter.1992@gmail.com'),
            Person('Katie',     'katie.heidrich@gmail.com'),
            Person('Marie',     'marie.cck@gmail.com')
        ]
        self.couples = [
            ('Franky',      'Penny'),
            ('Adrien',      'Emma'),
            # ('Ellie',       'Ben'),
            ('Grace',       'Marco'),
            ('Rhiannon',    'Loic'),
            ('Jess',        'Adam'),
        ]
        self.unacquainted = [
            (('Adrien',), ('Adam', 'Jess', 'Katie', 'Marie', 'Charlotte')),
            (('Rhiannon',), ('Adam',)),
            (('Loic',), ('Jess', 'Adam', 'Katie', 'Marie', 'Jennifer', 'Danielle')),
            (('Marco', 'Grace'), ('Adam', 'Jennifer', 'Danielle', 'Katie', 'Marie', 'Jess')),
            (('Charlotte',), ('Katie', 'Danielle', 'Jennifer', 'Adam', 'Marie')),
            (('Katherine',), ('Adam', 'Katie', 'Danielle')),
            (('Jess',), ('Marie', 'Jennifer')),
            (('Adam',), ('Franky', 'Penny', 'Emma', 'Kate', 'Ryan', 'Jennifer', 'Marie')),
        ]

        self.unassignedReceivers = copy.deepcopy(self.players)
        self.assignments = []
        self.previousYearAssignments = []
        with open('/Users/franky/Desktop/swamp/secret-santa/secret_santa_2015.txt', 'r') as f:
            for line in f.readlines():
                giver, sep, receiver = line.strip().split()
                self.previousYearAssignments.append((giver, receiver))

    # --

    def pickReceiverFor(self, giver):
        pickedReceiver = None

        if not any([self.checkPair(giver, x) for x in self.unassigned]):
            # No possible choices
            return None

        while not self.checkPair(giver, pickedReceiver):
            pickedReceiver = random.choice(self.unassigned)

        self.unassigned.remove(pickedReceiver)
        return pickedReceiver

    def checkPair(self, giver, receiver):
        if giver is None or receiver is None:
            return False
        if giver == receiver:
            return False

        # Exclude couples
        for couple in self.couples:
            if giver.name in couple and receiver.name in couple:
                return False

        # Exclude people that might not know each other
        for unacquainted in self.unacquainted:
            if giver.name in unacquainted[0] and receiver.name in unacquainted[1]:
                return False
            if giver.name in unacquainted[1] and receiver.name in unacquainted[0]:
                return False

        # Exclude previous year assignments
        for pya in self.previousYearAssignments:
            if giver.name == pya[0] and receiver.name == pya[1]:
                return False

        return True

    # --

    def run(self):
        while not self.check():
            self.unassigned = copy.deepcopy(self.players)
            players = copy.deepcopy(self.players)
            self.assignments = []

            while players:
                giver = random.choice(players)
                receiver = self.pickReceiverFor(giver)
                if receiver is None:
                    break
                players.remove(giver)
                self.assignments.append(Pair(giver, receiver))

    # --

    def check(self):
        if len(self.assignments) != len(self.players):
            return False

        # Check for direct exchanges
        reversedList = [p.reverse() for p in self.assignments]
        loops = [x == r for x in self.assignments for r in reversedList]
        if any(loops):
            return False
        return True

# ------------------------------------------------------------------------------

class EmailNotifier:
    def __init__(self):
        self.messageTemplate = """
Ho, Ho, Ho !

Hello {giver},

You have been cordially invited to Thanksmas on the 3rd of December, when we shall put gifts under the tree and open them after having stuffed ourselves with good food.

You are giving a gift to {receiver}.

The recommended budget is around 15 euros. Happy shopping !

Geekly yours,
The Secret Santa Gift Assignment Fun Bot.
"""

    # --

    def run(self, results):
        for pair in results:
            self.sendEmail(pair)

    def sendEmail(self, pair):
        message = self.messageTemplate.format(giver = pair.giver.name, receiver = pair.receiver.name)
        address = [pair.giver.email]
        self.internalSendEmail(address, message)
        print('Sent email to %s' % str(pair.giver))

    # --

    def internalSendEmail(self, recipients, message):
        smtpserver='smtp.gmail.com:587'
        header  = 'From: francoisbest@gmail.com\n'
        header += 'To: %s\n' % ','.join(recipients)
        header += 'Subject: Secret Santa\n\n'
        message = header + message

        server = smtplib.SMTP(smtpserver)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login('francoisbest', 'viiuxselzxfeykde')
        server.sendmail('francoisbest@gmail.com', recipients, message)
        server.quit()

# ------------------------------------------------------------------------------

class FileLogger:
    def __init__(self):
        self.path = '/Users/franky/Desktop/swamp/secret-santa/secret_santa_2016-friends.txt'

    # --

    def run(self, results):
        with open(self.path, 'w') as f:
            for pair in results:
                f.write(str(pair) + '\n')

# ------------------------------------------------------------------------------

def runGame():
    engine = Engine()
    engine.run()
    return engine.assignments

def testBias():
    results = []
    engine  = Engine()
    players = [x.name for x in engine.players]
    players.sort()

    for i in range(0, 100):
        print('Run %d' % i)
        results.append(runGame())

    # CSV Output
    with open('/Users/franky/Desktop/results.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        header = ['Players'] + players
        writer.writerow(header)

        for y in range(0, len(players)):
            giver = players[y]
            row = [giver]
            for x in range(0, len(players)):
                receiver = players[x]
                score = 0
                for result in results:
                    for pair in result:
                        if pair.giver.name == giver and pair.receiver.name == receiver:
                            score = score + 1
                row.append(score)
            writer.writerow(row)

def main():
    # testBias()
    results = runGame()
    logger = FileLogger()
    logger.run(results)
    notifier = EmailNotifier()
    notifier.run(results)

# ------------------------------------------------------------------------------
# Main entrypoint

if __name__ == '__main__':
    main()
