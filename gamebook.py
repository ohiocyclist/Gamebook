#############################################
#
# Gamebook.py
#
# By Benjamin Buck
#
# Run or Edit a Choose-Your-Own-Adventure Story
# Lines starting with a '#' are comments that do not
# affect code execution but may improve readability
#
##############################################
#
# adventure tree data structure: a dictionary
# top level should start with the nodes of the adventure
# there should be a "start" node
# each node is also a dictionary that has:
# - prompt "prompt"
# - choice messages "messages"
# - choice node names "nodes" (or "end")
#
# This setup doesn't *quite* demonstrate pointers, but
# every named target node should correspond to an actual
# possible named location (just like with pointers...)
#
##############################################

# we need os to check if gamebook source files exist
import os
# json (Jason) allows us to translate the instructions in memory
# into human readable strings to store as gamebook files
import json


# The general flow of the code is functions that call each
# other.  Which function gets called depends on what the user
# enters.  This is the first function, called at the bottom
# of the code ("if __name__ == '__main__'")
# The area between the triple quotes is a "docstring" and helps
# both users and apps understand what our functions do
def mainmenu():
    """

    Gamebook Main Menu

    inputs: None
    actions: selects what to do
    return: None
    """

    # run the main action loop forever, or until told to quit
    # initialize this to blank, so we can check it later
    # our adventure tree is a dictionary, allowing us to
    # reference locations in the adventure by name
    adventuretree = dict()
    while True:
        # skip a line
        print("")
        print("Welcome to Choose-Your-Own-Adventure!")
        print("Please select from the following options!")
        print("1. Open an adventure file")
        print("2. Run the current adventure")
        print("3. Edit the current adventure")
        print("4. Accuracy check the current adventure")
        print("5. Save the current adventure")
        print("6. Exit the program")
        userchoice = input()
        # the functions to handle these options are shown next
        if userchoice == "1":
            newtree = adventureopen()
            # do not overwrite the current tree if we fail to open
            if newtree is not None:
                adventuretree = newtree
        # elif is short for "else if".  Only check this if the first
        # condition wasn't met
        elif userchoice == "2":
            adventurerun(adventuretree)
        elif userchoice == "3":
            newtree = adventureedit(adventuretree)
            if newtree is not None:
                adventuretree = newtree
        elif userchoice == "4":
            adventurecheck(adventuretree)
        elif userchoice == "5":
            adventuresave(adventuretree)
        elif userchoice == "6":
            # this ends the always running loop
            break
        else:
            print("Please enter 1, 2, 3, 4, 5, or 6.  You entered", userchoice)
            print("")
            # at this point the loop starts over with the prompt again

# closing out the indentation ends the mainmenu() function


def adventureopen():
    """

    Read an adventure source file from the disk
    Adventure source files are in JSON format

    inputs: None
    actions: get a filename from the user and attempt to open it
    return: warnings and "None" if the file cannot be read otherwise an
            adventure tree
    """

    print("Please enter the name of an existing adventure file.")
    adventurefilename = input()
    # check that the file exists
    if not os.path.isfile(adventurefilename):
        print("I cannot find your adventure file.")
        # bail out here!
        return None
    # the file remains open through the indented block
    with open(adventurefilename, 'r') as fh:
        # read the whole file into our dictionary data structure
        # don't let the program fail out if this doesn't work
        # if there is an error, display it and continue
        try:
            wholefilecontents = fh.read()
            newtree = json.loads(wholefilecontents)
        except Exception as errormessage:
            print("I could not read the file and turn it into a dictionary.")
            print("I got the error:", errormessage)
            # bail out here!
            return None
    # do one last check that it's a valid adventure file
    if "start" not in newtree:
        print("bad adventure file loaded: no start node")
        return None
    # we're good!
    return newtree


def adventurerun(adventuretree, currentnode="start"):
    """

    Run the gamebook adventure  (it must be loaded)
    This is designed to run any node in the adventure,
    so it calls itself with the new node name when you choose

    inputs: the adventure tree to run
            which node to run the adventure from (defaults to the start)
    actions: guide the user through the entire adventure
    return: Nothing
    """

    # check for missing values
    if adventuretree is None:
        print("no adventure loaded to run")
        return None
    if currentnode not in adventuretree:
        print("adventure missing requested node", currentnode)
        return None
    # do some good data checks on our dictionary
    # the '\' allows me to span this line because it's too long
    if "prompt" not in adventuretree[currentnode] or "messages" not in \
            adventuretree[currentnode] or "nodes" not in \
            adventuretree[currentnode]:
        print("Corrupted node", currentnode,
              "it should have prompt, messages, and nodes.")
        return None
    if len(adventuretree[currentnode]["messages"]) != \
            len(adventuretree[currentnode]["nodes"]):
        print("number of target nodes must match the number of",
              "choice messages.")
        return None
    print(adventuretree[currentnode]["prompt"])
    # no more choices means the adventure is over.
    if len(adventuretree[currentnode]["messages"]) == 0:
        print("THE END")
        return None

    # list as many messages as are in the message list
    # counter counts from zero.  We want to count from 1, so there's a
    # little translation
    # the list information also counts from zero, so it needs translation too.
    for counter, mymessage in \
            enumerate(adventuretree[currentnode]["messages"]):
        print(str(counter + 1) + ".", mymessage)
    print("R. Return to the Main Menu")
    # make the user select one of our options
    while True:
        userselection = input()
        if userselection == "R":
            print("Bye, thanks for playing!")
            return None
        # scrub for things that don't coerce to integers
        try:
            int(userselection)
            isitint = True
        except ValueError:
            isitint = False
        # if not isitint it will stop processing conditions that would error
        if isitint and int(userselection) > 0 and int(userselection) <= \
                len(adventuretree[currentnode]["messages"]):
            # the list we present the user starts with 1 but the list
            # Python keeps starts from 0, hence - 1.
            targetnode = \
                adventuretree[currentnode]["nodes"][int(userselection) - 1]
            # more good data check
            if targetnode not in adventuretree:
                print("Bad node!  Missing node in the adventure", targetnode)
                return None
            # the same function runs the next node
            adventurerun(adventuretree, targetnode)
            # need to get out of this loop to get out of this function
            break
        print("Please select from one of the numbered selections or",
              "enter 'R' to return to the main menu.")


def adventurecheck(adventuretree):
    """

    Do an accuracy check on the current adventure.
    Find missing nodes.

    inputs: tree to check
    actions: show whether the check is good or not
    return: nothing
    """

    if adventuretree is None:
        print("No tree to check!")
        return None
    # this allows us to print "no errors" at the end
    cleancheck = True
    if "start" not in adventuretree:
        print("No start node!")
        return None
    # check that all target nodes exist
    for mynode in adventuretree:
        # these are all this nodes targets
        for mytargetnode in adventuretree[mynode]["nodes"]:
            if mytargetnode not in adventuretree:
                print("Missing Target Node:", mytargetnode)
                cleancheck = False
    if cleancheck:
        print("No missing nodes found")


def adventureedit(adventuretree):
    """

    Make Changes to the adventure tree
    select a node to change and enter new information

    inputs: the tree to modify
    actions: add or replace nodes
    return: modified tree
    """

    print("These nodes are already part of the tree:")
    linelen = 0
    for mynode in adventuretree:
        # end: print them all out as a string, not one per line
        print(mynode, end=", ")
        # well do some line tricks too
        linelen += len(mynode)
        if linelen > 70:
            # new line time!
            print("")
            linelen = 0
    # end the previous node list on a new line
    print("")
    print("Please name or create a node to edit, starting with 'start'",
          "(or type quit! to return to the main menu")
    # need to be able to come back to this
    while True:
        nodeedit = input()
        if nodeedit in adventuretree:
            print("You will be replacing an existing node. ",
                  "Is that ok? (Type Y -Enter for yes)")
            confirm = input()
            # accept a few forms of yes, anything starting with a "Y"
            if confirm.lower()[0] == 'y':
                break
        elif nodeedit.lower() == "quit!":
            return adventuretree
        else:
            # break for all new nodes
            break
    # we need to initialize a blank dictionary for a new node
    print("Please enter the prompt text for this node. ",
          "You may use several lines.  When you are done, enter '//'-Enter")
    # show what exists if we're replacing it
    if nodeedit in adventuretree:
        print("The current prompt is:", adventuretree[nodeedit]["prompt"])
    adventuretree[nodeedit] = {}
    adventuretree[nodeedit]["prompt"] = ""
    while True:
        newprompt = input()
        if newprompt == '//':
            break
        else:
            adventuretree[nodeedit]["prompt"] += newprompt + '\n'
    print("Thank you for the prompt.  How many branches would you like? ",
          "Please enter a number from 0 (making this an end node) to 9.")
    # scrub again for valid input
    while True:
        numbranches = input()
        # don't throw an error if we can't coerce to int
        try:
            int(numbranches)
            isitint = True
        except ValueError:
            isitint = False
        if isitint and int(numbranches) >= 0 and int(numbranches) <= 9:
            break
        print("Please enter a number from 0 to 9.")
    # make sure we have a place to put the results
    adventuretree[nodeedit]["messages"] = []
    adventuretree[nodeedit]["nodes"] = []
    for counter in range(int(numbranches)):
        # Python starts counting at 0
        print("Enter the message for choice #", counter + 1)
        adventuretree[nodeedit]["messages"].append(input())
        print("Enter the target node name for choice #", counter + 1)
        adventuretree[nodeedit]["nodes"].append(input())
    print("Thank you for entering node", nodeedit)
    # restart with a new node
    return adventureedit(adventuretree)


def adventuresave(adventuretree):
    """

    Save a tree as a JSON object

    inputs: the tree to save
    actions: create a file with that tree
    return: nothing
    """

    print("Please enter a filename to save the tree as:")
    myfile = input()
    # check to avoid saving over previous work
    if os.path.isfile(myfile):
        print("WARNING: FILE EXISTS. OVERWRITE?")
        overwrite = input()
        if overwrite.lower()[0] != 'y':
            print("Not overwriting, aborting save.")
            return None
    # catch errors, avoid losing work
    try:
        with open(myfile, 'w') as fh:
            fh.write(json.dumps(adventuretree))
    except Exception as errormessage:
        print("FILE SAVE ERROR:", errormessage)
    print("File Saved, returning to Main Menu")


if __name__ == '__main__':
    mainmenu()

# PEP-8 checking provided by Spyder
