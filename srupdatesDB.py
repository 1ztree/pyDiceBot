import smtplib, email, imaplib, os, re, random, msvcrt, time, Initiative
from email.mime.text import MIMEText

init_list = Initiative()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#TODO:
# 1. Define initiativeMessage, newRoundMessage, roundNotOver, and endCombatMessage functions.
# 2. Define file operations for Initiative.py's updateInitiative and endCombat functions.
# 3. Define file operations for users and passwords to get and send mail.
# 4. Refactor sendMail, buildMessage, modMessage, standardMessage, getMail, and npcMessage functions.
# 5. Refactor Initiative.py and Character.py
# 6. TEST.
# 7. Push to live.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#SEND REPLY EMAIL---------------------------------------------------------------------------------------	
	
def sendMail(email_body, email_subject, email_messageid) :
	user = '@gmail.com'
	pwd = ''
	group = '@gmail.com'

	#Initialize the message container
	msg = MIMEText(email_body)
	msg['Subject'] = email_subject
	msg['Message-ID'] = email_messageid
	msg['From'] = user
	msg['To'] = group

	
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(user,pwd)
	server.sendmail(user, group, msg.as_string())
	server.quit()

# Builds the email message to be sent.
def buildMessage(dice_input):
	# Initialize the modifier variable, the number of hits, and the glitch variable so typing errors are not thrown
	mod = 0
	hits = 0
	glitch = 0
	# Initialize variables representing:
	# 1. The number of dice to be rolled
	# 2. The type of dice to be rolled
	# 3. Any modifications to the roll
	try :
		m = re.match("@Roll ([1-9][0-9]?)D([1-9][0-9]?)\s?\+?\s?([1-9])?", dice_input)
		num_dice = m.group(1)
		type_dice = m.group(2)
		mod = m.group(3) 
		each_roll = []
		total_roll = 0
		each_roll = init_list.rollDice(type_dice, int(num_dice))
		
		#total up the dice, catch the number of hits & glitches
		for  roll in each_roll:
			total_roll = total_roll + roll
			if (roll == 5 or roll == 6):
				hits += 1
			if (roll == 1):
				glitch += 1
			
		if (mod):
			roll_message =  modMessage(num_dice, type_dice, total_roll, each_roll, mod)
		else:
			roll_message =  standardMessage(num_dice, type_dice, total_roll, each_roll)
			
		roll_message = roll_message + "\n\nNumber of Successes: " + str(hits)
		if (glitch > (int(num_dice) / 2)) :
			if (hits == 0) :
				roll_message = roll_message + "\nCritical Glitch!"
			else:
				roll_message = roll_message + "\nGlitch!"
		return roll_message
	except :
		return "\n\nDice roll was improperly formatted. Please format your dice roll request in the following form : \n XDY + Z where X, Y, are integers between 1-99 and Z is an integer between 0-9.\n\n"
		
# Constructs the email message when a modifier exists.
def modMessage(num_dice, type_dice,  total_roll, each_roll, mod):
		t = int(num_dice)
		roll_message = num_dice + "D" + type_dice + " +" + mod + " = "
		while t > 0:
			roll_message = roll_message + str(each_roll[t-1])
			if not (t == 1) :
				roll_message = roll_message + " + "
			else:
				roll_message = roll_message + " + " + str(int(mod))
			t = t - 1
		roll_message = roll_message + " = " + str((total_roll) + int(mod))
		return roll_message


# Constructs the email message when a standard roll is performed.
def standardMessage(num_dice, type_dice,  total_roll, each_roll):
	t = int(num_dice)
	roll_message = num_dice + "D" + type_dice + " = "
	while t > 0:
		roll_message = roll_message + str(each_roll[t-1]) 
		if not (t == 1) :
			roll_message = roll_message + " + "
		t = t - 1
	roll_message =  roll_message + " = " + str((total_roll))
	return roll_message
	
	
	
# GET NEW EMAILS-----------------------------------------------------------------------------------------
def getMail() :
	# directory where to save attachments (default: current)
	detach_dir = '.'
	# Login = @gmail.com
	# Password = 
	user = '@gmail.com'
	pwd = ''

	# connecting to the gmail imap server
	m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
	try:
		m.login(user,pwd)
	except imaplib.IMAP4.error:
		str("LOGIN FAILED!!!")
	# here you a can choose a mail box like INBOX instead
	m.select("inbox") 

	# Get all UNREAD emails.
	resp, items = m.search(None, 'UNSEEN')
	# getting the mail ids

	#For each new email :
	#	- Check for instances of @Roll
	#	- For each instance of @Roll, perform the random dice roll indicated.
	#	- If at least one instance of @Roll exists, compose an email to the group,	
	#		containing each requested dice roll.
	email_body = ""
	email_subject = ""
	email_messageid = ""
	
	try:
		for emailid in items[0].split() :
			# fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
			resp, data = m.fetch (emailid, '(RFC822)') 
			for response_part in data :
				if isinstance(response_part, tuple) :
					msg = email.message_from_string(response_part[1])
					payload = msg.get_payload()
					email_body = extract_body(payload)
					email_subject = msg['Subject']
					email_messageid = msg['Message-ID']
				typ, response = m.store(emailid, '+FLAGS', r'(\Seen)')
			
			if not msg['From'] == "pydicebot@gmail.com" :
				parseEmail(email_body, email_subject, email_messageid)
	finally:
		try:
			m.close()
		except:
			pass
		m.logout()
		
# Pulls apart the email object to get the actual email text.
def extract_body(payload) :
	if isinstance(payload, str) :
		return payload
	else :
		return '\n'.join([extract_body(part.get_payload()) for part in payload])
			
#Used for testing purposes only.
def debugFile(text) :
	f = open('debug.txt', 'w')
	f.write(text)
	f.close()
	
def npcMessage(num_dice, type_dice, total_roll, each_die, mod, this_npc):
	each_die = init_list.rollDice(type_dice, int(num_dice))
	total_roll = totalRoll(each_die)
	message = this_npc + ": "
	if (mod):
		message = message + modMessage(num_dice, type_dice, total_roll, each_die, mod)
	else:
		message = message + standardMessage(num_dice, type_dice, total_roll, each_die)
	return message
	
# Flags the variable representing whether or not the group is in combat, then parses NPC initiative rolls and returns a message to be sent via email.
def startCombat(email_body):
	#Flags the variable representing whether the group is in combat or not.
	init_list.startCombat()
	# This is the message we are going to return to the calling function.
	message = ""
	# If NPCs are involved in this combat, we find any instances of their initiative rolls and compute them.
	if "#Roll" in email_body:
		try:
			regex = re.compile('^#Roll .*\n', re.MULTILINE)
			npc_input = regex.findall(email_body)
			#Add rolls to the initiative list & update initiative doc.
			for each_roll in npc_input:
				# Roll the dice
				# Add each NPC to the initiative list
				init_list.addInitiative(each_roll)

			# Return a message to be sent via email.
			init_list.updateInitiative(False)
		except:
			return "NPC dice rolls improperly formatted. Please properly format your dice rolls and submit them again.\n"
	return message + "Roll for Initiative!\n"

# Adds a list of rolls to the initiative order.
# addInitiative List -> Void
	
# Parse the email body string
# parseEmail String, String, String -> Void
def parseEmail(email_body, email_subject, email_messageid) :
	# If 1+ @Roll exists 
	if "@Roll" in email_body:
		# Create a message text to be sent as an email
		message = ""
		regex = re.compile('^@Roll .*\n', re.MULTILINE)
		match = regex.findall(email_body)
		# For each @Roll, perform dice roll, add results to message text
		for each_roll in match:
			message = message + buildMessage(each_roll) + "\n"
		# Send email
		sendMail(message, email_subject, email_messageid)
	if "#RollInitiative" in email_body:
		sendMail(startCombat(email_body), email_subject, email_messageid)
	if "#Roll" in email_body:
		regex = re.compile('^#RolI .*\n', re.MULTILINE)
		match = regex.findall(email_body)
		for each_roll in match:
			init_list.addInitiative(each_roll)
			init_list.updateInitiative(False)
		sendMail(initiativeMessage(), email_subject, email_messageid)
	if "#NextRound" in email_body:
		try:
			init_list.updateInitiative(True)
			sendMail(newRoundMessage(), email_subject, email_messageid)
		except:
			sendMail(roundNotOverError(), email_subject, email_messageid)
	if "#EndCombat" in email_body:
		init_list.endCombat()
		sendMail(endCombatMessage(), email_subject, email_messageid)


#Main Body Loop
#	- Check new mail every X minutes.
while True :
	getMail()
	if msvcrt.kbhit() :
		break
	time.sleep(300)
	
